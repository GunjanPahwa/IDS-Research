"""Tests for GET /api/v1/model/info endpoint."""


def test_model_info_endpoint(client):
    """Verify model info metadata endpoint returns schemas, available datasets, and label info."""
    response = client.get("/api/v1/model/info")
    assert response.status_code == 200

    data = response.json()
    assert "available_datasets" in data
    assert "default_dataset" in data
    assert data["feature_space"] == "Common-5"

    features_schema = data["features_schema"]
    feature_names = [f["name"] for f in features_schema]
    assert feature_names == ["duration", "src_bytes", "dst_bytes", "protocol", "service"]

    datasets_info = data["datasets_info"]
    assert len(datasets_info) > 0
    for ds_key, details in datasets_info.items():
        assert details["dataset"] == ds_key
        assert isinstance(details["is_loaded"], bool)
        assert isinstance(details["classes"], list)
        assert isinstance(details["verified"], bool)
        if ds_key in {"unsw_nb15", "kdd99", "nsl_kdd"}:
            assert details["verified"] is True
        else:
            assert details["verified"] is False
