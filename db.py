import os

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.environ.get("DB_URL"), echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    first = Column(String(255))
    last = Column(String(255))
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

    def __repr__(self):
        return "<User(email='{}', password='{}')>".format(self.email, self.password,)


if __name__ == "__main__":
    session = Session()
    session.execute("DROP TABLE users;")
    session.commit()

    Base.metadata.create_all(engine)
