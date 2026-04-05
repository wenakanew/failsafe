import datetime
from peewee import CharField, DateTimeField, ForeignKeyField
from app.database import BaseModel
from app.models.user import User


class Post(BaseModel):
    user = ForeignKeyField(User, backref='posts')
    content = CharField(max_length=280) # Twitter limits!
    created_at = DateTimeField(default=datetime.datetime.now)
