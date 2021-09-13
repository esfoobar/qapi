from quart import Quart

from db import db_connection


def create_app(**config_overrides):
    app = Quart(__name__)

    # Load config
    app.config.from_pyfile("settings.py")

    # apply overrides for tests
    app.config.update(config_overrides)

    # import blueprints
    from app.routes import app_app
    from store.routes import store_app

    # register blueprints
    app.register_blueprint(app_app)
    app.register_blueprint(store_app)

    @app.before_serving
    async def create_db_conn():
        database = await db_connection()
        await database.connect()
        app.dbc = database

    @app.after_serving
    async def close_db_conn():
        await app.dbc.disconnect()

    return app
