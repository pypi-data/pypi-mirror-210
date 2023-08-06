# stdlib
import unittest
from pathlib import Path

# thirdparty
from clickhouse_driver import Client

from click_migrator.migrator import Migrator


class TestMigrator(unittest.TestCase):
    def execute_script(self, query):
        data = self.client.execute(query, with_column_types=True)
        column_names = tuple(c[0] for c in data[-1])
        return [dict(zip(column_names, d)) for d in data[0]]

    @classmethod
    def setUpClass(cls) -> None:
        db_host = "localhost"
        db_name = "default"
        db_user = "default"
        db_password = ""
        migrations_dir = Path("")
        db_port = 9000

        cls.migrator = Migrator(migrations_dir, db_host, db_name, db_user, db_password, db_port)
        cls.client = Client(db_host, port=db_port, user=db_user, password=db_password, database=db_name)

        cls.history_script = """
                select
                    version,
                    file_name,
                    checksum,
                    success
                from migration_history
        """

        cls.table1_script = """
                select
                    id,
                    value,
                    bool_value,
                    str_value
                from table1
        """

        cls.table2_script = """
                select
                    id,
                    value,
                    bool_value,
                    str_value
                from table2
        """

        cls.expected_table_data = [
            {"id": 1, "value": 2.3, "bool_value": 1, "str_value": "comment1"},
            {"id": 2, "value": 4.5, "bool_value": 0, "str_value": "comment2"},
            {"id": 3, "value": 6.7, "bool_value": 1, "str_value": "comment3"},
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.disconnect()

    def tearDown(self) -> None:
        self.client.execute("drop table if exists default.migration_history")
        self.client.execute("drop table if exists default.table1")
        self.client.execute("drop table if exists default.table2")

    def test_migrate_with_empty_folder(self):
        self.migrator.migrations_dir = Path("./empty_folder/")
        self.assertRaises(AssertionError, self.migrator.migrate)

    def test_migrate_with_some_migration_files(self):
        self.migrator.migrations_dir = Path("./some_migration_files/")
        self.migrator.migrate()

        history = self.execute_script(self.history_script)
        table1_data = self.execute_script(self.table1_script)
        table2_data = self.execute_script(self.table2_script)
        sorted_history = sorted(history, key=lambda d: d["version"])
        sorted_table1_data = sorted(table1_data, key=lambda d: d["id"])

        expected_history = [
            {
                "version": 1,
                "file_name": "001.create.default.table1.sql",
                "checksum": "d18349d55813148857afb191d85b7350",
                "success": True,
            },
            {
                "version": 2,
                "file_name": "002.insert.default.table1.sql",
                "checksum": "dec826b82a1960265a8091eaa4448069",
                "success": True,
            },
            {
                "version": 3,
                "file_name": "003.create.default.table2.sql",
                "checksum": "90cfb131c0a9b98bf8b597e323eacd85",
                "success": True,
            },
        ]
        self.assertListEqual(sorted_history, expected_history)
        self.assertListEqual(sorted_table1_data, self.expected_table_data)
        self.assertListEqual(table2_data, [])

    def test_migrate_with_some_scripts_in_one_migration_file(self):
        self.migrator.migrations_dir = Path("./some_scripts_in_one_migration_file/")
        self.migrator.migrate()

        history = self.execute_script(self.history_script)
        table1_data = self.execute_script(self.table1_script)
        table2_data = self.execute_script(self.table2_script)
        sorted_history = sorted(history, key=lambda d: d["version"])
        sorted_table1_data = sorted(table1_data, key=lambda d: d["id"])

        expected_history = [
            {
                "version": 1,
                "file_name": "001.create_and_insert.default.table1.sql",
                "checksum": "2ce3555d8210ba604b85a41bf9446d5d",
                "success": True,
            },
            {
                "version": 2,
                "file_name": "002.create.default.table2.sql",
                "checksum": "90cfb131c0a9b98bf8b597e323eacd85",
                "success": True,
            },
        ]
        self.assertListEqual(sorted_history, expected_history)
        self.assertListEqual(sorted_table1_data, self.expected_table_data)
        self.assertListEqual(table2_data, [])

    def test_migrate_with_same_version(self):
        self.migrator.migrations_dir = Path("./migrations_with_same_version/")
        self.assertRaises(AssertionError, self.migrator.migrate)


if __name__ == "__main__":
    unittest.main()
