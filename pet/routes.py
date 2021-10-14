from quart import Blueprint

from pet.views import PetAPI

pet_app = Blueprint("pet_app", __name__)

pet_view = PetAPI.as_view("pet_api")

pet_app.add_url_rule(
    "/pets/",
    defaults={"pet_uid": None},
    view_func=pet_view,
    methods=[
        "GET",
    ],
)

pet_app.add_url_rule(
    "/pets/",
    view_func=pet_view,
    methods=[
        "POST",
    ],
)
