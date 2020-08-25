import os
import datetime

from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import LtreeType, Ltree, EmailType
from sqlalchemy_utils.types.ltree import LQUERY
from flask import Flask, request, render_template, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# from modules.website import Website
from dotenv import load_dotenv


load_dotenv()

engine = create_engine(os.environ.get("DB_URL"), echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

app = Flask("researchy-api")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, db.Sequence("user_id_seq"), primary_key=True)
    first = db.Column(db.String(255))
    last = db.Column(EmailType)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password(self.password_hash, password)

    def __repr__(self):
        return "<User(name='{} {}' email='{}')>".format(
            self.first, self.last, self.email
        )


class File(db.Model):
    __tablename__ = "files"
    item_id = db.Column(db.Integer, db.Sequence("item_id_seq"), primary_key=True)
    path = db.Column(LtreeType, nullable=False)
    email = db.Column(EmailType, nullable=False)
    gaia_id = db.Column(db.String(31), nullable=False)
    delta = db.Column(db.JSON, nullable=False)
    bib = db.Column(db.JSON, default=lambda: {})
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<File(path='{}' email='{}' length='{}')>".format(
            self.path, self.email, self.delta
        )


# file = File(
#     path=Ltree("First.Second"),
#     email="kevinlu1248@gmail.com",
#     gaia_id="123",
#     delta={"ops": []},
# )

# db.metadata.create_all(engine)

# session.add(file)
# session.commit()

# class User(Base):
#     __tablename__ = "users"
#     user_id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
#     first = Column(String(255))
#     last = Column(String(255))
#     email = Column(String(255), nullable=False)
#     password = Column(String(255), nullable=False)

#     def __repr__(self):
#         return "<User(email='{}', password='{}')>".format(self.email, self.password,)

# if __name__ == "__main__":
#     session = Session()
#     session.execute("DROP TABLE users;")
#     session.commit()

#     Base.metadata.create_all(engine)
