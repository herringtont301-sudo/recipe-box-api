
"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes.
Authentication and authorization are added throughout Units 2 and 3.
"""

import sqlite3

from flask import Flask, g, jsonify, request
from password_utils import hash_password, verify_password

DATABASE = "recipes.db"

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
    }


@app.get("/")
def hello():
    return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})


@app.get("/recipes")
def list_recipes():
    rows = get_db().execute(
        "SELECT * FROM recipes ORDER BY id"
    ).fetchall()
    return jsonify([recipe_to_dict(row) for row in rows])


@app.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    row = get_db().execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()

    if row is None:
        return jsonify({"error": "recipe not found"}), 404

    return jsonify(recipe_to_dict(row))


@app.post("/recipes")
def create_recipe():
    data = request.get_json(silent=True)

    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400

    db = get_db()

    try:
        cur = db.execute(
            "INSERT INTO recipes (title, ingredients, instructions, is_public)"
            " VALUES (?, ?, ?, ?)",
            (
                data["title"],
                data["ingredients"],
                data.get("instructions", ""),
                1 if data.get("is_public", True) else 0,
            ),
        )
        db.commit()

    except sqlite3.IntegrityError:
        return jsonify(
            {"error": "a recipe with that title already exists"}
        ), 409

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)
    ).fetchone()

    return jsonify(recipe_to_dict(row)), 201


@app.patch("/recipes/<int:recipe_id>")
def update_recipe(recipe_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    fields, values = [], []

    for column in ("title", "ingredients", "instructions"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])

    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(1 if data["is_public"] else 0)

    if not fields:
        return jsonify({"error": "nothing to update"}), 400

    values.append(recipe_id)
    db = get_db()

    try:
        cur = db.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        db.commit()

    except sqlite3.IntegrityError:
        return jsonify(
            {"error": "a recipe with that title already exists"}
        ), 409

    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()

    return jsonify(recipe_to_dict(row))


@app.delete("/recipes/<int:recipe_id>")
def delete_recipe(recipe_id):
    db = get_db()

    cur = db.execute(
        "DELETE FROM recipes WHERE id = ?", (recipe_id,)
    )
    db.commit()

    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404

    return "", 204


@app.post("/users")
def register_user():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify(
            {"error": "username, email, and password are required"}
        ), 400

    # 1. Hash the password
    password_hash = hash_password(password)

    db = get_db()

    try:
        # 2. Insert into users table
        cur = db.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, password_hash),
        )
        db.commit()

    except sqlite3.IntegrityError:
        # 3. Duplicate username or email
        return jsonify(
            {"error": "a user with that username or email already exists"}
        ), 409

    # 4. Return safe data only
    return jsonify(
        {
            "id": cur.lastrowid,
            "username": username,
            "email": email,
        }
    ), 201


@app.post("/login")
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify(
            {"error": "username and password are required"}
        ), 400

    db = get_db()

    # 1. Look up the user by username
    row = db.execute(
        "SELECT id, username, email, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    # Same generic response for both authentication failures
    auth_error = jsonify(
        {"error": "invalid username or password"}
    ), 401

    if row is None:
        return auth_error

    stored_hash = row["password_hash"]

    # 2. Verify the password
    if not verify_password(stored_hash, password):
        return auth_error

    # 3. Return authenticated identity
    return jsonify(
        {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
        }
    ), 200


if __name__ == "__main__":
    demo_password = "correcthorsebatterystaple"
    stored = hash_password(demo_password)

    print("Demo stored hash:", stored)
    print(
        "Correct password check:",
        verify_password(stored, "correcthorsebatterystaple"),
    )
    print(
        "Wrong password check:",
        verify_password(stored, "wrongpassword"),
    )

    app.run(debug=True, port=5001)
