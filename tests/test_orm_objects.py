from webwithpy.orm.auth import Auth
from webwithpy.orm import DB, Table, Field
from unittest import TestCase


class Album(Table):
    photo_id = Field("reference photo.id")
    user_id = Field("reference auth_user.id")


class Photo(Table):
    table_name = 'photo'
    name = Field("string")
    bytes = Field("blob")


class TestOrm(TestCase):
    def setUp(self):
        self.db = DB("sqlite:/:memory:")
        self.auth = Auth()

    def tearDown(self):
        self.db.close()

    def test_table_create(self):
        self.db.create_tables(Photo, Album)
