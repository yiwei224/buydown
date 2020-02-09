import ccxt

binance = ccxt.binance(
    {
        'apiKey':'HFP38WJHSCd434aAGW3Bv0uyJ8PHtM1pwZFjNCtIZb2nvwDmtbEkQD3Z3XxRz2Iz',
        'secret':'QvDZhRYTKhlly2Pan2EAGU30ZuJEOBZjudEHNG0spUO90ITKRNyaizNihayvH0A7'
    }
)
SYMBOL = 'ETH/USDT'



#帳戶資訊(ETH/USDT)
def fetch_balance():
    balance = binance.fetch_balance()
    return balance['ETH'],balance['USDT']

#賣單總額
def total_sellprice():
    totalSell = 0
    orders1 = binance.fetch_orders(SYMBOL, since=1570021225338)
    orders2 = binance.fetch_orders(SYMBOL, since=1574870444483)
    orders = [orders1, orders2]
    for x in range(2):
        for y in range(len(orders[x])):
            order_side = orders[x][y]['side']
            order_price = orders[x][y]['price']
            if order_side == 'sell':
                totalSell = totalSell + order_price
    return  totalSell


#買單總額
def total_buyprice():
    totalBuy = 0
    orders1 = binance.fetch_orders(SYMBOL, since=1570021225338)
    orders2 = binance.fetch_orders(SYMBOL, since=1574870444483)
    orders = [orders1,orders2]
    for x in range(2):
        for y in range(len(orders[x])):
            order_side = orders[x][y]['side']
            order_price = orders[x][y]['price']
            if order_side == 'buy':
                totalBuy = totalBuy + order_price
    return  totalBuy

#當前掛單
def open_orders():
    open_orders = binance.fetch_open_orders(SYMBOL)
    print(open_orders)


def close_orders():
    close_orders = binance.fetch_closed_orders(SYMBOL)
    print(close_orders)



print('ETH: ' + str(fetch_balance()[0]))
print('USDT: ' + str(fetch_balance()[1]))
print('total_sellPrice: '+str(total_sellprice()))
print('total_buyPrice: '+str(total_buyprice()))
print('surplus: '+str(total_sellprice()-total_buyprice()))

