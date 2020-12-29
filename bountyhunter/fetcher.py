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
    #   ADD HANDLING FOR 404 ERRORS
    pyppeteer_logger = logging.getLogger('pyppeteer')
    pyppeteer_logger.setLevel(logging.WARNING)
    browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'], handleSIGINT=False,
                                     handleSIGTERM=False,
                                     handleSIGHUP=False)
    page = await browser.newPage()
    await page.setViewport({'width': 1912, 'height': 933})
    try:
        await page.goto('https://hackerone.com/' + handle + '?type=team', {'waitUntil': 'networkidle0'})
    except:
        print('Could not access the page')
        return ' '
    # await page.goto('https://hackerone.com/watson_group?type=team', {'waitUntil': 'networkidle0'})
    if handle != 'oooooooo':
        inner_text = await page.evaluate("() => {let my_text = ' ';"
                                         "let cards = document.querySelectorAll('.card__content');"
                                         "for (var i=0; i < cards.length; i++) {"
                                         "my_text += cards[i].innerText;"
                                         "}"
                                         "return my_text;"
                                         "}", force_expr=False)
    else:
        inner_text = ''' A.S. Watson Group
    
    A.S. Watson Group is the world's largest health and beauty retail group.
    
    https://www.aswatson.com
    Reports resolved
    26
    Assets in scope
    14
    Average bounty
    $250
    Submit report
    Bug Bounty Program
    Launched on Jul 2020
    Managed by HackerOneCritical
        
    High
        
    Medium
        
    Low
    
    $2,500	$750	$250	$100Rewards
    
    Please see the bounty table above. Once we add more assets, we will likely shift to multiple bounty tables. Our bounty table provides general guidelines, and all final decisions are at the discretion of A.S. Watson Group.
    
    Last updated on July 10, 2020. View changesLatest updates – A.S. Watson Microblog
    
    In this microblog we will keep you updated on the latest changes / additions to our public bounty program. For a detailed scope, please see the bottom of our policy page.
    
    • 2nd of December – We are now also accepting reports on our Superdrug and ThePerfumeShop mobile apps(Android and IOS)! Please check the policy page for out of scope items.
     • 8th of October – Fortress (Our Asian brand that focuses on electronics & household appliances) has been added to our public program. We are also interested in receiving reports regarding web-applications that run on subdomains.
     • 7th of September – We are now accepting reports on subdomain websites of ParknShop.
     • 24th of September – We included our UK-based perfume ecommerce website (including subdomains) to our program.
     • 10th of September – Our first Asian website was added to our program: ParknShop. This is our 24/7 online supermarket.
     • 29th of July – The A.S. Watson Public bug-bounty program launched with our UK-based Superdrug brand. This brand focusses on health & beauty products. Next to this main website, some specific subdomains were listed as in/out-of-scope.
    
    The A.S. Watson Bug Bounty Program
    
    The A.S. Watson Group is the world's largest health and beauty retail group, with over 15,700 stores in 25 markets worldwide serving over 28 million customers per week, and over 3 billion customers and members.
    
    A.S. Watson Group looks forward to working with the security community to discover vulnerabilities in order to keep our businesses and customers safe. As we operate in many different countries, we will be rolling out our bug bounty program in phases. Our main focus within this rollout, are our retail websites (and in the near future, mobile apps on both Android and IOS).
    
    Over the course of the next months, we will be adding more websites to our Hacker0ne scope. In our Microblog at the top of this page, you can see when we have added our latest assets. A more detailed scope can be found at the bottom of this page.
    
    Please note that some of our websites run on a similar codebase (Hybris/SAP CMS). This means that issues which are found on one asset, might also apply on another asset (If this is the case, it will be displayed in the asset description). These findings will be regarded and treated as a single issue.
    
    Our websites are always under development and have new releases on a regular basis. These new releases sometimes do introduce functionalities (and potentially new vulnerabilities). We encourage you to keep testing our assets to uncover these.
    
    Response Targets
    
    A.S. Watson Group will make a best effort to meet the following response targets for hackers participating in our program:
    
    Type of Response	SLA in business days
    First Response	2 days
    Time to Triage	2 days
    Time to Bounty	14 days
    Time to Resolution	depends on severity and complexity
    
    We’ll try to keep you informed about our progress throughout the process.
    
    Disclosure Policy
    
    • Please do not discuss this program or any vulnerabilities (even resolved ones) outside of the program without express consent from us. Disclosure of reports within Hacker0ne can be discussed.
     • Follow HackerOne's disclosure guidelines.
    
    Program Rules
    
    • Please provide detailed reports with reproducible steps. If the report is not detailed enough to reproduce the issue, the issue will not be eligible for a reward.
     • Submit one vulnerability per report, unless you need to chain vulnerabilities to provide impact.
     • When duplicates occur, we only award the first report that was received (provided that it can be fully reproduced).
     • Multiple vulnerabilities caused by one underlying issue will be awarded one bounty.
     • Social engineering (e.g. phishing, vishing, smishing) is prohibited.
     • Make a good faith effort to avoid privacy violations, destruction of data, and interruption or degradation of our service. Only interact with accounts you own or with explicit permission of the account holder.
     • Avoid sending more requests than required to proof a vulnerability (e.g. no need for multiple one-time-passwords).
    
    Known Vulnerabilities
    Rate limit on getting OTP feature(One Time Password)
    Weak Password Complexity
    Brute Force on Input Form
    Out of scope vulnerabilities
    
    When reporting vulnerabilities, please consider (1) attack scenario / exploitability, and (2) security impact of the bug.
     The following issues are considered out of scope:
     • Clickjacking on pages with no sensitive actions.
     • Unauthenticated/logout/login CSRF.
     • CSRF issues that do not lead to account theft (e.g. adding products to a cart/wishlist is out of scope).
     • Attacks requiring MITM or physical access to a user's device.
     • Previously known vulnerable libraries without a working Proof of Concept.
     • Comma Separated Values (CSV) injection without demonstrating a vulnerability.
     • Missing best practices in SSL/TLS configuration.
     • Any activity that could lead to the disruption of our service (DoS).
     • Content spoofing and text injection issues without showing an attack vector/without being able to modify HTML/CSS
     • User enumeration (Through Account creation, account update, authentication, newsletter subscriptions & forgotten password)
     • Brute force on Login, E-giftCards, Promo codes, Vouchers, user account registration
     • Forgot password token requests being leaked to third parties
    
    Out of scope vulnerabilities (mobile specific):
    
    • Exported components without permissions
     • Sensitive information in memory dump as clear text
     • Insecure data storage (Exception: Bounty cap for low if contains password data)
     • No session timeout
     • Lack of Root Protection
     • SSL certificate pinning related things
     • Ability to copy information to the pasteboard
     • Insecure WebView Implementation (javascript) (Exception: Unless an exploit is found)
     • Excessive Application Permission (Exception: Unless exploitable)
     • Sensitive Information Included in Snapshots
     • Lack of Code Obfuscation
    
    Safe Harbor
    
    Any activities conducted in a manner consistent with this policy will be considered authorized conduct and we will not initiate legal action against you. If legal action is initiated by a third party against you in connection with activities conducted under this policy, we will take steps to make it known that your actions were conducted in compliance with this policy.
    
    Thank you for helping keep A.S. Watson Group and our customers safe!Last updated on December 2, 2020.View changesIn Scope
    Domain	
    https://www.superdrug.com
    
    Superdrug is one of our leading e-commerce websites in health and beauty. If you are testing functionality that requires you to be authenticated, please ensure you register with your @wearehackerone.com email address.
    
    English
    SAP Hybris
        
    Critical
        
    Eligible
    
    Domain	
    https://www.parknshop.com/
        
    Critical
        
    Eligible
    
    Domain	
    https://www.theperfumeshop.com/
    
    The Perfume Shop is one of our leading e-commerce perfumery websites. If you are testing functionalities that requires you to be authenticated, please ensure you register with your @wearehackerone.com email address.
    
    English
    SAP Hybris
        
    Critical
        
    Eligible
    
    Domain	
    https://www.fortress.com.hk
        
    Critical
        
    Eligible
    
    Domain	
    https://www.superdrug.com/blog
    
    This is our Blog section of the website that runs on Wordpress.
    
        
    High
        
    Eligible
    
    Domain	
    https://www.theperfumeshop.com/blog
    
    This is our Blog section of the website that runs on Wordpress.
    
        
    High
        
    Eligible
    
    Android: Play Store	
    Superdrug.App.Android
    
    This is our Superdrug Mobile (Android) app. Please make sure to consult our policy page to see which items are out of scope for mobile apps.
    https://play.google.com/store/apps/details?id=superdrug.com.beautycard&hl=nl&gl=US
    
        
    Critical
        
    Eligible
    
    Android: Play Store	
    ThePerfumeShop.App.Android
    
    This is our ThePerfumeShop Mobile (Android) app. Please make sure to consult our policy page to see which items are out of scope for mobile apps.
    https://play.google.com/store/apps/details?id=com.theperfumeshop.customer&hl=nl&gl=US
    
        
    Critical
        
    Eligible
    
    iOS: App Store	
    Superdrug.App.IOS
    
    This is our Superdrug Mobile (IOS) app. Please make sure to consult our policy page to see which items are out of scope for mobile apps.
    https://apps.apple.com/gb/app/superdrug/id1267896687
    
        
    Critical
        
    Eligible
    
    iOS: App Store	
    ThePerfumeShop.App.IOS
    
    This is our ThePerfumeShop Mobile (IOS) app. Please make sure to consult our policy page to see which items are out of scope for mobile apps.
    https://apps.apple.com/gb/app/the-perfume-shop/id1202206665
    
        
    Critical
        
    Eligible
    
    Domain	
    *.superdrug.com
    *.nosuperdrug.com
    
    Subdomains for our websites are not the main scope for this program. We do however welcome reports that display security vulnerabilities.
    
        
    Critical
        
    Ineligible
    
    Domain
    
    Subdomains for our websites are not the main scope for this program. We do however welcome reports that display security vulnerabilities.
    
        
    Critical
        
    Ineligible
    
    Domain	
    *.parknshp.com
    
    Subdomains for our websites are not the main scope for this program. We do however welcome reports that display security vulnerabilities.
    
        
    Critical
        
    Ineligible
    
    Domain	
    *.fortress.com.hk
    
    Subdomains for our websites are not the main scope for this program. We do however welcome reports that display security vulnerabilities.
    
        
    Critical
        
    Ineligible
    Out of Scope
    Domain	https://healthclinics.superdrug.com/
    
    Out of scope.
    
    
    Domain	https://appt.healthclinics.superdrug.com/
    
    Out of scope.
    
    Download Burp Suite Project Configuration file (16 URLs)View changesLast updated on December 2, 2020.6 hrs
    Average time to first response
    about 1 day
    Average time to triage
    5 days
    Average time to bounty
    about 1 month
    Average time to resolution
    98% of reports
    Meet response standards
    Based on last 90 days$30,900
    Total bounties paid
    $250
    Average bounty
    $2,500
    Top bounty
    $7,700
    Bounties paid in the last 90 days
    165
    Reports received in the last 90 days
    a month ago
    Last report resolved
    26
    Reports resolved
    85
    Hackers thankedsaltedfish
    Reputation:364
    bugbound
    Reputation:76
    amakki
    Reputation:64
    hodkasia_sachin
    Reputation:57
    sec_a
    Reputation:57
    All Hackers'''
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
