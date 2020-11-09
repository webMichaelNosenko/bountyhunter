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
bounty_object = {
    'handle': '',
    'eligible_domains': [],
    'ineligible_domains': [],
    'out_scope': [],
    'offers_bounties': '',
    'resolved_reports': '',
    'avg_bounty': ''
}
scraped_programs = []
new_changes = []  # this will hold all the assets that have changed for the specific program

db.create_tables()

session = requests.Session()
programlist = session.get(hackerone)
bountiespage = json.loads(programlist.text)

program_counter = 0
for placeholdObj in bountiespage['results']:
    bounty_object = asyncio.run(look_for_scope(placeholdObj['handle']))
    scraped_programs.append(bounty_object)
    print(bounty_object)
    new_hash = hashtable.make_hash(bounty_object)
    check_res = hashtable.check_hash(bounty_object['handle'], new_hash)
    print(new_hash)
    if not check_res['new_program_added']:
        if check_res['eligible_changed']:
            print(1)
        if check_res['ineligible_changed']:
            print(2)
        if check_res['out_scope_changed']:
            print(3)
    else:
        db.insert_new_program(bounty_object)
        db.insert_hash(bounty_object['handle'], new_hash)
        for asset in bounty_object['eligible_domains']:
            db.add_asset(bounty_object, asset, 'eligible')
        for asset in bounty_object['ineligible_domains']:
            db.add_asset(bounty_object, asset, 'ineligible')
        for asset in bounty_object['out_scope']:
            db.add_asset(bounty_object, asset, 'out_scope')
        print(4)
    hashtable.push_hash(bounty_object['handle'], new_hash)
    program_counter += 1

print(scraped_programs)
