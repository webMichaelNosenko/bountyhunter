import hashlib

hash_table = {}


def push_hash(handle, new_hash):
    hash_table[handle] = new_hash


def hash_assets(bounty_object, asset_type):
    """
    Turns all of the bug bounty program's assets of the same type into a hash string (md5) OR returns
    '!eligible_domains:[NONE]', '!ineligible_domains:[NONE]' or '!out_scope:[NONE]'

    :param bounty_object: dict; the bounty data being used
    :param asset_type: string; either 'eligible_domains', 'ineligible_domains' or 'out_scope'
    """
    assets_hash = ''
    if len(bounty_object[asset_type]) != 0:
        assets_hash = assets_hash + ('!' + asset_type + ':[')
        for item in bounty_object[asset_type]:
            assets_hash = assets_hash + hashlib.md5(item.encode('utf-8')).hexdigest()
        assets_hash = assets_hash + ']'
    else:
        assets_hash = assets_hash + ('!' + asset_type + ':[NONE]')
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


def check_hash(handle, new_bounty_hash):
    """
    Checks if the new hash is different for a specific program

    :param handle: string; handle of bug bounty program
    :param new_bounty_hash: string; newly generated hash-string, see make_hash()
    :return: scope_changes: dict (bool); keys are: | eligible_changed | ineligible_changed | out_scope_changed |
            new_program_added
    """
    scope_changes = {
        'eligible_changed': False,
        'ineligible_changed': False,
        'out_scope_changed': False,
        'new_program_added': False
    }
    if handle in hash_table:
        old_bounty_hash = hash_table[handle]

        new_scope_hashes = new_bounty_hash.split('!')
        old_scope_hashes = old_bounty_hash.split('!')

        if new_scope_hashes[0] != old_scope_hashes[0]:
            scope_changes['eligible_changed'] = True
        if new_scope_hashes[1] != old_scope_hashes[1]:
            scope_changes['ineligible_changed'] = True
        if new_scope_hashes[2] != old_scope_hashes[2]:
            scope_changes['out_scope_changed'] = True

    else:
        push_hash(handle, new_bounty_hash)
        scope_changes['new_program_added'] = True

    return scope_changes
