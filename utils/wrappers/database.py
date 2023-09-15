import sqlite3

from utils.models import Task
from utils import constants


class Database:
    db_position = constants.DB_PATH
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

        alltables = cursor.execute("PRAGMA table_list;")
        tlist = alltables.fetchall()
        tlist_names = [x[1] for x in tlist]
        if "tasks" in tlist_names:
            otable_version = ""
            if "table_meta" not in tlist_names:
                otable_version = "UNDEFINED_ALPHA"
            else:
                otable_version = cursor.execute(
                    "SELECT value FROM table_meta WHERE key = 'version';"
                ).fetchall()[0][0]
            if otable_version != constants.VERSION:
                print(
                    f"Attempting update of old DB {otable_version} to new DB v{constants.VERSION}."
                )

                cursor.execute("ALTER TABLE tasks ADD COLUMN created_date TIMESTAMP;")
                cls.db.commit()
                cursor.execute(
                    "UPDATE table_meta SET value = ? WHERE key = 'version';",
                    (constants.VERSION,),
                )
                cls.db.commit()
                cursor.close()

                print(f"DB successfully updated to v{constants.VERSION}.")

        cursor = cls.db.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT, aliases TEXT, tasks_id INTEGER, FOREIGN KEY(tasks_id) REFERENCES tasks(id));"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, priority INTEGER, due TIMESTAMP, done BOOLEAN, created_date TIMESTAMP);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS table_meta (id INTEGER PRIMARY KEY, key TEXT, value TEXT);"
        )
        if "table_meta" not in tlist_names:
            cls.db.commit()
            cursor.execute(
                "INSERT INTO table_meta(key, value) VALUES (?, ?);",
                ("version", constants.VERSION),
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
        
        tasks = [Task.create_from_db(task) for task in tasks]
        return tasks

    def add_task(self, newtask: Task):
        cursor = self.db.cursor()
        insertQuery = (
            """INSERT INTO tasks(name, priority, due, done, created_date) VALUES (?, ?, ?, ?, ?);"""
        )
        cursor.execute(insertQuery, (newtask.name, newtask.priority, newtask.due, False, newtask.time_created))
        self.db.commit()
        cursor.execute("SELECT last_insert_rowid();")
        tid = cursor.fetchall()[0][0]
        cursor.close()
        newtask.id = tid
        return newtask

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

    def edit_task(self, task_id, task_name=None, task_priority=None, task_due=None):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM tasks WHERE id = {task_id};")
        task = cursor.fetchall()[0]
        task = Task.create_from_db(task)
        cursor.execute(
            "UPDATE tasks SET name = ?, priority = ?, due = ? WHERE id = ?;",
            (
                task_name if task_name else task.name,
                task_priority if task_priority else task.priority,
                task_due if task_due else task.due,
                task_id,
            ),
        )
        self.db.commit()
        cursor.close()

    def clean_tasks(self):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tasks WHERE done = ?;", (True,))
        self.db.commit()
        cursor.close()

    def get_ids(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT id FROM tasks;")
        ids = cursor.fetchall()
        cursor.close()
        return [x[0] for x in ids]