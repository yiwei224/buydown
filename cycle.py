import ccxt
from api.models import Order, KlineRecord, CycleState, BuydownState
from .log import log
import time


class Cycle:
    def __init__(self, _range, cover, quantity, point, symbols, benefit, APIKEY, SECRETKEY):
        self.cycle_state = 1
        self.binance = ccxt.binance(
            {
                'apiKey': APIKEY,
                'secret': SECRETKEY
            }
        )
        self.range = _range
        self.cover = cover
        self.quantity = quantity
        self.point = point
        self.symbols = symbols
        self.benefit = benefit
        self.is_activate = False
        self.ticker = None
        self.ohlcv = None
        self.balance_1 = None
        self.balance_2 = None
        self.cycle_a = None
        self.cycle_b = None

    def clean_state(self):
        self.cycle_state = 1
        self.balance_1 = None
        self.balance_2 = None
        self.cycle_a = None
        self.cycle_b = None

    def fetch_ticker(self):
        try:
            self.ticker = self.binance.fetch_ticker(self.symbols)
        except Exception as e:
            log.info(e)
            log.info('fetch ticker failed')
            self.fetch_ticker()
            time.sleep(1)

    def fetch_balance(self):
        try:
            symbols = self.symbols.split('/')
            symbol_1, symbol_2 = symbols[0], symbols[1]
            balance = self.binance.fetch_balance()
            self.balance_1 = balance[symbol_1]
            self.balance_2 = balance[symbol_2]
        except Exception as e:
            log.info(e)
            log.info('fetch balance failed')
            self.fetch_balance()
            time.sleep(1)

    def fetch_ohlcv(self):
        try:
            ohlcv = self.binance.fetch_ohlcv(self.symbols, timeframe='1h')
            current = ohlcv[-2]
            record = KlineRecord.objects.filter(timestamp=current[0]).first()
            self.ohlcv = ohlcv
            if not record:
                current = self.get_current_ohlcv()
                KlineRecord.objects.create(
                    timestamp=current[0],
                    cover=self.get_kline_cover(),
                    range=self.get_kline_range(),
                    high=current[2],
                    low=current[3]
                )
                self.clean_state()

        except Exception as e:
            log.info(e)
            log.info('fetch ohlcvs error')
            self.fetch_ohlcv()
            time.sleep(1)

    def get_current_ohlcv(self):
        return self.ohlcv[-2]

    def get_prev_ohlcv(self):
        return self.ohlcv[-3]

    def get_kline_range(self):
        current = self.get_current_ohlcv()
        return (current[2] - current[3]) / ((current[2] + current[3]) / 2)

    def get_kline_cover(self):
        current = self.get_current_ohlcv()
        prev = self.get_prev_ohlcv()
        if current[2] >= prev[2] and current[3] <= prev[3]:
            return 1
        elif current[2] <= prev[3] or current[3] >= prev[2]:
            return 0
        elif current[2] <= prev[2] and current[3] >= prev[3]:
            return (current[2] - current[3]) / (prev[2] - prev[3])
        elif prev[2] >= current[2] >= prev[3]:
            return (current[2] - prev[3]) / (prev[2] - prev[3])
        elif prev[3] <= current[3] <= prev[2]:
            return (prev[2] - current[3]) / (prev[2] - prev[3])

    def get_last(self):
        if not self.ticker:
            raise Exception
        return self.ticker['last']

    def get_sell_amount(self):
        return self.balance_1 - (3.5 / 3)

    def is_cycle_a_valid(self):
        return self.get_kline_cover() >= 0.6 and self.get_kline_range() >= self.range and self.balance_1[
            'free'] > self.quantity and self.balance_2['free'] > self.get_last()

    def get_kline_range(self):
        HIGH_INDEX = 2
        LOW_INDEX = 3
        ohlcv = self.get_current_ohlcv()
        kline_range = (ohlcv[HIGH_INDEX] - ohlcv[LOW_INDEX]) * self.point
        return kline_range

    def get_should_sell(self):
        return self.get_current_ohlcv()[2] - self.get_kline_range()

    def get_should_buy(self):
        return self.get_current_ohlcv()[3] + self.get_kline_range()

    def is_sell_valid(self):
        def get_valid_quantity(state):
            if state.cycle_state == 2:
                return 2 * state.quantity + self.quantity
            elif state.cycle_state == 3:
                return state.quantity + self.quantity

        state = BuydownState.objects.get(id=1)
        last = self.get_last()
        buydown_valid = not state.is_activate or self.balance_1 > get_valid_quantity(state)
        return self.get_should_sell() <= last < self.get_current_ohlcv()[2] and buydown_valid

    def is_buy_valid(self):
        last = self.get_last()
        return self.get_should_buy() >= last > self.get_current_ohlcv()[3] and self.balance_2[
            'free'] >= self.quantity * 1.004

    #------------------------------------------------------------------------------------------------------------------
    def cycle_b_buy_getstuck(self):
        order_b = self.binance.fetch_balance(id=self.cycle_b.order_id, symbol=self.symbols)
        status_b = order_b['status']
        side_b = order_b['side']
        if status_b == 'open' and side_b == 'buy':
            return True
        else:
            return False

    def cycle_b_sell_getstuck(self):
        order_b = self.binance.fetch_balance(id=self.cycle_b.order_id, symbol=self.symbols)
        status_b = order_b['status']
        side_b = order_b['side']
        if status_b == 'open' and side_b == 'sell':
            return True
        else:
            return False
    #------------------------------------------------------------------------------------------------------------------

    def do_cycle_a(self):
        try:
            if self.is_sell_valid():
                buy_stuck = self.cycle_b_buy_getstuck()
                if buy_stuck == True:
                    price = self.get_last() * 1.015
                    order = self.binance.create_order(amount=self.quantity, symbol=self.symbols, type='limit',
                                                      side='sell',
                                                      price=price)
                    self.cycle_state = 2
                    self.cycle_a = Order.objects.create(
                        order_id=order['id'],
                        symbol=self.symbols,
                        amount=self.quantity,
                        price=price,
                        timestamp=self.get_current_ohlcv()[0],
                        side='sell',
                        cycle_type='A',
                    )
                    return

                else:
                    order = self.binance.create_order(amount=self.quantity, symbol=self.symbols, type='limit',
                                                      side='sell',
                                                      price=self.get_last())
                    self.cycle_state = 2
                    self.cycle_a = Order.objects.create(
                        order_id=order['id'],
                        symbol=self.symbols,
                        amount=self.quantity,
                        price=self.get_last(),
                        timestamp=self.get_current_ohlcv()[0],
                        side='sell',
                        cycle_type='A',
                    )
                    return
            elif self.is_buy_valid():
                sell_stuck = self.order_b_sell_getstuck
                if sell_stuck == True:
                    quantity = self.quantity * 1.004
                    price = self.get_last() * 0.985
                    order = self.binance.create_order(amount=quantity, symbol=self.symbols, type='limit',
                                                      side='buy',
                                                      price=price)
                    self.cycle_state = 2
                    self.cycle_a = Order.objects.create(
                        order_id=order['id'],
                        symbol=self.symbols,
                        amount=quantity,
                        price=price,
                        timestamp=self.get_current_ohlcv()[0],
                        side='buy',
                        cycle_type='A',
                    )
                    return

                else:
                    quantity = self.quantity * 1.004
                    order = self.binance.create_order(amount=quantity, symbol=self.symbols, type='limit',
                                                      side='buy',
                                                      price=self.get_last())
                    self.cycle_state = 2
                    self.cycle_a = Order.objects.create(
                        order_id=order['id'],
                        symbol=self.symbols,
                        amount=quantity,
                        price=self.get_last(),
                        timestamp=self.get_current_ohlcv()[0],
                        side='buy',
                        cycle_type='A',
                    )
                    return
        except Exception as e:
            log.info(e)
            log.info('cycle a failed')
    #------------------------------------------------------------------------------------------------------------------
    def do_cycle_b(self):
        try:
            order_a = self.binance.fetch_order(id=self.cycle_a.order_id, symbol=self.symbols)
            side_a = order_a['side']
            if order_a['status'] == 'closed' and not self.cycle_b:
                filled = order_a['filled'] if side_a == 'buy' else order_a['filled'] * 1.004
                price = order_a['price'] * (1 + self.benefit) if side_a == 'buy' else order_a['price'] * (
                        1 - self.benefit)
                side = 'sell' if side_a == 'buy' else 'buy'
                order_b = self.binance.create_order(symbol=self.symbols, price=price, amount=filled, side=side,
                                                    type='limit')
                self.cycle_b = Order.objects.create(
                    order_id=order_b['id'],
                    symbol=self.symbols,
                    amount=filled,
                    price=price,
                    timestamp=self.get_current_ohlcv()[0],
                    side=side,
                    related_order=self.cycle_a,
                    cycle_type='B',
                )
            elif self.cycle_b:
                order = self.binance.fetch_order(id=self.cycle_b.order_id, symbol=self.symbols)
                if order['status'] == 'closed':
                    self.clean_state()

        except Exception as e:
            log.info(e)
            log.info('cycle b failed')

    def do_cycle(self):
        state = CycleState.objects.get(id=1)
        if not state.is_activate:
            self.clean_state()
            return
        elif state.is_activate and not self.is_activate:
            self.clean_state()
            self.is_activate = True
            log.info('cycle is activated')
            self.fetch_ohlcv()
            self.print_info()

        self.fetch_ticker()
        self.fetch_balance()
        self.fetch_ohlcv()

        if self.cycle_state == 1 and self.is_cycle_a_valid():
            self.do_cycle_a()
            return
        elif self.cycle_state == 2:
            self.do_cycle_b()
            return

    def print_info(self):
        log.info(self.get_current_ohlcv())
