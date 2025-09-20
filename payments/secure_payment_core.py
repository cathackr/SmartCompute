#!/usr/bin/env python3
import base64
import hashlib
import hmac
import json
import time
from typing import Dict, Any
from datetime import datetime, timedelta

class SC:
    def __init__(self):
        self._k1 = base64.b64decode(b'U01BUlRDT01QVVRFLVBBWU1FTlQtVkFMSURBVElPTi1TRUNSRVQtMjAyNQ==').decode()
        self._k2 = {'mp': {'t': 'VEVTVC1NUC1BQ0NFU1MtVE9LRU4tUkVQTEFDRS1JTi1QUk9EVUNUSU9O', 's': 'TVAtV0VCSE9PSy1TRUNSRVQtS0VZ', 'c': 'TVAtQ0xJRU5ULUlE'}, 'bt': {'k': 'QklUU08tQVBJLUtFWS1SRVBMQUNFLUlOLVBST0RVQ1RJT04=', 's': 'QklUU08tQVBJLVNFQ1JFVC1LRVk=', 'w': 'QklUU08tV0VCSE9PSy1TRUNSRVQ='}}
        self._p = {'e': 15000, 'i': 25000}

    def _h(self, d: Dict[str, Any]) -> str:
        s = {k: d[k] for k in sorted(d.keys())}
        ds = json.dumps(s, separators=(',', ':'))
        return hmac.new(self._k1.encode(), ds.encode(), hashlib.sha256).hexdigest()

    def _v(self, d: Dict[str, Any], h: str) -> bool:
        return hmac.compare_digest(self._h(d), h)

    def mp(self, t: str, e: str, c: str, co: str) -> Dict[str, Any]:
        r = 900
        p = self._p['e'] if t == 'enterprise' else self._p['i']
        pa = p * r

        d = {
            'items': [{'title': f'SC {t.title()}', 'quantity': 1, 'currency_id': 'ARS', 'unit_price': pa}],
            'payer': {'email': e, 'name': c[:50]},
            'external_reference': f'SC-{t}-{int(time.time())}',
            'notification_url': 'https://api.smartcompute.io/wh/mp'
        }

        return {'status': 'ok', 'data': d, 'hash': self._h(d), 'url': f'https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=SC-{t.upper()}'}

    def bt(self, t: str, e: str, c: str) -> Dict[str, Any]:
        p = self._p['e'] if t == 'enterprise' else self._p['i']

        d = {
            'amount': str(p),
            'currency': 'USD',
            'external_id': f'SC-BT-{t}-{int(time.time())}',
            'callback_url': 'https://api.smartcompute.io/wh/bt'
        }

        return {'status': 'ok', 'data': d, 'hash': self._h(d), 'url': f'https://bitso.com/pay/{d["external_id"]}'}

def init():
    return SC()