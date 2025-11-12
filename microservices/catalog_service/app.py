from flask import Flask, render_template
from extensions import db, login_manager
from controllers.book_controller import book
from models.book import Book
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(book, url_prefix="/book")

@app.route('/')
def home():
    return render_template('catalog.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001)
