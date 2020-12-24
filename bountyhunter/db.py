from configparser import ConfigParser
import psycopg2
import pathlib
import logging


def config(filename=str(pathlib.Path(__file__).parent.absolute()) + "/database.ini", section='postgresql'):
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
        """,
        """
            CREATE TABLE IF NOT EXISTS user_ids (
                user_id TEXT NOT NULL PRIMARY KEY
            );
        """
    )
    for command in commands:
        exec_sql(command)


def get_user_table():
    commands = (
        f"""
                SELECT user_id FROM user_ids;
            """
    )
    user_table = []
    results = fetch_all_results(commands)
    if results is not None:
        for found_id in results:
            user_table.append(found_id[0])
    return user_table


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


def insert_user_id(user_id):
    commands = (
        f"""
            INSERT INTO user_ids (user_id)
            VALUES ('{user_id}');
        """
    )
    exec_sql(commands)
    return 1


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
    print('Adding a new program...')
    handle = bounty_object['handle']
    for asset in bounty_object['eligible']:
        insert_asset(handle, asset, 'eligible')
        print('Eligible Asset ' + asset + ' has been added!')
    for asset in bounty_object['ineligible']:
        insert_asset(handle, asset, 'ineligible')
        print('Ineligible Asset ' + asset + ' has been added!')
    for asset in bounty_object['out_scope']:
        insert_asset(handle, asset, 'out_scope')
        print('Out of Scope Asset ' + asset + ' has been added!')
    return 1


def update_assets_of_type(bounty_object, asset_type):
    print('*** ' + asset_type + ' domains changed!')
    changes = find_differences(bounty_object, asset_type)
    for change in changes['to_remove']:
        delete_asset(bounty_object['handle'], change, asset_type)
        print('Asset ' + change + ' has been deleted!')
        logging.info(f'{bounty_object["handle"]}`s {asset_type} domain {change} has been deleted')
    for change in changes['to_add']:
        insert_asset(bounty_object['handle'], change, asset_type)
        print('Asset ' + change + ' has been added!')
        logging.info(f'{bounty_object["handle"]}`s {asset_type} domain {change} has been added')
    return changes


def insert_asset(handle, asset_value, asset_type):
    commands = (
        f"""
            INSERT INTO domains (handle, asset_value, asset_type)
            VALUES ('{handle}', '{asset_value}', 
            '{asset_type}');
        """
    )
    exec_sql(commands)
    return 1


def get_assets(handle, asset_type):
    commands = (
        f"""
            SELECT asset_value FROM domains 
            WHERE handle='{handle}' AND asset_type='{asset_type}'
        """
    )
    results = fetch_all_results(commands)
    return results


def delete_asset(handle, asset_value, asset_type):
    commands = (
        f"""
            DELETE FROM domains
            WHERE handle='{handle}' AND asset_value='{asset_value}' 
            AND asset_type='{asset_type}'
        """
    )
    exec_sql(commands)
    return 1


def delete_program(handle):
    exec_sql(
        f"""
            DELETE FROM domains
            WHERE handle='{handle}';
        """
    )
    delete_hash(handle)
    exec_sql(
        f"""
            DELETE FROM bounty_programs
            WHERE handle='{handle}';
        """
    )
    return 1


def delete_hash(handle):
    commands = (
        f"""
            DELETE FROM hash_table 
            WHERE handle='{handle}'
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
    if old_assets is None:
        old_assets = ()
    if new_assets is None:
        new_assets = ()
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
