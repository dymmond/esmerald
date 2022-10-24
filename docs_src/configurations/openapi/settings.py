from esmerald import EsmeraldAPISettings, OpenAPIConfig


class AppSettings(EsmeraldAPISettings):
    @property
    def openapi_config(self) -> OpenAPIConfig:
        """
        Override the default openapi_config from Esmerald.
        """
        from myapp.openapi.views import MyOpenAPIView

        return OpenAPIConfig(
            openapi_apiview=MyOpenAPIView,
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
        )
