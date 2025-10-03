from myapp.accounts.urls import route_patterns

from ravyn import Include

route_patterns = [Include(routes=route_patterns)]
