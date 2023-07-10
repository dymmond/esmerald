from typing import Any, Dict, List, Optional

from openapi_schemas_pydantic.v3_1_0.security_scheme import SecurityScheme
from pydantic import AnyUrl, BaseModel

from esmerald._openapi.models import Contact, License, Server, Tag


class OpenAPIConfig(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    contact: Optional[Contact] = None
    terms_of_service: Optional[AnyUrl] = None
    license: Optional[License] = None
    security: Optional[List[SecurityScheme]] = None
    servers: Optional[List[Server]] = None
    tags: Optional[List[Tag]] = None
    openapi_version: Optional[str] = "3.1.0"
    openapi_url: Optional[str] = "/openapi.json"
    docs_url: Optional[str] = "/docs/swagger"
    redoc_url: Optional[str] = "/docs/redoc"
    swagger_ui_oauth2_redirect_url: Optional[str] = "/docs/oauth2-redirect"
    root_path_in_servers: bool = (True,)
    swagger_ui_init_oauth: Optional[Dict[str, Any]] = None
    swagger_ui_parameters: Optional[Dict[str, Any]] = None
