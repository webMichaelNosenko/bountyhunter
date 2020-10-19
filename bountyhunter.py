import re
import requests
import json
#   import pymongo
import pyppeteer
import asyncio
#   /home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_display:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/third_party/thriftpy:/usr/lib/python38.zip:/usr/lib/python3.8:/usr/lib/python3.8/lib-dynload:/home/cyst/PycharmProjects/pythonProject/venv/lib/python3.8/site-packages:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_matplotlib_backend:/home/cyst/PycharmProjects/pythonProject:/home/cyst/bountyhunter/venv/lib/python3.8/site-packages:/home/cyst/bountyhunter


def print_scope(scopes):
    for x in range(0, len(scopes)):
        scope_to_print = scopes[x]
        scope_to_print = re.sub(r"\s+", ' ', scope_to_print)
        print('Domain ' + str(x + 1) + ': ' + scope_to_print + '\n')
    print('\n')


async def look_for_scope(handle):
    browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({'width': 1912, 'height': 933})
    await page.goto('https://hackerone.com/' + handle + '?type=team', {'waitUntil': 'networkidle0'})
#    await page.goto('https://hackerone.com/watson_group?type=team', {'waitUntil': 'networkidle0'})
    inner_text = await page.evaluate("() => {let my_text = ' ';"
                                     "let cards = document.querySelectorAll('.card__content');"
                                     "for (var i=0; i < cards.length; i++) {"
                                     "my_text += cards[i].innerText;"
                                     "}"
                                     "return my_text;"
                                     "}", force_expr=False)
    domains_pattern = re.compile('(Domain[a-zA-Z0-9:@_&()\'\";%!?+=^#|*\n\t \r/,.-]*?(?:[\n\t ]*Eligible|[\n\t '
                                 ']*Ineligible))')
    out_of_scope_pattern = re.compile('[Oo]ut of [Ss]cope[.:-]?[ \t\n]*[Dd]omain[ \t\n]*[a-zA-Z0-9:@_&('
                                      ')\'\";%!?+=^#|*,.-/]*')
    out_of_scope = out_of_scope_pattern.findall(inner_text)
    domains = domains_pattern.findall(inner_text)
    el_domains = []
    inel_domains = []
    for x in range(0, len(domains)):
        if re.search('Eligible', domains[x]) is not None:
            el_domains.append(domains[x])
        else:
            inel_domains.append(domains[x])
    print('****** PROGRAM NAME: ' + handle + ' ******\n')
    print('** ElIGIBLE SCOPES\n')
    print_scope(el_domains)
    print('** INElIGIBLE SCOPES\n')
    print_scope(inel_domains)
    print('** OUT OF SCOPE\n')
    print_scope(out_of_scope)
    await browser.close()

hackerone = 'https://hackerone.com/programs/search?query=bounties%3Ayes&sort=name%3Aascending&limit=1000'
bounty_object = {
    'curr_handle': '',
    'in_scope': '',
    'out_scope': '',
    'offers_bounties': '',
    'resolved_reports': '',
    'is_open': ''
}
session = requests.Session()
programlist = session.get(hackerone)
bountiespage = json.loads(programlist.text)
for placeholdObj in bountiespage['results']:
    bounty_object['curr_handle'] = placeholdObj['handle']
    asyncio.get_event_loop().run_until_complete(look_for_scope(bounty_object['curr_handle']))






