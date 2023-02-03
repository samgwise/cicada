import sqlite3

class Logger():
    def __init__(self, path):
        self.log_path
        self.log_db = SQLiteLogger(path)

        self.experiment_id = self.log_db.new_experiment()

    def log_parameters(self, params):

    def log_progress(self, loss, tick):
        self.log_db.

    def log_event(self, title, body, tick):


class SQLiteLogger():
    def __init__(self, db_path):
        self.db_file = Path(db_path).joinpath("logs/logs.sqlite")

        ### Queries ###
        self.insert_event_sql = """
        INSERT INTO event_log (
            experiment_id, tick, event_title, event_body, event_created
            ) VALUES (
                ?, ?, ?, ?, now
            )
        """

        self.insert_progress_sql = """
        INSERT INTO progress_log (
            experiment_id, tick, loss, progress_created
            ) VALUES (
                ?, ?, ?, NOW
            )
        """

        self.insert_experiment_sql = """
        INSERT INTO experiment (
            start_time
            ) VALUES (
                NOW
            )
        """

        self.update_params_sql = """
        UPDATE experiment (
            parameters = ?
            ) WHERE experiment_id = ?
        """

        self.update_completion_sql = """
        UPDATE experiment (
            completed = ?,
            run_duration_seconds = unixepoch(NOW) - unixepoch(start_time)
            ) WHERE experiment_id = ?
        """

        ### DB Init ###
        self.db_con = sqlite3.connect(self.db_file)
        db_cur = self.db_con.curser()

        create_experiment_table_sql = """
        CREATE TABLE IF NOT EXISTS experiment (
            experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME NOT NULL,
            run_duration_seconds INTEGER,
            completed INTEGER NOT NULL DEFAULT FALSE,
            parameters TEXT
        )"""
        db_cur.execute(create_experiment_table_sql)

        create_progress_table_sql = """
        CREATE TABLE IF NOT EXISTS progress_log (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            tick INTEGER NOT NULL,
            loss NUMBER NOT NULL,
            progress_created DATETIME NOT NULL
        )"""
        db_cur.execute(create_progress_table_sql)

        create_event_table_sql = """
        CREATE TABLE IF NOT EXISTS event_log (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            tick INTEGER,
            event_title TEXT NOT NULL,
            event_body TEXT,
            event_created DATETIME NOT NULL
        )"""
        db_cur.execute(create_event_table_sql)

    def insert_oneshot(self, query):
        db_cur = self.db_con.curser()
        row_id = db_cur.lastrowid
        db_cur.connection.commit()
        return row_id

    def new_experiment(self):
        return self.insert_oneshot(self.self.insert_experiment_sql)

    def log_progress(self, )