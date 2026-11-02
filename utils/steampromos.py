"""Find Steam promotions and check which offers are still active."""

import json
import time

from utils.steam import SteamError


def free_weekend_games(items, now=None):
    now = int(time.time()) if now is None else now
    return [(item, item['free_weekend']['end_time']) for item in items
            if item.get('type') == 0 and item.get('free_weekend', {}).get('start_time', now + 1) <= now
            < item.get('free_weekend', {}).get('end_time', 0)]


def free_games(items, now=None):
    """Only include paid games that Steam says are temporarily free to keep."""
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


async def promotion_items(client, app_id=None, *, kind='freegames'):
    """Search Steam's API, then fetch each game's offer details.

    Steam ignored a minimum discount of 100 in live checks, so use 99 and
    check for a free-to-keep offer separately. For weekends, search the
    global top 1,000 sellers.
    """
    ids = {app_id} if app_id else set()
    if not app_id:
        filters = {'type_filters': {'include_games': True}}
        if kind == 'freegames':
            filters['price_filters'] = {'min_discount_percent': 99}
        elif kind == 'freeweekends':
            filters['global_top_n_sellers'] = 1000
        else:
            raise ValueError('Unknown promotion kind')
        start = 0
        while True:
            params = {'input_json': json.dumps({
                'query': {'start': start, 'count': 100, 'sort': 1, 'filters': filters},
                'context': {'country_code': client.country.upper(), 'language': 'english'},
            })}
            if client.key:
                params['key'] = client.key
            data = await client.request(
                'https://api.steampowered.com/IStoreQueryService/Query/v1/', **params
            )
            response = data.get('response', {})
            candidates = response.get('ids')
            metadata = response.get('metadata', {})
            total = metadata.get('total_matching_records')
            # Steam may leave out the game list when there are no matches.
            if candidates is None and total == 0:
                break
            if (not isinstance(candidates, list) or not isinstance(total, int)
                    or total < 0 or metadata.get('start') != start):
                raise SteamError('Steam returned an invalid promotion list. Please try again.')
            if not candidates and start < total:
                raise SteamError('Steam did not return all search results. Please try again.')
            ids.update(item['appid'] for item in candidates if item.get('appid'))
            start += len(candidates)
            if start >= total:
                break
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
