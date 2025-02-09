# Permissions

Esmerald provides two different ways of declaring permissions: the Esmerald native system and the one provided by Lilya.

## Esmerald Native System

The Esmerald native system allows you to define permissions directly within your application. Here is an example:

```python
from esmerald.permissions import Permission

class ViewDashboardPermission(Permission):
    def has_permission(self, request, view): # or async has_permission
        return request.user.is_authenticated and request.user.has_role('admin')
```

## Lilya Permissions

Lilya is the core of Esmerald that can be integrated to manage permissions. Here is an example of how to use Lilya with Esmerald:

```python
from typing import Any

from lilya.protocols.permissions import PermissionProtocol
from lilya.types import ASGIApp

from esmerald.exceptions import NotAuthorized


class EditProfilePermission(PermissionProtocol):
    def __init__(self, app: ASGIapp, *args: Any, **kwargs: Any):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotAuthorized()
```

Both systems offer flexibility and can be used based on your project's requirements and both can
be combined.

Its entirely up to you.
