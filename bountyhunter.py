import re
import requests
import json
import pymongo

hackerone = 'https://hackerone.com/programs/search?query=bounties%3Ayes&sort=name%3Aascending&limit=1000'
bounty_object = {
    'curr_handle': '',
    'in_scope': '',
    'out_scope': '',
    'offers_bounties': '',
    'resolved_reports': '',
    'is_open': ''
}
# there may be a problem with the length of this shit due to whitespaces. Refer to burpsuite repeater
h1content = '{"operationName":"TeamAssets","variables":{"handle":"'+bounty_object['curr_handle']+'"}, ' \
            '"query":"query TeamAssets($handle: ' \
            'String!) {\n  me {\n    id\n    membership(team_handle: $handle) {\n      id\n      permissions\n      ' \
            '__typename\n    }\n    __typename\n  }\n  team(handle: $handle) {\n    id\n    handle\n    ' \
            'structured_scope_versions(archived: false) {\n      max_updated_at\n      __typename\n    }\n    ' \
            'in_scope_assets: structured_scopes(first: 500, archived: false, eligible_for_submission: true) {\n      ' \
            'edges {\n        node {\n          id\n          asset_type\n          asset_identifier\n          ' \
            'rendered_instruction\n          max_severity\n          eligible_for_bounty\n          labels(first: ' \
            '100) {\n            edges {\n              node {\n                id\n                name\n            ' \
            '    __typename\n              }\n              __typename\n            }\n            __typename\n       ' \
            '   }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ' \
            'out_scope_assets: structured_scopes(first: 500, archived: false, eligible_for_submission: false) {\n     ' \
            ' edges {\n        node {\n          id\n          asset_type\n          asset_identifier\n          ' \
            'rendered_instruction\n          __typename\n        }\n        __typename\n      }\n      __typename\n   ' \
            ' }\n    __typename\n  }\n}\n"} '
h1headers = {
    'Host': 'hackerone.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'https://hackerone.com/'+bounty_object['curr_handle']+'?type=team',
    'content-type': 'application/json',
    'X-Auth-Token': '----',
    'Connection': 'close',
    'Content-Length': str(len(h1content))
}

session = requests.Session()
# programlist = session.get(hackerone, headers=h1headers)
programlist = session.get(hackerone)
bountiespage = json.loads(programlist.text)
print('fugg')
