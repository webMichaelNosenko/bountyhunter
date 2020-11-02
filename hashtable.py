import hashlib


def hash_assets(bounty_object, asset_type):
    """
    Turns all of the bug bounty program's assets of the same type into a hash string (md5) OR returns
    '[no_eligible_domains]', '[no_ineligible_domains]' or '[no_out_scope]'

    :param bounty_object: dict; the bounty data being used
    :param asset_type: string; either 'eligible_domains', 'ineligible_domains' or 'out_scope'
    """
    assets_hash = ''
    if len(bounty_object[asset_type]) != 0:
        for item in bounty_object[asset_type]:
            assets_hash = assets_hash + hashlib.md5(item.encode('utf-8')).hexdigest()
    else:
        assets_hash = assets_hash + ('[no_' + asset_type + ']')
    return assets_hash


def make_hash(bounty_object):
    """
    Generates a hash from all assets of a program. This is used to save some database queries. Hash table of such hashes
    is not stored in db. If the script detects that the program's hash is different from the one generated previously,
    only then will it access the db to further investigate the changes

    :param bounty_object: dict, keys are: {
            curr_handle: ' ',
            eligible_domains: [ ],
            ineligible_domains: [ ],
            out_scope: [ ],
            offers_bounties: ' ',
            resolved_reports: ' ',
            avg_bounty: ' '
        }
    :return: bounty_hash: string; the hash for this bug bounty program
    """
    bounty_hash = ''
    bounty_hash = bounty_hash + hash_assets(bounty_object, 'eligible_domains')
    bounty_hash = bounty_hash + hash_assets(bounty_object, 'ineligible_domains')
    bounty_hash = bounty_hash + hash_assets(bounty_object, 'out_scope')
    return bounty_hash
