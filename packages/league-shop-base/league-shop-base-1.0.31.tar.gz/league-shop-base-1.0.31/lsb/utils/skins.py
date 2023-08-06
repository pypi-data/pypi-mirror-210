import json

import requests
import urllib3

urllib3.disable_warnings()


def get_rarity_by_value(skin_value):
    if skin_value in ['Special', 'special']:
        return 'LIMITED'
    if isinstance(skin_value, int) and skin_value >= 1350:
        return 'EPIC'
    if isinstance(skin_value, int) and skin_value >= 975:
        return 'STANDARD'
    return 'BUDGET'


DEFAULT_RARITIES = [
    'Mythic',
    'Epic',
    'Legendary',
    'Ultimate',
]


def ger_merai_analytics_data():
    try:
        res = requests.get(
            'https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions.json', timeout=30)
        meraianalytics = res.json()
    except (requests.exceptions.RequestException, json.decoder.JSONDecodeError):
        return None

    mapped_data = {}
    for champ in meraianalytics.values():
        for skin in champ['skins']:
            rarity = skin['rarity']
            value = skin['cost']

            release = skin['release']
            if rarity not in DEFAULT_RARITIES:
                rarity = get_rarity_by_value(value)
            if value == 'special':
                value = -1

            mapped_data[skin['id']] = {
                'id': skin['id'],
                'value': value,
                'rarity': rarity,
                'release': release
            }
    return mapped_data


def get_lol_client_skins():
    print('Parsing skin data...')
    try:
        res = requests.get(
            'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/skins.json', timeout=30)
        skins_data = res.json()
    except (requests.exceptions.RequestException, json.decoder.JSONDecodeError):
        return None

    non_base_skins = [s for s in skins_data.values() if not s['isBase']]

    print('Parsing meraianalytics...')
    meraianalytics = ger_merai_analytics_data()

    if meraianalytics is None:
        return None

    skins = {}
    for skin in non_base_skins:
        skin_id = skin['id']
        skin_name = skin['name']
        skin_data = meraianalytics.get(skin_id)
        if skin_data is None:
            print(f'Could not find skin {skin_id}, {skin_name}')
            return

        if skin_name == 'Annie-Versary':
            skin_data['rarity'] = 'LIMITED'

        skins[f'{skin_id}'] = {
            'skin_id': skin_id,
            'skin_name': skin_name,
            'skin_rarity': skin_data['rarity'].upper(),
            'skin_value': skin_data['value'],
            'release_date': skin_data['release'],
        }
    return skins
