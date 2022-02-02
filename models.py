from ast import Str
from numbers import Integral
from xmlrpc.client import Boolean
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from flask_login import UserMixin
import os


database_path = os.environ["DATABASE_URL"]
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = 'laimg ##ggserg%'
    db.app = app
    db.init_app(app)


def rollback():
    db.session.rollback()


################### User model #########################
class User(db.Model, UserMixin):
    id = Column(Integer, primary_key = True)
    email = Column(String(), unique=True)
    password = Column(String())
    first_name = Column(String())
    address = Column(String())
    phone_number = Column(String())
    phone_whats_number = Column(String())
    is_Admin = Column(Boolean(), default = False)
    status = Column(Boolean(), default=False) # if buy = True to filter 
    checkout = db.relationship("checkout")

################### products model #######################
class Products(db.Model):
   
    id = Column(Integer, primary_key=True)
    products_name = Column(String())
    products_quantity = Column(String())
    product_price = Column(Integer)
    category = Column(String())
    main_img = Column(String())
    img_one = Column(String())
    img_two = Column(String())
    describtion_one = Column(String())
    describtion_two = Column(String())
    

    def  insert( self ):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


################### cart model #######################
            # products_name = products_name,
            # products_quantity = products_quantity,
            # product_price = product_price,
            # total = total,
            # category = category,
            # main_img = main_img,
            # user_id = current_user.id
class carts(db.Model):
    id = Column(Integer, primary_key=True)
    products_name = Column(String())
    products_quantity = Column(String(), default=1)
    product_price = Column(Integer)
    total = Column(Integer)
    category = Column(String())
    main_img = Column(String())

    def  insert( self ):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
################### checkout model #######################

class checkout(db.Model):
    __tablename__ = "checkout"
    id = Column(Integer, primary_key=True)
    costumer_name = Column(String())
    coustmer_email = Column(String())
    costumer_phone = Column(String())
    costumer_whats_phone = Column(String())
    address = Column(String())
    landmark = Column(String())
    time = Column(String())
    notes = Column(String())
    user_id = Column(Integer, ForeignKey('user.id'))

class order(db.Model):
    id = Column(Integer, primary_key = True)
    products_img = Column(String())
    products_name = Column(String())
    products_price = Column(String())
    products_quantity = Column(String())
    item_total = Column(String())
    all_total = Column(String())

    def  insert( self ):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


################### total model #######################

