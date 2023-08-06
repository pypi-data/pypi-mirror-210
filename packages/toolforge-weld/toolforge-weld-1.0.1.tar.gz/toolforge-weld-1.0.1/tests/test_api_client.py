import pytest

from toolforge_weld.api_client import ToolforgeClient
from toolforge_weld.kubernetes_config import fake_kube_config


@pytest.fixture
def fake_api_client() -> ToolforgeClient:
    return ToolforgeClient(
        server="https://example.org/",
        kubeconfig=fake_kube_config(),
        user_agent="fake",
        timeout=5,
    )


def test_ToolforgeClient_make_kwargs(fake_api_client: ToolforgeClient):
    assert fake_api_client.make_kwargs(url="foo/bar/baz") == {
        "url": "https://example.org/foo/bar/baz",
        "timeout": 5,
    }


def test_ToolforgeClient_make_kwargs_url_starts_with_slash(
    fake_api_client: ToolforgeClient,
):
    assert fake_api_client.make_kwargs(url="/bar") == {
        "url": "https://example.org/bar",
        "timeout": 5,
    }


def test_ToolforgeClient_make_kwargs_custom_timeout(fake_api_client: ToolforgeClient):
    assert fake_api_client.make_kwargs(url="foo/bar/baz", timeout=4) == {
        "url": "https://example.org/foo/bar/baz",
        "timeout": 4,
    }
