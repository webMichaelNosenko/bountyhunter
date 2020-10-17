import re
import requests
import json
import pymongo
import pyppeteer
import asyncio


async def look_for_scope(handle):
    browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({'width': 1912, 'height': 933})
    await page.goto('https://hackerone.com/basecamp?type=team', {'waitUntil': 'networkidle0'})
    inner_text = await page.evaluate("let my_text = '';"
                                     "cards = document.querySelectorAll('.card');"
                                     "for (var i=0; i < cards.length; i++) {"
                                     "children = cards[i].getElementsByTagName('*');"
                                     "for (var b=0; b < children.length; b++) {"
                                     "my_text = my_text.concat(children[b].innerText);"
                                     "}"
                                     "}"
                                     "my_text;", force_expr=True)
    pattern = re.compile(r'([Dd]omain)+.[ \t]*[*a-z0-9]*.*[a-zA-Z0-9*]+.[a-z]+')
    print(inner_text)
    print(pattern.findall(inner_text))
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
    print(bounty_object['curr_handle'])
    asyncio.get_event_loop().run_until_complete(look_for_scope(bounty_object['curr_handle']))






