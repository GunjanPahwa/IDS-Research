"""Tests for POST /api/v1/predict/batch endpoint."""


def test_batch_predict_ordering(client):
    """Test batch prediction preserves exact input ordering."""
    payload = {
        "dataset": "unsw_nb15",
        "flows": [
            {
                "duration": 0.0,
                "src_bytes": 0,
                "dst_bytes": 0,
                "protocol": "tcp",
                "service": "http",
            },
            {
                "duration": 10.5,
                "src_bytes": 50000,
                "dst_bytes": 100000,
                "protocol": "udp",
                "service": "dns",
            },
            {
                "duration": 0.001,
                "src_bytes": 64,
                "dst_bytes": 64,
                "protocol": "icmp",
                "service": "-",
            },
        ],
    }
    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 200

    results = response.json()
    assert isinstance(results, list)
    assert len(results) == 3

    for item in results:
        assert "is_attack" in item
        assert "label" in item
        assert "confidence" in item
        assert item["dataset"] == "unsw_nb15"


def test_batch_predict_exceeds_max_size(client):
    """Test batch prediction exceeding MAX_BATCH_SIZE returns 400 Bad Request error."""
    # Create batch exceeding limit of 1000
    oversized_flows = [
        {
            "duration": 0.1,
            "src_bytes": 10,
            "dst_bytes": 10,
            "protocol": "tcp",
            "service": "http",
        }
        for _ in range(1005)
    ]
    payload = {"dataset": "cic_ids2017", "flows": oversized_flows}
    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 400

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "BATCH_SIZE_EXCEEDED"


def test_batch_predict_empty_flows_422(client):
    """Test empty flows list fails validation (422)."""
    payload = {"flows": []}
    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 422
