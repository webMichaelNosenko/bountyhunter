from telegram.ext import Updater
from telegram.ext import CommandHandler
#from bountyhunter.db import get_user_table as get_users
from db import get_user_table as get_users
from db import insert_user_id as insert_user
from db import delete_user_id as delete_user
from db import change_filtered
import requests
from configparser import ConfigParser
import pathlib


# noinspection DuplicatedCode
def config(filename=str(pathlib.Path(__file__).parent.absolute()) + "/config.ini", section='tgbottoken'):
    parser = ConfigParser()
    parser.read(filename)
    token = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            token[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in {1} config file'.format(section, filename))
    return token


updater = Updater(**(config()), use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="From now on you'll recieve notifications about new"
                                                                    " programs and also fresh assets for existing "
                                                                    "ones. Type '/stop' to stop, '/noempty' to not "
                                                                    "recieve notifications about programs with no "
                                                                    "found assets")
    if insert_user(update.effective_chat.id):
        user_list.append([update.effective_chat.id, 0])
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You are already signed up for notifications")


def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You will no longer recieve notifications.")
    for user in user_list:
        if str(user[0]) == str(update.effective_chat.id):
            user_list.remove(user)
            delete_user(update.effective_chat.id)


def noempty(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Repeat the command to activate/deactivate the "
                                                                    "filter.")
    for user in user_list:
        if str(user[0]) == str(update.effective_chat.id):
            user[1] = 0 if user[1] == 1 else 1
            change_filtered(user[0], user[1])


def notify_of_new_program(bounty_object):
    responses = []
    msg = "**** New program : " + bounty_object['handle'].upper() + " ****\n"
    msg += "+++ With eligible assets: \n"
    if len(bounty_object['eligible']):
        for asset in bounty_object['eligible']:
            msg += '\t' + asset + '\n'
    else:
        msg += 'not found \n'
    msg += "??? With ineligible assets: \n"
    if len(bounty_object['ineligible']):
        for asset in bounty_object['ineligible']:
            msg += '\t' + asset + '\n'
    else:
        msg += 'not found \n'
    msg += "--- With out-of-scope assets: \n"
    if len(bounty_object['out_scope']):
        for asset in bounty_object['out_scope']:
            msg += '\t' + asset + '\n'
    else:
        msg += 'not found \n'
    msg += '------------\n(go to https://hackerone.com/' + bounty_object['handle'] + '?type=team for more info)'
    for user in user_list:
        if (user[1] and ((len(bounty_object['eligible']) != 0) or (len(bounty_object['ineligible']) != 0))) or (not user[1]):
            send_text = 'https://api.telegram.org/bot1477848508:AAHxRodMzP1sN3m1bFDHt0cnciPezR2Sm98/sendMessage?chat_id=' + str(user[0]) + '&parse_mode=HTML&text=' + msg
            response = requests.get(send_text)
            responses.append(response.json())
        else:
            return 0
    return responses


def notify_of_change(handle, changes, asset_type):
    responses = []
    msg = "!!!! In program: " + handle.upper() + " !!!!\n"
    msg += "Assets of type " + asset_type.upper() + ":\n"
    for change in changes['to_remove']:
        msg += str(' --- ' + change + '\n')
    msg += "\nhave been DELETED;\n========"
    for change in changes['to_add']:
        msg += str(' >>> ' + change + '\n')
    msg += "\nhave been ADDED"
    msg += '\n------------\n(go to https://hackerone.com/' + handle + '?type=team for more info)'
    for user in user_list:
        send_text = 'https://api.telegram.org/bot1477848508:AAHxRodMzP1sN3m1bFDHt0cnciPezR2Sm98/sendMessage?chat_id=' + str(user[0]) + '&parse_mode=HTML&text=' + msg
        response = requests.get(send_text)
        responses.append(response.json())
    return responses


user_list = get_users()
start_handler = CommandHandler('start', start)
stop_handler = CommandHandler('stop', stop)
noempty_handler = CommandHandler('noempty', noempty)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(stop_handler)
dispatcher.add_handler(noempty_handler)

updater.start_polling()
