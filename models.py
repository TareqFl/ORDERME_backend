from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  ARRAY

db = SQLAlchemy()


# class Users(db.Model):
#     __tablename__ = "Users"
#     id = db.Column(db.Integer, primary_key=True, unique=True)
#     name = db.Column(db.String, unique=True, nullable=False)
#     email = db.Column(db.String, unique=True, nullable=False)
#     image = db.Column(db.String)
#     password = db.Column(db.String, nullable=False)


class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    products = db.relationship("Product", backref="store")
    # image = db.Column(db.LargeBinary, nullable=True)



class Product(db.Model):
    __tablename__ = "Product"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    brand = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("Users.id"))
    images = db.relationship("Images", backref="Product")
    thumbnail = db.Column(db.LargeBinary, nullable=True)




class Images(db.Model):
    __tablename__ = "Images"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    image = db.Column(db.LargeBinary, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("Product.id"))

