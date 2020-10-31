from configparser import ConfigParser
import psycopg2


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in {1} config file'.format(section, filename))
    return db


def connect():
    connection = None
    try:
        params = config()
        print('Connecting to PostgreSQL database...')
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()
        print('Postgres database version:')
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        print(db_version)
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            return connection


# def check_db_empty():


if __name__ == '__main__':
    connect()
