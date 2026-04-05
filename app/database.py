import os
import time

from peewee import DatabaseProxy, Model, PostgresqlDatabase

db = DatabaseProxy()

def retry_db_operation(operation, retries=3, delay=0.2):
    for attempt in range(retries):
        try:
            return operation()
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(delay)


class BaseModel(Model):
    class Meta:
        database = db


def init_db(app):
    if os.environ.get("TESTING") == "1":
        from peewee import SqliteDatabase
        database = SqliteDatabase('test_hackathon.db')
    else:
        database = PostgresqlDatabase(
            os.environ.get("DATABASE_NAME", "hackathon_db"),
            host=os.environ.get("DATABASE_HOST", "localhost"),
            port=int(os.environ.get("DATABASE_PORT", 5432)),
            user=os.environ.get("DATABASE_USER", "postgres"),
            password=os.environ.get("DATABASE_PASSWORD", "postgres"),
        )
    db.initialize(database)

    @app.before_request
    def _db_connect():
        db.connect(reuse_if_open=True)

    @app.teardown_appcontext
    def _db_close(exc):
        if not db.is_closed():
            db.close()
