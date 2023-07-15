import tempfile
from typing import AsyncGenerator, List, Mapping, Optional, Tuple, Union

from esmerald.datastructures import UploadFile
from esmerald.utils.multipart.decoder import MultipartDecoder
from esmerald.utils.multipart.events import DataEvent, EpilogueEvent, FieldEvent, FileEvent
from esmerald.utils.parsers import parse_options_header


class MultipartFormDataParser:
    __slots__ = ("headers", "stream", "decoder", "charset")

    def __init__(
        self,
        headers: Mapping[str, str],
        stream: AsyncGenerator[bytes, None],
        max_file_size: Optional[int],
        charset: str = "utf-8",
    ) -> None:
        """Parses multipart/formdata.

        Args:
            headers: A mapping of headers.
            stream: An async generator yielding a stream.
            max_file_size: Max file size allowed.
            charset: Charset used to encode the data.
        """
        self.headers = {k.lower(): v for k, v in headers.items()}
        _, options = parse_options_header(self.headers.get("content-type", ""))
        self.stream = stream
        self.charset = options.get("charset", charset)
        self.decoder = MultipartDecoder(
            message_boundary=options.get("boundary", ""),
            max_file_size=max_file_size,
            charset=charset,
        )

    async def parse(self) -> List[Tuple[str, Union[str, UploadFile]]]:
        """Parses a chunk into a list of items.

        Returns:
            A list of tuples, each containing the field name and its value - either a string or an upload file datum.
        """
        items: List[Tuple[str, Union[str, UploadFile]]] = []

        field_name = ""
        data = bytearray()
        upload_file: Optional[UploadFile] = None
        breakpoint()
        while True:
            event = self.decoder.next_event()
            if event is None or isinstance(event, EpilogueEvent):
                break
            if isinstance(event, FieldEvent):
                field_name = event.name
            elif isinstance(event, FileEvent):
                field_name = event.name
                upload_file = UploadFile(
                    file=tempfile.SpooledTemporaryFile(),
                    filename=event.filename,
                    headers=event.headers,
                )
            elif isinstance(event, DataEvent):
                if upload_file:
                    await upload_file.write(event.data)
                    if not event.more_data:
                        await upload_file.seek(0)
                        items.append((field_name, upload_file))
                        upload_file = None
                        data.clear()
                else:
                    data.extend(event.data)
                    if not event.more_data:
                        try:
                            items.append((field_name, data.decode(self.charset)))
                        except UnicodeDecodeError:
                            items.append((field_name, data.decode("latin-1")))
                        data.clear()
        return items

    async def __call__(self) -> List[Tuple[str, Union[str, UploadFile]]]:
        async for chunk in self.stream:
            self.decoder(chunk)
        return await self.parse()
