import os

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
