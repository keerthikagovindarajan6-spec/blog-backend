from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS   # ✅ ADD THIS
import jwt
import datetime

app = Flask(__name__)

CORS(app)  # ✅ ADD THIS (VERY IMPORTANT)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SECRET_KEY"] = "novablogsecret"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer)
    text = db.Column(db.String(300))

@app.route("/blogs", methods=["GET"])
def get_blogs():

    blogs = Blog.query.all()

    output = []

    for blog in blogs:
        output.append({
            "id": blog.id,
            "title": blog.title,
            "content": blog.content
        })

    return jsonify(output)

@app.route("/add-comment", methods=["POST"])
def add_comment():

    data = request.get_json()

    comment = Comment(
        blog_id=data["blog_id"],
        text=data["text"]
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "message": "Comment Added Successfully"
    })

@app.route("/delete-blog/<int:id>", methods=["DELETE"])
def delete_blog(id):

    blog = Blog.query.get(id)

    if not blog:
        return jsonify({
            "message": "Blog not found"
        }), 404

    db.session.delete(blog)
    db.session.commit()

    return jsonify({
        "message": "Blog Deleted Successfully"
    })
@app.route("/update-blog/<int:id>", methods=["PUT"])
def update_blog(id):

    blog = Blog.query.get(id)

    if not blog:
        return jsonify({
            "message": "Blog not found"
        }), 404

    data = request.get_json()

    blog.title = data["title"]
    blog.content = data["content"]

    db.session.commit()

    return jsonify({
        "message": "Blog Updated Successfully"
    })

@app.route("/comments/<int:blog_id>", methods=["GET"])
def get_comments(blog_id):

    comments = Comment.query.filter_by(
        blog_id=blog_id
    ).all()

    output = []

    for comment in comments:
        output.append({
            "id": comment.id,
            "text": comment.text
        })

    return jsonify(output)

@app.route("/")
def home():
    return "Nova Blog API Running"
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    existing_user = User.query.filter_by(
        email=data["email"]
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    hashed_password = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User Registered Successfully"
    })
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    check_password = bcrypt.check_password_hash(
        user.password,
        data["password"]
    )

    if not check_password:
        return jsonify({
            "message": "Invalid password"
        }), 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({
        "token": token
    })


@app.route("/create-blog", methods=["POST"])
def create_blog():

    data = request.get_json()

    blog = Blog(
        title=data["title"],
        content=data["content"]
    )

    db.session.add(blog)
    db.session.commit()

    return jsonify({
        "message": "Blog Created Successfully"
    })


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)