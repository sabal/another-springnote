import calendar
import json
import os
import re
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_resource(subdomain, path):
    with open(os.path.join(BASE_DIR, '_api', subdomain,
            os.path.normpath(path) + '.json')) as f:
        return json.loads(f.read())


def parse_timestamp(timestamp):
    m = re.match(r'^(?P<parsable>\d{4}/\d{2}/\d{2} '
        r'\d{2}:\d{2}:\d{2}) '
        r'(?P<tz_sign>[-+])'
        r'(?P<tz_hour>\d{2})(?P<tz_minute>\d{2})$',
        timestamp)
    # NOTE: strptime cannot parse timezone
    timestamp = calendar.timegm(time.strptime(m.group('parsable'),
        '%Y/%m/%d %H:%M:%S'))
    delta = (int(m.group('tz_hour')) * 3600 +
            int(m.group('tz_minute')) * 60)
    if m.group('tz_sign') == '-':
        delta = -delta
    timestamp += delta
    return timestamp


def is_public(subdomain, page_id):
    collaboration = load_resource(subdomain,
        'pages/{}/collaboration'.format(int(page_id)))
    if not collaboration:
        # same as its parent
        page = load_resource(subdomain, 'pages/{}'.format(int(page_id)))
        parent_id = page['page']['relation_is_part_of']
        if not parent_id:
            return True
        return is_public(subdomain, parent_id)
    for item in collaboration:
        if (item['collaboration']['access_rights'] == 'reader' and
                item['collaboration']['rights_holder'] == 'everybody'):
            return True
    return False


def makedirs(path, exist_ok=False):
    try:
        os.makedirs(path)
    except OSError as e:
        if not exist_ok:
            raise
        import errno
        if e.errno not in [errno.EEXIST]:
            raise
