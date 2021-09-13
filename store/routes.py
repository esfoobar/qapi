from quart import Blueprint

from store.views import StoreAPI

store_app = Blueprint("store_app", __name__)

store_view = StoreAPI.as_view("store_api")
store_app.add_url_rule(
    "/store/",
    view_func=store_view,
    methods=[
        "POST",
    ],
)
