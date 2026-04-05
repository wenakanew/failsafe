from dotenv import load_dotenv
from flask import Flask, jsonify

from app.database import init_db
from app.routes import register_routes


def create_app():
    load_dotenv()

    app = Flask(__name__)

    init_db(app)

    from app import models  # noqa: F401 - registers models with Peewee

    register_routes(app)

    import time
    from app.database import db
    
    from app.models.user import User
    from app.models.url import Url
    from app.models.event import Event
    db.create_tables([User, Url, Event], safe=True)

    @app.route("/health")
    def health():
        start = time.time()
        try:
            db.connect(reuse_if_open=True)
            db.execute_sql('SELECT 1')
            db.close()
            latency = time.time() - start
            return jsonify({"status": "healthy", "latency_ms": round(latency * 1000, 2)}), 200
        except Exception as e:
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": error.description if hasattr(error, 'description') else str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": error.description if hasattr(error, 'description') else "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error", "message": "System encountered an unexpected failure"}), 500

    return app
