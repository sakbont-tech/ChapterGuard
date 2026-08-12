import pytest
from types import SimpleNamespace


class _DummyModels:
    def generate_content(self, model, contents, config):
        return SimpleNamespace(text="Mocked answer from genai")


class _DummyClient:
    def __init__(self):
        self.models = _DummyModels()


@pytest.fixture(autouse=True)
def mock_genai_client(monkeypatch):
    """Automatically patch `backend.main.client` with a dummy client so tests
    never make real requests to the Gemini API.
    """
    dummy = _DummyClient()
    # Patch the client used by backend.main
    import backend.main as main
    monkeypatch.setattr(main, "client", dummy)
    yield dummy
