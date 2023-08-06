import contextlib
import logging
import time
from datetime import datetime

import pandas as pd
from binance.spot import Spot

from Exchanges.BaseExchange import BaseExchange
from Utils import BinanceHelpers, DataHelpers
from binance_f import RequestClient
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.model.balance import Balance


def is_symbol_status_valid(symbol_name, symbol_datas, futures=False):
    for symbol_data in symbol_datas:
        return bool(
            (
                futures
                and symbol_data.symbol == symbol_name
                and symbol_data.status == "TRADING"
                or not futures
                and symbol_data["symbol"] == symbol_name
                and symbol_data["status"] == "TRADING"
            )
        )


def is_order_data_valid(order: DataHelpers.OrderData):
    check_spot_order_type(order)
    check_order_side(order)
    check_spot_order_response_type(order)
    check_spot_order_time_in_force(order)

    if order.order_type == "LIMIT":
        check_limit_order_data_validity(order)

    elif order.order_type == "MARKET":
        check_spot_market_order_data_validity(order)

    elif order.order_type in ["STOP_LOSS", "TAKE_PROFIT"]:
        check_spot_stop_market_data_validity(order)

    elif order.order_type in ["STOP_LOSS_LIMIT", "TAKE_PROFIT_LIMIT"]:
        check_spot_stop_limit_order_data_validity(order)

    elif order.order_type == "LIMIT_MAKER":
        check_spot_limit_maker_order_data_validity(order)

    return False


def check_spot_limit_maker_order_data_validity(order):
    if order.quantity is None or order.price is None:
        raise ValueError("For LIMIT_MAKER order quantity and price must be specified.")


def check_spot_stop_limit_order_data_validity(order):
    if (
        order.time_in_force is None
        or order.quantity is None
        or order.price is None
        or order.stop_price is None
    ):
        raise ValueError(
            "For STOP_LOSS_LIMIT or TAKE_PROFIT_LIMIT orders timeInForce, quantity, price and stopPrice must be specified."
        )


def check_spot_stop_market_data_validity(order):
    if order.quantity is None or order.stop_price is None:
        raise ValueError(
            "For STOP_LOSS or TAKE_PROFIT orders quantity and stopPrice must be specified."
        )


def check_spot_market_order_data_validity(order):
    if order.quantity is None and order.quote_order_qty is None:
        raise ValueError(
            "For MARKET order either quantity or quoteOrderQty must be specified."
        )


def check_limit_order_data_validity(order):
    if order.time_in_force is None or order.quantity is None or order.price is None:
        raise ValueError(
            "For LIMIT order timeInForce, quantity and price must be specified"
        )


def check_spot_order_time_in_force(order):
    if order.time_in_force not in [None, "GTC", "IOC", "FOK"]:
        raise ValueError("Order time in force is not valid.")


def check_spot_order_response_type(order):
    if order.new_order_resp_type not in [None, "ACK", "RESULT", "FULL"]:
        raise ValueError("Order response type is not valid.")


def check_spot_order_type(order):
    if order.order_type not in BinanceExchange.spot_order_types:
        raise ValueError("Order type is not valid.")


def is_futures_order_data_valid(order: DataHelpers.FuturesOrderData):
    check_order_side(order)
    check_futures_order_type(order)
    check_futures_order_side(order)
    check_futures_order_time_in_force(order)
    check_futures_order_working_type(order)
    check_futures_order_response_type(order)
    check_futures_order_close_position(order)
    check_futures_order_callback_rate(order)
    check_futures_order_price_protect(order)
    check_simultaneous_close_position_and_quantity(order)
    check_futures_order_reduce_only(order)
    check_simultaneous_close_position_and_reduce_only(order)

    if order.orderType == "LIMIT":
        check_limit_order_data_validity(order)

    elif order.orderType == "MARKET":
        check_futures_market_order_data_validity(order)

    elif order.orderType in ["STOP", "TAKE_PROFIT"]:
        check_futures_stop_limit_order_data_validity(order)

    elif order.orderType in ["STOP_MARKET", "TAKE_PROFIT_MARKET"]:
        check_futures_stop_market_order_data_validity(order)

    elif order.orderType == "TRAILING_STOP_MARKET":
        check_futures_trailing_order_data_validity(order)


def check_futures_trailing_order_data_validity(order):
    if order.callback_rate is None:
        raise ValueError(
            "For futures TRAILING_STOP_MARKET orders callbackRate must be specified."
        )


def check_futures_stop_market_order_data_validity(order):
    if order.stop_price is None:
        raise ValueError(
            "For futures STOP_MARKET and TAKE_PROFIT_MARKET orders stopPrice must be specified"
        )


def check_futures_stop_limit_order_data_validity(order):
    if order.quantity is None or order.price is None or order.stop_price is None:
        raise ValueError(
            "For futures STOP or TAKE_PROFIT order quantity, price and stopPrice must be specified."
        )


def check_futures_market_order_data_validity(order):
    if order.quantity is None:
        raise ValueError("For MARKET order quantity must be specified.")


def check_simultaneous_close_position_and_reduce_only(order):
    if order.close_position is True and order.reduce_only is True:
        raise ValueError("Can't set both closePosition and reduceOnly to True.")


def check_futures_order_reduce_only(order):
    if order.reduce_only not in [None, True, False]:
        raise ValueError("Futures order reduceOnly is not valid.")


def check_simultaneous_close_position_and_quantity(order):
    if order.close_position is True and order.quantity is not None:
        raise ValueError("Must not specify quantity if closePosition is True.")


def check_futures_order_price_protect(order):
    if order.price_protect not in [None, True, False]:
        raise ValueError("Futures order priceProtect is not valid.")


def check_futures_order_callback_rate(order):
    if order.callback_rate is not None and not (0.1 <= order.callback_rate <= 5):
        raise ValueError("Futures order callbackRate is not valid.")


def check_futures_order_close_position(order):
    if order.close_position not in [None, True, False]:
        raise ValueError("Futures order closePosition is not valid.")


def check_futures_order_response_type(order):
    if order.new_order_resp_type not in [None, "ACK", "RESULT"]:
        raise ValueError("Futures order newOrderRespType is not valid.")


def check_futures_order_working_type(order):
    if order.working_type not in [None, "MARK_PRICE", "CONTRACT_PRICE"]:
        raise ValueError("Futures order workingType is not valid.")


def check_futures_order_time_in_force(order):
    if order.time_in_force not in [None, "GTC", "IOC", "FOK", "GTX"]:
        raise ValueError("Futures order timeInForce is not valid.")


def check_futures_order_side(order):
    if order.position_side not in [None, "BOTH", "LONG", "SHORT"]:
        raise ValueError("Futures order side is not valid")


def check_futures_order_type(order):
    if order.order_type not in BinanceExchange.futures_order_types:
        raise ValueError("Futures order type is not valid.")


def check_order_side(order):
    if order.side not in ["BUY", "SELL"]:
        raise ValueError("Order side can only be 'BUY' or 'SELL'")


class BinanceExchange(BaseExchange):
    time_intervals = [
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "4h",
        "6h",
        "8h",
        "12h",
        "1d",
        "3d",
        "1w",
        "1M",
    ]

    time_indexes_in_candle_data = [0, 6]
    desired_candle_data_indexes = [0, 1, 2, 3, 4, 5, 6, 8]

    spot_order_types = [
        "LIMIT",
        "MARKET",
        "STOP_LOSS",
        "STOP_LOSS_LIMIT",
        "TAKE_PROFIT",
        "TAKE_PROFIT_LIMIT",
        "LIMIT_MAKER",
    ]

    futures_order_types = [
        "LIMIT",
        "MARKET",
        "STOP",
        "STOP_MARKET",
        "TAKE_PROFIT",
        "TAKE_PROFIT_MARKET",
        "TRAILING_STOP_MARKET",
    ]

    def __init__(self, credentials, sandbox=False, unified_in_outs=True):
        self.credentials = credentials
        self.sandbox = sandbox
        self.unified_in_outs = unified_in_outs

        if sandbox:
            self.client = Spot(
                credentials["spot"]["key"],
                credentials["spot"]["secret"],
                base_url="https://testnet.binance.vision",
            )
            self.futures_client = RequestClient(
                api_key=credentials["futures"]["key"],
                secret_key=credentials["futures"]["secret"],
                url="https://testnet.binancefuture.com",
            )
        else:
            self.client = Spot(
                credentials["spot"]["key"], credentials["spot"]["secret"]
            )
            self.futures_client = RequestClient(
                api_key=credentials["futures"]["key"],
                secret_key=credentials["futures"]["secret"],
                url="https://fapi.binance.com",
            )

        self.sub_future_client = None

    def get_balance(self, asset="", futures=False):
        if not futures:
            try:
                balances = self.client.account()["balances"]
            except Exception as e:
                print(e)
                return None
            if asset == "" or asset is None:
                return balances
            return next(
                (balance for balance in balances if balance["asset"] == asset),
                None,
            )
        else:
            balances = [
                balance.toDict() for balance in self.futures_client.get_balance()
            ]
            if asset == "" or asset is None:
                return balances
            for balance in balances:
                if balance["asset"] == asset:
                    return balance
            return Balance.makeFreeBalance(asset)

    def symbol_account_trade_history(
        self, symbol, futures=False, from_id=None, limit=None
    ):
        try:
            if not futures:
                return self.client.my_trades(symbol, fromId=from_id, limit=limit)
            else:
                return [
                    trade.toDict()
                    for trade in self.futures_client.get_account_trades(
                        symbol=symbol, fromId=from_id, limit=limit
                    )
                ]
        except Exception as e:
            print(e)
            return None

    def test_spot_order(self, order_data):
        # sourcery skip: no-conditionals-in-tests
        if not is_order_data_valid(order_data):
            raise ValueError("Incomplete data provided.")

        order_data.set_timestamp()
        params = BinanceHelpers.get_spot_order_as_dict(order_data)

        return self.client.new_order_test(**params)

    def make_spot_order(self, order_data):
        params = BinanceHelpers.get_spot_order_as_dict(order_data)

        response = self.client.new_order(**params)
        logging.info(response)
        return response

    def create_and_test_spot_order(
        self,
        symbol,
        side,
        order_type,
        quantity=None,
        price=None,
        time_in_force=None,
        stop_price=None,
        iceberg_qty=None,
        new_order_resp_type=None,
        new_client_order_id=None,
        extra_params=None,
    ):
        curr_order = DataHelpers.set_spot_order_data(
            iceberg_qty,
            new_client_order_id,
            new_order_resp_type,
            order_type,
            price,
            quantity,
            side,
            stop_price,
            symbol,
            time_in_force,
            extra_params,
        )

        self.test_spot_order(curr_order)

        return curr_order

    def get_symbol_orders(
        self,
        symbol,
        futures=False,
        order_id=None,
        start_time=None,
        end_time=None,
        limit=None,
    ):
        if not futures:
            return self.client.get_orders(
                symbol=symbol,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                timestamp=time.time(),
            )
        else:
            return [
                order.toDict()
                for order in self.futures_client.get_all_orders(
                    symbol,
                    orderId=order_id,
                    startTime=start_time,
                    endTime=end_time,
                    limit=limit,
                )
            ]

    def get_open_orders(self, symbol, futures=False):
        try:
            if not futures:
                return self.client.get_open_orders(symbol, timestamp=time.time())
            else:
                return [
                    order.toDict()
                    for order in self.futures_client.get_open_orders(symbol=symbol)
                ]
        except Exception as e:
            print(e)
            return None

    def cancel_all_symbol_open_orders(self, symbol, futures=False):
        if not futures:
            open_orders = self.get_open_orders(symbol)
            if len(open_orders) == 0:
                return []
            else:
                return self.client.cancel_open_orders(symbol, timestamp=time.time())
        else:
            open_orders = self.get_open_orders(symbol, futures=True)

            if len(open_orders) == 0:
                return []
            order_ids = [order["orderId"] for order in open_orders]

            return [
                res.toDict()
                for res in self.futures_client.cancel_list_orders(
                    symbol=symbol, orderIdList=order_ids
                )
            ]

    def cancel_order(self, symbol, order_id=None, local_order_id=None, futures=False):
        error_message = (
            "Specify either order Id in the exchange or local Id sent with the order"
        )
        if futures:
            if order_id is not None:
                return self.futures_client.cancel_order(
                    symbol, orderId=order_id
                ).toDict()
            elif local_order_id is not None:
                return self.futures_client.cancel_order(
                    symbol, origClientOrderId=local_order_id
                ).toDict()
            else:
                raise ValueError(error_message)

        elif order_id is not None:
            return self.client.cancel_order(
                symbol, orderId=order_id, timestamp=time.time()
            )
        elif local_order_id is not None:
            return self.client.cancel_order(
                symbol, origClientOrderId=local_order_id, timestamp=time.time()
            )
        else:
            raise ValueError(error_message)

    def get_order(self, symbol, order_id=None, local_order_id=None, futures=False):
        error_message = (
            "Specify either order Id in the exchange or local Id sent with the order"
        )
        if futures:
            if order_id is not None:
                return self.futures_client.get_order(symbol, orderId=order_id).toDict()
            elif local_order_id is not None:
                return self.futures_client.get_order(
                    symbol, origClientOrderId=local_order_id
                ).toDict()
            else:
                raise ValueError(error_message)

        elif order_id is not None:
            return self.client.get_order(
                symbol, orderId=order_id, timestamp=time.time()
            )
        elif local_order_id is not None:
            return self.client.get_order(
                symbol, origClientOrderId=local_order_id, timestamp=time.time()
            )
        else:
            raise ValueError(error_message)

    def get_trading_fees(self, symbol=None, futures=False):
        if symbol:
            return self.client.trade_fee(symbol=symbol)[0]
        else:
            return self.client.trade_fee(symbol=symbol)

    def get_symbol_ticker_price(self, symbol, futures=False):
        if futures:
            return self.futures_client.get_symbol_price_ticker(symbol=symbol)[0].price
        else:
            return float(self.client.ticker_price(symbol)["price"])

    def get_symbol_klines(
        self,
        symbol,
        interval,
        start_time=None,
        end_time=None,
        limit=None,
        futures=False,
        blvtnav=False,
        convert_date_time=False,
        do_clean=False,
        to_clean_dataframe=False,
    ):
        if interval not in BinanceExchange.time_intervals:
            raise ValueError("Time interval is not valid.")

        if futures:
            data = self._get_futures_symbol_klines(
                blvtnav, end_time, interval, limit, start_time, symbol
            )
        else:
            data = self._get_spot_symbol_klines(
                end_time, interval, limit, start_time, symbol
            )

        if convert_date_time or to_clean_dataframe:
            BinanceHelpers.klines_convert_date(data, self.time_indexes_in_candle_data)

        if not do_clean and not to_clean_dataframe:
            return data

        final_data_array = BinanceHelpers.get_klines_desired_only_cols(
            data, self.desired_candle_data_indexes
        )

        if to_clean_dataframe:
            return BinanceHelpers.klines_convert_to_pandas(final_data_array)
        return final_data_array

    def _get_spot_symbol_klines(self, end_time, interval, limit, start_time, symbol):
        data = self.client.klines(
            symbol, interval, startTime=start_time, endTime=end_time, limit=limit
        )
        for datum in data:
            for idx in range(len(datum)):
                if idx in BinanceExchange.time_indexes_in_candle_data:
                    continue
                datum[idx] = float(datum[idx])
        return data

    def _get_futures_symbol_klines(
        self, blvtnav, end_time, interval, limit, start_time, symbol
    ):
        if blvtnav:
            candles = self.futures_client.get_blvt_nav_candlestick_data(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            )
        else:
            candles = self.futures_client.get_candlestick_data(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            )
        return [candle.toArray() for candle in candles]

    def get_exchange_time(self, futures=False):
        try:
            if not futures:
                return self.client.time()["serverTime"]
            else:
                return self.futures_client.get_servertime()
        except Exception as e:
            print(e)
            return None

    def get_symbol_24h_ticker(self, symbol):
        try:
            return self.client.ticker_24hr(symbol)
        except Exception as e:
            print(e)
            return None

    def test_futures_order(self, futures_order_data):
        # sourcery skip: no-conditionals-in-tests
        if not is_futures_order_data_valid(futures_order_data):
            raise ValueError("Incomplete data provided.")
        return futures_order_data

    def make_futures_order(self, futures_order_data):
        params = BinanceHelpers.get_futures_order_as_dict(futures_order_data)

        response = self.futures_client.post_order(**params)
        return response.toDict()

    def create_and_test_futures_order(
        self,
        symbol,
        side,
        order_type,
        position_side=None,
        time_in_force=None,
        quantity=None,
        reduce_only=None,
        price=None,
        new_client_order_id=None,
        stop_price=None,
        close_position=None,
        activation_price=None,
        callback_rate=None,
        working_type=None,
        price_protect=None,
        new_order_resp_type=None,
        recv_window=None,
        extra_params=None,
        quote_quantity=None,
    ):
        curr_order = DataHelpers.set_futures_order_data(
            activation_price,
            callback_rate,
            close_position,
            extra_params,
            new_client_order_id,
            new_order_resp_type,
            order_type,
            position_side,
            price,
            price_protect,
            quantity,
            reduce_only,
            side,
            stop_price,
            symbol,
            time_in_force,
            working_type,
            quote_quantity,
        )

        self.test_futures_order(curr_order)

        return curr_order

    def make_batch_futures_order(self, futures_order_datas):
        batch_orders = BinanceHelpers.make_batch_order_data(futures_order_datas)

        order_results = self.futures_client.post_batch_order(batch_orders)

        return [order.toDict() for order in order_results]

    def cancel_all_symbol_futures_orders_with_countdown(self, symbol, countdown_time):
        return self.futures_client.auto_cancel_all_orders(symbol, countdown_time)

    def change_initial_leverage(self, symbol, leverage):
        return self.futures_client.change_initial_leverage(
            symbol=symbol, leverage=leverage
        ).toDict()["leverage"]

    def change_margin_type(self, symbol, margin_type, params=None):
        if margin_type not in ["ISOLATED", "CROSSED"]:
            raise ValueError("Margin type specified is not acceptable")
        with contextlib.suppress(BinanceApiException):
            result = self.futures_client.change_margin_type(
                symbol=symbol, marginType=margin_type
            )
            return result["code"] == 200

    def change_position_margin(self, symbol, amount):
        add_or_sub = 1 if amount >= 0 else 2
        result = self.futures_client.change_position_margin(
            symbol=symbol, amount=amount, type=add_or_sub
        )
        return result["code"] == 200

    def get_position(self):
        return self.futures_client.get_position()

    def spot_best_bid_asks(self, symbol):
        return self.client.book_ticker(symbol=symbol)

    def get_symbol_order_book(self, symbol, limit=None, futures=False):
        if not futures:
            return (
                self.client.depth(symbol)
                if limit is None
                else self.client.depth(symbol, limit=limit)
            )
        if limit is None:
            return self.futures_client.get_order_book(symbol=symbol).toDict()
        else:
            return self.futures_client.get_order_book(
                symbol=symbol, limit=limit
            ).toDict()

    def get_symbol_recent_trades(self, symbol, limit=None, futures=False):
        if limit is not None:
            if limit > 1000:
                limit = 1000
            elif limit < 1:
                limit = 1
        if not futures:
            return (
                pd.DataFrame(self.client.trades(symbol=symbol))
                if limit is None
                else pd.DataFrame(self.client.trades(symbol, limit=limit))
            )
        if limit is None:
            return pd.DataFrame(
                self.futures_client.get_recent_trades_list(symbol=symbol)
            )
        else:
            return pd.DataFrame(
                self.futures_client.get_recent_trades_list(symbol=symbol, limit=limit)
            )

    def get_position_info(self, symbol=None):
        return self.futures_client.get_position_v2(symbol)

    def get_symbol_min_trade(self, symbol, futures=False):
        ticker_price = self.get_symbol_ticker_price(symbol, futures=futures)

        if futures:
            exchange_info = self.futures_client.get_exchange_information()

            for sym in exchange_info.symbols:
                if sym.symbol == symbol:
                    symbol_filters = sym.filters
                    return BinanceHelpers.extract_symbol_info_from_filters(
                        symbol_filters, ticker_price
                    )
        else:
            exchange_info = self.client.exchange_info()

            for sym in exchange_info["symbols"]:
                if sym["symbol"] == symbol:
                    symbol_filters = sym["filters"]
                    return BinanceHelpers.extract_symbol_info_from_filters(
                        symbol_filters, ticker_price
                    )
        return None

    def get_income_history(
        self, symbol, income_type=None, start_time=None, end_time=None, limit=None
    ):
        return self.futures_client.get_income_history(
            symbol=symbol,
            incomeType=income_type,
            startTime=start_time,
            endTime=end_time,
            limit=limit,
        )

    def make_sl_tp_limit_futures_order(
        self,
        symbol,
        order_side,
        quantity=None,
        quote_quantity=None,
        enter_price=None,
        take_profit=None,
        stop_loss=None,
        leverage=None,
        margin_type=None,
    ):
        symbol_info = self.get_symbol_min_trade(symbol=symbol, futures=True)

        quantity = DataHelpers.get_quantity(
            enter_price, quantity, quote_quantity, symbol_info["precisionStep"]
        )
        self._set_leverage(leverage, symbol)
        self.change_margin_type(symbol, margin_type)
        tp_sl_order_side = "BUY" if order_side.upper() == "SELL" else "SELL"

        main_order, stop_loss_order, take_profit_order = self.create_sl_tp_limit_orders(
            enter_price,
            order_side,
            quantity,
            stop_loss,
            symbol,
            take_profit,
            tp_sl_order_side,
        )

        ordering_result = self.make_batch_futures_order(
            [main_order, stop_loss_order, take_profit_order]
        )

        return DataHelpers.get_tp_sl_limit_order_ids(ordering_result)

    def create_sl_tp_limit_orders(
        self,
        enter_price,
        order_side,
        quantity,
        stop_loss,
        symbol,
        take_profit,
        tp_sl_order_side,
    ):
        main_order = self.create_and_test_futures_order(
            symbol,
            order_side.upper(),
            "LIMIT",
            quantity=str(quantity),
            price=str(enter_price),
            time_in_force="GTC",
        )
        stop_loss_order = self.create_and_test_futures_order(
            symbol,
            tp_sl_order_side,
            "STOP_MARKET",
            stop_price=str(stop_loss),
            close_position=True,
            price_protect=True,
            working_type="MARK_PRICE",
            time_in_force="GTC",
        )
        take_profit_order = self.create_and_test_futures_order(
            symbol,
            tp_sl_order_side,
            "TAKE_PROFIT_MARKET",
            stop_price=str(take_profit),
            close_position=True,
            price_protect=True,
            working_type="MARK_PRICE",
            time_in_force="GTC",
        )
        return main_order, stop_loss_order, take_profit_order

    def make_sl_tp_market_futures_order(
        self,
        symbol,
        order_side,
        quantity=None,
        quote_quantity=None,
        take_profit=None,
        stop_loss=None,
        leverage=None,
        margin_type=None,
    ):
        symbol_info = self.get_symbol_min_trade(symbol=symbol, futures=True)
        market_price = self.get_symbol_ticker_price(symbol=symbol, futures=True)

        quantity = DataHelpers.get_quantity(
            market_price, quantity, quote_quantity, symbol_info["precisionStep"]
        )
        self._set_leverage(leverage, symbol)
        self.change_margin_type(symbol, margin_type)
        tp_sl_order_side = "BUY" if order_side.upper() == "SELL" else "SELL"

        has_sl, has_tp, orders_list = self.create_sl_tp_market_orders(
            order_side, quantity, stop_loss, symbol, take_profit, tp_sl_order_side
        )

        ordering_result = self.make_batch_futures_order(orders_list)

        return DataHelpers.get_tp_sl_market_order_ids(
            ordering_result, has_sl=has_sl, has_tp=has_tp
        )

    def create_sl_tp_market_orders(
        self, order_side, quantity, stop_loss, symbol, take_profit, tp_sl_order_side
    ):
        main_order = self.create_and_test_futures_order(
            symbol, order_side.upper(), "MARKET", quantity=str(quantity)
        )
        orders_list = [main_order]
        has_tp = False
        has_sl = False
        if stop_loss is not None:
            stop_loss_order = self.create_and_test_futures_order(
                symbol,
                tp_sl_order_side,
                "STOP_MARKET",
                stop_price=str(stop_loss),
                close_position=True,
                price_protect=True,
                working_type="MARK_PRICE",
                time_in_force="GTC",
            )
            orders_list.append(stop_loss_order)
            has_sl = True
        if take_profit is not None:
            take_profit_order = self.create_and_test_futures_order(
                symbol,
                tp_sl_order_side,
                "TAKE_PROFIT_MARKET",
                stop_price=str(take_profit),
                close_position=True,
                price_protect=True,
                working_type="MARK_PRICE",
                time_in_force="GTC",
            )
            orders_list.append(take_profit_order)
            has_tp = True
        return has_sl, has_tp, orders_list

    def _set_leverage(self, leverage, symbol):
        set_leverage_result = self.change_initial_leverage(symbol, leverage)
        print("Leverage changed.")
        if (
            isinstance(set_leverage_result, dict)
            and set_leverage_result["leverage"] != leverage
            or not isinstance(set_leverage_result, dict)
            and isinstance(set_leverage_result, float)
            and set_leverage_result != leverage
            or not isinstance(set_leverage_result, dict)
            and not isinstance(set_leverage_result, float)
        ):
            raise ConnectionError("Could not change leverage.")

    def get_symbol_list(self, futures=False):
        if futures:
            return [
                symbolInfo.symbol
                for symbolInfo in self.futures_client.get_exchange_information().symbols
                if symbolInfo.status == "TRADING"
            ]

    def get_symbol_24h_changes(self, futures=False):
        symbol_datas = []
        if futures:
            symbol_status = self.futures_client.get_exchange_information().symbols
            symbol_datas.extend(
                (symbolInfo.symbol, symbolInfo.priceChangePercent)
                for symbolInfo in self.futures_client.get_ticker_price_change_statistics()
                if is_symbol_status_valid(
                    symbolInfo.symbol, symbol_status, futures=True
                )
            )
        else:
            symbol_status = self.client.exchange_info()["symbols"]
            symbol_datas.extend(
                (symbolInfo["symbol"], float(symbolInfo["priceChangePercent"]))
                for symbolInfo in self.client.ticker_24hr()
                if is_symbol_status_valid(
                    symbolInfo["symbol"], symbol_status, futures=False
                )
            )
        return sorted(symbol_datas, key=lambda x: x[1], reverse=True)

    def get_latest_symbol_names(self, num_of_symbols=None, futures=False):
        symbol_datas = []
        if not futures:
            raise NotImplementedError("Only available for futures market.")

        for symbolInfo in self.futures_client.get_exchange_information().symbols:
            symbol_datas.append(
                (
                    symbolInfo.symbol,
                    datetime.fromtimestamp(float(symbolInfo.onboardDate) / 1000),
                )
            )
            symbol_datas.sort(key=lambda x: x[1], reverse=True)
        if num_of_symbols is not None and num_of_symbols > len(symbol_datas):
            num_of_symbols = len(symbol_datas)
        return symbol_datas[:num_of_symbols]

    def get_long_short_ratios(
        self, symbol, period, limit=None, start_time=None, end_time=None
    ):
        if limit is None:
            limit = 30
        top_long_short_accounts = self.futures_client.get_top_long_short_accounts(
            symbol=symbol,
            period=period,
            startTime=start_time,
            endTime=end_time,
            limit=limit,
        )
        top_long_short_positions = self.futures_client.get_top_long_short_positions(
            symbol=symbol,
            period=period,
            startTime=start_time,
            endTime=end_time,
            limit=limit,
        )
        long_short_ratio = self.futures_client.get_global_long_short_accounts(
            symbol=symbol,
            period=period,
            startTime=start_time,
            endTime=end_time,
            limit=limit,
        )

        return {
            "topLongShortAccounts": top_long_short_accounts,
            "topLongShortPositions": top_long_short_positions,
            "longShortRatio": long_short_ratio,
        }

    def get_deposit_address(self, coin, network=None):
        return self.client.deposit_address(coin=coin, network=network)
