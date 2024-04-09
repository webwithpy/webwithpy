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

    def create_fields_test_tbl(self, size: int = 100):
        db = self.db

        for n in range(size):
            db.test.insert(num=n)

    def test_insert_and_select_field(self):
        db = self.db
        size = 100
        self.create_fields_test_tbl(size)

        self.assertEqual(len((db.test.id != -1).select()), size)
        db.test.insert(num=randint(0, 100))
        self.assertNotEqual(len((db.test.id != -1).select()), size)

    def test_reference(self):
        db = self.db
        self.create_fields_test_tbl()

        ids: list[dict[str, int]] = (db.test.id >= 0).select(fields=["id"])

        for sql_id in ids:
            db.test2.insert(test_1_id=sql_id["id"])

        self.assertFalse(
            "INNER JOIN" in (db.test.id == db.test2.test_1_id).select(debug=True)[0]
        )

        # This should never be a left join since test.id isn't a reference to
        self.assertTrue(
            "INNER JOIN" in (db.test2.test_1_id == db.test.id).select(debug=True)[0]
        )

    def test_update_field(self):
        db = self.db

        self.create_fields_test_tbl()
        (db.test.id >= 0).update(num=100)
        nums: list[dict[str, int]] = (db.test.id >= 0).select(fields=["num"])

        for d in nums:
            self.assertTrue(d["num"], 100)

    def test_delete_field(self):
        db = self.db

        self.create_fields_test_tbl()
        (db.test.id >= 0).delete()
        self.assertTrue(len((db.test.id >= 0).select()) == 0)
