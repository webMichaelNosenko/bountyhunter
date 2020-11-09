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


def fetch_all_results(sql):
    connection = None
    results = None
    try:
        params = config()
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            return results


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


def get_hash_table():
    commands = (
        f"""
            SELECT handle, hash_value FROM hash_table;
        """
    )
    hash_table = {}
    results = fetch_all_results(commands)
    if len(results) != 0:
        for hash_item in results:
            hash_table[hash_item[0]] = hash_item[1]
    return hash_table


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


def insert_asset(bounty_object, asset_value, asset_type):
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
    commands = (
        f"""
            SELECT asset_value FROM domains 
            WHERE handle='{bounty_object['handle']}' AND asset_type='{asset_type}'
        """
    )
    results = fetch_all_results(commands)
    return results


def delete_asset(bounty_object, asset_value, asset_type):
    commands = (
        f"""
            DELETE FROM domains
            WHERE handle='{bounty_object['handle']}' AND asset_value='{asset_value}' 
            AND asset_type='{asset_type}'
        """
    )
    exec_sql(commands)
    return 1


def delete_program(bounty_object):
    exec_sql(
        f"""
            DELETE FROM domains
            WHERE handle='{bounty_object['handle']}';
        """
    )
    delete_hash(bounty_object)
    exec_sql(
        f"""
            DELETE FROM bounty_programs
            WHERE handle='{bounty_object['handle']}';
        """
    )
    return 1


def delete_hash(bounty_object):
    commands = (
        f"""
            DELETE FROM hash_table 
            WHERE handle='{bounty_object['handle']}'
        """
    )
    exec_sql(commands)
    return 1


def find_differences(bounty_object, asset_type):
    changes = {
        'to_add': [],
        'to_remove': []
    }
    old_assets = get_assets(bounty_object, asset_type)
    new_assets = bounty_object[asset_type]
    for asset in new_assets:
        if asset not in old_assets:
            changes['to_add'].append(asset)
    for asset in old_assets:
        if asset not in new_assets:
            changes['to_remove'].append(asset)
    return changes


if __name__ == '__main__':
    create_tables()
    #   insert_new_program({'curr_handle': 'fuck', 'offers_bounties': True, 'resolved_reports': 69, 'avg_bounty': 666})
