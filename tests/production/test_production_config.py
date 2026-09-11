import pytest
from app.config.settings import settings


def test_production_secret_validation_fails_closed():
    """Verify that settings.validate_production_secrets() fails closed if default secrets are present in production."""
    settings.ENVIRONMENT = "production"
    settings.DEBUG = True
    with pytest.raises(ValueError, match="SECURITY RISK"):
        settings.validate_production_secrets()

    # Reset for other tests
    settings.ENVIRONMENT = "development"
    settings.DEBUG = True
