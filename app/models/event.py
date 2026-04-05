import datetime
from peewee import CharField, DateTimeField, ForeignKeyField, TextField
import json
from app.database import BaseModel
from app.models.user import User
from app.models.url import Url

class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value) if value is not None else None
    def python_value(self, value):
        if value is not None:
            return json.loads(value)
        return None

class Event(BaseModel):
    url = ForeignKeyField(Url, backref='events')
    user = ForeignKeyField(User, backref='events', null=True)
    event_type = CharField()
    details = JSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
