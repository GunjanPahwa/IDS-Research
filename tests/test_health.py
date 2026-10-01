"""Tests for GET /api/v1/health endpoint."""


def test_health_check_endpoint(client):
    """Verify health endpoint status, loaded models list, and default dataset."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert isinstance(data["loaded_models"], list)
    assert len(data["loaded_models"]) > 0
    assert "default_dataset" in data
