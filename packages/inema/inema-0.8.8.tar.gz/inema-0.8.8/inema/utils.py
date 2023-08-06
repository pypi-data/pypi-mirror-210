# SPDX-Identifier: LGPL-3.0-or-later

import hashlib
from datetime import datetime
from pytz import timezone

def compute_1c4a_hash(partner_id, req_ts, key_phase, key):
    """Compute 1C4A request hash according to Section 4 of service description."""
    # trim leading and trailing spaces of each argument
    partner_id = partner_id.strip()
    req_ts = req_ts.strip()
    key_phase = key_phase.strip()
    key = key.strip()
    # concatenate with "::" separator
    inp = "%s::%s::%s::%s" % (partner_id, req_ts, key_phase, key)
    # compute MD5 hash as 32 hex nibbles
    md5_hex = hashlib.md5(inp.encode('utf8')).hexdigest()
    # return the first 8 characters
    return md5_hex[:8]

def gen_timestamp():
    """Compute a timestamp as used in the 1C4A and WaPoInt APIs."""
    de_zone = timezone("Europe/Berlin")
    de_time = datetime.now(de_zone)
    return de_time.strftime("%d%m%Y-%H%M%S")
