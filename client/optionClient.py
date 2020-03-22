from client.client import AsyncClient

async def create(api_key='', api_secret='', INSTRUMENT_TYPE = 'option'):
    return await AsyncClient.create(api_key, api_secret, INSTRUMENT_TYPE)
