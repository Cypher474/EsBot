import pymysql
from mysql.connector import Error
from dotenv import load_dotenv
import os 
# Database configuration
load_dotenv()

print(os.getenv("DB_HOST"))
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(**self.config)
            print("Connection established successfully.")
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Connection closed.")

    # Method to check if the database is connected
    def check_connection(self):
        if self.connection and self.connection.open:
            print("Database is connected.")
        else:
            print("No active database connection.")

    # Method to get table structure
    def get_table_structure(self):
        if not self.connection:
            print("No connection to the database.")
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    print(f"\nTable: {table_name}")

                    cursor.execute(f"DESCRIBE {table_name};")
                    columns = cursor.fetchall()
                    print("\nColumns:")
                    for column in columns:
                        print(f" - {column[0]}: {column[1]} ({'NULL' if column[2] == 'YES' else 'NOT NULL'})")

                    cursor.execute(f"SHOW INDEX FROM {table_name};")
                    indexes = cursor.fetchall()
                    print("\nIndexes:")
                    for index in indexes:
                        if index[1] == 0:  # Checking for non-unique index (1 for unique, 0 for not unique)
                            print(f" - {index[2]}: Non-unique key on column {index[4]}")
                        else:
                            print(f" - {index[2]}: Unique key on column {index[4]}")
        except Exception as e:
            print(f"Error fetching table structure: {str(e)}")

    # Method to display the contents of a table
    def display_table_contents(self, table_name):
        if not self.connection:
            print("No connection to the database.")
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                print(f"\nContents of table {table_name}:")
                for row in rows:
                    print(row)
        except Exception as e:
            print(f"Error fetching contents of table {table_name}: {str(e)}")

    # Method to drop a table
    def drop_table(self, table_name):
        if not self.connection:
            print("No connection to the database.")
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                self.connection.commit()
                print(f"Table {table_name} dropped successfully.")
        except Exception as e:
            print(f"Error dropping table {table_name}: {str(e)}")

    # Method to create the ChatData table
    def create_table(self, table_name):
        if not self.connection:
            print("No connection to the database.")
            return
        try:
            with self.connection.cursor() as cursor:
                create_query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    ChatID INT(11) NOT NULL AUTO_INCREMENT,
                    StudentEmail VARCHAR(255) NOT NULL,
                    ThreadID VARCHAR(255) NULL,
                    AssistantID VARCHAR(255) NULL,
                    ChatHistory TEXT NULL,
                    PRIMARY KEY (ChatID),
                    UNIQUE KEY StudentEmail (StudentEmail),
                    KEY ThreadID (ThreadID)
                );
                """
                cursor.execute(create_query)
                self.connection.commit()
                print(f"Table {table_name} created successfully.")
        except Exception as e:
            print(f"Error creating table {table_name}: {str(e)}")

    # Method to alter the table (rename StudentEmail to StudentID)
    def alter_table(self, table_name):
        if not self.connection:
            print("No connection to the database.")
            return
        try:
            with self.connection.cursor() as cursor:
                alter_query = f"""
                ALTER TABLE {table_name} 
                CHANGE COLUMN StudentEmail StudentID VARCHAR(255) NOT NULL;
                """
                cursor.execute(alter_query)
                self.connection.commit()
                print(f"Table {table_name} altered successfully (StudentEmail -> StudentID).")
        except Exception as e:
            print(f"Error altering table {table_name}: {str(e)}")

# Usage example
def main():
    # Initialize the database manager
    db_manager = DatabaseManager(DB_CONFIG)

    # Connect to the database
    db_manager.connect()


    db_manager.create_table('ChatData')
    # Check if the database is connected
    db_manager.check_connection()

    # Get table structure before alteration
    db_manager.get_table_structure()

    # Display contents of a specific table (example: 'ChatData')
    db_manager.display_table_contents('ChatData')

    # Alter the ChatData table (rename StudentEmail to StudentID)
    #db_manager.alter_table('ChatData')

    # Get table structure after alteration
    #db_manager.get_table_structure()

    # Close the connection
    db_manager.close()

if __name__ == "__main__":
    main()
