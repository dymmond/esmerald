from typing import Dict, List, Optional

from pydantic import AnyUrl
from spectree.config import (
    DEFAULT_PAGE_TEMPLATES,
    Configuration,
    Contact,
    License,
    ModeEnum,
    SecurityScheme,
    Server,
)


class OpenAPIConfig(Configuration):
    """Configuration for OpenAPI.

    To enable OpenAPI schema generation and serving, pass an instance of
    this class to the [Esmerald][esmerald.applications.Esmerald] constructor
    using the 'openapi_config' kwargs.
    """

    title: str = "Esmerald API"
    #: service OpenAPI document description
    description: Optional[str] = None
    #: service version
    version: str = "0.1.0"
    #: terms of service url
    terms_of_service: Optional[AnyUrl] = None
    #: author contact information
    contact: Optional[Contact] = None
    #: license information
    license: Optional[License] = None

    # SpecTree configurations
    #: OpenAPI doc route path prefix (i.e. /apidoc/)
    path: str = "docs"
    #: OpenAPI file route path suffix (i.e. /apidoc/openapi.json)
    filename: str = "openapi.json"
    #: OpenAPI version (doesn't affect anything)
    openapi_version: str = "3.0.3"
    #: the mode of the SpecTree validator :class:`ModeEnum`
    mode: ModeEnum = ModeEnum.normal
    #: A dictionary of documentation page templates. The key is the
    #: name of the template, that is also used in the URL path, while the value is used
    #: to render the documentation page content. (Each page template should contain a
    #: `{spec_url}` placeholder, that'll be replaced by the actual OpenAPI spec URL in
    #: the rendered documentation page
    page_templates = DEFAULT_PAGE_TEMPLATES
    #: opt-in type annotation feature, see the README examples
    annotations = False
    #: servers section of OAS :py:class:`spectree.models.Server`
    servers: Optional[List[Server]] = []
    #: OpenAPI `securitySchemes` :py:class:`spectree.models.SecurityScheme`
    security_schemes: Optional[List[SecurityScheme]] = None
    #: OpenAPI `security` JSON at the global level
    security: Dict = {}
    # Swagger OAuth2 configs
    #: OAuth2 client id
    client_id: str = ""
    #: OAuth2 client secret
    client_secret: str = ""
    #: OAuth2 realm
    realm: str = ""
    #: OAuth2 app name
    app_name: str = "esmerald_app"
    #: OAuth2 scope separator
    scope_separator: str = " "
    #: OAuth2 scopes
    scopes: List[str] = []
    #: OAuth2 additional query string params
    additional_query_string_params: Dict[str, str] = {}
    #: OAuth2 use basic authentication with access code grant
    use_basic_authentication_with_access_code_grant: bool = False
    #: OAuth2 use PKCE with authorization code grant
    use_pkce_with_authorization_code_grant: bool = False

    @property
    def spec_url(self) -> str:
        return f"/{self.path}/{self.filename}"
