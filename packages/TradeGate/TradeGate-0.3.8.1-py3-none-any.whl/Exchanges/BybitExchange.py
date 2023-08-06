import logging
import warnings
from datetime import datetime

from pybit.unified_trading import HTTP

from Exchanges.BaseExchange import BaseExchange
from Utils import DataHelpers, BybitHelpers


def is_spot_order_data_valid(order_data: DataHelpers.OrderData):
    check_spot_order_mandatory_fields(order_data)

    check_spot_order_type(order_data)

    check_spot_order_side(order_data)

    check_spot_order_time_in_force(order_data)

    check_spot_order_limit_price(order_data)


def check_spot_order_limit_price(order_data):
    if order_data.order_type in ["LIMIT", "LIMIT_MAKER"] and order_data.price is None:
        raise ValueError("Price must be specified for limit orders.")


def check_spot_order_time_in_force(order_data):
    if order_data.time_in_force not in BybitExchange.spot_time_in_forces:
        raise ValueError(
            "Time-in-force not correctly specified. Available time-in-force for spot market: {}".format(
                BybitExchange.spot_time_in_forces
            )
        )


def check_spot_order_mandatory_fields(order_data):
    if (
        order_data.symbol is None
        or order_data.quantity is None
        or order_data.side is None
        or order_data.order_type is None
    ):
        raise ValueError("Missing mandatory fields.")


def check_spot_order_side(order_data):
    if order_data.side not in ["BUY", "SELL"]:
        raise ValueError("Order side can only be 'BUY' or 'SELL'")


def check_spot_order_type(order_data):
    if order_data.order_type not in BybitExchange.spot_order_types:
        raise ValueError(
            "Order type not correctly specified. Available order types for spot market: {}".format(
                BybitExchange.spot_order_types
            )
        )


def is_futures_order_data_valid(order_data: DataHelpers.FuturesOrderData):
    check_futures_order_symbol(order_data)
    check_futures_order_quantity(order_data)
    check_futures_order_side(order_data)
    check_futures_order_type(order_data)
    check_futures_order_time_in_force(order_data)
    check_futures_order_close_position(order_data)
    check_futures_order_reduce_only(order_data)

    if order_data.orderType.startswith("STOP"):
        check_futures_stop_order_datas(order_data)

    if "LIMIT" in order_data.orderType and order_data.price is None:
        raise ValueError("Specify 'price' for limit orders.")

    if order_data.extra_params is not None:
        check_futures_order_trigger_by(order_data)
        check_futures_order_tp_trigger_by(order_data)
        check_futures_order_sl_trigger_by(order_data)
        check_futures_order_position_idx(order_data)


def check_futures_order_position_idx(order_data):
    if "positionIdx" in order_data.extra_params.keys() and order_data.extra_params[
        "positionIdx"
    ] not in [0, 1, 2]:
        raise ValueError("'positionIdx' was not correctly specified.")


def check_futures_order_sl_trigger_by(order_data):
    if "slTriggerBy" in order_data.extra_params.keys() and order_data.extra_params[
        "slTriggerBy"
    ] not in ["LastPrice", "IndexPrice", "MarkPrice"]:
        raise ValueError("'slTriggerBy' was not correctly specified.")


def check_futures_order_tp_trigger_by(order_data):
    if "tpTriggerBy" in order_data.extra_params.keys() and order_data.extra_params[
        "tpTriggerBy"
    ] not in ["LastPrice", "IndexPrice", "MarkPrice"]:
        raise ValueError("'tpTriggerBy' was not correctly specified.")


def check_futures_order_trigger_by(order_data):
    if "triggerBy" in order_data.extra_params.keys() and order_data.extra_params[
        "tpTriggerBy"
    ] not in ["LastPrice", "IndexPrice", "MarkPrice"]:
        raise ValueError("'triggerBy' was not correctly specified.")


def check_futures_stop_order_datas(order_data):
    if order_data.extra_params is None:
        raise ValueError("Specify 'basePrice' in 'extraParams'")
    if "basePrice" not in order_data.extra_params.keys():
        raise ValueError("Specify 'basePrice' in 'extraParams'")
    if order_data.stop_price is None:
        raise ValueError("Specify 'stopPrice'.")


def check_futures_order_reduce_only(order_data):
    if order_data.reduce_only is None:
        raise ValueError("Specify reduceOnly.")


def check_futures_order_close_position(order_data):
    if order_data.close_position is None:
        raise ValueError("Specify closePosition.")


def check_futures_order_time_in_force(order_data):
    if order_data.time_in_force is None:
        raise ValueError("Specify timeInForce.")

    if (
        order_data.time_in_force not in BybitExchange.futures_time_in_forces.keys()
        and order_data.time_in_force
        not in BybitExchange.futures_time_in_forces.values()
    ):
        raise ValueError("'timeInForce' is not correct.")


def check_futures_order_type(order_data):
    if order_data.order_type is None:
        raise ValueError("Specify order type.")

    if order_data.order_type not in BybitExchange.futures_order_types:
        raise ValueError(
            "Bad order type specified. Available order types for futures: {}".format(
                BybitExchange.futures_order_types
            )
        )


def check_futures_order_side(order_data):
    if order_data.side is None:
        raise ValueError("Specify order side.")


def check_futures_order_quantity(order_data):
    if order_data.quantity is None:
        raise ValueError("Specify quantity.")


def check_futures_order_symbol(order_data):
    if order_data.symbol is None:
        raise ValueError("Specify symbol.")


class PyBitHTTP(HTTP):
    def __init__(
        self,
        testnet=False,
        api_key=None,
        api_secret=None,
    ):
        super().__init__(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret,
        )

    def query_history_order(self, **kwargs):
        if self.spot is True:
            suffix = "/spot/v1/history-orders"

            return self._submit_request(
                method="GET", path=self.endpoint + suffix, query=kwargs, auth=True
            )
        else:
            raise NotImplementedError("Not implemented for futures market.")

    def get_active_order_spot(self, **kwargs):
        if self.spot is True:
            suffix = "/spot/v1/order"

            return self._submit_request(
                method="GET", path=self.endpoint + suffix, query=kwargs, auth=True
            )
        else:
            raise NotImplementedError("Not implemented for futures market.")


class BybitExchange(BaseExchange):
    time_indexes_in_candle_data = [0, 6]
    desired_candle_data_indexes = [0, 1, 2, 3, 4, 5, 6, 8]

    spot_order_types = ["LIMIT", "MARKET", "LIMIT_MAKER"]
    spot_time_in_forces = ["GTC", "FOK", "IOC"]

    futures_order_types = ["MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"]
    futures_time_in_forces = {
        "GTC": "GoodTillCancel",
        "IOC": "ImmediateOrCancel",
        "FIK": "FillOrKill",
        "PO": "PostOnly",
    }

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
        "12h",
        "1d",
        "1w",
        "1M",
    ]

    def __init__(self, credentials, sandbox=False, unified_in_outs=True):
        self.api_key = credentials["spot"]["key"]
        self.secret = credentials["spot"]["secret"]
        self.sandbox = sandbox
        self.unified_in_outs = unified_in_outs

        if sandbox:
            self.spot_session = PyBitHTTP(
                testnet=True, api_key=self.api_key, api_secret=self.secret
            )
            self.futures_session = PyBitHTTP(
                testnet=True,
                api_key=self.api_key,
                api_secret=self.secret,
            )
        else:
            self.spot_session = PyBitHTTP(
                testnet=False, api_key=self.api_key, api_secret=self.secret
            )
            self.futures_session = PyBitHTTP(
                testnet=False, api_key=self.api_key, api_secret=self.secret
            )

    def get_balance(self, asset="", futures=False):
        if futures:
            return (
                BybitHelpers.get_balance_out(
                    self.futures_session.get_wallet_balance(accountType="CONTRACT")[
                        "result"
                    ],
                    futures=True,
                )
                if asset in [None, ""]
                else BybitHelpers.get_balance_out(
                    self.futures_session.get_wallet_balance(
                        accountType="CONTRACT", coin=asset
                    )["result"],
                    single=True,
                    futures=True,
                )
            )
        if asset in [None, ""]:
            return BybitHelpers.get_balance_out(
                self.spot_session.get_wallet_balance(accountType="SPOT")["result"][
                    "balances"
                ]
            )
        assets = self.spot_session.get_wallet_balance(accountType="SPOT")["result"][
            "balances"
        ]
        for coin in assets:
            if asset == coin["coin"]:
                return BybitHelpers.get_balance_out(coin, single=True)

        try:
            self.futures_session.get_wallet_balance(coin=asset)
            return BybitHelpers.make_dummy_balance(asset)
        except Exception as e:
            raise ValueError("Coin not found.") from e

    def symbol_account_trade_history(
        self, symbol, futures=False, from_id=None, limit=None
    ):
        if futures:
            trade_history = self.futures_session.user_trade_records(
                symbol=symbol, limit=limit, fromId=from_id
            )
            return BybitHelpers.get_my_trade_history_out(
                trade_history["result"]["data"], futures=True
            )
        else:
            trade_history = self.spot_session.user_trade_records(
                symbol=symbol, limit=limit, fromId=from_id
            )
            return BybitHelpers.get_my_trade_history_out(trade_history["result"])

    def test_spot_order(self, order_data: DataHelpers.OrderData):
        is_spot_order_data_valid(order_data)

        # sourcery skip: no-conditionals-in-tests
        if (
            order_data.iceberg_qty is not None
            or order_data.new_order_resp_type is not None
            or order_data.quote_order_qty is not None
            or order_data.recv_window is not None
            or order_data.stop_price is not None
        ):
            warnings.warn("Some of the given parameters have no use in ByBit exchange.")

        return order_data

    def make_spot_order(self, order_data):
        order_params = BybitHelpers.get_spot_order_as_dict(order_data)

        return BybitHelpers.get_make_spot_order_out(
            self.spot_session.place_active_order(**order_params)["result"]
        )

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
        if futures:
            history_list = []
            page_number = 1
            end_time_string = None
            start_time_string = None
            done = False

            while not done:
                history = self.futures_session.get_active_order(
                    symbol=symbol, page=page_number, limit=50
                )

                if start_time is not None:
                    start_time_string = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                if end_time is not None:
                    end_time_string = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

                for order in history["result"]["data"]:
                    if end_time is not None and end_time_string < order["create_time"]:
                        continue

                    if (
                        start_time is not None
                        and order["created_time"] < start_time_string
                    ):
                        done = True
                        break

                    history_list.append(order)

                if limit is not None and limit <= len(history_list):
                    done = True

                if len(history["result"]["data"]) < 50:
                    done = True

                page_number += 1

            return history_list
        else:
            history = self.spot_session.query_history_order(
                symbol=symbol,
                orderId=order_id,
                startTime=start_time,
                endtime=end_time,
                limit=limit,
            )
            return history["result"]

    def get_open_orders(self, symbol, futures=False):
        if futures:
            return self.get_futures_open_orders(symbol)
        else:
            return self.get_spot_open_orders(symbol)

    def get_spot_open_orders(self, symbol):
        open_orders = (
            self.spot_session.query_active_order()["result"]
            if symbol is None
            else self.spot_session.query_active_order(symbol=symbol)["result"]
        )
        return BybitHelpers.get_open_orders_out(open_orders)

    def get_futures_open_orders(self, symbol):
        open_active_orders = self.futures_session.query_active_order(symbol=symbol)
        open_orders = [
            BybitHelpers.futures_order_out(activeOrder)
            for activeOrder in open_active_orders["result"]
        ]
        open_conditional_orders = self.futures_session.query_conditional_order(
            symbol=symbol
        )
        open_orders.extend(
            BybitHelpers.futures_order_out(conditionalOrder, is_conditional=True)
            for conditionalOrder in open_conditional_orders["result"]
        )
        return open_orders

    def cancel_all_symbol_open_orders(self, symbol, futures=False):
        if futures:
            result = self.futures_session.cancel_all_active_orders(symbol=symbol)
            canceled_orders_ids = [result["result"]]
            result = self.futures_session.cancel_all_conditional_orders(symbol=symbol)
            canceled_orders_ids.append(result["result"])
        else:
            result = self.spot_session.batch_fast_cancel_active_order(
                symbol=symbol, orderTypes="LIMIT,LIMIT_MAKER,MARKET"
            )
            return result["result"]["success"]

    def cancel_order(self, symbol, order_id=None, local_order_id=None, futures=False):
        if futures:
            return self.cancel_futures_order(local_order_id, order_id, symbol)
        else:
            return self.cancel_spot_order(local_order_id, order_id)

    def cancel_spot_order(self, local_order_id, order_id):
        if order_id is not None:
            result = self.spot_session.cancel_active_order(orderId=order_id)
        elif local_order_id is not None:
            result = self.spot_session.cancel_active_order(orderLinkId=local_order_id)
        else:
            raise ValueError("Must specify either 'orderId' or 'localOrderId'")
        return result

    def cancel_futures_order(self, local_order_id, order_id, symbol):
        if order_id is not None:
            try:
                result = self.futures_session.cancel_active_order(
                    symbol=symbol, order_id=order_id
                )
            except Exception as e:
                try:
                    result = self.futures_session.cancel_conditional_order(
                        symbol=symbol, order_id=order_id
                    )
                except Exception as e:
                    raise RuntimeError(
                        "Problem in canceling order in bybit: {}".format(str(e))
                    ) from e
        elif local_order_id is not None:
            try:
                result = self.futures_session.cancel_active_order(
                    symbol=symbol, order_link_id=local_order_id
                )
            except Exception as e:
                try:
                    result = self.futures_session.cancel_conditional_order(
                        symbol=symbol, order_link_id=local_order_id
                    )
                except Exception as e:
                    raise RuntimeError(
                        "Problem in canceling order in bybit: {}".format(str(e))
                    ) from e
        else:
            raise ValueError("Must specify either 'orderId' or 'localOrderId'")
        return result

    def get_order(self, symbol, order_id=None, local_order_id=None, futures=False):
        if futures:
            order = self.get_futures_order(local_order_id, order_id, symbol)
            return BybitHelpers.futures_order_out(order["result"])
        else:
            order = self.get_spot_order(local_order_id, order_id)
            return BybitHelpers.get_order_out(order)

    def get_spot_order(self, local_order_id, order_id):
        if order_id is not None:
            try:
                order = self.spot_session.get_active_order_spot(orderId=order_id)[
                    "result"
                ]
            except Exception as e:
                raise RuntimeError("Problem in fetching order from bybit.") from e
        elif local_order_id is not None:
            try:
                order = self.spot_session.get_active_order_spot(
                    orderLinkId=local_order_id
                )["result"]
            except Exception as e:
                raise RuntimeError("Problem in fetching order from bybit.") from e
        else:
            raise ValueError(
                "Specify either order Id in the exchange or local Id sent with the order"
            )
        return order

    def get_futures_order(self, local_order_id, order_id, symbol):
        if order_id is not None:
            try:
                order = self.futures_session.query_active_order(
                    symbol=symbol, order_id=order_id
                )
            except Exception as e:
                try:
                    order = self.futures_session.query_conditional_order(
                        symbol=symbol, order_id=order_id
                    )
                except Exception as e:
                    raise RuntimeError(
                        "Problem in fetching order from bybit: {}".format(str(e))
                    ) from e
        elif local_order_id is not None:
            try:
                order = self.futures_session.query_active_order(
                    symbol=symbol, order_link_id=local_order_id
                )
            except Exception as e:
                try:
                    order = self.futures_session.query_conditional_order(
                        symbol=symbol, order_link_id=local_order_id
                    )
                except Exception as e:
                    raise RuntimeError(
                        "Problem in fetching order from bybit: {}".format(str(e))
                    ) from e
        else:
            raise ValueError(
                "Specify either order Id in the exchange or local Id sent with the order"
            )
        return order

    def get_trading_fees(self, futures=False):
        raise NotImplementedError()

    def get_symbol_ticker_price(self, symbol, futures=False):
        if futures:
            symbol_info = self.futures_session.latest_information_for_symbol(
                symbol=symbol
            )["result"]
            return float(symbol_info[0]["last_price"])
        else:
            symbol_info = self.spot_session.latest_information_for_symbol(symbol=symbol)
            return float(symbol_info["result"]["lastPrice"])

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
        if interval not in self.time_intervals:
            raise ValueError("Time interval is not valid.")

        if futures:
            data = self._get_futures_symbol_klines(interval, limit, start_time, symbol)
        else:
            data = self._get_spot_symbol_klines(
                end_time, interval, limit, start_time, symbol
            )

        if convert_date_time or to_clean_dataframe:
            BybitHelpers.klines_convert_date(
                data, futures, self.time_indexes_in_candle_data
            )

        if not do_clean and not to_clean_dataframe:
            return data
        final_data_array = BybitHelpers.get_klines_desired_only_cols(
            data, self.desired_candle_data_indexes
        )

        if to_clean_dataframe:
            return BybitHelpers.klines_convert_to_pandas(final_data_array)
        return final_data_array

    def _get_spot_symbol_klines(self, end_time, interval, limit, start_time, symbol):
        start_timestamp = None if start_time is None else start_time.timestamp() * 1000
        end_timestamp = end_time.timestamp() * 1000 if end_time is not None else None

        if limit is not None:
            if limit > 1000:
                limit = 1000
            elif limit < 1:
                limit = 1

        data = self.spot_session.query_kline(
            symbol=symbol,
            interval=interval,
            startTime=start_timestamp,
            endTime=end_timestamp,
            limit=limit,
        )["result"]
        for datum in data:
            for idx in range(len(datum)):
                if idx in self.time_indexes_in_candle_data:
                    continue
                datum[idx] = float(datum[idx])
        return data

    def _get_futures_symbol_klines(self, interval, limit, start_time, symbol):
        futures_interval = BybitHelpers.convert_interval_to_futures_klines(interval)
        data = []

        if limit is not None and limit > 200 or limit is None:
            limit = 200
        elif limit < 1:
            limit = 1

        if start_time is None:
            start_timestamp = int(
                datetime.now().timestamp()
                - BybitHelpers.get_interval_in_seconds(interval, self.time_intervals)
                * limit
            )
        elif isinstance(start_time, int):
            start_timestamp = start_time
        else:
            start_timestamp = int(start_time.timestamp)

        candles = self.futures_session.query_kline(
            symbol=symbol,
            interval=futures_interval,
            from_time=start_timestamp,
            limit=limit,
        )
        for candle in candles["result"]:
            data_array = [
                float(candle["open_time"]),
                float(candle["open"]),
                float(candle["high"]),
                float(candle["low"]),
                float(candle["close"]),
                float(candle["volume"]),
                int(candle["open_time"])
                + BybitHelpers.get_interval_in_seconds(interval, self.time_intervals),
                None,
                None,
                None,
                None,
            ]
            data.append(data_array)
        return data

    def get_exchange_time(self, futures=False):
        if futures:
            return self.futures_session.server_time()["time_now"]
        else:
            return int(self.spot_session.server_time()["result"]["serverTime"])

    def get_symbol_24h_ticker(self, symbol):
        raise NotImplementedError()

    def test_futures_order(self, futures_order_data):
        # sourcery skip: no-conditionals-in-tests
        if futures_order_data.time_in_force is None:
            futures_order_data.time_in_force = "GoodTillCancel"

        if futures_order_data.close_position is None:
            futures_order_data.close_position = False

        if futures_order_data.reduce_only is None:
            futures_order_data.reduce_only = False

        is_futures_order_data_valid(futures_order_data)

        return futures_order_data

    def make_futures_order(self, futures_order_data: DataHelpers.FuturesOrderData):
        order_params = BybitHelpers.get_futures_order_as_dict(
            futures_order_data, self.futures_time_in_forces
        )

        if "STOP" in futures_order_data.orderType:
            result = self.futures_session.place_conditional_order(**order_params)
            return BybitHelpers.futures_order_out(result["result"], is_conditional=True)
        else:
            result = self.futures_session.place_active_order(**order_params)
            return BybitHelpers.futures_order_out(result["result"])

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
        batch_orders = []
        batch_conditional_orders = []
        for order in futures_order_datas:
            order_as_dict = BybitHelpers.get_futures_order_as_dict(
                order, self.futures_time_in_forces
            )

            if "STOP" in order.order_type:
                batch_conditional_orders.append(order)
            else:
                batch_orders.append(order_as_dict)

        results = []
        if batch_conditional_orders:
            put_results = self.futures_session.place_conditional_order_bulk(
                batch_conditional_orders
            )
            results.extend(
                BybitHelpers.futures_order_out(result["result"], is_conditional=True)
                for result in put_results
            )
        if batch_orders:
            put_results = self.futures_session.place_active_order_bulk(batch_orders)
            results.extend(
                BybitHelpers.futures_order_out(result["result"])
                for result in put_results
            )
        return results

    def change_initial_leverage(self, symbol, leverage):
        return self.futures_session.set_leverage(
            symbol=symbol, buy_leverage=leverage, sell_leverage=leverage
        )["result"]

    def change_margin_type(self, symbol, margin_type, params):
        try:
            buy_leverage = params["buyLeverage"]
            sell_leverage = params["sellLeverage"]
            if margin_type.upper() == "ISOLATED":
                is_isolated = True
            elif margin_type.upper() == "CROSS":
                is_isolated = False
            else:
                raise ValueError("Margin type must either be 'ISOLATED' or 'CROSS'.")
        except Exception as e:
            raise ValueError(
                "Must specify 'buyLeverage' and 'sellLeverage' in 'params"
            ) from e

        self.futures_session.cross_isolated_margin_switch(
            symbol=symbol,
            is_isolated=is_isolated,
            buy_leverage=buy_leverage,
            sell_leverage=sell_leverage,
        )
        return True

    def change_position_margin(self, symbol, amount):
        result = self.futures_session.change_margin(symbol=symbol, margin=amount)
        return result["ret_code"] == 0

    def get_position(self):
        return self.futures_session.my_position()["result"]

    def spot_best_bid_asks(self, symbol=None):
        return self.spot_session.best_bid_ask_price(symbol=symbol)["result"]

    def get_symbol_order_book(self, symbol, limit=None, futures=False):
        if futures:
            return self.futures_session.orderbook(symbol=symbol)["result"]
        else:
            return self.spot_session.orderbook(symbol=symbol)["result"]

    def get_symbol_recent_trades(self, symbol, limit=None, futures=False):
        if futures:
            limit = min(limit, 1000) if limit is not None and limit > 0 else 500

            recent_trades = self.futures_session.public_trading_records(
                symbol=symbol, limit=limit
            )["result"]
            return BybitHelpers.get_recent_trade_history_out(
                recent_trades, futures=True
            )
        else:
            limit = min(limit, 60) if limit is not None and limit > 0 else 60

            recent_trades = self.spot_session.public_trading_records(
                symbol=symbol, limit=limit
            )["result"]
            return BybitHelpers.get_recent_trade_history_out(recent_trades)

    def get_position_info(self, symbol=None):
        result = self.futures_session.my_position(symbol=symbol)
        return result["result"]

    def get_symbol_min_trade(self, symbol, futures=False):
        symbol_ticker_price = self.get_symbol_ticker_price(
            symbol=symbol, futures=futures
        )

        min_quantity = None
        min_quote_quantity = None
        step_quantity = None
        step_price = None

        if futures:
            symbol_infos = self.futures_session.query_symbol()["result"]

            for symbolInfo in symbol_infos:
                if symbolInfo["name"] == symbol:
                    min_quantity = float(
                        symbolInfo["lot_size_filter"]["min_trading_qty"]
                    )
                    min_quote_quantity = symbol_ticker_price * min_quantity
                    step_quantity = float(symbolInfo["lot_size_filter"]["qty_step"])
                    step_price = symbolInfo["price_filter"]["tick_size"]

        else:
            symbol_infos = self.spot_session.query_symbol()["result"]

            for symbolInfo in symbol_infos:
                if symbolInfo["name"] == symbol:
                    min_quantity = float(symbolInfo["minTradeQuantity"])
                    min_quote_quantity = float(symbolInfo["minTradeAmount"])
                    step_quantity = float(symbolInfo["basePrecision"])
                    step_price = symbolInfo["minPricePrecision"]

        return {
            "minQuantity": min_quantity,
            "minQuoteQuantity": min_quote_quantity,
            "precisionStep": step_quantity,
            "stepPrice": step_price,
        }

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
        if (
            enter_price is None
            or take_profit is None
            or stop_loss is None
            or leverage is None
            or margin_type is None
        ):
            raise ValueError("Specify all inputs.")

        symbol_info = self.get_symbol_min_trade(symbol=symbol, futures=True)

        quantity = DataHelpers.get_quantity(
            enter_price, quantity, quote_quantity, symbol_info["precisionStep"]
        )

        self.set_margin_leverage(leverage, margin_type, symbol)
        order_params = {
            "takeProfit": take_profit,
            "stopLoss": stop_loss,
            "tpTriggerBy": "MarkPrice",
            "slTriggerBy": "MarkPrice",
        }

        futures_order = self.create_and_test_futures_order(
            symbol=symbol,
            side=order_side,
            order_type="LIMIT",
            time_in_force="GTC",
            quantity=quantity,
            price=enter_price,
            close_position=False,
            extra_params=order_params,
        )
        ordering_result = self.make_futures_order(futures_order)
        return ordering_result["orderId"]

    def set_margin_leverage(self, leverage, margin_type, symbol):
        params = {"buyLeverage": leverage, "sellLeverage": leverage}
        self.change_initial_leverage(leverage, symbol)
        self.change_margin_type(symbol, margin_type, params)

    def get_symbol_24h_changes(self, futures=False):
        changes_list = []
        if futures:
            for ticker in self.futures_session.latest_information_for_symbol()[
                "result"
            ]:
                print(ticker)
                if not ticker["is_block_trade"]:
                    changes_list.append((ticker["symbol"], 0))
        else:
            symbol_infos = self.spot_session.query_symbol()["result"]
            changes_list.extend((ticker["name"], 0) for ticker in symbol_infos)
        return sorted(changes_list, key=lambda x: x[1], reverse=True)

    def get_symbol_list(self, futures=False):
        raise NotImplementedError()

    def get_latest_symbol_names(self, num_of_symbols=None, futures=False):
        raise NotImplementedError()

    def get_income_history(
        self, symbol, income_type=None, start_time=None, end_time=None, limit=None
    ):
        args = {
            "start_date": start_time,
            "end_date": end_time,
            "wallet_fund_type": income_type,
            "limit": limit,
            "coin": symbol,
        }
        args = {k: v for k, v in args.items() if v is not None}

        return self.futures_session.wallet_fund_records(**args)

    def get_long_short_ratios(
        self, symbol, period, limit=None, start_time=None, end_time=None
    ):
        raise NotImplementedError()

    def get_deposit_address(self, coin, network=None):
        raise NotImplementedError()
