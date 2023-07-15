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

from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote_to_bytes

from esmerald.utils.multipart.constants import (
    OPTION_HEADER_PIECE_RE,
    OPTION_HEADER_START_MIME_RE,
    RFC2231_HEADER_CONTINUATION_RE,
)


def get_buffer_last_newline(buffer: bytearray) -> int:
    """Returns the position of the last new line break. Handles malformed new
    line formatting.

    Notes:
        - This function makes use of rindex specifically because -1 is also used. Hence, using find cannot work.
        -  Multipart line breaks MUST be CRLF (\r\n) by RFC-7578, except that many implementations break this and either
            use CR or LF alone.

    Returns:
        Last new line index.
    """
    try:
        last_nl = buffer.rindex(b"\n")
    except ValueError:
        last_nl = len(buffer)
    try:
        last_cr = buffer.rindex(b"\r")
    except ValueError:
        last_cr = len(buffer)

    return min(last_nl, last_cr)


def parse_headers(data: bytes, charset: str = "utf-8") -> Dict[str, str]:
    """Given a message byte string, parse the headers component of it and
    return a dictionary of normalized key/value pairs.

    Args:
        data: A byte string.
        charset: Encoding charset used

    Returns:
        A string / string dictionary of parsed values.
    """
    data = RFC2231_HEADER_CONTINUATION_RE.sub(b" ", data)

    headers: Dict[str, str] = {}
    for name, value in [
        line.decode(charset).split(":", 1) for line in data.splitlines() if line.strip() != b""
    ]:
        headers[name.strip().lower()] = value.strip()

    return headers


def unquote_header_value(value: str, is_filename: bool = False) -> str:
    """Unquotes a header value. This does not use the real unquoting but what
    browsers are actually using for quoting.

    Args:
        value: Value to unquoted.
        is_filename: Boolean flag dictating whether the value is a filename.

    Returns:
        The unquoted value.
    """
    if value and value[0] == value[-1] == '"':
        value = value[1:-1]
        if not is_filename or value[:2] != "\\\\":
            return value.replace("\\\\", "\\").replace('\\"', '"')
    return value


def parse_options_header(value: Optional[str]) -> Tuple[str, Dict[str, str]]:
    """Parses a 'Content-Type' or 'Content-Disposition' header, returning the
    header value and any options as a dictionary.

    Args:
        value: An optional header string.

    Returns:
        A tuple with the parsed value and a dictionary containing any options send in it.
    """
    if not value:
        return "", {}

    result: List[str] = []

    value = "," + value.replace("\n", ",")
    while value:
        match = OPTION_HEADER_START_MIME_RE.match(value)
        if not match:
            break

        result.append(match.group(1))  # mimetype

        options: Dict[str, str] = {}
        rest = match.group(2)
        encoding: Optional[str]
        continued_encoding: Optional[str] = None
        while rest:
            optmatch = OPTION_HEADER_PIECE_RE.match(rest)
            if not optmatch:
                break

            option, count, encoding, _, option_value = optmatch.groups()
            if count and encoding:
                continued_encoding = encoding
            elif count:
                encoding = continued_encoding
            else:
                continued_encoding = None

            option = unquote_header_value(option).lower()

            if option_value is not None:
                option_value = unquote_header_value(option_value, option == "filename")

                if encoding is not None:
                    option_value = unquote_to_bytes(option_value).decode(encoding)

            if not count:
                options[option] = option_value or ""
            elif option_value is not None:
                options[option] = options.get(option, "") + option_value

            rest = rest[optmatch.end() :]
        return result[0], options

    return result[0] if result else "", {}
