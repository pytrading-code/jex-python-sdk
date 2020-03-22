import asyncio
from client import spotClient, swapClient, optionClient, utils

# fill your api_key and api_secret
api_key = ""
api_secret = ""


async def run():
    spot_client = await spotClient.create(api_key=api_key, api_secret=api_secret)
    swap_client = await swapClient.create(api_key=api_key, api_secret=api_secret)
    option_client = await optionClient.create(api_key=api_key, api_secret=api_secret)

    while True:
        spot_orderbook = await spot_client.get_order_book(symbol = 'btcusdt', limit = 5)
        print("spot orderbook...")
        print(spot_orderbook)

        swap_orderbook = await swap_client.get_order_book(symbol = 'BTCUSDT', limit = 5)
        print("swap orderbook...")
        print(swap_orderbook)

        option_orderbook = await option_client.get_order_book(symbol = 'BTC0422CALL', limit = 5)
        print("option orderbook...")
        print(option_orderbook)

        await asyncio.sleep(1)

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(run())
    loop.run_forever()

if __name__ == "__main__":
    main()
