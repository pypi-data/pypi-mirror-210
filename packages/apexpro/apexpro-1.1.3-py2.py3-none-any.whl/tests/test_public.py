import os

from apexpro import HTTP
from apexpro.constants import MARKET_BTC_USD, APEX_HTTP_TEST
from apexpro.constants import MARKET_STATISTIC_DAY_ONE

from tests.constants import DEFAULT_HOST

ADDRESS_1 = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C0'
API_HOST = APEX_HTTP_TEST


class TestPublic():

    def test_check_if_user_exists(self):
        public = HTTP(API_HOST).public
        resp = public.check_if_user_exists(ADDRESS_1)
        expected_data = {
            'exists': False,
            'contractAddress': '',
            'isProxySigner': False
        }
        assert resp.data == expected_data
        assert resp.headers != {}

    def test_check_if_username_exists(self):
        public = HTTP(API_HOST).public
        resp = public.check_if_username_exists('foo')
        assert resp.data == {'exists': False}
        assert resp.headers != {}

    def test_get_markets(self):
        public = HTTP(API_HOST).public
        resp = public.get_markets()
        assert resp.data != {}
        assert resp.headers != {}

    def test_get_orderbook(self):
        public = HTTP(API_HOST).public
        resp = public.get_orderbook(MARKET_BTC_USD)
        assert resp.data != {}
        assert resp.headers != {}

    def test_get_stats(self):
        public = HTTP(API_HOST).public
        resp = public.get_stats(
            MARKET_BTC_USD,
            MARKET_STATISTIC_DAY_ONE,
        )
        assert resp.data != {}
        assert resp.headers != {}

    def test_get_trades(self):
        public = HTTP(API_HOST).public
        resp = public.get_trades(MARKET_BTC_USD)
        assert resp.data != {}
        assert resp.headers != {}

    def test_get_historical_funding(self):
        public = HTTP(API_HOST).public
        resp = public.get_historical_funding(MARKET_BTC_USD)
        assert resp.data != {}
        assert resp.headers != {}

    def test_get_candles(self):
        public = HTTP(API_HOST).public
        resp = public.get_candles(MARKET_BTC_USD)
        assert resp.data != {}
        assert resp.headers != {}

    def test_get_fast_withdrawal(self):
        public = HTTP(API_HOST).public
        resp = public.get_fast_withdrawal()
        assert resp.data != {}
        assert resp.headers != {}

    def test_verify_email(self):
        try:
            public = HTTP(API_HOST).public
            public.verify_email('token')
        except Exception as e:
            # No userId gotten with token: token so no verification
            # has occurred
            assert e.status_code == 400

    def test_public_retroactive_mining(self):
        public = HTTP(API_HOST).public
        resp = public.get_public_retroactive_mining_rewards(ADDRESS_1)
        assert resp.data != {}
        assert resp.headers != {}
