import sqlalchemy
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "postgres://vcommvznlesvvf:306a5c86a2c5b206725287d7231a26563d8ad1fc6289173261218b8312485e81@ec2-3-208-50-226.compute-1.amazonaws.com:5432/dde9qpdu2gb4s2",
    echo=True,
)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    email = Column(String(255))
    password = Column(String(255))

    def __repr__(self):
        return "<User(email='{}', password='{}')>".format(self.email, self.password,)
