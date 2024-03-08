# Background

This is the reference for the `BackgroundTask` and `BackgroundTasks` objects where it contains
all API informationhow to use it.

Like Lilya, in Esmerald you can define background tasks to run after the returning response.

This can be useful for those operations that need to happen after the request without blocking the client (the client doesn't have to wait to complete) from receiving that same response.

Example:

1. Registering a user in the system and send an email confirming the registration.
2. Processing a file that can take "some time". Simply return a HTTP 202 and process the file in the background.

::: esmerald.BackgroundTask

::: esmerald.BackgroundTasks
