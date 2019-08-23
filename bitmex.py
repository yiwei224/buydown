import pandas as pd
from settings import APIKEY, SECRETKEY, YIWEIAPI, YIWEISEC, SYMBOLS
import time
import ccxt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# binance = ccxt.binance(
#     {
#         'apiKey': YIWEIAPI,
#         'secret': YIWEISEC
#     }
# )

binance = ccxt.binance(
    {
        'apiKey': APIKEY,
        'secret': SECRETKEY
    }
)

limit = 20000
current_time = int(time.time() // 60 * 60 * 1000)  # 毫秒
since_time = current_time - (limit * 60 * 1000)

data = binance.fetch_ohlcv(SYMBOLS, timeframe='1d', since=since_time)
df = pd.DataFrame(data)
df = df.rename(columns={0: 'open_time', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
df['open_time'] = pd.to_datetime(df['open_time'], unit='ms') + pd.Timedelta(hours=8)
print('週期內每一天的數據：')
print(df)
print(' ----------------------------------------------------------------------------------------------------------------------')

df = pd.DataFrame(df, columns=['high'])
df.loc['max'] = df.max(axis=0)
print('最高價:')
print(df.loc['max'])
print(' ----------------------------------------------------------------------------------------------------------------------')

#帳戶資訊
balance = binance.fetch_balance()
df = pd.DataFrame(balance)
print('帳戶資訊:')
print(df)
print('ETH', balance['ETH'])
print('USDT', balance['USDT'])
print(' ----------------------------------------------------------------------------------------------------------------------')

#訂單資訊
orders = binance.fetch_orders(SYMBOLS)
df = pd.DataFrame(orders)
print('訂單資訊:')
print(len(orders))
print(df)
print(' ----------------------------------------------------------------------------------------------------------------------')

#獲取當前掛單
open_orders = binance.fetch_open_orders(SYMBOLS)
df = pd.DataFrame(open_orders)
print('當前掛單：')
print(df)
# print(' -----------------------------------------------------------------------------------------------------------------------')
# print(len(open_orders))
print(' -----------------------------------------------------------------------------------------------------------------------')


# #當前價格, 成交價
# while(1):
#     ticker = binance.fetch_ticker(SYMBOLS)
#     orderbook = ticker
#     bid = orderbook['bid']
#     ask = orderbook['ask']
#     # 為了獲得當前最優價格（查詢市場價格）併計算bid ask點差，請從bid和ask中獲取第一個元素
#     spread = (ask - bid) if (bid and ask) else None
#     #print('market price', {'bid': bid, 'ask': ask, 'spread': spread})
#     print('當前價格：', bid)
#     print('成交價：', ask)
#     print('手續費：', spread)
#     print(' ----------------------------------------------------------------------------------------------------------------------')
#     cycle_highest_price = df.loc['max']  # 週期內最高價
#     current_price = bid  # 當前價格
#     final_price = ask  # 成交價
#
#     # 總持倉-1手(cycle一次的賣單量)/3 = sell[1]要賣出的數量 = X
#
#     sell = 0
#     if float(cycle_highest_price * 0.8) > (current_price):
#         sell = 1
#         sell_order1 = binance.create_order(SYMBOLS, type='market', side='sell', amount='X')
#         print(sell_order1['info']['price'])
#         print('sell(1) completed')
#     else:
#         print()
#
#     if sell == 1 & float(cycle_highest_price * 0.75) > (current_price):
#         sell = 2
#         sell_order2 = binance.create_order(SYMBOLS, type='market', side='sell', amount='X')
#         print(sell_order2['info']['price'])
#         print('sell(2) completed')
#         if ask >= float(sell_order1['info']['price']) + (sell_order2['info']['price']) / (2.0):
#             buy_order2 = binance.create_order(SYMBOLS, type='market', side='buy', amount='2X')
#             print(buy_order2)
#             print('buy_order(2) completed')
#         else:
#             print()
#     else:
#         print()
#
#     if sell == 2 & float(cycle_highest_price * 0.7) > (current_price):
#         sell_order3 = binance.create_order(SYMBOLS, type='market', side='sell', amount='X')
#         print(sell_order3['info']['price'])
#         print('sell(3) complete')
#         if ask >= float(sell_order1['info']['price']) + (sell_order2['info']['price']) + (
#                 sell_order3['info']['price']) / (3.0):
#             buy_order3 = binance.create_order(SYMBOLS, type='market', side='buy', amount='3X')
#             print(buy_order3)
#             print('buy_order(3) completed')
#         else:
#             print()
#     else:
#         print()
#
#     sell = 0
