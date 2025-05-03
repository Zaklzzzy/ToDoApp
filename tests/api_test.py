import pytest
from app import app, db
from models import Task
from datetime import datetime, timedelta
import json


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_post_tasks(client):
    todo_time = (datetime.now() + timedelta(days=1)).isoformat()
    response = client.post("/tasks", json={
        "title": "Test Task",
        "description": "Test Description",
        "todo": todo_time
    })
    assert response.status_code == 201
    assert response.get_json()["message"] == "Task successful created"


def test_get_tasks(client):
    task = Task(
        title="Sample",
        description="Test",
        done=False,
        todo=datetime.now() + timedelta(days=1),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(task)
    db.session.commit()

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(t["title"] == "Sample" for t in data)


def test_get_tasks_by_id(client):
    task = Task(
        title="ByID",
        description="Desc",
        done=False,
        todo=datetime.now() + timedelta(days=2),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(task)
    db.session.commit()

    response = client.get(f"/task/{task.id}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "ByID"


def test_put_tasks_by_id(client):
    task = Task(
        title="Old Title",
        description="Old",
        done=False,
        todo=datetime.now() + timedelta(days=3),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(task)
    db.session.commit()

    new_data = {
        "title": "New Title",
        "done": True
    }

    response = client.put(f"/tasks/{task.id}", json=new_data)
    assert response.status_code == 200
    updated = response.get_json()["task"]
    assert updated["title"] == "New Title"
    assert updated["done"] is True


def test_delete_tasks_by_id(client):
    task = Task(
        title="Delete Me",
        description="To be removed",
        done=False,
        todo=datetime.now() + timedelta(days=1),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(task)
    db.session.commit()

    response = client.delete(f"/task/{task.id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task successful deleted"

    followup = client.get(f"/task/{task.id}")
    assert followup.status_code == 400
