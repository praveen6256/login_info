from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from db import db, cursor
import bcrypt
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CORS(app)

@app.route("/")
def home():
    return "Welcome to User Management Backend"

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data["username"]
    email = data["email"]
    password = data["password"]

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    sql = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """

    values = (
        username,
        email,
        hashed_password.decode("utf-8")
    )

    cursor.execute(sql, values)
    db.commit()

    return jsonify({
        "message": "User Registered Successfully"
    })


@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data["email"]
    password = data["password"]

    sql = "SELECT * FROM users WHERE email = %s"

    cursor.execute(sql, (email,))

    user = cursor.fetchone()

    if user is None:
        return jsonify({
            "message": "User Not Found"
        }), 404

    stored_password = user[3]

    if bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password.encode("utf-8")
    ):

        return jsonify({
            "message": "Login Successful",
            "username": user[1]
        })

    else:
        return jsonify({
            "message": "Incorrect Password"
        }), 401
@app.route("/users", methods=["GET"])

def get_users():

    sql = "SELECT id, username, email, profile_photo FROM users"

    cursor.execute(sql)

    users = cursor.fetchall()

    user_list = []

    for user in users:

       user_list.append({
    "id": user[0],
    "username": user[1],
    "email": user[2],
    "profile_photo": user[3]
})

    return jsonify(user_list)
@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):

    sql = "DELETE FROM users WHERE id=%s"

    cursor.execute(sql, (id,))
    db.commit()

    return jsonify({
        "message": "User Deleted Successfully"
    })
@app.route("/upload/<int:id>", methods=["POST"])
def upload_photo(id):

    if "photo" not in request.files:
        return jsonify({
            "message": "No File Selected"
        }), 400

    photo = request.files["photo"]

    if photo.filename == "":
        return jsonify({
            "message": "No File Selected"
        }), 400

    filename = secure_filename(photo.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    photo.save(filepath)

    sql = """
    UPDATE users
    SET profile_photo=%s
    WHERE id=%s
    """

    cursor.execute(sql, (filename, id))

    db.commit()

    return jsonify({
        "message": "Photo Uploaded Successfully"
    })
@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
