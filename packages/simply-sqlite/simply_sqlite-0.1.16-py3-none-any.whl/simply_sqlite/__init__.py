'''
Author: Oscar Gutierrez
Email: o.guty66@gmail.com
Date: 2021-04-22
Python Version: 3.6.9
Version: 0.1.13
'''

# -*- coding: utf-8 -*-

# __LIBRARIES__ #
import sqlite3
from sqlite3 import Error

# __MAIN CODE__ #


class SQL:
    def __init__(self, data_base):
        self.__pk_col = None
        if not '.db' in data_base:
            data_base = data_base + '.db'
        self.__create_connection(data_base)
        self.__cursorObj = self.__conn.cursor()

    def __create_connection(self, data_base):  # crea la conexión a la BDD o la propia BDD        
        self.__conn = None  # creamos el objeto connect
        try:  # caso de omitir la ruta se crea en el directorio actual
            self.__conn = sqlite3.connect(
                database=data_base
            )  # crea la BD en la ruta
        except Error as e:
            print('Connection failed')
            return(e)
        
    def get_pk_column(self, table):
        '''
        Gets the Primary Key column of the table

        Args:
            table (str): table name from which we want to gwt the PK
        '''
        self.__cursorObj.execute(
            'PRAGMA table_info(%s);' % (table)
        )
        tabla_info = self.__cursorObj.fetchall()
        for column in tabla_info:
            if column[5] == 1:
                self.__pk_col = column[1]
                return column[1]

    def get_tables(self): 
        '''
        Returns a list with the names of the tables in the current DB

        Returns:
            list: Table names in the current DB
        '''
        self.__table_names = list()
        self.__cursorObj.execute(
            'SELECT name FROM sqlite_master WHERE type="table";')
        for name in self.__cursorObj.fetchall():
            self.__table_names.append(str(name)[2:-3])
        return self.__table_names

    def create_table(self, name, p_key:tuple=None, kwargs:dict=None):
        '''
        Create a new table and sets the primary key

        Args:
            name (str): Name of the new table
            p_key (tuple): Pk columns of the table, must be (name, type), if not provided, creates no pk 
            kwargs (dict): If provided, creates the additional columns of the new table, the structure must be {col_name: col_type}
        '''
        if p_key is not None:
            self.__cursorObj.execute(
                'CREATE TABLE %s(%s %s PRIMARY KEY)' % (name, p_key[0], p_key[1])
            )
        else:
            col = list(kwargs.keys())[0]
            self.__cursorObj.execute(
                'CREATE TABLE %s (%s %s)' % (name, col, kwargs[col])
            )
            del kwargs[col]
        if kwargs is not None:
            for key in kwargs.keys():
                self.insert_column(name, key, kwargs[key])

    def insert_column(self, table, column, type):
        '''
        creates a new column in the specified table

        Args:
            table (str): Name of the table in which the column will be created
            column (str): Name of the new column
            type (str): Type of the new column
        '''
        self.__cursorObj.execute(
            'ALTER TABLE %s ADD COLUMN %s %s' % (table, column, type)
        )
        self.__commit()

    def insert_info(self, table, column, info):
        '''
        Inserts information in the specified column of the specified table

        Args:
            table (str): Name of the table 
            column (str): column in which the information will be inserted
            info (any): Information to be written in the column
        '''
        value = (str(info),)
        self.__cursorObj.execute(
            'INSERT INTO %s(%s) VALUES(?)' % (table, column), value
        )
        self.__commit()

    def update_item(self, table, column, info, key_col=None):
        '''
        Updates the specified item

        Args:
            table (str): Name of the table in which the item is
            column (str): Name of the column we want to update
            key_col (str): name of the PK column, if not provided, will get automatically
            info (tuple): Information provided to update (value, key)
                value(any): Value to be written in the specified position
                key (str): key of the row to be updated
        '''
        if key_col is None:
            if self.__pk_col is None:
                self.get_pk_column(table)
            key_col = self.__pk_col
        self.__cursorObj.execute(
            'UPDATE %s SET %s = ? WHERE %s = ?' % (table, column, key_col), info
        )  # UPDATE Replicas SET Modelo = val1 WHERE SN = val2
        self.__commit()
    
    def new_row(self, table, p_key, columns:dict):
        '''
        Creates a new row in the specified table

        Args:
            table (str): Table in which we want to create the new row
            p_key (any): Primary key of the row.
            columns (dict): Rest of the columns to be created, structure must be {col_name: information}
        '''
        if self.__pk_col is None:
            self.get_pk_column(table)
        self.insert_info(table, self.__pk_col, p_key)
        for key in columns.keys():
            #print(key, columns[key])
            try:
                self.update_item(table, key, (columns[key], p_key), self.__pk_col)
            except:
                pass

    def get_all_rows(self, table):
        '''
        Returns all the row of the selected table

        Args:
            table (str): Name of the table from which we want to get the information

        Returns:
            list: All the rows of the specified Table.
        '''
        self.__cursorObj.execute(
            'SELECT * FROM %s' % (table)
        )
        return self.__cursorObj.fetchall()

    def get_matches(self, table, info, column=None):
        '''
        Returns the complete row that contains the given information

        Args:
            table (str): Table where the information will be searched
            column (str): Optional. If provided, the information given will be searched in that column.
            info (any): Information to be searched

        Returns:
            list: The row that matches de information
        '''
        if column is not None:
            ind = self.get_column_names(table).index(column)
            row = [elem for elem in self.get_all_rows(table) if info == elem[ind]]
        else:
            row = [elem for elem in self.get_all_rows(table) for item in elem if info == item]
        return row

    def get_column_names(self, table):
        '''
        Returns the columns in the given table

        Args:
            table (str): Name of the table from we want ti get the columns

        Returns:
            list: List of columns from the given table
        '''
        point = self.__cursorObj.execute('SELECT * FROM %s' % (table))
        names = [description[0] for description in point.description]
        return names

    def delete_row(self, table, column, info):
        '''
        Deletes the row with the given information

        Args:
            table (str): Table from which to delete the row
            column (str): Column where the coincidence will be searched
            info (any): Information to be searched for deletion
        '''
        value = (info,)
        self.__cursorObj.execute(
            'DELETE FROM %s WHERE %s = ?' % (table, column), value
        )
        self.__commit()
    
    def update_all(self, table, column, old, new):
        pass

    def __commit(self):
        self.__conn.commit()


'''

    def list(self):

    def delete(self):
'''


def run():
    db = SQL(data_base='paquete/simply_sqlite/Mia')
    table = 'Replicas'
    #db.new_row(table, '0023568', {'Modelo':'Glok23', 'Fabricante':'Glok'})
    print(
        db.get_matches(table, info='Glok'),
        sep = '\n'
    )


if __name__ == '__main__':
    run()

# __NOTES__ #
'''
    __init__(name):
        {name}  hace referencia a la variable que almacena el nombre de la base
                de datos.

    create_connexion():
        Crea la conexion con la base de datos.
'''
# __BIBLIOGRAPHY__ #
