import aiohttp
import asyncio
import hashlib
import hmac
import time
import datetime
from abc import ABC, abstractmethod
from operator import itemgetter

from client.utils import *
from client.constants import *

class BaseClient(ABC):
    def __init__(self, api_key, api_secret, INSTRUMENT_TYPE):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = self._init_session()
        self.INSTRUMENT_TYPE = INSTRUMENT_TYPE

    def _get_headers(self):
        return {
            'X-JEX-APIKEY': self.api_key
        }

    @abstractmethod
    def _init_session(self):
        pass

    def _create_api_uri(self, path, signed=True, version=API_VERSION):
        v = API_VERSION if signed else version
        return API_URL + '/' + v + '/' + path

    def _create_website_uri(self, path):
        return WEBSITE_URL + '/' + path

    def _generate_signature(self, data):
        ordered_data = data
        query_string = '&'.join(["{}={}".format(k, v) for k,v in ordered_data.items()])
        m = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256)
        return m.hexdigest()

    @staticmethod
    def _order_params(data):
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, str(value)))
        # sort parameters by key
        params.sort(key=itemgetter(0))
        if has_signature:
            params.append(('signature', data['signature']))
        return params

    def _get_request_kwargs(self, method, signed, force_params=False, **kwargs):

        # set default requests timeout
        kwargs['timeout'] = 10
        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del(kwargs['data']['requests_params'])

        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000)
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params or method == 'delete'):
            kwargs['params'] = kwargs['data']
            del(kwargs['data'])

        return kwargs

class AsyncClient(BaseClient):

    @classmethod
    async def create(cls, api_key='', api_secret='', INSTRUMENT_TYPE = None):

        self = cls(api_key, api_secret, INSTRUMENT_TYPE)

        await self.ping()

        return self

    def _init_session(self):

        loop = asyncio.get_event_loop()
        session = aiohttp.ClientSession(
            loop=loop,
            headers=self._get_headers()
        )
        return session

    async def _request(self, method, uri, signed, force_params=False, **kwargs):

        kwargs = self._get_request_kwargs(method, signed, force_params, **kwargs)
        async with getattr(self.session, method)(uri, **kwargs) as response:
            return await self._handle_response(response)

    async def _handle_response(self, response):
        if not str(response.status).startswith('2'):
            raise Exception(response, response.status, await response.text())
        try:
            return await response.json()
        except ValueError:
            txt = await response.text()
            raise Exception('Invalid Response: {}'.format(txt))

    async def _request_api(self, method, path, signed=False, version=API_VERSION, **kwargs):
        uri = self._create_api_uri(path, signed, version)
        return await self._request(method, uri, signed, **kwargs)

    async def _request_website(self, method, path, signed=False, **kwargs):
        uri = self._create_website_uri(path)
        return await self._request(method, uri, signed, **kwargs)

    async def get(self, path, signed=False, version=API_VERSION, **kwargs):
        return await self._request_api('get', path, signed, version, **kwargs)

    async def post(self, path, signed=False, version=API_VERSION, **kwargs):
        return await self._request_api('post', path, signed, version, **kwargs)

    async def put(self, path, signed=False, version=API_VERSION, **kwargs):
        return await self._request_api('put', path, signed, version, **kwargs)

    async def delete(self, path, signed=False, version=API_VERSION, **kwargs):
        return await self._request_api('delete', path, signed, version, **kwargs)

    # Exchange Endpoints
    async def get_exchange_info(self):
        return await self.get('exchangeInfo')

    async def get_symbol_info(self):
        return await self.get(self.INSTRUMENT_TYPE + 'Info')

    # General Endpoints

    async def ping(self):
        return await self.get('ping')

    async def get_server_time(self):
        return await self.get('time')

    # Market Data Endpoints
    async def get_order_book(self, **params):
        return await self.get( self.INSTRUMENT_TYPE + '/' + 'depth', data=params)

    async def get_recent_trades(self, **params):
        return await self.get( self.INSTRUMENT_TYPE + '/' + 'trades', data=params)

    async def get_historical_trades(self, **params):
        return await self.get( self.INSTRUMENT_TYPE + '/' + 'historicalTrades', data=params)

    async def _get_klines(self, **params):
        return await self.get( self.INSTRUMENT_TYPE + '/' + 'klines', data=params)

    async def get_historical_klines(self, symbol, interval, startTime, endTime, limit = 1000):
        startTime = strtime_to_timestamp(startTime)
        endTime = strtime_to_timestamp(endTime)
        klines = await self._get_klines(symbol = symbol, interval = interval, startTime = startTime, endTime = endTime, limit = limit) 
        return [{'startTime' : timestamp_to_strtime(int(k[0])), 'open' : float(k[1]), 'high' : float(k[2]), 'low' : float(k[3]), 'close' : float(k[4]), 'volume' : float(k [5]), 'endTime' : timestamp_to_strtime(int(k[6]))} for k in klines]

    async def get_recent_klines(self, symbol, interval, limit = 1000): 
        endTime = datetime.now()
        startTime = endTime - timedelta(seconds = limit * interval_to_seconds(interval))
        endTime = datetime_to_strtime(endTime)
        startTime = datetime_to_strtime(startTime)
        return await self.get_historical_klines(symbol, interval, startTime, endTime, limit)

    async def get_ticker(self, **params):
        return await self.get( self.INSTRUMENT_TYPE + '/' + 'ticker/24hr', data=params)

    async def get_symbol_ticker(self, **params):
        return await self.get( self.INSTRUMENT_TYPE + '/' + 'ticker/price', data=params, version=API_VERSION)

    async def get_orderbook_ticker(self, **params):
        return await self.get( self.INSTRUMENT_TYPE + '/' + 'ticker/bookTicker', data=params, version=API_VERSION)

    #Trade API
    async def create_order(self, **params):
        return await self.post( self.INSTRUMENT_TYPE + '/' + 'order', True, data=params)

    async def create_test_order(self, **params):
        return await self.post( self.INSTRUMENT_TYPE + '/' + 'order/test', True, data=params)

    async def get_order(self, **params):
        return await self.get(self.INSTRUMENT_TYPE + '/' + 'order', True, data=params)

    async def cancel_order(self, **params):
        return await self.delete(self.INSTRUMENT_TYPE + '/' + 'order', True, data=params)

    async def get_open_orders(self, **params):
        return await self.get(self.INSTRUMENT_TYPE + '/' + 'openOrders', True, data=params)

    async def get_position(self, **params):
        return await self.get(self.INSTRUMENT_TYPE + '/' + 'position', True, data=params)

    async def set_leverage(self, **params):
        return await self.post( self.INSTRUMENT_TYPE + '/' + 'position/leverage', True, data=params)

    async def get_account(self, **params):
        return await self._get('account', True, data=params)