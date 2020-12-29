import requests
import json
import asyncio
import logging
import bountyhunter.hashtable as hashtable
import bountyhunter.db as db
import bountyhunter.tgbot as tgbot
from bountyhunter.fetcher import look_for_scope
import threading
import queue


class BountyThread (threading.Thread):
    def __init__(self, threadid, name, queue_items):
        threading.Thread.__init__(self)
        self.threadID = threadid
        self.name = name
        self.queue_items = queue_items

    def run(self):
        print("Starting " + self.name)
        process_program(self, self.queue_items)
        print("Exiting " + self.name)


#   /home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_display:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/third_party/thriftpy:/usr/lib/python38.zip:/usr/lib/python3.8:/usr/lib/python3.8/lib-dynload:/home/cyst/PycharmProjects/pythonProject/venv/lib/python3.8/site-packages:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_matplotlib_backend:/home/cyst/PycharmProjects/pythonProject:/home/cyst/bountyhunter/venv/lib/python3.8/site-packages:/home/cyst/bountyhunter
# Since hackerone is a Single-page application (damn hispters), we'll need to execute JS on pages to get the data
# necessary. In order to do that, we use pyppeteer - a library that allows us to run a headless version of Chromium
# and control it through code

hackerone = 'https://hackerone.com/programs/search?query=bounties%3Ayes&sort=name%3Aascending&limit=1000'

scraped_programs = []
program_counter = 0
exitFlag = 0


def process_program(calling_thread, queue_items):
    while not exitFlag:
        queue_lock.acquire()
        if not queue_items.empty():
            placehold_bounty = queue_items.get()
            queue_lock.release()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # print('////// asyncio.run_coroutine_threadsafe, Thread '
            # + str(calling_thread.threadID) + ', handle ' + placehold_bounty['handle'] + '\n')
            # bounty_object = asyncio.run_coroutine_threadsafe(look_for_scope(placehold_bounty['handle']),
            #                                                 loop)
            # print('////// loop.run_until_complete, Thread '
            # + str(calling_thread.threadID) + ', handle ' + placehold_bounty['handle'] + '\n')
            bounty_object = loop.run_until_complete(look_for_scope(placehold_bounty['handle']))
            # bounty_object = bounty_object.result()
            loop.stop()
            loop.close()

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
            global program_counter
            program_counter += 1
        else:
            queue_lock.release()


if __name__ == '__main__':
    loop_count = 0
    logging.basicConfig(filename='events.log', level=logging.DEBUG)
    db.create_tables()
    while True:
        threadsTerminated = 0
        session = requests.Session()
        programlist = session.get(hackerone)
        bountiespage = json.loads(programlist.text)
        hashtable.hash_table = db.get_hash_table()
        print('!!! LOOP NUMBER ' + str(loop_count) + ' !!!')

        bounty_queue = queue.Queue(int(len(bountiespage['results'])))
        queue_lock = threading.Lock()

        queue_lock.acquire()
        for result in bountiespage['results']:
            bounty_queue.put(result)
        queue_lock.release()

        thread_list = ['Thread 0', 'Thread 1', 'Thread 2']
        threads = []
        loop_counter = 0
        for thread_it in thread_list:
            thread = BountyThread(loop_counter, thread_it, bounty_queue)
            thread.start()
            threads.append(thread)
            loop_counter += 1

        while not bounty_queue.empty():
            pass
        exitFlag = 1

        for thread_it in threads:
            thread_it.join()

        loop_count = loop_count + 1
