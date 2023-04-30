import sqlite3
import csv
from sqlite3 import Error
import pipelines.funcs as funcs

class BaseTask:
    """Base Pipeline Task"""

    def run(self):
        raise RuntimeError('Do not run BaseTask!')

    def short_description(self):
        pass

    def __str__(self):
        task_type = self.__class__.__name__
        return f'{task_type}: {self.short_description()}'


class CopyToFile(BaseTask):
    """Copy table data to CSV file"""

    def __init__(self, table, output_file):
        self.table = table
        self.output_file = output_file

    def short_description(self):
        return f'{self.table} -> {self.output_file}'

    def run(self):
        file = open(self.output_file, 'w', newline='')
        writer = csv.writer(file)
        try:
            con = sqlite3.connect('pipesql.db')
            cursor = con.cursor()
            cursor.execute(f"PRAGMA table_info('{self.table}')")
            t = cursor.fetchall()
            headers = [i[1] for i in t]
            writer.writerow(headers)
            cursor.execute(f"SELECT * FROM {self.table}")
            t = cursor.fetchall()
            for i in t:
                 writer.writerow(i)
            con.commit()
        except Error as er:
            print(er.args)
        finally:
            con.close()
        print(f"Copy table `{self.table}` to file `{self.output_file}`")


class LoadFile(BaseTask):
    """Load file to table"""

    def __init__(self, table, input_file):
        self.table = table
        self.input_file = input_file

    def short_description(self):
        return f'{self.input_file} -> {self.table}'

    def run(self):
        csvfile = open(self.input_file)
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames[0].split(',')
        try:
            con = sqlite3.connect('pipesql.db')
            cursor = con.cursor()
            cursor.execute('CREATE TABLE ' + self.table + '(' + ','.join(headers) + ')')
            to_db = [i[','.join(headers)].split(',') for i in reader]
            cursor.executemany('INSERT INTO ' + self.table + ' (' + ','.join(headers) + ') VALUES (?' + ', ?' * (len(headers) - 1) + ');', to_db)
            cursor.execute('SELECT * FROM ' + self.table)
            con.commit()
        except Error as er:
            print(er.args)
        finally:
            con.close()
        print(f"Load file `{self.input_file}` to table `{self.table}`")


class RunSQL(BaseTask):
    """Run custom SQL query"""

    def __init__(self, sql_query, title=None):
        self.title = title
        self.sql_query = sql_query

    def short_description(self):
        return f'{self.title}'

    def run(self):
        try:
            con = sqlite3.connect('pipesql.db')
            cursor = con.cursor()
            for key, value in funcs.funcs.items():
                con.create_function(key.__name__, value, key)
            cursor.execute(self.sql_query)
            con.commit()
        except Error as er:
            print(er.args)
        finally:
            con.close()
        print(f"Run SQL ({self.title}):\n{self.sql_query}")



class CTAS(BaseTask):
    """SQL Create Table As Task"""

    def __init__(self, table, sql_query, title=None):
        self.table = table
        self.sql_query = sql_query
        self.title = title or table

    def short_description(self):
        return f'{self.title}'

    def run(self):
        try:
            con = sqlite3.connect('pipesql.db')
            cursor = con.cursor()
            for key, value in funcs.funcs.items():
                con.create_function(key.__name__, value, key)
            t = f"CREATE TABLE {self.table} AS {self.sql_query}"
            cursor.execute(f"CREATE TABLE {self.table} AS {self.sql_query}")
            con.commit()
        except Error as er:
            print(er.args)
        finally:
            con.close()
        print(f"Create table `{self.table}` as SELECT:\n{self.sql_query}")


# LoadFile(input_file='original\\original.csv', table='original').run()
# CTAS(table='norm',sql_query='''select *, url from original;''').run()
# CopyToFile(
#         table='norm',
#         output_file='norm.csv',
#     ).run()

#     # clean up:
# RunSQL('drop table original').run()
# RunSQL('drop table norm').run()

