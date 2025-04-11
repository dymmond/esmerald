import functools
import math
import warnings
from typing import Any, Callable, Dict, Optional, Sequence, Union

import bcrypt
from monkay import load

from esmerald.conf import settings
from esmerald.exceptions import ImproperlyConfigured
from esmerald.utils.crypto import get_random_string as _get_random_string

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


async def check_password(
    password: str,
    encoded: str,
    setter: Callable[..., Any] = None,
    preferred: str = "default",
) -> bool:
    """
    Return a boolean of whether the raw password matches the three
    part encoded.

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
    is_correct: bool = hasher_handler.verify(password, encoded)

    if setter and is_correct and must_update:
        await setter(password)
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

    return hasher_handler.get_hashed_password(password)


@functools.lru_cache
def get_hashers() -> Sequence["BasePasswordHasher"]:
    hashers: Sequence["BasePasswordHasher"] = []

    password_hashers = getattr(settings, "password_hashers", None)
    if not password_hashers:
        warnings.warn("`password_hashers` missing from settings.", stacklevel=2)
        return hashers

    for hasher_path in settings.password_hashers:
        hasher_cls = load(hasher_path)
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
                "Did you specify it in your settings?" % algorithm
            ) from e


def identify_hasher(encoded: str) -> "BasePasswordHasher":
    """
    Return an instance of a loaded password hasher.

    Identify hasher algorithm by examining the encoded hash and call
    get_hasher() to return the correct hasher. Raise ValueError if
    algorithm cannot be identified, or if hasher is not loaded.
    """
    if encoded.startswith("$2b$") or encoded.startswith("$2a$") or encoded.startswith("$2y$"):
        # Identify bcrypt hash format
        algorithm = "bcrypt"
    else:
        # Extract algorithm identifier from the encoded string (split by '$' and get the first part)
        algorithm = encoded.split("$", 1)[0]

    return get_hasher(algorithm)


class BasePasswordHasher:
    hasher: Any
    algorithm: str
    algorithm_name: str
    salt_entropy: int = 128

    def __init__(self, **kwargs: Any) -> None:
        if self.algorithm is None or self.algorithm_name is None:
            raise NotImplementedError(
                "subclasses of BasePasswordHasher must provide an algorithm and algorithm_name."
            )

    def get_hashed_password(self, password: str) -> Union[str, Any]:
        # Use bcrypt to hash the password
        salt = bcrypt.gensalt().decode("utf-8")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8"))
        return hashed_password.decode("utf-8")

    def decode(self, encoded: str) -> Dict[str, Any]:
        """
        Since bcrypt includes the salt in the hash, we don't need to manually decode.
        """
        return {"algorithm": self.algorithm_name, "hash": encoded}

    def must_update(self, encoded: str) -> bool:
        # bcrypt hashes don't require manual salt updates
        return False


class BcryptPasswordHasher(BasePasswordHasher):
    """
    Handles bcrypt password hashing in a similar way to PBKDF2PasswordHasher.
    """

    algorithm = "bcrypt"
    algorithm_name = "bcrypt"
    salt_entropy: int = 128
    rounds: int = 10  # Default cost factor for bcrypt

    def verify(self, password: str, encoded: str) -> bool:
        """
        Verify the password against the encoded hash.
        """
        # Use bcrypt's checkpw to verify password against full encoded hash
        return bcrypt.checkpw(password.encode("utf-8"), encoded.encode("utf-8"))

    def get_hashed_password(self, password: str) -> Union[str, Any]:
        """
        Hashes the password using bcrypt, returning a hash in the passlib-compatible format.
        """
        # Generate bcrypt salt
        salt = bcrypt.gensalt(rounds=self.rounds).decode("utf-8")
        # Hash the password with the generated salt
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8"))
        return hashed_password.decode("utf-8")  # Return full bcrypt hash (salt + hash)

    def decode(self, encoded: str) -> Dict[str, Any]:
        """
        Decode the bcrypt hash, splitting the salt and hash components.
        """
        salt, _hash = encoded[:29], encoded[29:]
        return {
            "algorithm": self.algorithm_name,
            "hash": _hash,
            "salt": salt,
            "rounds": self.rounds,  # Include the rounds cost factor
        }

    def must_update(self, encoded: str) -> bool:
        """
        Check if the bcrypt hash requires an update, such as updating salt entropy or rounds.
        """
        decoded = self.decode(encoded)
        update_salt = must_update_salt(decoded["salt"], self.salt_entropy)

        return update_salt or decoded["rounds"] != self.rounds
