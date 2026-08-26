from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_exams_endpoint_lists_supported_exams():
    response = client.get("/api/exams")

    assert response.status_code == 200
    names = [item["exam"] for item in response.json()["exams"]]
    assert names == ["JEE Main", "NEET", "CUET"]


def test_track_endpoint_returns_fallback_timeline_without_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    response = client.post(
        "/api/track",
        json={"exam": "JEE Main", "current_stage": "Admit Card Released"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "fallback"
    assert len(payload["timeline"]) == 5
    assert payload["timeline"][0]["status"] == "completed"
    assert payload["timeline"][1]["status"] == "current"
    assert len(payload["readiness_items"]) >= 3
