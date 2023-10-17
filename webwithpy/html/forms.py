from ..orm.query import Query
from ..orm.db import DB
from ..app import App
from ..http import url
from pathlib import Path
import jwt


# TODO: add jwt
class SQLForm:
    def __init__(
        self,
        query: Query,
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
        dbset=None,
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
        self.dbset = dbset or {}
        self.query = query

    def as_html(self):
        return self.default_styling() + self.rows_to_table()

    def rows_to_table(self):
        db_tables = self.query.__tables__()
        table_keys = self.table_keys(db_tables)
        table_values = self.table_from_query()

        return f"""
                <div class="scroll_div">
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

    def table_from_query(self):
        rows = ""
        for row in self.query.select():
            blocks = [f"<td>{value}</td>" for value in row.values()]
            rows += f'<tr>{"".join(blocks)}'

            if self.view:
                rows += f'<td> {self.view_button()} </td>'
            if self.edit:
                rows += f'<td> {self.edit_button()} </td>'
            if self.delete:
                rows += f'<td> {self.delete_button()} </td>'

            rows += '</tr>'

        return rows

    def table_keys(self, tables):
        keys = ""
        for table in tables:
            for field_name in DB.tables[table].fields.keys():
                keys += f"<td class='block'>{field_name}</td>"
        keys += "<th class='block'></th>" * (
                int(self.view) + int(self.edit) + int(self.delete) + len(self.links)
        )
        return keys

    @classmethod
    def no_records(cls):
        return "<h3>No Records Found!</h3>"

    @classmethod
    def insert_button(cls):
        # TODO: go to correct path!
        return f"""
            <a class ="button btn btn-default btn-secondary insert" href="/">
                    <span title="Insert">Insert</span></a>
        """

    @classmethod
    def view_button(cls):
        return f"""
            <a class ="button btn btn-default btn-secondary insert" href="{url(App.request.path)}">
                        <span title="View">View</span></a>
        """

    @classmethod
    def edit_button(cls):
        # TODO: go to correct path!
        return f"""
                <a class ="button btn btn-default btn-secondary insert" href="{url(App.request.path)}">
                        <span title="Edit">Edit</span></a>
            """

    @classmethod
    def delete_button(cls):
        return f"""
                <a class ="button btn btn-default btn-secondary insert" href="{url(App.request.path)}">
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
                block {
                    width: 80px;
                    height:80px
                }
            </style>
        """
