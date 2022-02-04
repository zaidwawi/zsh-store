from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect , render_template, request, jsonify, url_for, make_response
from models import Products, User, setup_db, rollback, checkout, carts, order




def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS (app)
    db = SQLAlchemy(app)
    
    
    @app.route('/')
    def home():
        return "zaid"
    return app 




APP = create_app()

if __name__ == '__main__':
    APP.run(debug=True)
