import requests
import json
import asyncio
import logging
#import bountyhunter.hashtable as hashtable
import hashtable as hashtable
import db as db
import tgbot as tgbot
from fetcher import look_for_scope
import threading
import queue
import os
from random import randint
from time import sleep


class BountyThread (threading.Thread):
    def __init__(self, threadid, name, queue_items):
        threading.Thread.__init__(self)
        self.threadID = threadid
        self.name = name
        self.queue_items = queue_items

    def run(self):
        print("Starting " + self.name)
        process_program(self.queue_items)
        print("Exiting " + self.name)


#   /home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_display:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/third_party/thriftpy:/usr/lib/python38.zip:/usr/lib/python3.8:/usr/lib/python3.8/lib-dynload:/home/cyst/PycharmProjects/pythonProject/venv/lib/python3.8/site-packages:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_matplotlib_backend:/home/cyst/PycharmProjects/pythonProject:/home/cyst/bountyhunter/venv/lib/python3.8/site-packages:/home/cyst/bountyhunter
# Since hackerone is a Single-page application (damn hispters), we'll need to execute JS on pages to get the data
# necessary. In order to do that, we use pyppeteer - a library that allows us to run a headless version of Chromium
# and control it through code

hackerone = 'https://hackerone.com/programs/search?query=bounties%3Ayes&sort=name%3Aascending&limit=1000'

scraped_programs = []
program_counter = 0
exitFlag = 0


def process_program(queue_items):
    while not exitFlag:
        queue_lock.acquire()
        if not queue_items.empty():
            placehold_bounty = queue_items.get()
            queue_lock.release()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            sleep(randint(1, 6))
            try:
                bounty_object = loop.run_until_complete(look_for_scope(placehold_bounty['handle']))
            except TimeoutError:
                print('Could not load page ' + placehold_bounty['handle'])
                loop.stop()
                loop.close()
                continue
            loop.stop()
            loop.close()

            handle = bounty_object['handle']
            scraped_programs.append(bounty_object)
            print(bounty_object)
            new_hash = hashtable.make_hash(bounty_object)
            hash_lock.acquire()
            check_res = hashtable.check_hash(handle, new_hash)
            hash_lock.release()
            print(new_hash)
            if not check_res['new_program_added']:

                if check_res['eligible_changed']:
                    db_lock.acquire()
                    changes = db.update_assets_of_type(bounty_object, 'eligible')
                    db_lock.release()
                    tgbot.notify_of_change(handle, changes, "eligible")

                if check_res['ineligible_changed']:
                    db_lock.acquire()
                    changes = db.update_assets_of_type(bounty_object, 'ineligible')
                    db_lock.release()
                    tgbot.notify_of_change(handle, changes, "ineligible")

                if check_res['out_scope_changed']:
                    db_lock.acquire()
                    changes = db.update_assets_of_type(bounty_object, 'out_scope')
                    db_lock.release()
                    tgbot.notify_of_change(handle, changes, "out_scope")
            else:
                logging.info(f'A new program "{handle}" has been added!')
                db_lock.acquire()
                db.insert_new_program(bounty_object)
                db_lock.release()
                tgbot.notify_of_new_program(bounty_object)
            db_lock.acquire()
            db.delete_hash(handle)
            db.insert_hash(handle, new_hash)
            hashtable.push_hash(handle, new_hash)
            db_lock.release()
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
        exitFlag = 0
        threadsTerminated = 0
        session = requests.Session()
        programlist = session.get(hackerone)
        bountiespage = json.loads(programlist.text)
        hashtable.hash_table = db.get_hash_table()
        print('!!! LOOP NUMBER ' + str(loop_count) + ' !!!')

        bounty_queue = queue.Queue(int(len(bountiespage['results'])))
        queue_lock = threading.Lock()
        hash_lock = threading.Lock()
        db_lock = threading.Lock()

        queue_lock.acquire()
        for result in bountiespage['results']:
            bounty_queue.put(result)
        queue_lock.release()

        thread_list = ['Thread 0', 'Thread 1']
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
