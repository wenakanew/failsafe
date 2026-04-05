import datetime
from peewee import CharField, BooleanField, DateTimeField, ForeignKeyField
from app.database import BaseModel
from app.models.user import User

class Url(BaseModel):
    user = ForeignKeyField(User, backref='urls')
    original_url = CharField()
    short_code = CharField(unique=True)
    title = CharField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
