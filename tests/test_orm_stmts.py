from webwithpy.orm import DB, Table, Field
from unittest import TestCase
from random import randint


class Test(Table):
    table_name = "test"
    num = Field("int")


class Test2(Table):
    table_name = "test2"
    test_1_id = Field("reference test.id")


class TestOrm(TestCase):
    def setUp(self):
        self.db = DB("sqlite:/:memory:")
        self.db.create_tables(Test, Test2)

    def tearDown(self):
        self.db.close()

    def test_insert_and_select_field(self):
        db = self.db
        range_len = 100

        for n in range(range_len):
            db.test.insert(num=n)

        self.assertEqual(len((db.test.id != -1).select()), range_len)
        db.test.insert(num=randint(0, 100))
        self.assertNotEqual(len((db.test.id != -1).select()), range_len)

    def test_reference(self):
        db = self.db
        range_len = 100

        for n in range(range_len):
            db.test.insert(num=n)

        ids: list[dict[str, int]] = (db.test.id >= 0).select(fields=["id"])

        for sql_id in ids:
            db.test2.insert(test_1_id=sql_id["id"])

        print((db.test.id == db.test2.test_1_id).select(debug=True))
