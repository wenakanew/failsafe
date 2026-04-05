from peewee import CharField, IntegerField
from app.database import BaseModel


class User(BaseModel):
    name = CharField()
    email = CharField(unique=True) # Enforces idempotency at the DB level
    age = IntegerField()
