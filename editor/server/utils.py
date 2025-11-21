import json
import os

from flask import request
from . import root_dir


loc_data: dict = None

def read_loc_file(path: str):
    try:
        with open(os.path.join(root_dir, path)) as f:
            return json.load(f)
    except:
        return


def get_cf_location(loc: str):
    global loc_data
    loc = loc.upper()
    if loc_data is None:
        loc_data = read_loc_file('editor/server/cf-colos.json')
    if loc_data is None:
        # From https://github.com/Netrvin/cloudflare-colo-list/blob/main/DC-Colos.json
        loc_data = read_loc_file('editor/server/cf-colos.bundled.json')
    if loc_data is None:
        return
    data: dict = loc_data.get(loc)
    if not data:
        return
    return data.get('city')


def fill_cf_template_params(params: dict):
    # Get real Ray ID / data center location from Cloudflare header
    ray_id_loc = request.headers.get('Cf-Ray')
    if ray_id_loc:
        params['ray_id'] = ray_id_loc[:16]

        cf_status: dict = params.get('cloudflare_status', {})
        if not cf_status.get('location'):
            loc = get_cf_location()
            if loc:
                cf_status['location'] = loc

    # Get real client ip from Cloudflare header or request.remote_addr
    client_ip = request.headers.get('X-Forwarded-For')
    if not client_ip:
        client_ip = request.remote_addr
    params['client_ip'] = client_ip
