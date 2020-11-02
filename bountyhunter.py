import re
import requests
import json
import pyppeteer
import asyncio
import hashtable
#   /home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pydev:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_display:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/third_party/thriftpy:/usr/lib/python38.zip:/usr/lib/python3.8:/usr/lib/python3.8/lib-dynload:/home/cyst/PycharmProjects/pythonProject/venv/lib/python3.8/site-packages:/home/cyst/jetTools/apps/PyCharm-P/ch-0/202.6397.98/plugins/python/helpers/pycharm_matplotlib_backend:/home/cyst/PycharmProjects/pythonProject:/home/cyst/bountyhunter/venv/lib/python3.8/site-packages:/home/cyst/bountyhunter
# Since hackerone is a Single-page application (damn hispters), we'll need to execute JS on pages to get the data
# necessary. In order to do that, we use pyppeteer - a library that allows us to run a headless version of Chromium
# and control it through code.


def print_scope(scopes):
    for x in range(0, len(scopes)):
        scope_to_print = scopes[x]
        scope_to_print = re.sub(r"\s+", ' ', scope_to_print)
        print('Domain ' + str(x + 1) + ': ' + scope_to_print + '\n')
    print('\n')


async def look_for_scope(handle):
    """
    Parses the page of a bug bounty program. Returns all of its domain-type assets in three groups: eligible or
    ineligible for award or out of scope, along with some other data.

    :param handle: name of a program, defines url of its page (located at https://hackerone.com/"HANDLE"?type=team)
    :return: curr_handle: the program name |
             eligible_domains:  reward-eligible domains; |
             ineligible_domains; |
             out_scope: out-of-scope domains that mustn't be tested; |
             offers_bounties: boolean, whether the program pays for bugs; |
             resolved_reports: number of resolved reports; |
             avg_bounty: average reward for a valid bug
    """
    # We should REALLY make the browser run in sandbox. FIX THIS SHITE
    browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({'width': 1912, 'height': 933})
    await page.goto('https://hackerone.com/' + handle + '?type=team', {'waitUntil': 'networkidle0'})
#    await page.goto('https://hackerone.com/affirm?type=team', {'waitUntil': 'networkidle0'})
    inner_text = await page.evaluate("() => {let my_text = ' ';"
                                     "let cards = document.querySelectorAll('.card__content');"
                                     "for (var i=0; i < cards.length; i++) {"
                                     "my_text += cards[i].innerText;"
                                     "}"
                                     "return my_text;"
                                     "}", force_expr=False)

    domains_pattern = re.compile('(Domain[a-zA-Z0-9:@_&()\'\";%!?+=^#|*\n\t \r/,.-]*?(?:[\n\t ]*Eligible|[\n\t '
                                 ']*Ineligible))')
    # Maybe also include strings that do not end with severity and eligibility? Those are usually out-of-scope domains,
    # see att program
    out_of_scope_pattern = re.compile('[Oo]ut of [Ss]cope[.:-]?[ \t\n]*[Dd]omain[ \t\n]*[a-zA-Z0-9:@_&('
                                      ')\'\";%!?+=^#|*,.-/]*')
    domain_addr_pattern = re.compile('([a-zA-Z0-9.:-]*[\n\t ]*)([a-zA-Z0-9:@_&()\'\";%!?+=^#|*/,.-]*)')
    resolved_reports_pattern = re.compile('(Reports resolved[ \n\t:-]*)([0-9]*)')
    avg_bounty_pattern = re.compile('(Average bounty[ \n\t:-]*)([$kK0-9-]*)')

    avg_bounty = avg_bounty_pattern.search(inner_text)
    avg_bounty = 'N/A' if avg_bounty is None else avg_bounty.groups()[1]
    resolved_reports = resolved_reports_pattern.search(inner_text)
    resolved_reports = 'N/A' if resolved_reports is None else resolved_reports.groups()[1]
    out_of_scope = out_of_scope_pattern.findall(inner_text)
    domains = domains_pattern.findall(inner_text)

    el_domains = []
    inel_domains = []
    for x in range(0, len(domains)):
        if re.search('Eligible', domains[x]) is not None:
            addr = domain_addr_pattern.match(domains[x])
            el_domains.append(addr.groups()[1])
        else:
            addr = domain_addr_pattern.match(domains[x])
            inel_domains.append(addr.groups()[1])

    print('****** PROGRAM NAME: ' + handle + ' ******\n')
    print('** ElIGIBLE SCOPES\n')
    print_scope(el_domains)
    print('** INElIGIBLE SCOPES\n')
    print_scope(inel_domains)
    print('** OUT OF SCOPE\n')
    print_scope(out_of_scope)
    await browser.close()
    return {
        'curr_handle': handle,
        'eligible_domains': el_domains,
        'ineligible_domains': inel_domains,
        'out_scope': out_of_scope,
        'offers_bounties': True if len(el_domains) > 0 else False,
        'resolved_reports': resolved_reports,
        'avg_bounty': avg_bounty
    }

hackerone = 'https://hackerone.com/programs/search?query=bounties%3Ayes&sort=name%3Aascending&limit=1000'
bounty_object = {
    'curr_handle': '',
    'eligible_domains': [],
    'ineligible_domains': [],
    'out_scope': [],
    'offers_bounties': '',
    'resolved_reports': '',
    'avg_bounty': ''
}
scraped_programs = []

session = requests.Session()
programlist = session.get(hackerone)
bountiespage = json.loads(programlist.text)
program_counter = 0
for placeholdObj in bountiespage['results']:
    bounty_object['curr_handle'] = placeholdObj['handle']
    scraped_programs.append(asyncio.get_event_loop().run_until_complete(look_for_scope(bounty_object['curr_handle'])))
    print(scraped_programs[program_counter])
    fuck = hashtable.make_hash(scraped_programs[program_counter])
    print(fuck)
    program_counter += 1

print(scraped_programs)






