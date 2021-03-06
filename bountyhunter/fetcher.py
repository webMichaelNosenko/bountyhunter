import pyppeteer
import re
import logging


def print_scope(scopes):
    for x in range(0, len(scopes)):
        scope_to_print = scopes[x]
        scope_to_print = re.sub(r"\s+", ' ', scope_to_print)
        print('Domain ' + str(x + 1) + ': ' + scope_to_print + '\n')
    print('\n')


def check_validity(value):
    if value.isdecimal():
        return int(value)
    else:
        int_pattern = re.compile('[0-9]*')
        new_value = int_pattern.search(value)
        if new_value.lastindex is not None:
            new_value = new_value.groups()[0]
            return int(new_value)
        return 0


async def fetch_page(handle):
    pyppeteer_logger = logging.getLogger('pyppeteer')
    pyppeteer_logger.setLevel(logging.WARNING)
    browser = await pyppeteer.launch(headless=True, args=['--no-sandbox',
                                                          '--disable-setuid-sandbox',
                                                          '--disable-dev-shm-usage',
                                                          '--disable-accelerated-2d-canvas',
                                                          '--no-first-run',
                                                          '--no-zygote',
                                                          '--single-process',
                                                          '--disable-gpu'],
                                     handleSIGINT=False,
                                     handleSIGTERM=False,
                                     handleSIGHUP=False)
    page = await browser.newPage()
    await page.setViewport({'width': 1912, 'height': 933})
    try:
        await page.goto('https://hackerone.com/' + handle + '?type=team', {'waitUntil': 'networkidle0'})
    except:
        raise TimeoutError
    # await page.goto('https://hackerone.com/watson_group?type=team', {'waitUntil': 'networkidle0'})
    inner_text = await page.evaluate("() => {let my_text = ' ';"
                                     "let cards = document.querySelectorAll('.card__content');"
                                     "for (var i=0; i < cards.length; i++) {"
                                     "my_text += cards[i].innerText;"
                                     "}"
                                     "return my_text;"
                                     "}", force_expr=False)
    await browser.close()
    return inner_text


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
    inner_text = await fetch_page(handle)

    domains_pattern = re.compile('(Domain[a-zA-Z0-9:@_&()\'\";%!?+=^#|*\n\t \r/,.-]*?(?:[\n\t ]*Eligible|[\n\t '
                                 ']*Ineligible))')
    # Maybe also include strings that do not end with severity and eligibility? Those are usually out-of-scope domains,
    # see att program
    out_of_scope_pattern = re.compile('[Oo]ut of [Ss]cope[.:-]?[ \t\n]*[Dd]omain[ \t\n]*[a-zA-Z0-9:@_&('
                                      ')\'\";%!?+=^#|*,.-/]*')
    domain_addr_pattern = re.compile('([a-zA-Z0-9.:-]*[\n\t ]*)([a-zA-Z0-9:@_&()\'\";%!?+=^#|*/,.-]*)')
    resolved_reports_pattern = re.compile('(Reports resolved[ \n\t:-]*)([0-9]*)')
    avg_bounty_pattern = re.compile('(Average bounty[ \n\t:-]*).([kK0-9]*)')

    avg_bounty = avg_bounty_pattern.search(inner_text)
    avg_bounty = 0 if (avg_bounty is None or avg_bounty == '') else avg_bounty.groups()[1]
    resolved_reports = resolved_reports_pattern.search(inner_text)
    resolved_reports = 0 if resolved_reports is None else resolved_reports.groups()[1]

    filtered_out_scope = []
    out_of_scope = out_of_scope_pattern.findall(inner_text)
    out_of_scope_pattern = re.compile('([^ \t\n]+?[.a-zA-Z0-9:/*-]*[.]+[.a-zA-Z0-9:/*-]+)')
    for asset in out_of_scope:
        new_asset = out_of_scope_pattern.search(asset) if out_of_scope_pattern.search(asset) is not None else ''
        if new_asset != '':
            filtered_out_scope.append(new_asset.groups()[0])
    domains = domains_pattern.findall(inner_text)
    # ([^ \t\n]+?[.a-zA-Z0-9:/*-]*[.]+[.a-zA-Z0-9:/*-]*)
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

    return {
        'handle': handle,
        'eligible': el_domains,
        'ineligible': inel_domains,
        'out_scope': filtered_out_scope,
        'offers_bounties': True if len(el_domains) > 0 else False,
        'resolved_reports': 0 if resolved_reports == 0 else check_validity(resolved_reports),
        'avg_bounty': 0 if avg_bounty == 0 else check_validity(avg_bounty)
    }
