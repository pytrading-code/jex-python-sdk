[jex-python-sdk](https://pytrading.io/index.php/2020/03/24/binance-jex-exchange-python-sdk/) is a python async client of Binance Jex exchange, it provides a REST client according to [jex api doc](https://jexapi.github.io/api-doc/#185368440e) based on aiohttp. 

### Crypto market is very volatile, please use this sdk at your own risk.


```python
%load_ext autoreload
%autoreload 2
from client import spotClient, swapClient, optionClient, utils

# fill your api_key and api_secret
api_key = ""
api_secret = ""
spot_client = await spotClient.create(api_key=api_key, api_secret=api_secret)
swap_client = await swapClient.create(api_key=api_key, api_secret=api_secret)
option_client = await optionClient.create(api_key=api_key, api_secret=api_secret)
```

### Spot API (The 3 clients have similiar interface, use spot as example below)

#### General API

[Get server time](https://jexapi.github.io/api-doc/spot.html#check-server-time)


```python
server_time = await spot_client.get_server_time()
server_time
```

I provide some time transformation method in utils, you can change timestamp to a readable time or datetime.


```python
utils.timestamp_to_strtime(server_time['serverTime'])
```


```python
utils.timestamp_to_datetime(server_time['serverTime'])
```

#### Market API
[Get the current trading rules and symbol information  ](https://jexapi.github.io/api-doc/spot.html#exchange-information)

[Get spot orderbook](https://jexapi.github.io/api-doc/spot.html#depth-information-for-spot


```python
await spot_client.get_order_book(symbol = 'btcusdt', limit = 5)
```

[Get recent trades](https://jexapi.github.io/api-doc/spot.html#recent-trades-for-spot)


```python
await spot_client.get_recent_trades(symbol = 'btcusdt', limit = 5)
```

[Get recent klines](https://jexapi.github.io/api-doc/spot.html#kline-candlestick-data)


```python
await spot_client.get_recent_klines('btcusdt', '1m', limit = 5)
```

Get historical klines


```python
await spot_client.get_historical_klines('btcusdt', '5m', startTime = '2020-03-23 22:00:00', endTime = '2020-03-23 22:30:00')
```

[24 hour rolling window price change statistics. Careful when accessing this with no symbol.](https://jexapi.github.io/api-doc/spot.html#24hr-ticker-price-change-statistics)


```python
await spot_client.get_ticker(symbol='btcusdt')
```

[Spot latest price](https://jexapi.github.io/api-doc/spot.html#price-ticker-for-spot)


```python
await spot_client.get_symbol_ticker(symbol='btcusdt')
```

#### Trade API

[Spot Create Order](https://jexapi.github.io/api-doc/spot.html#place-order-in-coins-transaction-trade)


```python
await spot_client.create_order(symbol='btcusdt', side='BUY', type = 'LIMIT', quantity = 0.0001, price = 4000)
```

[Get open orders](https://jexapi.github.io/api-doc/spot.html#check-entry-orders-of-coins-transaction-of-this-account-user_data)


```python
await spot_client.get_open_orders(symbol='btcusdt')
```

[Get order status](https://jexapi.github.io/api-doc/spot.html#check-orders-of-coins-transaction-user_data)


```python
# The orderId should be the return orderId when you create order
await spot_client.get_order(symbol='btcusdt', orderId=45504774)
```

[Cancel order](https://jexapi.github.io/api-doc/spot.html#cancel-order-for-coins-transaction-trade)


```python
await spot_client.cancel_order(symbol='btcusdt', orderId=45504774)
```

### Swap(Futures) && Option
Most of their interfaces are the same with spot, I just show how to get order books here.


```python
await swap_client.get_order_book(symbol = 'BTCUSDT', limit = 5)
```


```python
await option_client.get_order_book(symbol = 'BTC0422CALL', limit = 5)
```

#### Option and Swap have postion interface, which spot doesn't.
[option postion](https://jexapi.github.io/api-doc/option.html#options-positions-of-the-account-user_data)
[swap positon](https://jexapi.github.io/api-doc/future.html#check-contract-positions-of-the-account-user_data)


```python
await swap_client.get_position()
```


```python
await option_client.get_position()
```
