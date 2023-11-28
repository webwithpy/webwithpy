from ..app import App
from ..http import url
from .pyhtml import Input, Span, Div, H4, H3, A, Form
from ..routing.router import Router
import pkgutil
import jwt

# Add everything for type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..orm.db import DB
    from ..orm.query import Query
    from ..orm.objects import Table, Field


class SQLForm:
    """
    Form inspired by web2py.
    Note that the use of these kind of forms is only made for admins not regular users
    """

    def __init__(
        self,
        query: Query,
        fields: list = None,
        smart=False,
        create=True,
        view=True,
        edit=True,
        delete=True,
        delete_popup=True,
        max_row_length=20,
        slider=True,
        links: list = None,
        oncreate=None,
        onupdate=None,
        ondelete=None,
    ):
        self.smart = smart
        self.create = create
        self.view = view
        self.edit = edit
        self.delete = delete
        self.delete_popup = delete_popup
        self.max_row_length = max_row_length
        self.slider = (slider,)
        self.links = links or []
        self.oncreate = oncreate
        self.onupdate = onupdate
        self.ondelete = ondelete
        self.query = query
        self.db: DB = query.db

        # get all the names of the fields, normally a field is something like table.field_name
        # however in this case we only want field_name, that's why we remove the table name
        self.fields = [str(field).split(".")[1] for field in fields]

    def as_html(self):
        """
        convert the SQLTable to html based on given instance params
        """

        # check if the form has given us any data(button click or form-submit)
        if "jwt" in App.request.vars:
            # decode the given data and check if the actual user has sent us this data
            # this is a hopeful attempt to stop any hacker if they got past any user group check(like they are acting to
            # be admin by being some1 else)
            jwt_decoded = self.decode_jwt(App.request.vars["jwt"])

            # give the user the insert form
            if "insert" in jwt_decoded:
                return self.default_styling() + self.insert_form()
            # give the user the view form
            elif "view" in jwt_decoded:
                return self.default_styling() + self.view_form(jwt_decoded["idx"])
            # give the user the ability to edit data via a form
            elif "edit" in jwt_decoded:
                return self.default_styling() + self.edit_form(jwt_decoded["idx"])
            # user submitted data that can be inserted into the database
            elif "insert_data" in jwt_decoded:
                # get the id of the field we are going te be selecting
                table: Table = getattr(self.db, self.query.__tables__()[0])
                table.insert(**App.request.form_data)
            # we can edit data that has been sent to the database
            elif "edit_data" in jwt_decoded:
                # TODO, make the user give the table, rn we are only gonna grab the first table from the table
                fields = self.query.select()

                # get the id of the field we are going te be selecting
                table: Table = getattr(self.db, self.query.__tables__()[0])
                (table.id == fields[jwt_decoded["idx"]]["id"]).update(
                    **App.request.form_data
                )
            # delete data based on given params
            elif "delete_data" in jwt_decoded:
                # TODO, make the user give the table, rn we are only gonna grab the first table from the table
                fields = self.query.select()

                # get the id of the field we are going te be selecting
                table: Table = getattr(self.db, self.query.__tables__()[0])
                (table.id == fields[jwt_decoded["idx"]]["id"]).delete(
                    **App.request.form_data
                )

        return (
            f"<head>{self.default_styling()}</head>"
            + f"<body>{self.rows_to_table()}</body>"
        )

    def rows_to_table(self):
        values = self.query.select()

        if len(values) == 0:
            return self.no_records()

        db_tables = self.query.__tables__()
        table_keys = self.table_keys(db_tables)
        table_values = self.table_from_query(values)

        return f"""
                <div class="scroll_div">
                    {self.add_button()}
                    <table>
                        <thead>
                            <tr>
                                {table_keys}
                            </tr>
                        </thead>
                        <tbody>
                            {table_values}
                        </tbody>
                    </table>
                </div>
                """

    def table_from_query(self, selected_values):
        rows = ""
        for idx, row in enumerate(selected_values):
            blocks = [f"<td>{row[name]}</td>" for name in self.fields]

            rows += f'<tr>{"".join(blocks)}'

            if self.view:
                rows += f"<td> {self.view_button(idx)} </td>"
            if self.edit:
                rows += f"<td> {self.edit_button(idx)} </td>"
            if self.delete:
                rows += f"<td> {self.delete_button(idx)} </td>"

            rows += "</tr>"

        return rows

    def table_keys(self, tables):
        keys = ""
        for table in tables:
            for field_name in (
                self.db.tables[table].fields.keys()
                if len(self.fields) == 0
                else self.fields
            ):
                keys += f"<td class='block'>{field_name}</td>"

        for _ in range(
            int(self.view) + int(self.edit) + int(self.delete) + len(self.links)
        ):
            keys += "<th class='block'></th>"

        return keys

    def insert_form(self):
        """
        form where you can insert any sql row you want
        """
        jwt_encoded = self.encode_jwt({"insert_data": 1})

        insert_html = Form(
            *[
                Input(
                    _name=field_name,
                    placeholder=field_name,
                    _type=self.get_field_type(self.query.table_name, field_name),
                ).__str__()
                for field_name in self.db.tables[self.query.table_name].fields.keys()
                if field_name != "id"
            ],
            Div(self.back_button(), self.submit_button()),
            action=url(App.request.path, jwt=jwt_encoded),
            method="POST",
            _class="container",
        )

        return insert_html

    def view_form(self, idx):
        """
        form where you can view a sql row(you can't edit anything here!), also not really a form, only a div
        """
        selected_fields = self.query.select()
        view_html = Div(
            *[
                Div(
                    H4(_class="field_block"),
                    Input(disabled=True, value=value),
                    _class="child",
                ).__str__()
                for key, value in selected_fields[idx].items()
            ],
            self.back_button(),
            _class="container",
        )

        return view_html.__str__()

    def edit_form(self, idx: int):
        """
        form that allows users to edit form-row data
        """
        selected_fields = self.query.select()
        jwt_encoded = self.encode_jwt({"edit_data": 1, "idx": idx})

        edit_html = Form(
            *[
                Div(
                    H4(_class="field_block", text=key),
                    Input(_name=key, value=value),
                    _class="child",
                ).__str__()
                for key, value in selected_fields[idx].items()
                if key != "id"
            ],
            Div(self.back_button(), self.submit_button()).__str__(),
            action=url(App.request.path, jwt=jwt_encoded).__str__(),
            _class="container",
            method="POST",
        )

        return edit_html.__str__()

    def get_field_type(self, table_name, field_name):
        """
        gets the type of fields in html, so we can display it better in html
        """

        field_type = self.db.tables[table_name].fields[field_name].field_type
        translation_table = {"IMAGE": "file"}

        return translation_table.get(field_type, "text")

    @classmethod
    def no_records(cls):
        """
        display add button and no records found when no records are found
        """
        return f"""
                {cls.add_button()}
                {H3(text="No Records Found!")}
                <h3>No Records Found!</h3>
        """

    @classmethod
    def add_button(cls):
        """
        Button that goes to a page that will allow users to add rows to the database
        """

        jwt_encoded = cls.encode_jwt({"insert": 1})

        return A(
            Span("Add", title="Add"),
            _class="button btn btn-default btn-secondary insert",
            _href=url(App.request.path, jwt=jwt_encoded).__str__(),
        )

    @classmethod
    def submit_button(cls):
        """
        submits form information
        """
        return Input(
            _type="submit", _class="button btn btn-default btn-secondary insert"
        )

    @classmethod
    def back_button(cls):
        """
        removes all params from url and goes back to starting sql grid
        """
        return A(
            Span("Back", title="Back"),
            _class="button btn btn-default btn-secondary insert",
            _href=url(App.request.path),
        ).__str__()

    @classmethod
    def view_button(cls, button_idx):
        """
        goes to the view row page
        """
        jwt_encoded = cls.encode_jwt(
            {"view": 1, "idx": button_idx},
        )

        return A(
            Span("View", title="View"),
            _class="button btn btn-default btn-secondary insert",
            _href=url(App.request.path, jwt=jwt_encoded).__str__(),
        )

    @classmethod
    def edit_button(cls, button_idx):
        """
        goes to the edit row page
        """
        jwt_encoded = cls.encode_jwt({"edit": 1, "idx": button_idx})

        return A(
            Span("Edit", title="Edit"),
            _class="button btn btn-default btn-secondary insert",
            _href=url(App.request.path, jwt=jwt_encoded).__str__(),
        )

    @classmethod
    def delete_button(cls, button_idx):
        """
        goes to the 'url?delete_data=1' page so we can remove a sql row
        """
        jwt_encoded = cls.encode_jwt({"delete_data": 1, "idx": button_idx})

        return A(
            Span(
                "Delete",
                title="Delete",
            ),
            _class="button btn btn-default btn-secondary insert",
            _href=url(App.request.path, jwt=jwt_encoded).__str__(),
        )

    @classmethod
    def default_styling(cls):
        """
        default styling for all sql grids
        """
        return f"""
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
            <link rel="stylesheet" 
            href="//cdn.jsdelivr.net/gh/highlightjs/cdn-release@10.1.2/build/styles/default.min.css">
            <style type="text/css" media="screen">
                {pkgutil.get_data(__name__, "../static/form.css").decode()}
            </style>
        """

    @classmethod
    def encode_jwt(cls, items: dict):
        """
        encodes items in jwt
        """
        return jwt.encode(
            items,
            App.response.cookies["session"],
            algorithm="HS256",
        )

    @classmethod
    def decode_jwt(cls, jwt_str: str):
        """
        decodes encode jwt string
        """

        return jwt.decode(
            jwt_str,
            key=App.response.cookies["session"],
            algorithms=["HS256"],
        )


# This is a form in the literal sense
class TableForm:
    def __init__(self, table):
        ...
