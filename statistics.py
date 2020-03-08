import ccxt
import time
from setting import apiKey, secretKey

binance = ccxt.binance(
    {
        'apiKey':apiKey,
        'secret':secretKey
    }
)

SYMBOL = 'ETH/USDT'
# 時間戳網址: https://www.cadch.com/article/timestamp/index.php
SINCE = 1577808000000 #當月1號的 00 時: 00分: 00秒
END = 1580486399000 #當月最後一號的 23 時: 59分: 59秒
YEAR = '2020年'
MONTH = '1月'

def fetch_balance():
    balance = binance.fetch_balance()
    return balance['ETH'],balance['USDT']


def closed_orders():
    orders = binance.fetch_orders(SYMBOL, SINCE)
    for x in range(len(orders)):
        if orders[x]['status'] == 'closed':
            if orders[x]['timestamp'] > END:
                break
            print('symbol: '+str(orders[x]['info']['symbol'])+'\t\torderId: '+str(orders[x]['info']['orderId'])+
                  '\t\tprice: '+str(orders[x]['info']['price'])+'\t\tside: '+str(orders[x]['info']['side'])+
                  '\t\ttime: '+str(orders[x]['datetime']))

def closed_sell():
    totalSell = 0
    orders = binance.fetch_orders(SYMBOL, SINCE)
    for x in range(len(orders)):
        if orders[x]['timestamp'] > END:
            break
        if orders[x]['side'] == 'sell' and orders[x]['status'] == 'closed':
            totalSell = totalSell + orders[x]['price']
    return totalSell

def closed_buy():
    totalBuy = 0
    orders = binance.fetch_orders(SYMBOL, SINCE)
    for x in range(len(orders)):
        if orders[x]['timestamp'] > END:
            break
        if orders[x]['side'] == 'buy' and orders[x]['status'] == 'closed':
            totalBuy = totalBuy + orders[x]['price']
    return totalBuy





def open_orders():
    orders = binance.fetch_orders(SYMBOL, SINCE)
    for x in range(len(orders)):
        if orders[x]['status'] == 'open':
            if orders[x]['timestamp'] > END:
                break
            print('symbol: ' + str(orders[x]['info']['symbol']) + '\t\torderId: ' + str(orders[x]['info']['orderId']) +
                  '\t\tprice: ' + str(orders[x]['info']['price']) + '\t\tside: ' + str(orders[x]['info']['side']) +
                  '\t\ttime: ' + str(orders[x]['datetime']))

def open_sell():
    totalSell = 0
    orders = binance.fetch_orders(SYMBOL, SINCE)
    for x in range(len(orders)):
        if orders[x]['timestamp'] > END:
            break
        if orders[x]['side'] == 'sell' and orders[x]['status'] == 'open':
            totalSell = totalSell + orders[x]['price']
    return totalSell

def open_buy():
    totalBuy = 0
    orders = binance.fetch_orders(SYMBOL, SINCE)
    for x in range(len(orders)):
        if orders[x]['timestamp'] > END:
            break
        if orders[x]['side'] == 'buy' and orders[x]['status'] == 'open':
            totalBuy = totalBuy + orders[x]['price']
    return totalBuy




def canceled_orders():
    orders = binance.fetch_orders(SYMBOL,SINCE)
    for x in range(len(orders)):
        if orders[x]['status'] == 'canceled':
            if orders[x]['timestamp'] > END:
                break
            print('symbol: ' + str(orders[x]['info']['symbol']) + '\t\torderId: ' + str(orders[x]['info']['orderId']) +
                  '\t\tprice: ' + str(orders[x]['info']['price']) + '\t\tside: ' + str(orders[x]['info']['side']) +
                  '\t\ttime: ' + str(orders[x]['datetime']))

def canceled_sell():
    totalSell = 0
    orders = binance.fetch_orders(SYMBOL, SINCE)
    for x in range(len(orders)):
        if orders[x]['timestamp'] > END:
            break
        if orders[x]['side'] == 'sell' and orders[x]['status'] == 'canceled':
            totalSell = totalSell + orders[x]['price']
    return totalSell

def canceled_buy():
    totalBuy = 0
    orders = binance.fetch_orders(SYMBOL, SINCE)
    for x in range(len(orders)):
        if orders[x]['timestamp'] > END:
            break
        if orders[x]['side'] == 'buy' and orders[x]['status'] == 'canceled':
            totalBuy = totalBuy + orders[x]['price']
    return totalBuy



print(YEAR + MONTH)
print(fetch_balance())
print('已結單 {'+'賣單: ' + str(closed_sell())+'\t買單: ' + str(closed_buy())+'}')
print('已結單盈餘: ' + str(closed_sell()-closed_buy()-open_buy()))

print('\n未結單 {'+'賣單: ' + str(open_sell())+'\t買單: ' + str(open_buy())+'}')
print('未結單訂單資訊')
open_orders()

print('\n未結單 {'+'賣單: ' + str(canceled_sell())+'\t買單: ' + str(canceled_buy())+'}')
print('取消單訂單資訊')
canceled_orders()


