"""Tests for POST /api/v1/predict single flow endpoint."""


def test_predict_valid_benign(client):
    """Test valid prediction request returning classification result."""
    payload = {
        "dataset": "cic_ids2017",
        "features": {
            "duration": 0.5,
            "src_bytes": 100,
            "dst_bytes": 200,
            "protocol": "TCP",
            "service": "HTTP",
        },
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "is_attack" in data
    assert isinstance(data["is_attack"], bool)
    assert "label" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert "probabilities" in data
    assert data["dataset"] == "cic_ids2017"
    assert data["latency_ms"] >= 0.0
    if not data["is_attack"]:
        assert data["label"] == "BENIGN"
        assert data["attack_type"] is None
    else:
        assert data["attack_type"] == data["label"]


def test_predict_unknown_categorical_values(client):
    """Test prediction handling unknown protocol/service values gracefully without crash."""
    payload = {
        "dataset": "nsl_kdd",
        "features": {
            "duration": 1.2,
            "src_bytes": 500,
            "dst_bytes": 0,
            "protocol": "unknown_proto_xyz",
            "service": "custom_exotic_service",
        },
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "is_attack" in data
    assert "label" in data
    assert "confidence" in data


def test_predict_default_dataset_fallback(client):
    """Test request without explicit dataset uses default dataset."""
    payload = {
        "features": {
            "duration": 0.1,
            "src_bytes": 64,
            "dst_bytes": 64,
            "protocol": "udp",
            "service": "dns",
        }
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["dataset"] == "unsw_nb15"


def test_predict_unknown_dataset_404(client):
    """Test unknown dataset identifier returns 404 Not Found."""
    payload = {
        "dataset": "non_existent_dataset_123",
        "features": {
            "duration": 0.1,
            "src_bytes": 64,
            "dst_bytes": 64,
            "protocol": "tcp",
            "service": "http",
        },
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 404

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNKNOWN_DATASET"


def test_predict_validation_negative_numbers(client):
    """Test negative duration and negative bytes fail schema validation (422)."""
    payload = {
        "features": {
            "duration": -5.0,
            "src_bytes": 100,
            "dst_bytes": 200,
            "protocol": "tcp",
            "service": "http",
        }
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422


def test_predict_validation_nan_inf(client):
    """Test NaN / Inf values fail schema validation (422)."""
    payload = {
        "features": {
            "duration": "NaN",
            "src_bytes": 100,
            "dst_bytes": 200,
            "protocol": "tcp",
            "service": "http",
        }
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422


def test_predict_validation_extra_forbidden_fields(client):
    """Test extra unallowed fields fail validation (extra='forbid')."""
    payload = {
        "features": {
            "duration": 1.0,
            "src_bytes": 100,
            "dst_bytes": 200,
            "protocol": "tcp",
            "service": "http",
            "unallowed_extra_field": "hack",
        }
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422


def test_integration_real_model_attack_prediction(client):
    """Integration test loading a real model (unsw_nb15) and predicting a known attack row."""
    payload = {
        "dataset": "unsw_nb15",
        "features": {
            "duration": 0.0,
            "src_bytes": 0,
            "dst_bytes": 0,
            "protocol": "tcp",
            "service": "http",
        },
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["dataset"] == "unsw_nb15"
    assert data["is_attack"] is True
    assert data["label"] != "BENIGN"
    assert data["attack_type"] is not None
    assert data["attack_type"] == data["label"]

