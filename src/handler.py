from flask import request, jsonify
from app import app, db
from models import Task
from datetime import datetime


@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    tasks_list = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "done": t.done,
            "todo": t.todo,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat(),
        }
        for t in tasks
    ]
    return jsonify(tasks_list), 200


@app.route("/task/<int:task_id>", methods=["GET"])
def get_task_by_id(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 400

    result = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "done": task.done,
        "todo": task.todo,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }

    return jsonify(result), 200


@app.route("/tasks", methods=["POST"])
def post_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    todo = datetime.fromisoformat(data.get("todo"))

    required_fields = ["title", "description", "todo"]
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({"error": "At least one field must be provided"}), 400

    new_task = Task(
        title=title,
        description=description,
        done=False,
        todo=todo,
        creasted_at=datetime.fromisoformat(datetime.now()),
        updated_at=datetime.fromisoformat(datetime.now()),
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task successful created"}), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def put_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()

    if not any(key in data for key in ["title", "description", "todo", "done"]):
        return jsonify({"error": "At least one field must be provided",}), 400

    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "todo" in data:
        task.todo = datetime.fromisoformat(data["todo"])
    if "done" in data:
        task.done = data["done"]

    task.updated_at = datetime.fromisoformat(datetime.now())

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "done": task.done,
            "todo": task.todo,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
    }), 200


@app.route("/task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task successful deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)
