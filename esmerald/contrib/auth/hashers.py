import functools
import asyncio
import hashlib
import math
import warnings
from typing import Any, Callable, Dict, Optional, Sequence, Union

from passlib.context import CryptContext

from esmerald.conf import settings
from esmerald.exceptions import ImproperlyConfigured
from esmerald.utils.crypto import get_random_string as _get_random_string
from esmerald.utils.module_loading import import_string

from .constants import (
    RANDOM_STRING_CHARS,
    UNUSABLE_PASSWORD_PREFIX,
    UNUSABLE_PASSWORD_SUFFIX_LENGTH,
)


def is_password_usable(encoded: Optional[str]) -> bool:
    """
    Return True if this password wasn't generated by
    User.set_unusable_password(), i.e. make_password(None).
    """
    return encoded is None or not encoded.startswith(UNUSABLE_PASSWORD_PREFIX)


def check_password(
    password: str,
    encoded: str,
    setter: Callable[..., Any] = None,
    preferred: str = "default",
) -> bool:
    """
    Return a boolean of whether the raw password matches the three
    part encoded digest.

    If setter is specified, it'll be called when you need to
    regenerate the password.
    """
    if password is None or not is_password_usable(encoded):
        return False

    preferred_hasher: BasePasswordHasher = get_hasher(preferred)
    try:
        hasher_handler = identify_hasher(encoded)
    except ValueError:
        # encoded is gibberish or uses a hasher that's no longer installed.
        return False

    hasher_changed = hasher_handler.algorithm != preferred_hasher.algorithm
    must_update: bool = hasher_changed or preferred_hasher.must_update(encoded)
    is_correct: bool = hasher_handler.hasher.verify(password, encoded)

    if setter and is_correct and must_update:
        if asyncio.iscoroutinefunction(setter):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(setter(password))
        else:
            setter(password)
    return is_correct


def make_password(password: Optional[str], hasher: str = "default") -> str:
    """
    Turn a plain-text password into a hash for database storage

    Same as encode() but generate a new random salt. If password is None then
    return a concatenation of UNUSABLE_PASSWORD_PREFIX and a random string,
    which disallows logins. Additional random string reduces chances of gaining
    access to staff or superuser accounts. See ticket #20079 for more info.
    """
    if password is None:
        return UNUSABLE_PASSWORD_PREFIX + get_random_string(UNUSABLE_PASSWORD_SUFFIX_LENGTH)
    if not isinstance(password, (bytes, str)):
        raise TypeError(
            "Password must be a string or bytes, got %s." % type(password).__qualname__
        )

    hasher_handler: BasePasswordHasher = get_hasher(hasher)

    # Passlib includes salt in almost every hash
    return hasher_handler.get_hashed_password(password)


@functools.lru_cache
def get_hashers() -> Sequence["BasePasswordHasher"]:
    hashers: Sequence["BasePasswordHasher"] = []

    password_hashers = getattr(settings, "password_hashers", None)
    if not password_hashers:
        warnings.warn("`password_hashers` missing from settings.", stacklevel=2)
        return hashers

    for hasher_path in settings.password_hashers:
        hasher_cls = import_string(hasher_path)
        hasher = hasher_cls()
        if not hasher.algorithm:
            raise ImproperlyConfigured(
                "hasher doesn't specify an algorithm name: %s" % hasher_path
            )
        hashers.append(hasher)
    return hashers


@functools.lru_cache
def get_hashers_by_algorithm() -> Dict[str, "BasePasswordHasher"]:
    return {hasher.algorithm_name: hasher for hasher in get_hashers()}


def must_update_salt(salt: str, expected_entropy: int) -> bool:
    # Each character in the salt provides log_2(len(alphabet)) bits of entropy.
    return len(salt) * math.log2(len(RANDOM_STRING_CHARS)) < expected_entropy


def get_random_string(length: int, allowed_chars: str = RANDOM_STRING_CHARS) -> str:
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits
    """
    return _get_random_string(length=length, allowed_chars=allowed_chars)


def get_hasher(algorithm: str = "default") -> "BasePasswordHasher":
    """
    Return an instance of a loaded password hasher.

    If algorithm is 'default', return the default hasher. Lazily import hashers
    specified in the project's settings config if needed.
    """
    if algorithm == "default":
        return get_hashers()[0]

    else:
        hashers = get_hashers_by_algorithm()
        try:
            return hashers[algorithm]
        except KeyError as e:
            raise ValueError(
                "Unknown password hashing algorithm '%s'. "
                "Did you specify it in your settings? "
                "setting?" % algorithm
            ) from e


def identify_hasher(encoded: str) -> "BasePasswordHasher":
    """
    Return an instance of a loaded password hasher.

    Identify hasher algorithm by examining encoded hash, and call
    get_hasher() to return hasher. Raise ValueError if
    algorithm cannot be identified, or if hasher is not loaded.
    """
    # Ancient versions of some framworks created plain MD5 passwords
    # and accepted MD5 passwords with an empty salt.
    if (len(encoded) == 32 and "$" not in encoded) or (
        len(encoded) == 37 and encoded.startswith("md5$$")
    ):
        algorithm = "unsalted_md5"
    elif len(encoded) == 46 and encoded.startswith("sha1$$"):
        algorithm = "unsalted_sha1"
    else:
        algorithm = encoded.split("$", 1)[0]
    return get_hasher(algorithm)


class BasePasswordHasher:
    hasher: CryptContext
    algorithm: str
    algorithm_name: str
    digest: Any
    library = None
    salt_entropy: int = 128

    def __init__(self, **kwargs: Any) -> None:
        if self.algorithm is None or self.algorithm_name is None:
            raise NotImplementedError(
                "subclasses of BasePasswordHasher must provide an algorithm and algorithm_name."
            )
        self.hasher = CryptContext(schemes=[self.algorithm], deprecated="auto")

    def get_hashed_password(self, password: str) -> Union[str, Any]:
        return self.hasher.hash(password)

    def salt(self) -> str:
        """
        Generate a cryptographically secure nonce salt in ASCII with an entropy
        of at least `salt_entropy` bits.
        """
        # Each character in the salt provides
        # log_2(len(alphabet)) bits of entropy.
        char_count = math.ceil(self.salt_entropy / math.log2(len(RANDOM_STRING_CHARS)))
        return get_random_string(char_count, allowed_chars=RANDOM_STRING_CHARS)

    def decode(self, encoded: str) -> Dict[str, Any]:
        """
        Return a decoded database value.

        The result is a dictionary and should contain `algorithm`, `hash`, and
        `salt`. Extra keys can be algorithm specific like `iterations` or
        `work_factor`.
        """
        raise NotImplementedError(
            "subclasses of BasePasswordHasher must provide a decode() method."
        )

    def _check_encode_args(self, password: str, salt: str) -> None:
        if password is None:
            raise TypeError("password must be provided.")
        if not salt or "$" in salt:
            raise ValueError("salt must be provided and cannot contain $.")

    def must_update(self, encoded: str) -> bool:
        return False


class PBKDF2PasswordHasher(BasePasswordHasher):
    """
    Handles PBKDF2 passwords
    """

    algorithm = "django_pbkdf2_sha256"
    algorithm_name = "pbkdf2_sha256"
    iterations = 390000
    digest = hashlib.sha256

    def decode(self, encoded: str) -> Dict[str, Any]:
        algorithm, iterations, salt, _hash = encoded.split("$", 3)
        assert algorithm == self.algorithm_name
        return {
            "algorithm": algorithm,
            "hash": _hash,
            "iterations": int(iterations),
            "salt": salt,
        }

    def must_update(self, encoded: str) -> bool:
        decoded = self.decode(encoded)
        update_salt = must_update_salt(decoded["salt"], self.salt_entropy)
        return (decoded["iterations"] != self.iterations) or update_salt


class PBKDF2SHA1PasswordHasher(PBKDF2PasswordHasher):
    """
    Alternate PBKDF2 hasher which uses SHA1, the default PRF
    recommended by PKCS #5. This is compatible with other
    implementations of PBKDF2, such as openssl's
    PKCS5_PBKDF2_HMAC_SHA1().
    """

    algorithm = "django_pbkdf2_sha1"
    algorithm_name = "pbkdf2_sha1"
    digest = hashlib.sha1
