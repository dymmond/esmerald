# Security

Security, authentication, and authorization can be approached in various ways.

These topics are often considered complex and challenging to master.

In many frameworks and systems, managing security and authentication requires significant effort,
often accounting for 50% or more of the total codebase.

**Ravyn**, however, offers a range of tools that simplify handling security.
These tools enable you to implement secure systems quickly, efficiently,
and in compliance with standards—without needing to dive deeply into all the technical specifications of security.

Before diving in, let’s explore a few key concepts.

## Quick Note

If you don't need to worry about these concepts, terms and terminologies or you are simply familiar with those, you can
jump directly to the next sections.

## OAuth

OAuth2 is a comprehensive specification that outlines multiple methods for managing authentication and authorization.

It is designed to handle a wide range of complex scenarios.

One of its key features is enabling authentication through a "third party."

This is the foundation for systems that offer options like "Sign via Facebook",
"Sign in using Google" or "Login via GitHub".

### OAuth (first version)

OAuth 1 was an earlier version of the OAuth specification, significantly different from OAuth2.
It was more complex because it included detailed requirements for encrypting communication.

Today, OAuth 1 is rarely used or popular.

In contrast, OAuth2 simplifies this aspect by not defining how to encrypt communication.
Instead, it assumes that your application is served over HTTPS, ensuring secure communication by
relying on the encryption provided by the protocol.

## OpenID Connect

OpenID Connect is a specification built on top of **OAuth2**.

It extends OAuth2 by addressing ambiguities in the original specification, aiming to improve interoperability across systems.

For instance, Google login leverages OpenID Connect, which operates on top of OAuth2.

However, Facebook login does not support OpenID Connect and instead uses its own customized version of OAuth2.

## OpenID (not "OpenID Connect")

There was also an earlier specification called "OpenID," which aimed to address the same challenges as **OpenID Connect**.
However, it was not built on OAuth2 and functioned as a completely separate system.

Unlike OpenID Connect, OpenID did not achieve widespread adoption and is rarely used today.

## The OpenAPI

Did you know that OpenAPI in the past was called **Swagger**? You probably did and this is we still have the *swagger ui*
and the constant use of that name.

**Ravyn** provides a native integration with **OpenAPI** as well with its automatic documentation generation.

Why this? Well, using the OpenAPI specification it can also take advantage of the standard-based tools for security.

The following `security schemes` are supported by OpenAPI:

* `apiKey` - An application specific key that can come from:
    * Cookie parameter
    * Header parameter
    * Header parameter
* `http` - The standard HTTP authentication system that includes:
    * `bearer` - An header `Authorization` followed by a value of `Bearer` with the corresponding token.
    * HTTP Basic Auth
    * HTTP Digest

OpenAPI also supports the previously mentioned `OAuth2` and `OpenID Connect`.
