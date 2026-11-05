import pytest

from service.web import app, text_stats


@pytest.fixture
def client():
    return app.test_client()


def test_healthz_reports_healthy(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json["healthy"] is True


def test_text_stats_counts_unique_words_case_insensitively():
    assert text_stats("Build test build") == {"characters": 16, "words": 3, "unique_words": 2}


def test_stats_endpoint_returns_counts(client):
    response = client.post("/stats", json={"text": "ship it"})
    assert response.status_code == 200
    assert response.json["words"] == 2


@pytest.mark.parametrize("body", [{}, {"text": 42}])
def test_stats_endpoint_rejects_invalid_text(client, body):
    assert client.post("/stats", json=body).status_code == 400
