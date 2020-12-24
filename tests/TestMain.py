import pytest
import bountyhunter.main as bh
import bountyhunter.db as db
import bountyhunter.hashtable as hashtable
import requests
import json


def test_asset_change():
    session = requests.Session()
    programlist = session.get(bh.hackerone)
    bountiespage = db.fetch_all_results("SELECT handle FROM bounty_programs;")
    objects = []
    for n in bountiespage:
        objects.append(n[0])
    for placeholdObj in objects:
        old_el_assets = list(db.get_assets(placeholdObj, 'eligible'))
        old_inel_assets = list(db.get_assets(placeholdObj, 'ineligible'))
        old_out_assets = list(db.get_assets(placeholdObj, 'out_scope'))

        new_el_assets = old_el_assets
        new_el_assets.append('fugg')
        new_inel_assets = ['oop', 'woop']
        new_out_assets = old_out_assets

        bounty_object = {
            'handle': placeholdObj,
            'eligible': new_el_assets,
            'ineligible': new_inel_assets,
            'out_scope': new_out_assets
        }

        hashtable.hash_table = db.get_hash_table()
        new_hash = hashtable.make_hash(bounty_object)
        check_res = {
            'eligible_changed': False,
            'ineligible_changed': False,
            'out_scope_changed': False,
            'new_program_added': False
        }
        if placeholdObj in hashtable.hash_table:
            old_bounty_hash = hashtable.hash_table[placeholdObj]
            new_scope_hashes = new_hash.split('!')
            old_scope_hashes = old_bounty_hash.split('!')

            if new_scope_hashes[0] != old_scope_hashes[0]:
                check_res['eligible_changed'] = True
            if new_scope_hashes[1] != old_scope_hashes[1]:
                check_res['ineligible_changed'] = True
            if new_scope_hashes[2] != old_scope_hashes[2]:
                check_res['out_scope_changed'] = True

        else:
            check_res['new_program_added'] = True

        print(placeholdObj)
    #    assert check_res['new_program_added'] is False
        assert new_hash != hashtable.hash_table[placeholdObj]
        assert check_res['eligible_changed'] is True
        assert check_res['ineligible_changed'] is True
        assert check_res['out_scope_changed'] is False
        db.update_assets_of_type(bounty_object, 'eligible')
        db.update_assets_of_type(bounty_object, 'ineligible')
        db.update_assets_of_type(bounty_object, 'out_scope')
        new_el_assets = list(db.get_assets(placeholdObj, 'eligible'))
        new_inel_assets = list(db.get_assets(placeholdObj, 'ineligible'))
        new_out_assets = list(db.get_assets(placeholdObj, 'out_scope'))
        assert tuple('fugg') in new_el_assets
        assert 'oop' in new_inel_assets
        assert 'woop' in new_inel_assets
        assert new_out_assets == old_out_assets


if __name__ == '__main__':
    test_asset_change()
