"""Tests for ProviderProtocol runtime checkability."""

from gac.providers.protocol import ProviderProtocol


def test_protocol_is_runtime_checkable():
    class FakeProvider:
        def generate(self, model, messages, temperature, max_tokens, **kwargs):
            return "test"

        @property
        def name(self):
            return "fake"

        @property
        def api_key_env(self):
            return "FAKE_API_KEY"

        @property
        def base_url(self):
            return "http://fake.url"

        @property
        def timeout(self):
            return 30

    assert isinstance(FakeProvider(), ProviderProtocol)


def test_non_conforming_class_fails_protocol():
    class BadProvider:
        pass

    assert not isinstance(BadProvider(), ProviderProtocol)


def test_partial_implementation_fails_protocol():
    class PartialProvider:
        def generate(self, model, messages, temperature, max_tokens, **kwargs):
            return "test"

    assert not isinstance(PartialProvider(), ProviderProtocol)


def test_missing_generate_fails_protocol():
    class NoGenerateProvider:
        @property
        def name(self):
            return "no-gen"

        @property
        def api_key_env(self):
            return "KEY"

        @property
        def base_url(self):
            return "http://url"

        @property
        def timeout(self):
            return 10

    assert not isinstance(NoGenerateProvider(), ProviderProtocol)
