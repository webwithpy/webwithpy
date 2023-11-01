from ..orm.query import Query
from ..orm.db import DB
from ..app import App
from ..http import url
import jwt


# TODO: add jwt
class SQLForm:
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
        self.fields = [str(field).split(".")[1] for field in fields]

    def as_html(self):
        if "jwt" in App.request.vars:
            jwt_decoded = jwt.decode(
                App.request.vars["jwt"],
                key=App.request.cookies["session"],
                algorithms=["HS256"],
            )
            if "insert" in jwt_decoded:
                return self.default_styling() + self.insert_form()
            elif "view" in jwt_decoded:
                return self.default_styling() + self.view_form(jwt_decoded["idx"])
            elif "edit" in jwt_decoded:
                return self.default_styling() + self.edit_form(jwt_decoded["idx"])
            elif "insert_data" in jwt_decoded:
                db = self.query.db

                # get the id of the field we are going te be selecting
                table = getattr(db, self.query.__tables__()[0])
                table.insert(**App.request.form_data)
            elif "edit_data" in jwt_decoded:
                db = self.query.db
                # TODO, make the user give the table, rn we are only gonna grab the first table from the table
                fields = self.query.select()

                # get the id of the field we are going te be selecting
                table = getattr(db, self.query.__tables__()[0])
                (table.id == fields[jwt_decoded["idx"]]["id"]).update(
                    **App.request.form_data
                )
            elif "delete_data" in jwt_decoded:
                db = self.query.db

                # TODO, make the user give the table, rn we are only gonna grab the first table from the table
                fields = self.query.select()

                # get the id of the field we are going te be selecting
                table = getattr(db, self.query.__tables__()[0])
                (table.id == fields[jwt_decoded["idx"]]["id"]).delete(
                    **App.request.form_data
                )

        return f"<head>{self.default_styling()}</head>" + f"<body>{self.rows_to_table()}</body>"

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
                DB.tables[table].fields.keys() if len(self.fields) == 0 else self.fields
            ):
                keys += f"<td class='block'>{field_name}</td>"
        keys += "<th class='block'></th>" * (
            int(self.view) + int(self.edit) + int(self.delete) + len(self.links)
        )
        return keys

    def insert_form(self):
        jwt_encoded = jwt.encode(
            {"insert_data": 1},
            App.request.cookies["session"],
            algorithm="HS256",
        )

        insert_html = f"<form action='{url(App.request.path, jwt=jwt_encoded)}' class='container' method='POST'>"
        insert_html += "".join(
            [
                f"<input name='{field_name}' placeholder='{field_name}'/>"
                for field_name in DB.tables[self.query.table_name].fields.keys()
                if field_name != "id"
            ]
        )
        insert_html += f"<div>{self.back_button()}{self.submit_button()}</div>"
        insert_html += "</form>"
        return insert_html

    def view_form(self, idx):
        selected_fields = self.query.select()
        view_html = "<div class='container'>"
        view_html += "".join(
            [
                f"<div class='child'> <h4 class='field_block'>{key}:</h4><input value='{value}' disabled /> </div>"
                for key, value in selected_fields[idx].items()
            ]
        )
        view_html += self.back_button()
        view_html += "</div>"
        return view_html

    def edit_form(self, idx):
        selected_fields = self.query.select()

        jwt_encoded = jwt.encode(
            {"edit_data": 1, "idx": idx},
            App.request.cookies["session"],
            algorithm="HS256",
        )

        edit_html = f"<form action='{url(App.request.path, jwt=jwt_encoded)}' class='container' method='POST'>"
        edit_html += "".join(
            [
                f"<div class='child'> <h4 class='field_block'>{key}:</h4><input name='{key}' value='{value}' /> </div>"
                for key, value in selected_fields[idx].items()
                if key != "id"
            ]
        )
        edit_html += f"<div>{self.back_button()}{self.submit_button()}<div>"
        edit_html += "</form>"
        return edit_html

    @classmethod
    def no_records(cls):
        return f"""
                {cls.add_button()}
                <h3>No Records Found!</h3>
        """

    @classmethod
    def add_button(cls):
        jwt_encoded = jwt.encode(
            {"insert": 1},
            App.request.cookies["session"],
            algorithm="HS256",
        )

        return f"""
                <a class ="button btn btn-default btn-secondary insert" href="{url(App.request.path, jwt=jwt_encoded)}">
                        <span title="Add">Add</span></a>
            """

    @classmethod
    def submit_button(cls):
        return f"""
            <input type='submit' class="button btn btn-default btn-secondary insert""/>
        """

    @classmethod
    def back_button(cls):
        return f"""
            <a class="button btn btn-default btn-secondary insert" href="/">
                    <span title="Back">Back</span></a>
        """

    @classmethod
    def view_button(cls, button_idx):
        jwt_encoded = jwt.encode(
            {"view": 1, "idx": button_idx},
            App.request.cookies["session"],
            algorithm="HS256",
        )
        return f"""
            <a class ="button btn btn-default btn-secondary insert" href="{url(App.request.path, jwt=jwt_encoded)}">
                        <span title="View">View</span></a>
        """

    @classmethod
    def edit_button(cls, button_idx):
        jwt_encoded = jwt.encode(
            {"edit": 1, "idx": button_idx},
            App.request.cookies["session"],
            algorithm="HS256",
        )

        return f"""
                <a class ="button btn btn-default btn-secondary insert" href="{url(App.request.path, jwt=jwt_encoded)}">
                        <span title="Edit">Edit</span></a>
            """

    @classmethod
    def delete_button(cls, button_idx):
        jwt_encoded = jwt.encode(
            {"delete_data": 1, "idx": button_idx},
            App.request.cookies["session"],
            algorithm="HS256",
        )

        return f"""
                <a class ="button btn btn-default btn-secondary insert" href="{url(App.request.path, jwt=jwt_encoded)}">
                        <span title="Delete">Delete</span></a>
            """

    @classmethod
    def default_styling(cls):
        return """
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
            <link rel="stylesheet" href="//cdn.jsdelivr.net/gh/highlightjs/cdn-release@10.1.2/build/styles/default.min.css">
            <style type="text/css" media="screen">
                table {
                    border-collapse: collapse;
                    margin-top: 7px;
                }
            
                table td {
                    padding: 2px 5px;
                    min-width: 67px;
                    min-height: 40px;
                    text-align: center;
                    height: 40px;
                    font-size: 14px;
                    line-height: 1.42857143;
                    box-sizing: border-box;
                    margin: 0 auto;
                }
            
                table th {
                    color: #29abe0;
                    padding: 10px 5px;
                    background-color: #EAEAEA;
                    box-sizing: border-box;
                }
            
                tbody tr:nth-child(odd) {
                    background-color: #F9F9F9;
                }
                tbody tr:nth-child(even) {
                    background-color: #ffffff;
                }
            
                tbody tr:hover {
                    background-color: #F2F2F2;
                }
            
                .insert {
                    margin-bottom: 10px;
                }
            
                .btn-default {
                    color: #ffffff;
                    background-color: #3e3f3a;
                    border-color: transparent;
                }
                
                .block {
                    background-color: #EBEBEB;
                }
                
                .scroll_div {
                    margin: 10 10;
                    overflow-x: auto;
                    max-width: 95%;
                }
                .container {
                    display: grid;
                    grid-template-columns: repeat(1, 2fr);
                    gap: 30px;
                    justify-items: center;
                    margin-top: 20px;
                    min-height: 200px;
                    border-style: solid;
                }
 
                .child {
                    display: grid;
                    grid-template-columns: auto 1fr;
                    gap: 20px;
                    align-items: center;
                }
                
                .field_block {
                    min-width: 200px;
                }

            </style>
        """
