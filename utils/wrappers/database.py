from pathlib import Path
import os
import sqlite3


class Database:
    db_position = Path(os.getenv("HOME"), ".config", "kaam", "sqlite.db")
    db = None

    def __init__(self):
        pass

    @classmethod
    def setup_databases(cls):
        cls.__setup_tasks_db()

    @classmethod
    def __setup_tasks_db(cls):
        if not cls.db_position.parent.exists():
            cls.db_position.parent.mkdir(parents=True)

        cls.db = sqlite3.connect(cls.db_position.absolute())
        cursor = cls.db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, priority INTEGER, due TEXT, done INTEGER);"
        )

        cls.db.commit()
        cursor.close()

    def get_tasks(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM tasks;")
        tasks = cursor.fetchall()
        cursor.close()
        return tasks

    @classmethod
    def reset_database(cls):
        cls.db.close()
        cls.db_position.unlink()
        cls.setup_databases()
        
    @classmethod
    def dispose(cls):
        cls.db.close()
