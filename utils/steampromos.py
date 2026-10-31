"""Manual Steam promotion discovery and conservative offer classification."""

import json
import time

from utils.steam import SteamError


def free_weekend_games(items, now=None):
    now = int(time.time()) if now is None else now
    return [(item, item['free_weekend']['end_time']) for item in items
            if item.get('type') == 0 and item.get('free_weekend', {}).get('start_time', now + 1) <= now
            < item.get('free_weekend', {}).get('end_time', 0)]


def free_games(items, now=None):
    """Require explicit keep entitlement AND evidence of a nonzero normal price."""
    now = int(time.time()) if now is None else now
    found = []
    for item in items:
        if item.get('type') != 0:
            continue
        options = list(item.get('purchase_options', []))
        options += [item.get('best_purchase_option') or {}, item.get('self_purchase_option') or {}]
        for option in options:
            if (option.get('is_free_to_keep') is True
                    and int(option.get('final_price_in_cents', -1)) == 0
                    and int(option.get('original_price_in_cents', 0)) > 0
                    and option.get('free_to_keep_ends', 0) > now
                    and not option.get('free_with_master_sub_appid')
                    and not option.get('recurrence_info')):
                found.append((item, option['free_to_keep_ends']))
                break
    return found


async def promotion_items(client, app_id=None):
    """Inspect a specific app or a bounded sample of Steam's public search results."""
    ids = {app_id} if app_id else set()
    if not app_id:
        for price_filters in ({'min_discount_percent': 1}, {'only_free_items': True}):
            params = {'input_json': json.dumps({
                'query': {'start': 0, 'count': 100, 'filters': {
                    'type_filters': {'include_apps': True, 'include_games': True},
                    'price_filters': price_filters,
                }},
                'context': {'country_code': client.country.upper(), 'language': 'english'},
            })}
            if client.key:
                params['key'] = client.key
            data = await client.request(
                'https://api.steampowered.com/IStoreQueryService/Query/v1/', **params
            )
            candidates = data.get('response', {}).get('ids')
            if not isinstance(candidates, list):
                raise SteamError('Steam promotion query returned an unexpected response.')
            ids.update(item['appid'] for item in candidates if item.get('appid'))
    items = []
    ordered = sorted(ids)
    for start in range(0, len(ordered), 50):
        params = {'input_json': json.dumps({
            'ids': [{'appid': value} for value in ordered[start:start + 50]],
            'context': {'country_code': client.country.upper(), 'language': 'english'},
            'data_request': {'include_all_purchase_options': True, 'include_assets': True,
                             'include_release': True, 'include_platforms': True,
                             'include_reviews': True},
        })}
        if client.key:
            params['key'] = client.key
        data = await client.request(
            'https://api.steampowered.com/IStoreBrowseService/GetItems/v1/', **params
        )
        batch = data.get('response', {}).get('store_items')
        if not isinstance(batch, list):
            raise SteamError('Steam store browse unavailable. Check your Steam API key and try again.')
        if any(item.get('success', 1) != 1 for item in batch) or len(batch) != len(ordered[start:start + 50]):
            raise SteamError('Steam could not inspect every candidate; please retry later.')
        items.extend(batch)
    return items
