#!/bin/python
import psycopg2
from psycopg2.extras import RealDictCursor
from src.customLogger import custom_logger


class PostgresHandler:
    """
    This is a class to handle postgres operations
    """
    def __init__(self, hostname, port, database, user, pwd):
        self._hostname = hostname
        self._port = port
        self._database = database
        self._user = user
        self._pwd = pwd
        self._conn = None
        # logger
        self.logger = custom_logger("PostgresHandler")

        self.initialize_connection()
        # self.create_table_if_not_exists()


    def initialize_connection(self):
        """
        Initialize the connection
        :return: Connection
        """
        try:
            self._conn = psycopg2.connect(
                "dbname='{}' user='{}' host='{}' password='{}' port='{}'".format(
                    self._database, self._user, self._hostname, self._pwd, self._port
                )
            )
        except Exception as e:
            self.logger.error(e)
            return None

    def close_connection(self):
        """
        Close the connection
        :return:
        """
        try:
            self._conn.close()
            return True
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Problem closing the bookkeeper connection")
            return False

    def refresh_connection(self):
        self.close_connection()
        self.initialize_connection()

    def create_table_if_not_exists(self):
        """
        Create table processed_time.processed_time if not exists yet
        :return: None
        """
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * FROM pg_catalog.pg_tables 
                WHERE schemaname='processed_time' 
                AND tablename='processed_time';
        """)
        tables = cur.fetchall()
        if len(tables) == 0:
            try:
                cur.execute("CREATE SCHEMA processed_time;")
                cur.execute("""
                    CREATE TABLE processed_time.processed_time (
                        dataset_name VARCHAR(100) PRIMARY KEY,
                        modified_timestamp TIMESTAMPTZ
                    );
                    """)
                self._conn.commit()
            except Exception as e:
                self.logger.error(e)
            finally:
                cur.close()

    def get_latest_modified_timestamp(self, dataset_name):
        """
        Get latest modified timestamp for dataset
        :param dataset_name: Dataset name
        :return: Timestamp
        """
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT modified_timestamp from processed_time.processed_time
                WHERE dataset_name='{}';
        """.format(dataset_name))
        try:
            modified_time = cur.fetchall()
            if len(modified_time) == 0:
                return None
            else:
                return modified_time[0]["modified_timestamp"]
        except Exception as e:
            self.logger.error(e)
            return None
        finally:
            cur.close()


    def get_cluster_assignments(self):
        """
        Get cluster assignments
        :return: assignments in a dict
        """
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, data from persistence.cluster_feedback_ns_current;
        """)
        try:
            assignments = cur.fetchall()
            if len(assignments) == 0:
                return None
            else:
                return assignments
        except Exception as e:
            self.logger.error(e)
            return None
        finally:
            cur.close()


    def update_latest_modified_timestamp(self, dataset_name, timestamp):
        """
        Update latest modified timestamp for dataset
        :param dataset_name: Dataset name
        :param timestamp: Timestamp to be updated with
        :return: Timestamp if successful. Otherwise None
        """
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("""
                UPDATE processed_time.processed_time 
                    SET dataset_name='{}', modified_timestamp='{}' WHERE dataset_name='{}';
                INSERT INTO processed_time.processed_time (dataset_name, modified_timestamp)
                    SELECT '{}', '{}'
                    WHERE NOT EXISTS (SELECT 1 FROM processed_time.processed_time WHERE dataset_name='{}');
                """.format(dataset_name, timestamp.strftime("%Y-%m-%d %H:%M:%S.%f %z"), dataset_name,
                           dataset_name, timestamp.strftime("%Y-%m-%d %H:%M:%S.%f %z"), dataset_name))
            self._conn.commit()
            return timestamp
        except Exception as e:
            self.logger.error(e)
            return None
        finally:
            cur.close()

    def get_all_tables(self):
        """
        (For test only)
        Get all tables under the database, as validation of connection.
        :return: True if successful. Otherwise False.
        """
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * from pg_catalog.pg_tables;
        """)
        try:
            all_tables = cur.fetchall()
            if len(all_tables) == 0:
                print("Problem getting tables from deltabooks database")
                return False
            else:
                for table in all_tables:
                    print(table)
                return True
        except Exception as e:
            print(e)
            print("ERROR: Problem getting tables from deltabooks database")
            return False
        finally:
            cur.close()
