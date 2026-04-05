def register_routes(app):
    from app.routes.users import users_bp
    from app.routes.posts import posts_bp
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)
