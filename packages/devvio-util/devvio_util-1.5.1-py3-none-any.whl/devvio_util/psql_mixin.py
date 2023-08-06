import psycopg2
import time


SQL_ATTEMPTS = 5


class PsqlMixin:
    def __init__(self, *args, **kwargs):
        """
        :param logger: Logging object
        :param db_secrets: Dict passing DB credentials (db_host, db_user, db_pass, db_name, db_port)
        :param sql_attempts: Number of attempts the query must try before throwing a timeout exception
        """
        try:
            super().__init__(*args, **kwargs)  # forwards all unused arguments
        except Exception as e:
            kwargs["logger"].debug("super().__init__() failed: {}".format(e))
        self._logger = kwargs["logger"]
        self._conn_string = None
        self._conn = None
        self._db_secrets = kwargs["db_secrets"]
        self._sql_attempts = kwargs.get("sql_attempts", SQL_ATTEMPTS)

    def set_conn_string(self):
        """
        Set the database connection string
        :return:
        :rtype:
        """
        db_host, db_user, db_pass, db_name, db_port = self.get_db_cred()
        self._conn_string = "host=" + db_host
        self._conn_string += " dbname=" + db_name
        self._conn_string += " user=" + db_user
        self._conn_string += " password=" + db_pass
        self._conn_string += " port=" + db_port

    def connect(self, autocommit: bool = True):
        """
        Connect to the database and set session options
        :return:
        :rtype:
        """
        # self._logger.info("Connecting to database: %s", self._conn_string)
        self._conn = psycopg2.connect(self._conn_string)
        self._logger.info("Database connected.")
        self._conn.set_session(autocommit=autocommit)

    def dbquery(self, *args, **kwargs):
        """
        Query the connected database. Attempt reconnect upon Operational or Interface error
        :param args:
        :param kwargs:
        :return:
        """
        attempts = self._sql_attempts
        while attempts > 0:
            attempts = attempts - 1
            try:
                n = len(self._conn.notices)
                cursor = self._conn.cursor()
                self._logger.debug(f"{args}")
                cursor.execute(*args, **kwargs)
                for notice in self._conn.notices[n:]:
                    self._logger.info(f'{notice}.')
                return cursor
            except psycopg2.OperationalError as e:
                self._logger.exception(e)
                self._logger.notice("psycopg2.OperationalError: {}".format(e))
                time.sleep(0.2)
                self.connect()
            except psycopg2.InterfaceError as e:
                self._logger.exception(e)
                self._logger.notice("psycopg2.InterfaceError: {}".format(e))
                time.sleep(0.2)
                self.connect()
            except psycopg2.Error as e:
                self._logger.exception(e)
                raise

        raise TimeoutError("Reached maximum number of DB connection retries.")

    def commit(self):
        """
        Commit DB updates.
        :return:
        """
        self._conn.commit()

    def rollback(self):
        """
        Rollback uncommitted updates.
        :return:
        """
        self._conn.rollback()

    def get_db_cred(self):
        db_host = self._db_secrets.get("DEVV_DB_HOST")
        db_user = self._db_secrets.get("DEVV_DB_USER")
        db_pass = self._db_secrets.get("DEVV_DB_PASS")
        db_name = self._db_secrets.get("DEVV_DB_NAME")
        db_port = self._db_secrets.get("DEVV_DB_PORT")
        return db_host, db_user, db_pass, db_name, db_port
