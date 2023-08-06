# stdlib
import hashlib
import logging
import os
import pathlib
from typing import List

# thirdparty
from clickhouse_driver import Client


class Migrator:
    """
    Script Migrator for ClickHouse Database

    :param migrations_dir: Directory with sql migration files
    :param db_host: Database host
    :param db_name: Database name
    :param db_user: Database user
    :param db_password: Database user password
    :param db_port: Database port (default: 8999)
    :param create_db_if_not_exists: Flag to create a database 'db_name',
                                    if it does not exist (default: True)
    """

    def __init__(
        self,
        migrations_dir: pathlib.Path,
        db_host: str = "localhost",
        db_name: str = "default",
        db_user: str = "default",
        db_password: str = "",
        db_port: int = 8999,
        create_db_if_not_exists: bool = True,
    ):
        self.migrations_dir = migrations_dir
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_password
        self.create_db_if_not_exists = create_db_if_not_exists

    def migrate(self):
        """Starts the process of performing migrations for the ClickHouse database"""
        self.connection = self._get_connection()

        if self.create_db_if_not_exists:
            self._create_database()

        self._create_history_table()
        self._apply_migrations()
        self.connection.disconnect()

    def _get_connection(self):
        """Gets a database connection"""
        return Client(self.db_host, port=self.db_port, user=self.db_user, password=self.db_pass, database=self.db_name)

    def _create_database(self):
        """Executes a script to create a database"""
        self.connection.execute(f"create database if not exists {self.db_name}")

    def _create_history_table(self):
        """Executes a script to create a migration accounting table"""
        query = """
            create table if not exists migration_history
                (
                version UInt16 comment 'Порядковый номер скрипта',
                file_name String comment 'Наименование файла',
                checksum String comment 'Контрольная сумма',
                installed_on DateTime DEFAULT now() comment 'Дата выполнения',
                success Bool comment 'Подтверждение выполнения миграции'
                )
            engine = MergeTree order by tuple(installed_on)
        """
        self.connection.execute(query)

    def _apply_migrations(self):
        """The main function of applying migrations"""
        self.migrations_from_dir = self._get_migrations_from_dir()
        self.applied_migrations = self._get_applied_migrations_dict()

        self._compare_and_execute_migrations()

    def _get_migrations_from_dir(self) -> List[dict]:
        """Gets a list of migrations from the 'migrations_dir' directory"""
        migrations = []
        for f in os.scandir(f"{self.migrations_dir}"):
            if not f.name.endswith(".sql"):
                continue
            content = pathlib.Path(f"{self.migrations_dir}/{f.name}").read_bytes()
            checksum = hashlib.md5(content).hexdigest()
            content = content.decode(encoding="utf-8")
            migration = {
                "version": int(f.name.split(".")[0]),
                "file_name": f.name,
                "content": content,
                "checksum": checksum,
            }
            migrations.append(migration)

        return migrations

    def _get_applied_migrations_dict(self) -> dict:
        """Gets a dict of previously executed migrations from the 'migration_history' table"""
        query = """
            select version,
                file_name,
                checksum,
                success
            from migration_history
        """
        applied_migrations = self.connection.execute(query, with_column_types=True)
        column_names = tuple(c[0] for c in applied_migrations[-1])
        applied_migrations = (dict(zip(column_names, d)) for d in applied_migrations[0])
        applied_migrations_dict = {
            m["version"]: {"file_name": m["file_name"], "checksum": m["checksum"], "success": m["success"] == 1}
            for m in applied_migrations
        }

        return applied_migrations_dict

    def _compare_and_execute_migrations(self):
        """Performs comparison and application of migrations"""
        if not self.migrations_from_dir:
            raise AssertionError(f"{self.migrations_dir} directory missing migration files")
        if len(self.migrations_from_dir) < len(self.applied_migrations.keys()):
            raise AssertionError(
                f"The number of executable migrations cannot be less than those already applied,"
                f"Applied: {len(self.applied_migrations.keys())},"
                f"Executable: {len(self.migrations_from_dir)}"
            )

        self.migrations_from_dir.sort(key=lambda m: m["version"])

        for m in self.migrations_from_dir:
            version, checksum = m["version"], m["checksum"]
            filename, migration_script = m["file_name"], m["content"]

            if not self._is_already_applied(version):
                self._execute_migration(version, checksum, filename, migration_script)
            elif not self._is_success(version):
                raise AssertionError(f"Error: script {filename} was previously executed incorrectly")
            elif self._is_checksum_equal(version, checksum):
                continue
            else:
                raise AssertionError(f"Error: retrying to apply migrations {filename}, checksum does not match")
        logging.info("Migrations completed")

    def _is_already_applied(self, version: int) -> bool:
        """Indicates if the migration script is previously applied"""
        return version in self.applied_migrations

    def _is_checksum_equal(self, version: int, checksum: str) -> bool:
        """Indicates if checksums of migrations match"""
        return self.applied_migrations[version]["checksum"] == checksum

    def _is_success(self, version: int) -> bool:
        """Indicates if the migration was applied successfully"""
        return self.applied_migrations[version]["success"]

    def _execute_migration(self, version: int, checksum: str, filename: str, migration_script: str):
        """Performs migrations, including those consisting of several scripts"""
        script, success = None, False
        try:
            scripts = self._form_scripts_for_execute(migration_script)
            for script in scripts:
                self.connection.execute(script)
            success = True
            self.applied_migrations[version] = {"file_name": filename, "checksum": checksum, "success": success}
        except Exception as err:
            success = False
            raise Exception(
                f"Error while executing the script:\n" f"{script}\n" f"Filename: {filename}\n" f"Error: {err}"
            )
        finally:
            self._add_record_to_history(version, filename, checksum, success)

    @staticmethod
    def _form_scripts_for_execute(migration_script: str) -> List[str]:
        """Generates a list of scripts from a migration"""
        scripts = []
        for s in migration_script.split(";"):
            clean_script = s.strip()
            if clean_script:
                scripts.append(clean_script)
        return scripts

    def _add_record_to_history(self, version: int, filename: str, checksum: str, success: bool):
        """Adds a record to the migration history table"""
        self.connection.execute(
            """insert into migration_history (
                    version, file_name, checksum, success
                ) values""",
            [
                {
                    "version": version,
                    "file_name": filename,
                    "checksum": checksum,
                    "success": success,
                }
            ],
        )
