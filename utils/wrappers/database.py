from pathlib import Path
import os
import sqlite3

from utils.models import Task


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

        cls.db = sqlite3.connect(
            cls.db_position.absolute(),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        cursor = cls.db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, priority INTEGER, due TIMESTAMP, done BOOLEAN);"
        )

        cls.db.commit()
        cursor.close()

    @classmethod
    def reset_database(cls):
        cls.db.close()
        cls.db_position.unlink()
        cls.setup_databases()

    @classmethod
    def dispose(cls):
        cls.db.close()

    def get_tasks(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM tasks;")
        tasks = cursor.fetchall()
        cursor.close()
        tasks = [Task.create_from_db(task) for task in tasks]
        return tasks

    def add_task(self, task_name, task_priority, task_due):
        cursor = self.db.cursor()
        insertQuery = (
            """INSERT INTO tasks(name, priority, due, done) VALUES (?, ?, ?, ?);"""
        )
        cursor.execute(insertQuery, (task_name, task_priority, task_due, False))
        self.db.commit()
        cursor.close()

    def remove_task(self, task_id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
        self.db.commit()
        cursor.close()

    def mark_task_as_done(self, task_id):
        cursor = self.db.cursor()
        cursor.execute("UPDATE tasks SET done = ? WHERE id = ?;", (True, task_id))
        self.db.commit()
        cursor.close()
    
    def mark_task_as_undone(self, task_id):
        cursor = self.db.cursor()
        cursor.execute("UPDATE tasks SET done = ? WHERE id = ?;", (False, task_id))
        self.db.commit()
        cursor.close()
    
    def edit_task(self, task_id, task_name, task_priority=None, task_due=None):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM tasks WHERE id = {task_id};")
        task = cursor.fetchall()[0]
        task = Task.create_from_db(task)
        cursor.execute(
            "UPDATE tasks SET name = ?, priority = ?, due = ? WHERE id = ?;",
            (task_name, task_priority if task_priority else task.priority, task_due if task_due else task.due, task_id),
        )
        self.db.commit()
        cursor.close()
    
    def clean_tasks(self):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tasks WHERE done = ?;", (True,))
        self.db.commit()
        cursor.close()
