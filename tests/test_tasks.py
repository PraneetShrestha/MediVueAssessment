"""
Tests for task endpoints: creation, validation, filtering, PATCH.
Uses pytest + TestClient (httpx under the hood) per assessment spec.
"""
import pytest
from fastapi.testclient import TestClient


def test_create_task_success(client: TestClient):
    """Successful task creation returns 201 and task with id and tags."""
    payload = {
        "title": "Interview prep",
        "description": "Review API design",
        "priority": 5,
        "due_date": "2030-01-15",
        "tags": ["work", "urgent"],
    }
    resp = client.post("/tasks", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["priority"] == 5
    assert data["due_date"] == "2030-01-15"
    assert set(data["tags"]) == {"work", "urgent"}
    assert "id" in data
    assert data["completed"] is False


def test_create_task_validation_priority_out_of_range(client: TestClient):
    """Priority outside 1–5 returns 422."""
    resp = client.post(
        "/tasks",
        json={
            "title": "Bad priority",
            "priority": 10,
            "due_date": "2030-01-01",
        },
    )
    assert resp.status_code == 422


def test_create_task_validation_due_date_in_past(client: TestClient):
    """due_date in the past returns 422."""
    resp = client.post(
        "/tasks",
        json={
            "title": "Past task",
            "priority": 1,
            "due_date": "2020-01-01",
        },
    )
    assert resp.status_code == 422


def test_create_task_validation_title_empty(client: TestClient):
    """Empty title returns 422."""
    resp = client.post(
        "/tasks",
        json={
            "title": "",
            "priority": 1,
            "due_date": "2030-01-01",
        },
    )
    assert resp.status_code == 422


def test_list_tasks_filter_priority(client: TestClient):
    """GET /tasks?priority=N returns only tasks with that priority."""
    client.post("/tasks", json={"title": "P1", "priority": 1, "due_date": "2030-01-01"})
    client.post("/tasks", json={"title": "P5", "priority": 5, "due_date": "2030-01-02"})
    resp = client.get("/tasks", params={"priority": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["priority"] == 5


def test_list_tasks_filter_tags(client: TestClient):
    """GET /tasks?tags=work,urgent returns tasks that have any of those tags."""
    client.post(
        "/tasks",
        json={"title": "Tagged", "priority": 1, "due_date": "2030-01-01", "tags": ["work", "urgent"]},
    )
    resp = client.get("/tasks", params={"tags": "work,urgent"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert "work" in item["tags"] or "urgent" in item["tags"]


def test_list_tasks_pagination(client: TestClient):
    """limit and offset work."""
    resp = client.get("/tasks", params={"limit": 2, "offset": 0})
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 2
    assert data["limit"] == 2
    assert data["offset"] == 0


def test_get_task_404(client: TestClient):
    """GET /tasks/99999 returns 404."""
    resp = client.get("/tasks/99999")
    assert resp.status_code == 404
    assert "error" in resp.json().get("detail", {}) or resp.json()


def test_patch_partial_update(client: TestClient):
    """PATCH only updates provided fields."""
    create = client.post(
        "/tasks",
        json={"title": "Original", "priority": 1, "due_date": "2030-01-01", "tags": ["a"]},
    )
    assert create.status_code == 201
    tid = create.json()["id"]

    # Update only title and completed
    patch = client.patch(
        f"/tasks/{tid}",
        json={"title": "Updated title", "completed": True},
    )
    assert patch.status_code == 200
    data = patch.json()
    assert data["title"] == "Updated title"
    assert data["completed"] is True
    # Unchanged
    assert data["priority"] == 1
    assert data["due_date"] == "2030-01-01"
    assert "a" in data["tags"]


def test_patch_empty_body_allowed(client: TestClient):
    """PATCH with empty body is valid (no-op)."""
    create = client.post("/tasks", json={"title": "No-op", "priority": 1, "due_date": "2030-01-01"})
    assert create.status_code == 201
    tid = create.json()["id"]
    resp = client.patch(f"/tasks/{tid}", json={})
    assert resp.status_code == 200
    assert resp.json()["title"] == "No-op"


def test_delete_soft_then_get_404(client: TestClient):
    """After DELETE, GET same id returns 404 (soft delete)."""
    create = client.post("/tasks", json={"title": "To delete", "priority": 1, "due_date": "2030-01-01"})
    assert create.status_code == 201
    tid = create.json()["id"]
    del_resp = client.delete(f"/tasks/{tid}")
    assert del_resp.status_code == 204
    get_resp = client.get(f"/tasks/{tid}")
    assert get_resp.status_code == 404
