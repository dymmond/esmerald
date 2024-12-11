# HTTP Basic Auth

For simple scenarios, HTTP Basic Auth can be used.

With HTTP Basic Auth, the application expects a header containing a username and password.

If the header is missing, the application responds with an HTTP 401 "Unauthorized" error and includes a `WWW-Authenticate` header with a value of `Basic` and an optional `realm` parameter.

This prompts the browser to display a login dialog for the username and password. Once entered, the browser automatically sends the credentials in the header.

## Simple HTTP Basic Auth

1. Import `HTTPBasic` and `HTTPBasicCredentials`.
2. Create a security scheme using `HTTPBasic`.
3. Apply this security scheme as a dependency in your path operation.
4. The dependency returns an `HTTPBasicCredentials` object, which includes the provided `username` and `password`.

```python hl_lines="10 20"
{!> ../../../docs_src/security/advanced/basic.py !}
```

When you first open the URL (or click the "Execute" button in the docs), the browser will prompt you for your username and password:

<img src="https://res.cloudinary.com/dymmond/image/upload/v1733928287/esmerald/security/basic_cbkrjk.png" alt="Basic">

## Verify the Username

Here's a more comprehensive example.

Use a dependency to verify if the username and password are correct.

For this, use the Python standard module <a href="https://docs.python.org/3/library/secrets.html" class="external-link" target="_blank">`secrets`</a> to check the username and password.

`secrets.compare_digest()` requires `bytes` or a `str` containing only ASCII characters, meaning it won't work with characters like `ú`, as in `Araújo`.

To handle this, first convert the `username` and `password` to `bytes` by encoding them with UTF-8.

Then use `secrets.compare_digest()` to ensure that `credentials.username` is `"alice123"` and `credentials.password` is `"sunshine"`.

```python
{!> ../../../docs_src/security/advanced/basic_complex.py !}
```

This would be similar to:

```python
if not (credentials.username == "alice123") or not (credentials.password == "sunshine"):
    # Return some error
    ...
```

### Timing Attacks

What exactly is a "timing attack"?

Imagine some attackers are attempting to figure out a valid username and password combination.

They send a request with the username `alice123` and the password `sunshine`.

In your Python application, the logic might look something like this:

```Python
if "alice123" == "charlie_admin" and "sunshine" == "openSesame":
    ...
```

When Python compares the first character of `alice123` (`a`) with the first character of `charlie_admin` (`c`), it instantly determines that the strings do not match and returns `False`. No further comparisons are needed because the mismatch is already clear. Consequently, your application responds with "Invalid username or password."

Next, the attackers try a different username, such as `charlie_adminx`, with the same password `sunshine`.

Your application logic then processes something like this:

```Python
if "charlie_adminx" == "charlie_admin" and "sunshine" == "openSesame":
    ...
```

Python will need to compare the entire string `charlie_admi` in both `charlie_adminx` and `charlie_admin` before determining they are not the same. This will take a few extra microseconds to respond with "Invalid username or password."

Here’s the rewritten version with new names and terms:

#### The time to respond helps attackers

Attackers can notice that the server took slightly longer to respond with "Invalid username or password." This indicates that some initial characters in the username might be correct.

They can then try again, refining their guesses, knowing that the correct username is likely closer to `charlie_adminx` than `alice123`.

#### Automated Attacks

Attackers typically don't guess usernames and passwords manually. Instead, they use scripts to automate the process, making thousands or even millions of attempts per second. These scripts can identify one correct character at a time.

By exploiting timing information unintentionally leaked by the application, attackers can eventually determine the correct username and password within minutes or hours.

#### Fix it with `secrets.compare_digest()`

Using `secrets.compare_digest()` in our code ensures that comparing any two strings, such as `charlie_adminx` to `charlie_admin` or `alice123` to `charlie_admin`, takes the same amount of time. This also applies to password comparisons.

By integrating `secrets.compare_digest()` into your application, you can effectively protect against timing attacks.

### Return the error

If the credentials are incorrect, return an `HTTPException` with a status code of 401. This is the same status code used when no credentials are provided. Additionally, include the `WWW-Authenticate` header to prompt the browser to display the login screen again:

```python hl_lines="16-25"
{!> ../../../docs_src/security/advanced/basic_complex.py !}
```

## Notes

These step by step guides were inspired by **FastAPI** great work of providing simple and yet effective examples for everyone to understand.

Esmerald adopts a different implementation internally but with the same purposes as any other framework to achieve that.
