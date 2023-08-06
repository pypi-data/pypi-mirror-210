import sqlite3
import time
import os

from sqlite3 import Error
from .chapters import chapters, modules


class Equation:
    def __init__(self, chapter, parent_path):
        '''
        chapter -> kinematics, projectile ...
        parent_path -> '/Users/vaibhavblayer/10xphysics'
        '''

        self.chapter = chapter
        self.parent_path = parent_path


    def path_equation(self):
        '''
        returns the path for respective equation chapterwise
        '''

        if self.chapter in chapters[0]:
            return f'{self.parent_path}/{modules[0]}/{self.chapter}/equations'
        elif self.chapter in chapters[1]:
            return f'{self.parent_path}/{modules[1]}/{self.chapter}/equations'
        elif self.chapter in chapters[2]:
            return f'{self.parent_path}/{modules[2]}/{self.chapter}/equations'
        elif self.chapter in chapters[3]:
            return f'{self.parent_path}/{modules[3]}/{self.chapter}/equations'
        elif self.chapter in chapters[4]:
            return f'{self.parent_path}/{modules[4]}/{self.chapter}/equations'





    def create_connection(self):
        '''
        creates connection with sqlite database at given path.
        '''

        db_file = f'{self.path_equation()}/equation.db'
        try:
            conn = sqlite3.connect(db_file)
        except:
            os.makedirs(self.path_equation())

        return conn


    def create_database(self):
        '''
        creates the database according to init params in the respective directory
        '''
        database = self.create_connection()
        try:
            database.execute(
                """ CREATE TABLE IF NOT EXISTS equation(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter TEXT NOT NULL,
                    date TEXT
                ); """
                )
        except Error as e:
            print(e)

        database.close()


    def get_data(self, n):
        try:
            database = self.create_connection()
            cursor = database.cursor()
            execute_statement = f'SELECT * FROM equation ORDER BY id DESC LIMIT {n};'
            output = cursor.execute(execute_statement)
            return output.fetchmany(n)
            database.close()
        except:
            self.create_database()


    def insert_data(self):
        try:
            database = self.create_connection()
            cursor = database.cursor()
            time_date = f'{int(time.strftime("%H%M%S%d%m%Y")):14}'
            execute_statement = f'INSERT INTO equation(chapter, date) VALUES("{self.chapter}", "{time_date}");'
            cursor.execute(execute_statement)
            database.commit()
            database.close()
        except Error as e:
            print(e)




