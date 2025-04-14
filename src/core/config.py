import pydantic
import pydantic_settings


class Export(pydantic.BaseModel):
    name: str
    doc_types: list[str]
    schedule_time: str | None = None


class Config(pydantic_settings.BaseSettings):
    """
    Environment configuration for the application.
    """
    # Azure
    AZURE_CLIENT_ID: str
    AZURE_TENANT_ID: str
    AZURE_FEDERATED_TOKEN_FILE: str = "/var/run/secrets/azure/tokens/azure-identity-token"

    # CosmosDB
    COSMOS_URL: str
    COSMOS_DB: str
    COSMOS_RETRY_COUNT: int = 3
    COSMOS_DOCUMENT_CONTAINER: str = "document"

    # Exports
    EXPORT_DIR: str = "/tmp"
    EXPORT_DEFAULT_AGE_IN_DAYS: int = 365
    EXPORT_SETUP: list[Export] = []

    # General
    LOG_LEVEL: pydantic.constr(to_upper=True) = "INFO"


CONFIG = Config()
