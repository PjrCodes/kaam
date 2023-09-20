import sqlite3
from typing import Any

from utils.models import Task
from utils import constants

import json

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
            "CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT, aliases TEXT);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, priority INTEGER, due TIMESTAMP, done BOOLEAN, created_date TIMESTAMP);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS table_meta (id INTEGER PRIMARY KEY, key TEXT, value TEXT);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS task_category (id INTEGER PRIMARY KEY, tasks_id INTEGER, categories_id INTEGER);"
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
        
        tasksf = []
        for task in tasks:
            t = Task.create_from_db(task)
            t.category = self.get_task_category(t.id)
            tasksf.append(t)

        cursor.close()
        return tasksf

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

        if newtask.category:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM categories WHERE name = ?;", (newtask.category,))
            category = cursor.fetchall()
            if not category:
                print("Category does not exist, but the task has been added.")
                return
            category = category[0]
            cursor.execute("INSERT INTO task_category(tasks_id, categories_id) VALUES (?, ?);", (tid, category[0]))
            self.db.commit()
            cursor.close()
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

    def edit_task(self, task_id, task_name=None, task_priority=None, task_due=None, cat=None):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM tasks WHERE id = {task_id};")
        task = cursor.fetchall()[0]
        task = Task.create_from_db(task)
        task.category = self.get_task_category(task.id)
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

        if cat:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM categories WHERE name = ?;", (cat,))
            category = cursor.fetchall()
            print(category)
            if not category:
                print("Category does not exist, but the other values have been edited.")
                return
            category = category[0]
            cursor.execute("SELECT * FROM task_category WHERE tasks_id = ?;", (task_id,))
            task_category = cursor.fetchall()
            if task_category:
                cursor.execute("UPDATE task_category SET categories_id = ? WHERE tasks_id = ?;", (category[0], task_id))
            else:
                cursor.execute("INSERT INTO task_category(tasks_id, categories_id) VALUES (?, ?);", (task_id, category[0]))
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
    
    def add_category(self, name, aliases):
        cursor = self.db.cursor()
        # convert aliases to json list
        cursor.execute("SELECT * FROM categories WHERE name = ?;", (name,))
        if (cursor.fetchall()):
            print("Category already exists.")
            return
        if not aliases:
            aliases = []
        jstr = json.dumps(aliases)
        cursor.execute("INSERT INTO categories(name, aliases) VALUES (?, ?);", (name, jstr))
        self.db.commit()
        cursor.close()

    def remove_category(self, name):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM categories WHERE name = ?;", (name,))
        self.db.commit()
        cursor.close()

    def get_categories(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM categories;")
        categories = cursor.fetchall()
        cursor.close()
        return categories
    
    def edit_category(self, name, new_name):
        cursor = self.db.cursor()
        cursor.execute("UPDATE categories SET name = ? WHERE name = ?;", (new_name, name))
        self.db.commit()
        cursor.close()

    def add_category_alias(self, name, alias):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM categories WHERE name = ?;", (name,))
        category = cursor.fetchall()
        if not category:
            print("Category does not exist.")
            return
        category = category[0]
        aliases = json.loads(category[2])
        if alias in aliases:
            print("Alias already exists.")
            return
        aliases.append(alias)
        jstr = json.dumps(aliases)
        cursor.execute("UPDATE categories SET aliases = ? WHERE name = ?;", (jstr, name))
        self.db.commit()
        cursor.close()

    def remove_category_alias(self, name, alias):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM categories WHERE name = ?;", (name,))
        category = cursor.fetchall()
        if not category:
            print("Category does not exist.")
            return
        category = category[0]
        aliases = json.loads(category[2])
        if alias not in aliases:
            print("Alias does not exist.")
            return
        aliases.remove(alias.lower())
        jstr = json.dumps(aliases)
        cursor.execute("UPDATE categories SET aliases = ? WHERE name = ?;", (jstr, name))
        self.db.commit()
        cursor.close()

    def get_category_aliases(self, name):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM categories WHERE name = ?;", (name,))
        category = cursor.fetchall()
        if not category:
            print("Category does not exist.")
            return
        category = category[0]
        aliases = json.loads(category[2])
        cursor.close()
        return aliases

    def get_task_category(self, task_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM task_category WHERE tasks_id = ?;", (task_id,))
        category = cursor.fetchall()
        if not category:
            return None
        category = category[0]
        cursor.close()
        return self.get_category_by_id(category[2])
    
    def get_category_by_id(self, category_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?;", (category_id,))
        category = cursor.fetchall()
        if not category:
            return None
        category = category[0]
        cursor.close()
        return category[1]
