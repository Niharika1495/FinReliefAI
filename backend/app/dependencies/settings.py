from app.core.settings import Settings, settings

def get_settings() -> Settings:
    """
    Dependency injection provider yielding the centralized application
    Settings instance to route handlers.
    """
    return settings
