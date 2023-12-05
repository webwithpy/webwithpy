from ...html.forms import SQLForm, InputForm
from ...http.redirect import Redirect
from ...routing.router import Router
from ..objects import Table, Field
from ..db import DB
from ...app import App
import bcrypt
import re


class AuthUser(Table):
    table_name = "auth_user"
    username = Field("string")
    email = Field("string")
    password = Field("string", encrypt=True)
    password_two = Field("string", encrypt=True)
    uuid = Field("string")


class AuthValidator:
    def __init__(self, db: DB, min_pass_len: int):
        self.db = db
        self.min_pass_len = min_pass_len

    def logged_in(self):
        return (
            len((self.db.auth_user.uuid == App.request.cookies.get("session")).select())
            != 0
        )

    def register_form_controller(self, form, form_data: dict):
        if not self.verify_email(form, form_data):
            return False
        elif not self.verify_password(form, form_data):
            return False

        return True

    def verify_password(self, form, form_data: dict):
        if (
            not isinstance(form_data["password"], str)
            or len(form_data["password"]) < self.min_pass_len
        ):
            form.error_msg = f"length of password should at least be greater or equal to {self.min_pass_len}"
            return False
        if form_data["password"] != form_data["password_two"]:
            form.error_msg = "passwords don't match!"
            return False
        return True

    def verify_email(self, form, form_data: dict):
        if not re.match(r"[\w.]+@([\w-]+\.)+[\w-]{2,4}$", form_data.get("email")):
            form.error_msg = f"Invalid email given!"
            return False
        elif len((self.db.auth_user.email == form_data.get("email")).select()) > 0:
            form.error_msg = f"Email Already Exists!"
            return False
        return True


class Auth(AuthValidator):
    def __init__(self, min_pass_len: int = 4):
        self.db = DB()
        self.db.create_table(AuthUser)
        super().__init__(self.db, min_pass_len)
        Router.add_route(self.login_form, url="/login", method="ANY")
        Router.add_route(self.register_form, url="/register", method="ANY")

    def login_form(self):
        if self.logged_in():
            return Redirect("/")

        form = InputForm(self.db.auth_user, fields=["email", "password"])

        if form.accepted:
            user: dict = (
                self.db.auth_user.email == form.form_data.get("email")
            ).select(self.db.auth_user.id, self.db.auth_user.password)[0]

            from_pass = form.form_data.get("password").encode()

            if bcrypt.checkpw(from_pass, user["password"]):
                (self.db.auth_user.id == user["id"]).update(
                    uuid=App.request.cookies.get("session")
                )

                return Redirect("/")

            form.error_msg = "wrong_password!"

        return form

    def register_form(self):
        if self.logged_in():
            return Redirect("/")

        form = InputForm(
            self.db.auth_user,
            form_controller=self.register_form_controller,
            fields=["username", "email", "password", "password_two"],
        )

        if form.accepted:
            user_data: dict = form.form_data
            user_data.update({"uuid": App.request.cookies.get("session")})
            self.db.auth_user.insert(**user_data)
            return Redirect("/")

        return form
