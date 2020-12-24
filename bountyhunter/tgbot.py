from telegram.ext import Updater
from telegram.ext import CommandHandler
from bountyhunter.db import get_user_table as get_users
from bountyhunter.db import insert_user_id as insert_user
import requests


updater = Updater(token='yourtoken', use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="From now on you'll recieve notifications about new"
                                                                    " programs and also fresh, new assets for existing "
                                                                    "programs. Type '/stop' to stop, duh")
    user_list.append(update.effective_chat.id)
    insert_user(update.effective_chat.id)


def notify_of_new_program(bounty_object):
    responses = []
    msg = "**** New program : " + bounty_object['handle'].upper() + " ****\n"
    msg += "+++ With eligible assets: \n"
    for asset in bounty_object['eligible']:
        msg += '\t' + asset + '\n'
    msg += "??? With ineligible assets: \n"
    for asset in bounty_object['ineligible']:
        msg += '\t' + asset + '\n'
    msg += "--- With out-of-scope assets: \n"
    for asset in bounty_object['out_scope']:
        msg += '\t' + asset + '\n'
    for user in user_list:
        send_text = 'https://api.telegram.org/botyourtoken/sendMessage?chat_id=' + str(user) + '&parse_mode=HTML&text=' + msg
        response = requests.get(send_text)
        responses.append(response.json())
    return responses


def notify_of_change(handle, changes, asset_type):
    responses = []
    msg = "In program :" + handle + "\n"
    for change in changes['to_remove']:
        msg += str(' - Asset ' + change + 'of type' + asset_type + ' has been deleted!\n')
    for change in changes['to_add']:
        msg += str(' + Asset ' + change + 'of type' + asset_type + ' has been added!\n')
    for user in user_list:
        send_text = 'https://api.telegram.org/bot1477848508:AAHxRodMzP1sN3m1bFDHt0cnciPezR2Sm98/sendMessage?chat_id=' + str(user) + '&parse_mode=HTML&text=' + msg
        response = requests.get(send_text)
        responses.append(response.json())
    return responses


user_list = get_users()
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
