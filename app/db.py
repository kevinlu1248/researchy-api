import os
import datetime
import re
import logging

from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates
from sqlalchemy_utils import LtreeType, Ltree, EmailType
from sqlalchemy_utils.types.ltree import LQUERY
from sqlalchemy.sql import functions
from sqlalchemy.dialects.postgresql import Insert, insert

from flask import Flask, request, render_template, make_response, redirect
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
from app.utils import encode, decode

load_dotenv()

engine = create_engine(os.environ.get("DB_URL"), echo=True)

app = Flask("researchy-api")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


logging.basicConfig(filename="logs/main.log", level=logging.DEBUG)
db = SQLAlchemy(app)

# TODO FIX LOGGING
# TODO FIX SECURITY ON BACKEND

with open("app/email.regex") as file:
    EMAIL_CHECKER_REGEX = file.read()


class User(db.Model):
    EMAIL_CHECKER = re.compile(EMAIL_CHECKER_REGEX)

    __tablename__ = "users"
    email = db.Column(EmailType, nullable=False, primary_key=True, unique=True)
    gaia_id = db.Column(db.String(31), nullable=False)

    @validates("email")
    def validate_email(self, key, email):
        assert User.EMAIL_CHECKER.match(email)
        return email

    @staticmethod
    def getIdByEmail(email):
        ans = db.session.query(User.gaia_id).filter_by(email=email).first()
        return ans[0] if ans else None

    @staticmethod
    def validate(email, gaia_id):
        # TODO: get auth instead
        server_id = User.getIdByEmail(email)
        if server_id is not None:
            return str(server_id) == str(gaia_id)
        else:
            db.session.add(User(email=email, gaia_id=gaia_id))
            return True

    def __repr__(self):
        return "<User(email='{}')>".format(self.email)


class File(db.Model):
    __tablename__ = "files"
    email = db.Column(EmailType, nullable=False)
    path = db.Column(LtreeType, nullable=False)
    delta = db.Column(db.JSON, nullable=False)
    bib = db.Column(db.JSON, default=lambda: {})
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_modified = db.Column(
        db.DateTime, server_default=functions.now(), onupdate=functions.now()
    )
    __table_args__ = (db.PrimaryKeyConstraint("email", "path", name="primary"), {})

    @validates("email")
    def validate_email(self, key, email):
        assert (
            db.session.query(User.gaia_id).filter_by(email=email).scalar() is not None
        )
        return email

    @staticmethod
    def upsert(email, path, delta, bib={}):
        insert_stmt = insert(File).values(path=path, email=email, delta=delta, bib=bib)
        do_update_stmt = insert_stmt.on_conflict_do_update(
            constraint="unique_paths", set_=dict(delta=delta, bib=bib)
        )
        return db.session.execute(do_update_stmt)

    @staticmethod
    def handleStorage(email, gaia_id, fs):
        """
        Expect some input of the form:
        {
            email: "",
            id: "",
            storage: ...,
        }
        """

        User(email=email, gaia_id=gaia_id)
        assert User.validate(email, gaia_id), "Invalid email and gaia_id combination"

        # TODO OPTIMIZE BY SENDING IN BULK
        for path, file in fs.items():
            File.upsert(email, Ltree(encode(path)), file)  # TODO FOR BIB

        return True

    def __repr__(self):
        return "<File(path='{}' email='{}' length='{}')>".format(
            self.path, self.email, self.delta
        )


# db.metadata.create_all(engine)

if __name__ == "__main__":
    TEST_OBJ = {
        "second/Third/test8": {
            "timeCreated": "2020-08-25T06:12:27.652Z",
            "timeModified": "2020-08-25T06:12:27.652Z",
            "name": "test8",
            "delta": {"ops": [{"insert": " emailconneroku\n commk\nfaor \n"}]},
            "selection": {"index": 0, "length": 0},
            "type": "rtf",
            "length": 29,
        },
        "second/Third/test4": {
            "timeCreated": "2020-08-25T06:12:27.652Z",
            "timeModified": "2020-08-25T06:12:27.652Z",
            "name": "test4",
            "delta": {
                "ops": [
                    {"insert": "Title"},
                    {"attributes": {"header": 1}, "insert": "\n"},
                    {"insert": "Pursue your scholarly desires..."},
                ]
            },
            "selection": {"index": 0, "length": 0},
            "type": "rtf",
            "length": 38,
        },
        "second/test1": {
            "timeCreated": "2020-08-25T06:12:27.652Z",
            "timeModified": "2020-08-25T06:12:27.652Z",
            "name": "test1",
            "delta": {
                "ops": [
                    {"insert": "Title"},
                    {"attributes": {"header": 1}, "insert": "\n"},
                    {"insert": "Pursue your scholarly desires..."},
                ]
            },
            "selection": {"index": 0, "length": 0},
            "type": "rtf",
            "length": 38,
        },
        "Third/File 1": {
            "timeCreated": "2020-08-25T06:12:27.652Z",
            "timeModified": "2020-08-25T06:12:27.652Z",
            "name": "File 1",
            "delta": {
                "ops": [
                    {"insert": "Title"},
                    {"attributes": {"header": 1}, "insert": "\n"},
                    {"insert": "Pursue your scholarly desires..."},
                ]
            },
            "selection": {"index": 0, "length": 0},
            "type": "rtf",
            "length": 38,
        },
        "Third/File 2": {
            "timeCreated": "2020-08-25T06:12:27.652Z",
            "timeModified": "2020-08-25T06:12:27.652Z",
            "name": "File 2",
            "delta": {
                "ops": [
                    {"insert": "Title"},
                    {"attributes": {"header": 1}, "insert": "\n"},
                    {"insert": "Pursue your scholarly desires..."},
                ]
            },
            "selection": {"index": 0, "length": 0},
            "type": "rtf",
            "length": 38,
        },
    }

    File.handleStorage("joe@gmail.com", "125", TEST_OBJ)

    # print(User.getIdByEmail("kevinlu1248@gmail.com"))

    # print(User.validate("12", "kevinlu1248@gmail.com"))

    # db.metadata.create_all(engine)

    # user = User(email="kevinlu1248@gmail.com", gaia_id="124")
    # user2 = User(email="joe@gmail.com", gaia_id="124")

    # db.session.add(user, user2)

    # db.session.commit()
