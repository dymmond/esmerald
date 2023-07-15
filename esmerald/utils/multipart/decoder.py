"""The contents of this file incorporate code adapted from
https://github.com/pallets/werkzeug.

Copyright 2007 Pallets

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1.  Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

2.  Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

3.  Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import re
from typing import Optional, Union

from esmerald.utils.multipart.constants import (
    BLANK_LINE_RE,
    LINE_BREAK,
    SEARCH_BUFFER_LENGTH,
    ProcessingStage,
)
from esmerald.utils.multipart.events import (
    DataEvent,
    EpilogueEvent,
    FieldEvent,
    FileEvent,
    MultipartMessageEvent,
    PreambleEvent,
)
from esmerald.utils.multipart.utils import (
    get_buffer_last_newline,
    parse_headers,
    parse_options_header,
)


class RequestEntityTooLarge(Exception):
    pass


class MultipartDecoder:
    __slots__ = (
        "boundary_re",
        "buffer",
        "charset",
        "max_file_size",
        "message_boundary",
        "preamble_re",
        "processing_stage",
        "search_position",
    )

    def __init__(
        self,
        message_boundary: Union[bytes, str],
        max_file_size: Optional[int] = None,
        charset: str = "utf-8",
    ) -> None:
        """A decoder for multipart messages.

        Args:
            message_boundary: The message message_boundary as specified by [RFC7578][https://www.rfc-editor.org/rfc/rfc7578]
            max_file_size: Maximum number of bytes allowed for the message.
        """
        self.buffer = bytearray()
        self.charset = charset
        self.max_file_size = max_file_size
        self.processing_stage = ProcessingStage.PREAMBLE
        self.search_position = 0
        self.message_boundary = (
            message_boundary
            if isinstance(message_boundary, bytes)
            else message_boundary.encode("latin-1")
        )

        # The preamble must end with a message_boundary where the message_boundary is prefixed by a line break, RFC2046.
        self.preamble_re = re.compile(
            rb"%s?--%s(--[^\S\n\r]*%s?|[^\S\n\r]*%s)"
            % (LINE_BREAK, re.escape(self.message_boundary), LINE_BREAK, LINE_BREAK),
            re.MULTILINE,
        )
        # A message_boundary must include a line break prefix and suffix, and may include trailing whitespace.
        self.boundary_re = re.compile(
            rb"%s--%s(--[^\S\n\r]*%s?|[^\S\n\r]*%s)"
            % (LINE_BREAK, re.escape(self.message_boundary), LINE_BREAK, LINE_BREAK),
            re.MULTILINE,
        )

    def __call__(self, data: bytes) -> None:
        if data:
            if (
                self.max_file_size is not None
                and len(self.buffer) + len(data) > self.max_file_size
            ):
                raise RequestEntityTooLarge()
            self.buffer.extend(data)

    def _process_preamble(self) -> Optional[PreambleEvent]:
        event: Optional[PreambleEvent] = None
        match = self.preamble_re.search(self.buffer, self.search_position)
        if match is not None:
            if match.group(1).startswith(b"--"):
                self.processing_stage = ProcessingStage.EPILOGUE
            else:
                self.processing_stage = ProcessingStage.PART

            data = bytes(self.buffer[: match.start()])
            del self.buffer[: match.end()]
            event = PreambleEvent(data=data)
        if event:
            self.search_position = 0
        else:
            self.search_position = max(
                0, len(self.buffer) - len(self.message_boundary) - SEARCH_BUFFER_LENGTH
            )
        return event

    def _process_part(self) -> Optional[Union[FileEvent, FieldEvent]]:
        event: Optional[Union[FileEvent, FieldEvent]] = None
        match = BLANK_LINE_RE.search(self.buffer, self.search_position)
        if match is not None:
            headers = parse_headers(self.buffer[: match.start()], charset=self.charset)
            del self.buffer[: match.end()]

            content_disposition_header = headers.get("content-disposition")
            if not content_disposition_header:
                raise ValueError("Missing Content-Disposition header")

            _, extra = parse_options_header(content_disposition_header)
            if "filename" in extra:
                event = FileEvent(
                    filename=extra["filename"],
                    headers=headers,
                    name=extra.get("name", ""),
                )
            else:
                event = FieldEvent(
                    headers=headers,
                    name=extra.get("name", ""),
                )
        if event:
            self.search_position = 0
            self.processing_stage = ProcessingStage.DATA
        else:
            self.search_position = max(0, len(self.buffer) - SEARCH_BUFFER_LENGTH)
        return event

    def _process_data(self) -> Optional[DataEvent]:
        match = (
            self.boundary_re.search(self.buffer)
            if self.buffer.find(b"--" + self.message_boundary) != -1
            else None
        )
        if match is not None:
            if match.group(1).startswith(b"--"):
                self.processing_stage = ProcessingStage.EPILOGUE
            else:
                self.processing_stage = ProcessingStage.PART
            data = bytes(self.buffer[: match.start()])
            more_data = False
            del self.buffer[: match.end()]
        else:
            data_length = get_buffer_last_newline(self.buffer)
            data = bytes(self.buffer[:data_length])
            more_data = True
            del self.buffer[:data_length]
        return DataEvent(data=data, more_data=more_data) if data or not more_data else None

    def _process_epilogue(self) -> EpilogueEvent:
        event = EpilogueEvent(data=bytes(self.buffer))
        del self.buffer[:]
        self.processing_stage = ProcessingStage.COMPLETE
        return event

    def next_event(self) -> Optional[MultipartMessageEvent]:
        """Processes the data according the parser's processing_stage. The
        processing_stage is updated according to the parser's processing_stage
        machine logic. Thus calling this method updates the processing_stage as
        well.

        Returns:
            An optional event instance, depending on the processing_stage of the message processing.
        """
        if self.processing_stage == ProcessingStage.PREAMBLE:
            return self._process_preamble()
        if self.processing_stage == ProcessingStage.PART:
            return self._process_part()
        if self.processing_stage == ProcessingStage.DATA:
            return self._process_data()
        if self.processing_stage == ProcessingStage.EPILOGUE:
            return self._process_epilogue()
        return None
