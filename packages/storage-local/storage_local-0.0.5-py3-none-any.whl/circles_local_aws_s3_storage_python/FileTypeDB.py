import os
import mysql.connector
from dotenv.main import load_dotenv
load_dotenv()


class file_type_db:
    def __init__(self) -> None:
        self.mydb = mysql.connector.connect(
            host=os.getenv("RDS_HOSTNAME"),
            user=os.getenv("RDS_USERNAME"),
            passwd=os.getenv("RDS_PASSWORD"),
            database=os.getenv("RDS_DB_NAME")
        )
        self.cursor = self.mydb.cursor()

    def select_from_DB(self, select_stmt, select_data):
        self.cursor.execute(select_stmt, [select_data])
        folder = self.cursor.fetchone()[0]
        return folder
