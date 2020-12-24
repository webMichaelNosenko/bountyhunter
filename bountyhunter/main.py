import requests
import json
import asyncio
import logging
import bountyhunter.hashtable as hashtable
import bountyhunter.db as db
import bountyhunter.tgbot as tgbot
from bountyhunter.fetcher import look_for_scope

#   /home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_display:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/third_party/thriftpy:/usr/lib/python38.zip:/usr/lib/python3.8:/usr/lib/python3.8/lib-dynload:/home/cyst/PycharmProjects/pythonProject/venv/lib/python3.8/site-packages:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_matplotlib_backend:/home/cyst/PycharmProjects/pythonProject:/home/cyst/bountyhunter/venv/lib/python3.8/site-packages:/home/cyst/bountyhunter
# Since hackerone is a Single-page application (damn hispters), we'll need to execute JS on pages to get the data
# necessary. In order to do that, we use pyppeteer - a library that allows us to run a headless version of Chromium
# and control it through code

hackerone = 'https://hackerone.com/programs/search?query=bounties%3Ayes&sort=name%3Aascending&limit=1000'


def main():
    logging.basicConfig(filename='events.log', level=logging.DEBUG)
    db.create_tables()
    session = requests.Session()
    programlist = session.get(hackerone)
    bountiespage = json.loads(programlist.text)
    scraped_programs = []
    program_counter = 0
    hashtable.hash_table = db.get_hash_table()
    for placeholdObj in bountiespage['results']:
        bounty_object = asyncio.run(look_for_scope(placeholdObj['handle']))
        handle = bounty_object['handle']
        scraped_programs.append(bounty_object)
        print(bounty_object)
        new_hash = hashtable.make_hash(bounty_object)
        check_res = hashtable.check_hash(handle, new_hash)
        print(new_hash)
        if not check_res['new_program_added']:

            if check_res['eligible_changed']:
                changes = db.update_assets_of_type(bounty_object, 'eligible')
                tgbot.notify_of_change(handle, changes, "eligible")

            if check_res['ineligible_changed']:
                changes = db.update_assets_of_type(bounty_object, 'ineligible')
                tgbot.notify_of_change(handle, changes, "ineligible")

            if check_res['out_scope_changed']:
                changes = db.update_assets_of_type(bounty_object, 'out_scope')
                tgbot.notify_of_change(handle, changes, "out_scope")
        else:
            logging.info(f'A new program "{handle}" has been added!')
            db.insert_new_program(bounty_object)
            tgbot.notify_of_new_program(bounty_object)

        db.delete_hash(handle)
        db.insert_hash(handle, new_hash)
        hashtable.push_hash(handle, new_hash)
        print('Added the hash...')
        program_counter += 1


if __name__ == '__main__':
    loop_count = 0
    while True:
        print('!!! LOOP NUMBER ' + str(loop_count) + ' !!!')
        main()
        loop_count = loop_count + 1
