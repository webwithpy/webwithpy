from ..html.forms import InputForm
from ..http.redirect import Redirect
from ..routing.router import Router, Route
from .objects.objects import Table, Field
from .core import DB
from ..app import App
from typing import Type
import bcrypt
import re


# Tqble for authentication
class AuthUser(Table):
    table_name = "auth_user"
    username = Field(field_text="name", field_type="string")
    email = Field(field_type="string")
    password = Field(field_type="string", encrypt=True)
    uuid = Field(field_type="string")


class AuthValidator:
    """
    In here are all validators stored for authentication
    """

    def __init__(self, db: DB, min_pass_len: int):
        self.db = db
        self.min_pass_len = min_pass_len

    def logged_in(self):
        """
        check if the user is logged in
        """
        return (
            len((self.db.auth_user.uuid == App.request.cookies.get("session")).select())
            != 0
        )

    def register_form_controller(self, form: InputForm, form_data: dict):
        """
        validates if the field in the register form are valid/correct
        """
        if not self.verify_email(form, form_data):
            return False
        elif not self.verify_password(form, form_data):
            return False

        return True

    def verify_password(self, form: InputForm, form_data: dict):
        """
        validates if the password is good
        """
        if (
            not isinstance(form_data["password"], str)
            or len(form_data["password"]) < self.min_pass_len
        ):
            form.error_msg = f"length of password should at least be greater or equal to {self.min_pass_len}"
            return False
        return True

    def verify_email(self, form: InputForm, form_data: dict):
        """
        validates if a given email is valid
        """
        if not re.match(r"[\w.]+@([\w-]+\.)+[\w-]{2,4}$", form_data.get("email")):
            form.error_msg = f"Invalid email given!"
            return False
        elif len((self.db.auth_user.email == form_data.get("email")).select()) > 0:
            form.error_msg = f"Email Already Exists!"
            return False
        return True


class Auth(AuthValidator):
    """
    creates auth tables and forms
    """

    def __init__(
        self,
        auth_table: Type[Table] = AuthUser,
        min_pass_len: int = 4,
        login_url: str = "/login",
        registration_url: str = "/register",
        pretty_form: bool = False,
    ):
        self.pretty_form = pretty_form
        self.db = DB(DB._settings.uri)
        self.db.create_table(auth_table)
        super().__init__(self.db, min_pass_len)
        Router.add_route(Route(self.login_form, url=login_url, method="ANY"))
        Router.add_route(Route(self.register_form, url=registration_url, method="ANY"))

    def login_form(self):
        """
        login form for users
        """
        if self.logged_in():
            return Redirect("/")

        if self.pretty_form:
            form = InputForm(
                self.db.auth_user,
                fields=["email", "password"],
                form_title="Login",
                custom_css_dir="../static/improved_reg_form.css",
            )
        else:
            form = InputForm(
                self.db.auth_user,
                fields=["email", "password"],
            )

        # logic if form is accepted
        if form.accepted:
            user: dict = (
                self.db.auth_user.email == form.form_data.get("email")
            ).select(fields=["id", "password"])

            if not user:
                form.error_msg = "Email not found!"
                return form

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

        if self.pretty_form:
            form = InputForm(
                self.db.auth_user,
                form_controller=self.register_form_controller,
                exclude_fields=["uuid"],
                form_title="Register",
                custom_css_dir="../static/improved_reg_form.css",
            )
        else:
            form = InputForm(
                self.db.auth_user,
                form_controller=self.register_form_controller,
                exclude_fields=["uuid"],
            )

        # register user and log him in if the form is validated correctly
        if form.accepted:
            user_data: dict = form.form_data
            user_data.update({"uuid": App.request.cookies.get("session")})
            self.db.auth_user.insert(**user_data)
            return Redirect("/")

        return form
