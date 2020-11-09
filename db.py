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
        print('Connecting to PostgreSQL database....')
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


def exec_sql(sql):
    connection = None
    try:
        params = config()
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.close()
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()


def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS bounty_programs (
            handle varchar(45) PRIMARY KEY,
            offers_bounties BOOLEAN,
            resolved_reports INTEGER, 
            avg_bounty INTEGER
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS domains (
            asset_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            handle varchar(45) NOT NULL,
            asset_value varchar(200),
            asset_type varchar(20),
            CONSTRAINT fk_handle
                FOREIGN KEY(handle)
                    REFERENCES bounty_programs(handle)
                    ON DELETE CASCADE 
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS hash_table (
            handle varchar(45) PRIMARY KEY,
            hash_value TEXT NOT NULL
        );
        """
    )
    for command in commands:
        exec_sql(command)


def insert_hash(handle, hash_value):
    commands = (
        f"""
            INSERT INTO hash_table (handle, hash_value)
            VALUES ('{handle}', '{hash_value}');
        """
    )
    exec_sql(commands)
    return 1


def insert_new_program(bounty_object):
    commands = (
        f"""
        INSERT INTO bounty_programs (handle, offers_bounties, resolved_reports, avg_bounty)
        VALUES ('{bounty_object['handle']}', {bounty_object['offers_bounties']}, 
        {bounty_object['resolved_reports']}, {bounty_object['avg_bounty']});
        """
    )
    exec_sql(commands)
    return 1


def add_asset(bounty_object, asset_value, asset_type):
    commands = (
        f"""
            INSERT INTO domains (handle, asset_value, asset_type)
            VALUES ('{bounty_object['handle']}', '{asset_value}', 
            '{asset_type}');
            """
    )
    exec_sql(commands)
    return 1


def get_assets(bounty_object, asset_type):
    return 1


def remove_asset(bounty_object):
    return 1


def delete_program(bounty_object):
    return 1


def find_differences():
    return 1


if __name__ == '__main__':
    create_tables()
    #   insert_new_program({'curr_handle': 'fuck', 'offers_bounties': True, 'resolved_reports': 69, 'avg_bounty': 666})
