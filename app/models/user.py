from peewee import CharField, IntegrityError
from app.database import BaseModel

class User(BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
