import sqlite3

class DBConnection:

    def __init__(self, db_path: str) -> None:
        """
        constructor for DBConnection object
        attributes:
            db_path (str): the database file path to be connected him
        """
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def create_table(self, types: dict[str, str]) -> None:
        """
        create table with the relevant fields of the item
        parameters:
            types (dict): the type of each one field in the table
        """
        fields = []
        for key in types.keys():
            type = types[key]
            if fields:
                fields.append(f'{key} {type} NOT NULL')
            else:
                fields.append(f'{key} {type} PRIMARY KEY')
        query = 'CREATE TABLE IF NOT EXISTS RESULTS (' + ','.join(fields) + ')'
        try:
            self.cur.execute(query)
            self.con.commit()
        except sqlite3.Error as e:
            print(e)

    def select_query(self) -> list[any]:
        """
        perform select query on results table
        returns:
            rows (list): list of records from table to display to user
        """
        try:
            self.cur.execute('SELECT * FROM RESULTS')
            self.con.commit()
            rows = self.cur.fetchall()
            return rows
        except sqlite3.Error as e:
            print(e)

    def insert_query(self, result: list[any]) -> None:
        """
        insert into results table all data that are cumulative from the dataset progress per row
        parameters:
            result (list): row from the table to be inserted
        """
        try:
            self.cur.execute('INSERT OR IGNORE INTO RESULTS VALUES (' + ','.join('?'*len(result)) + ')', result)
            self.con.commit()
        except sqlite3.Error as e:
            print(e)

    def __exit__(self) -> None:
        """ close the database """
        self.cur.close()
        self.con.close()
