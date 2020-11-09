import requests
import json
import asyncio
import hashtable
import db
from fetcher import look_for_scope

#   /home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_display:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/third_party/thriftpy:/usr/lib/python38.zip:/usr/lib/python3.8:/usr/lib/python3.8/lib-dynload:/home/cyst/PycharmProjects/pythonProject/venv/lib/python3.8/site-packages:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_matplotlib_backend:/home/cyst/PycharmProjects/pythonProject:/home/cyst/bountyhunter/venv/lib/python3.8/site-packages:/home/cyst/bountyhunter
# Since hackerone is a Single-page application (damn hispters), we'll need to execute JS on pages to get the data
# necessary. In order to do that, we use pyppeteer - a library that allows us to run a headless version of Chromium
# and control it through code

hackerone = 'https://hackerone.com/programs/search?query=bounties%3Ayes&sort=name%3Aascending&limit=1000'


def main():
    db.create_tables()
    session = requests.Session()
    programlist = session.get(hackerone)
    bountiespage = json.loads(programlist.text)
    scraped_programs = []
    program_counter = 0
    hashtable.hash_table = db.get_hash_table()
    for placeholdObj in bountiespage['results']:
        bounty_object = asyncio.run(look_for_scope(placeholdObj['handle']))
        scraped_programs.append(bounty_object)
        print(bounty_object)
        new_hash = hashtable.make_hash(bounty_object)
        check_res = hashtable.check_hash(bounty_object['handle'], new_hash)
        print(new_hash)
        if not check_res['new_program_added']:
            print('Not a new program...')
            if check_res['eligible_changed']:
                print('*** Eligible domains changed!')
                el_changes = db.find_differences(bounty_object, 'eligible_domains')
                for change in el_changes['to_remove']:
                    db.delete_asset(bounty_object, change, 'eligible')
                    print('Asset ' + change + ' has been deleted!')
                for change in el_changes['to_add']:
                    db.insert_asset(bounty_object, change, 'eligible')
                    print('Asset ' + change + 'has been added!')

            if check_res['ineligible_changed']:
                print('*** Ineligible domains changed!')
                inel_changes = db.find_differences(bounty_object, 'ineligible_domains')
                for change in inel_changes['to_remove']:
                    db.delete_asset(bounty_object, change, 'ineligible')
                    print('Asset ' + change + 'has been deleted!')
                for change in inel_changes['to_add']:
                    db.insert_asset(bounty_object, change, 'ineligible')
                    print('Asset ' + change + 'has been added!')

            if check_res['out_scope_changed']:
                print('*** Out of scope domains changed!')
                out_changes = db.find_differences(bounty_object, 'out_scope')
                for change in out_changes['to_remove']:
                    db.delete_asset(bounty_object, change, 'out_scope')
                    print('Asset ' + change + 'has been deleted!')
                for change in out_changes['to_add']:
                    db.insert_asset(bounty_object, change, 'out_scope')
                    print('Asset ' + change + 'has been added!')
        else:
            print('Adding a new program...')
            db.insert_new_program(bounty_object)
            db.insert_hash(bounty_object['handle'], new_hash)
            for asset in bounty_object['eligible_domains']:
                db.insert_asset(bounty_object, asset, 'eligible')
                print('Eligible Asset ' + asset + 'has been added!')
            for asset in bounty_object['ineligible_domains']:
                db.insert_asset(bounty_object, asset, 'ineligible')
                print('Ineligible Asset ' + asset + 'has been added!')
            for asset in bounty_object['out_scope']:
                db.insert_asset(bounty_object, asset, 'out_scope')
                print('Out of Scope Asset ' + asset + 'has been added!')

        hashtable.push_hash(bounty_object['handle'], new_hash)
        print('Added the hash...')
        program_counter += 1


if __name__ == '__main__':
    loop_count = 0
    while True:
        print('!!! LOOP NUMBER ' + str(loop_count) + ' !!!')
        main()
        loop_count = loop_count + 1
