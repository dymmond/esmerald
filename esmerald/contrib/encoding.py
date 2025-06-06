import codecs
import datetime
import locale
from decimal import Decimal
from typing import Any, Optional, Union
from urllib.parse import quote

_PROTECTED_TYPES = (
    type(None),
    int,
    float,
    Decimal,
    datetime.datetime,
    datetime.date,
    datetime.time,
)


class ExtraUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self, obj: Any, *args: Any) -> None:
        self.obj = obj
        super().__init__(*args)

    def __str__(self) -> str:
        return "{}. You passed in {!r} ({})".format(
            super().__str__(),
            self.obj,
            type(self.obj),
        )


def smart_str(
    s: Any, encoding: str = "utf-8", strings_only: bool = False, errors: str = "strict"
) -> str:
    """
    Return a string representing 's'. Treat bytestrings using the 'encoding'
    codec.
    """
    return force_str(s, encoding, strings_only, errors)


def is_protected_type(obj: Any) -> bool:
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_str(strings_only=True).
    """
    return isinstance(obj, _PROTECTED_TYPES)


def force_str(
    s: Any, encoding: str = "utf-8", strings_only: bool = False, errors: str = "strict"
) -> Union[Any, str]:
    """
    Similar to smart_str(), except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if issubclass(type(s), str):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if isinstance(s, bytes):
            s = str(s, encoding, errors)
        else:
            s = str(s)
    except UnicodeDecodeError as e:
        raise ExtraUnicodeDecodeError(s, *e.args) from e
    return s


def smart_bytes(
    s: Any, encoding: str = "utf-8", strings_only: bool = False, errors: str = "strict"
) -> bytes:
    """
    Return a bytestring version of 's', encoded as specified in 'encoding'.
    """
    return force_bytes(s, encoding, strings_only, errors)


def force_bytes(
    s: Any, encoding: str = "utf-8", strings_only: bool = False, errors: str = "strict"
) -> Union[Any, bytes]:
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == "utf-8":
            return s
        else:
            return s.decode("utf-8", errors).encode(encoding, errors)
    if strings_only and is_protected_type(s):
        return s
    if isinstance(s, memoryview):
        return bytes(s)
    return str(s).encode(encoding, errors)


# list of byte values that uri_to_iri() decodes from percent encoding.
# First, the unreserved characters from RFC 3986:
_ascii_ranges = [[45, 46, 95, 126], range(65, 91), range(97, 123)]
_hextobyte = {
    (fmt % char).encode(): bytes((char,))
    for ascii_range in _ascii_ranges
    for char in ascii_range
    for fmt in ["%02x", "%02X"]
}
# And then everything above 128, because bytes ≥ 128 are part of multibyte
# Unicode characters.
_hexdig = "0123456789ABCDEFabcdef"
_hextobyte.update({(a + b).encode(): bytes.fromhex(a + b) for a in _hexdig[8:] for b in _hexdig})


def uri_to_iri(uri: Optional[Union[str, bytes]] = None) -> Union[str, bytes, None]:
    """
    Convert a Uniform Resource Identifier(URI) into an Internationalized
    Resource Identifier(IRI).

    This is the algorithm from section 3.2 of RFC 3987, excluding step 4.

    Take an URI in ASCII bytes (e.g. '/I%20%E2%99%A5%20Django/') and return
    a string containing the encoded result (e.g. '/I%20♥%20Django/').
    """
    if uri is None:
        return uri
    uri = force_bytes(uri)
    # Fast selective unquote: First, split on '%' and then starting with the
    # second block, decode the first 2 bytes if they represent a hex code to
    # decode. The rest of the block is the part after '%AB', not containing
    # any '%'. Add that to the output without further processing.
    # deepcode ignore BadMixOfStrAndBytes: False positive
    bits = uri.split(b"%")
    if len(bits) == 1:
        iri = uri
    else:
        parts = [bits[0]]
        append = parts.append
        hextobyte = _hextobyte
        for item in bits[1:]:
            _hex = item[:2]
            if _hex in hextobyte:
                append(hextobyte[item[:2]])
                append(item[2:])
            else:
                append(b"%")
                append(item)
        iri = b"".join(parts)
    return repercent_broken_unicode(iri).decode()  # type: ignore


def escape_uri_path(path: str) -> Union[str, bytes]:
    """
    Escape the unsafe characters from the path portion of a Uniform Resource
    Identifier (URI).
    """
    # These are the "reserved" and "unreserved" characters specified in
    # sections 2.2 and 2.3 of RFC 2396:
    #   reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" | "$" | ","
    #   unreserved  = alphanum | mark
    #   mark        = "-" | "_" | "." | "!" | "~" | "*" | "'" | "(" | ")"
    # The list of safe characters here is constructed subtracting ";", "=",
    # and "?" according to section 3.3 of RFC 2396.
    # The reason for not subtracting and escaping "/" is that we are escaping
    # the entire path, not a path segment.
    return quote(path, safe="/:@&+$,-_.!~*'()")


def punycode(domain: bytes) -> str:
    """Return the Punycode of the given domain if it's non-ASCII."""
    domain = domain.encode("idna")
    return domain.decode("ascii")


def repercent_broken_unicode(path: str) -> str:
    """
    As per section 3.2 of RFC 3987, step three of converting a URI into an IRI,
    repercent-encode any octet produced that is not part of a strictly legal
    UTF-8 octet sequence.
    """
    while True:
        try:
            path.decode()
        except UnicodeDecodeError as e:
            # CVE-2019-14235: A recursion shouldn't be used since the exception
            # handling uses massive amounts of memory
            repercent = quote(path[e.start : e.end], safe=b"/#%[]=:;$&()+,!?*@'~")
            path = path[: e.start] + repercent.encode() + path[e.end :]  # type: ignore
        else:
            return path


def filepath_to_uri(path: Optional[str] = None) -> Union[str, None]:
    """Convert a file system path to a URI portion that is suitable for
    inclusion in a URL.

    Encode certain chars that would normally be recognized as special chars
    for URIs. Do not encode the ' character, as it is a valid character
    within URIs. See the encodeURIComponent() JavaScript function for details.
    """
    if path is None:
        return path
    # I know about `os.sep` and `os.altsep` but I want to leave
    # some flexibility for hardcoding separators.
    return quote(str(path).replace("\\", "/"), safe="/~!*()'")


def get_system_encoding() -> str:
    """
    The encoding for the character type functions. Fallback to 'ascii' if the
    #encoding is unsupported by Python or could not be determined. See tickets
    #10335 and #5846.
    """
    try:
        encoding = locale.getlocale()[1] or "ascii"
        codecs.lookup(encoding)
    except Exception:
        encoding = "ascii"
    return encoding


DEFAULT_LOCALE_ENCODING = get_system_encoding()
