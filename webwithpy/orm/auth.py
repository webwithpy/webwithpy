from .objects import Table, Field
from ..html.forms import SQLForm
from .db import DB


class AuthUser(Table):
    table_name = "auth_user"
    username = Field("string")
    email = Field("string")
    password = Field("string", encrypt=True)
    password_two = Field("string", encrypt=True)


def register_form():
    ...


def login_form():
    ...
