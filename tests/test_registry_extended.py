"""Extended tests for provider registry to achieve 100% coverage."""

from unittest.mock import MagicMock

from gac.providers.registry import PROVIDER_REGISTRY, create_provider_func, register_provider


class TestRegistryExtended:
    """Test provider registry functions with comprehensive coverage."""

    def test_create_provider_func_metadata(self):
        """Test that create_provider_func sets proper metadata (lines 35-36)."""
        # Create a mock provider class with config
        mock_config = MagicMock()
        mock_config.name = "Test Provider"

        mock_provider_class = MagicMock()
        mock_provider_class.config = mock_config
        mock_provider_class.generate.__name__ = "generate"
        mock_provider_class.generate.__doc__ = "Original generate method"

        # Create the provider function
        provider_func = create_provider_func(mock_provider_class)

        # Test that metadata was set correctly (lines 35-36)
        assert provider_func.__name__ == "call_test_provider_api"
        assert provider_func.__doc__ == "Call Test Provider API to generate text."

        # Test that it's a callable
        assert callable(provider_func)

    def test_register_provider_adds_to_registry(self):
        """Test that register_provider adds to the registry."""
        # Clear any existing test provider
        if "test_provider" in PROVIDER_REGISTRY:
            del PROVIDER_REGISTRY["test_provider"]

        # Create a mock provider class
        mock_config = MagicMock()
        mock_config.name = "Test Provider"

        mock_provider_class = MagicMock()
        mock_provider_class.config = mock_config
        mock_provider_class.generate.__name__ = "generate"

        # Register the provider
        register_provider("test_provider", mock_provider_class)

        # Verify it was added to registry
        assert "test_provider" in PROVIDER_REGISTRY
        assert callable(PROVIDER_REGISTRY["test_provider"])

        # Clean up
        del PROVIDER_REGISTRY["test_provider"]

    def test_registry_dict_structure(self):
        """Test that PROVIDER_REGISTRY has the expected structure."""
        # Should be a dictionary
        assert isinstance(PROVIDER_REGISTRY, dict)

        # All values should be callable
        for name, func in PROVIDER_REGISTRY.items():
            assert isinstance(name, str)
            assert callable(func)

        # Should have some registered providers
        assert len(PROVIDER_REGISTRY) > 0
