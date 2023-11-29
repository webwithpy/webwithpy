from webwithpy.html.forms import SQLForm, InputForm
from webwithpy.http.redirect import Redirect
from webwithpy.routing.router import Router
from webwithpy.orm.objects import Table, Field
from webwithpy.orm import DB
import re


class AuthUser(Table):
    table_name = "auth_user"
    username = Field("string")
    email = Field("string")
    password = Field("string", encrypt=True)
    password_two = Field("string", encrypt=True)


class AuthValidator:
    def __init__(self, db: DB, min_pass_len: int):
        self.db = db
        self.min_pass_len = min_pass_len

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
        form = InputForm(self.db.auth_user, fields=["email", "password"])

        if form.accepted:
            return Redirect("/")

        return form

    def register_form(self):
        form = InputForm(
            self.db.auth_user, form_controller=self.register_form_controller
        )

        if form.accepted:
            self.db.auth_user.insert(**form.form_data)
            return Redirect("/")

        return form
