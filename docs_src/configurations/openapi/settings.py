from esmerald import EsmeraldAPISettings, OpenAPIConfig


class AppSettings(EsmeraldAPISettings):
    @property
    def openapi_config(self) -> OpenAPIConfig:
        """
        Override the default openapi_config from Esmerald.
        """
        return OpenAPIConfig(
            title=self.title,
            version=self.version,
            contact=self.contact,
            description=self.description,
            terms_of_service=self.terms_of_service,
            license=self.license,
            servers=self.servers,
            summary=self.summary,
            security=self.security,
            tags=self.tags,
            docs_url=self.docs_url,
            redoc_url=self.redoc_url,
            swagger_ui_oauth2_redirect_url=self.swagger_ui_oauth2_redirect_url,
            redoc_js_url=self.redoc_js_url,
            redoc_favicon_url=self.redoc_favicon_url,
            swagger_ui_init_oauth=self.swagger_ui_init_oauth,
            swagger_ui_parameters=self.swagger_ui_parameters,
            swagger_js_url=self.swagger_js_url,
            swagger_css_url=self.swagger_css_url,
            swagger_favicon_url=self.swagger_favicon_url,
            root_path_in_servers=self.root_path_in_servers,
            openapi_version=self.openapi_version,
            openapi_url=self.openapi_url,
        )
