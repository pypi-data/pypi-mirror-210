import time
from datetime import datetime

import pandas as pd

from Exchanges.BaseExchange import BaseExchange
from Utils import KuCoinHelpers, DataHelpers
from kucoin.client import User, Trade, Market
from kucoin_futures.client import FuturesUser, FuturesTrade, FuturesMarket


def is_symbol_status_valid(symbolName, symbolDatas, futures=False):
    if futures:
        for symbolData in symbolDatas:
            if symbolData.symbol == symbolName:
                if symbolData.status == "TRADING":
                    return True
                else:
                    return False
    else:
        for symbolData in symbolDatas:
            if symbolData["symbol"] == symbolName:
                if symbolData["enableTrading"]:
                    return True
                else:
                    return False
    return False


def checkSpotOrderDataValid(orderData: DataHelpers.OrderData):
    checkOrderSide(orderData, futures=False)
    checkOrderSymbol(orderData)
    checkOrderType(orderData, futures=False)

    if orderData.order_type == "market":
        checkOrderSize(orderData)
    else:
        if "limit" in orderData.order_type:
            checkOrderPrice(orderData)
            checkOrderSize(orderData)
        elif "stop" in orderData.order_type:
            checkStopOrderDatas(orderData)

        checkOrderTimeInForce(orderData)
        checkExtraParams(orderData)


def checkFuturesOrderDataValid(orderData):
    checkOrderSide(orderData, futures=True)
    checkOrderSymbol(orderData)
    checkOrderType(orderData, futures=True)

    if orderData.order_type == "market":
        checkOrderSize(orderData, futures=True)
    elif orderData.order_type == "limit":
        checkOrderPrice(orderData)
        checkOrderSize(orderData, futures=True)
        checkOrderTimeInForce(orderData, futures=True)
        checkExtraParams(orderData, futures=True)
    if orderData.stop_price is not None:
        checkStopOrderDatas(orderData, futures=True)


def checkExtraParams(orderData, futures=False):
    if orderData.extra_params is not None:
        if futures:
            checkPostOnlyOrder(orderData, futures)
            checkIceBergOrder(orderData)
            checkOrderLeverage(orderData)
        else:
            checkCancelAfterOrder(orderData)
            checkPostOnlyOrder(orderData, futures)


def checkCancelAfterOrder(orderData):
    if "cancelAfter" in orderData.extra_params.keys():
        if orderData.time_in_force != "GTT":
            raise ValueError(
                "'cancelAfter' field can only be used with 'GTT' as 'timeInForce' field."
            )


def checkOrderLeverage(orderData):
    if "leverage" not in orderData.extra_params.keys():
        if orderData.close_position is None:
            raise ValueError("Missing 'leverage' field.")
        if not orderData.close_position:
            raise ValueError("Missing 'leverage' field.")


def checkIceBergOrder(orderData):
    if "iceberg" in orderData.extra_params.keys():
        if "visibleSize" not in orderData.extra_params.keys():
            raise ValueError("Specify 'visibleSize' with 'iceberg' set as true")


def checkPostOnlyOrder(orderData, futures=False):
    if "postOnly" in orderData.extra_params.keys():
        if futures:
            if orderData.time_in_force in ["FOK"]:
                raise ValueError(
                    "'postOnly' field can not be used with 'IOC' as 'timeInForce' field."
                )
            if "hidden" in orderData.extra_params.keys():
                raise ValueError("Can't use 'hidden' with 'postOnly'")
            if "iceberg" in orderData.extra_params.keys():
                raise ValueError("Can't use 'iceberg' with 'postOnly'")
        else:
            if orderData.time_in_force in ["IOC", "FOK"]:
                raise ValueError(
                    "'postOnly' field can not be used with 'IOC' or 'FOK' as 'timeInForce' field."
                )


def checkOrderTimeInForce(orderData, futures=False):
    errorString = "Invalid value for 'timeInForce' specified"

    if futures:
        validValues = ["GTC", "IOC"]
    else:
        validValues = ["GTC", "GTT", "IOC", "FOK"]

    if orderData.time_in_force not in validValues:
        raise ValueError(errorString)


def checkOrderPrice(orderData):
    if orderData.price is None:
        raise ValueError("Missing 'price' field for limit order type.")


def checkStopOrderDatas(orderData, futures=False):
    if futures:
        if "stop" not in orderData.extra_params.keys():
            raise ValueError(
                "Specify 'stop' inside 'extraParams'. Either 'down' or 'up'."
            )
        if "stopPriceType" not in orderData.extra_params.keys():
            raise ValueError(
                "Specify 'stopPriceType' inside 'extraParams'. Either 'TP', 'IP' or 'MP'."
            )
    else:
        if orderData.extra_params is not None:
            if "stop" not in orderData.extra_params.keys():
                raise ValueError("Specify 'stop' in 'extraParams' for stop order.")
        else:
            raise ValueError("Specify 'stopPrice' in 'extraParams' for stop order.")

        if orderData.quantity is None:
            raise ValueError("Missing 'quantity' field for stop order type.")


def checkOrderSize(orderData, futures=False):
    errorString = "Provide either 'quantity' or 'quoteOrderQty'."
    if futures:
        if orderData.quantity is None and orderData.quote_quantity is None:
            if orderData.close_position is None:
                raise ValueError(errorString)
            if not orderData.close_position:
                raise ValueError(errorString)
    else:
        if orderData.quantity is None and orderData.quote_order_qty is None:
            raise ValueError(errorString)


def checkOrderType(orderData, futures=False):
    if futures:
        validTypes = ["limit", "market", "LIMIT", "MARKET", "Limit", "Market"]
    else:
        validTypes = [
            "limit",
            "market",
            "stop_market",
            "LIMIT",
            "MARKET",
            "STOP_MARKET",
            "Limit",
            "Market",
            "Stop_Market",
        ]

    if orderData.order_type is None or orderData.order_type not in validTypes:
        raise ValueError("Missing 'type' field.")
    orderData.order_type = orderData.order_type.lower()


def checkOrderSymbol(orderData):
    if orderData.symbol is None:
        raise ValueError("Missing 'symbol' field.")


def checkOrderSide(orderData, futures=False):
    errorString = "Missing or incorrect 'side' field."
    if futures:
        if orderData.side is None or orderData.side not in [
            "buy",
            "sell",
            "BUY",
            "SELL",
            "Buy",
            "Sell",
        ]:
            if orderData.close_position is None:
                raise ValueError(errorString)
            if not orderData.close_position:
                raise ValueError(errorString)
        if orderData.side is not None:
            orderData.side = orderData.side.lower()
    else:
        if orderData.side is None or orderData.side not in [
            "buy",
            "sell",
            "BUY",
            "SELL",
            "Buy",
            "Sell",
        ]:
            raise ValueError(errorString)
        orderData.side = orderData.side.lower()


class KuCoinExchange(BaseExchange):
    timeIntervals = [
        "1min",
        "3min",
        "5min",
        "15min",
        "30min",
        "1hour",
        "2hour",
        "4hour",
        "6hour",
        "8hour",
        "12hour",
        "1day",
        "1week",
    ]

    timeIntervalTranslate = {
        "1m": "1min",
        "3m": "3min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1hour",
        "2h": "2hour",
        "4h": "4hour",
        "6h": "6hour",
        "8h": "8hour",
        "12h": "12hour",
        "1d": "1day",
        "1w": "1week",
    }

    noOrderIdsErrorString = (
        "Specify either 'orderId' or 'localOrderId' (only for active orders)"
    )

    def __init__(self, credentials, sandbox=False, unified_in_outs=True):
        self.spotApiKey = credentials["spot"]["key"]
        self.spotSecret = credentials["spot"]["secret"]
        self.spotPassphrase = credentials["spot"]["passphrase"]

        self.futuresApiKey = credentials["futures"]["key"]
        self.futuresSecret = credentials["futures"]["secret"]
        self.futuresPassphrase = credentials["futures"]["passphrase"]

        self.sandbox = sandbox
        self.unifiedInOuts = unified_in_outs

        self.unavailableErrorText = "This method is unavailable in KuCoin exchange"

        if sandbox:
            self.spotUser = User(
                key=self.spotApiKey,
                secret=self.spotSecret,
                passphrase=self.spotPassphrase,
                is_sandbox=True,
            )
            self.spotTrade = Trade(
                key=self.spotApiKey,
                secret=self.spotSecret,
                passphrase=self.spotPassphrase,
                is_sandbox=True,
            )
            self.spotMarket = Market(
                key=self.spotApiKey,
                secret=self.spotSecret,
                passphrase=self.spotPassphrase,
                is_sandbox=True,
            )

            self.futuresUser = FuturesUser(
                key=self.futuresApiKey,
                secret=self.futuresSecret,
                passphrase=self.futuresPassphrase,
                is_sandbox=True,
            )
            self.futuresTrade = FuturesTrade(
                key=self.futuresApiKey,
                secret=self.futuresSecret,
                passphrase=self.futuresPassphrase,
                is_sandbox=True,
            )
            self.futuresMarket = FuturesMarket(
                key=self.futuresApiKey,
                secret=self.futuresSecret,
                passphrase=self.futuresPassphrase,
                is_sandbox=True,
            )
        else:
            self.spotUser = User(
                key=self.spotApiKey,
                secret=self.spotSecret,
                passphrase=self.spotPassphrase,
            )
            self.spotTrade = Trade(
                key=self.spotApiKey,
                secret=self.spotSecret,
                passphrase=self.spotPassphrase,
            )
            self.spotMarket = Market(
                key=self.spotApiKey,
                secret=self.spotSecret,
                passphrase=self.spotPassphrase,
            )

            self.futuresUser = FuturesUser(
                key=self.futuresApiKey,
                secret=self.futuresSecret,
                passphrase=self.futuresPassphrase,
            )
            self.futuresTrade = FuturesTrade(
                key=self.futuresApiKey,
                secret=self.futuresSecret,
                passphrase=self.futuresPassphrase,
            )
            self.futuresMarket = FuturesMarket(
                key=self.futuresApiKey,
                secret=self.futuresSecret,
                passphrase=self.futuresPassphrase,
            )

    def get_balance(self, asset=None, futures=False):
        if futures:
            if asset is None:
                return KuCoinHelpers.unify_get_balance_futures_out(
                    [
                        self.futuresUser.get_account_overview(),
                        self.futuresUser.get_account_overview(currency="USDT"),
                    ]
                )
            else:
                return KuCoinHelpers.unify_get_balance_futures_out(
                    self.futuresUser.get_account_overview(currency=asset),
                    is_single=True,
                )

        else:
            if asset is None:
                return KuCoinHelpers.unify_get_balance_spot_out(
                    self.spotUser.get_account_list(currency=asset)
                )
            else:
                return KuCoinHelpers.unify_get_balance_spot_out(
                    self.spotUser.get_account_list(currency=asset), is_single=True
                )

    def symbol_account_trade_history(
        self, symbol, futures=False, from_id=None, limit=None
    ):
        if futures:
            return KuCoinHelpers.unify_trade_history(
                self.futuresTrade.get_fills_details(symbol=symbol)["items"],
                futures=True,
            )
        else:
            return KuCoinHelpers.unify_trade_history(
                self.spotTrade.get_fill_list(tradeType="TRADE")["items"]
            )

    def test_spot_order(self, order_data):
        checkSpotOrderDataValid(order_data)
        return order_data

    def make_spot_order(self, order_data):
        params = KuCoinHelpers.get_spot_order_as_dict(order_data)
        response = None

        if params["type"] == "market":
            response = self.spotTrade.create_market_order(**params)
        if params["type"] == "limit":
            response = self.spotTrade.create_limit_order(**params)
        if params["type"] == "stop_limit":
            params["type"] = "limit"
            response = self.spotTrade.create_limit_stop_order(**params)
        if params["type"] == "stop_market":
            params["type"] = "market"
            response = self.spotTrade.create_market_stop_order(**params)

        return self.get_order(
            params["symbol"], order_id=response["orderId"], futures=False
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
        currOrder = DataHelpers.set_spot_order_data(
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

        self.test_spot_order(currOrder)

        return currOrder

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
            args = {}
            if start_time is not None:
                args["startAt"] = start_time
            if end_time is not None:
                args["endAt"] = end_time
            args["symbol"] = symbol
            orderList = self.futuresTrade.get_order_list(**args)["items"]
            return KuCoinHelpers.unify_get_symbol_orders(orderList, futures=True)
        else:
            args = {}
            if start_time is not None:
                args["startAt"] = start_time
            if end_time is not None:
                args["endAt"] = end_time
            args["symbol"] = symbol
            orderList = self.spotTrade.get_order_list(**args)["items"]
            return KuCoinHelpers.unify_get_symbol_orders(orderList)

    def get_open_orders(self, symbol, futures=False):
        args = {"symbol": symbol, "status": "active"}
        if futures:
            lotSize = self.get_symbol_min_trade(symbol=symbol, futures=True)[
                "precisionStep"
            ]
            orderList = self.futuresTrade.get_order_list(**args)["items"]
            return KuCoinHelpers.unify_get_symbol_orders(
                orderList, futures=True, lot_size=lotSize
            )
        else:
            orderList = self.spotTrade.get_order_list(**args)["items"]
            return KuCoinHelpers.unify_get_symbol_orders(orderList)

    def cancel_all_symbol_open_orders(self, symbol, futures=False):
        if futures:
            result = self.futuresTrade.cancel_all_limit_order(symbol)[
                "cancelledOrderIds"
            ]
            result.append(
                self.futuresTrade.cancel_all_stop_order(symbol)["cancelledOrderIds"]
            )
            return result
        else:
            args = {"symbol": symbol}
            result = self.spotTrade.cancel_all_orders(**args)
            return result["cancelledOrderIds"]

    def cancel_order(self, symbol, order_id=None, local_order_id=None, futures=False):
        if futures:
            if order_id is not None:
                cancelledOrderId = self.futuresTrade.cancel_order(order_id)[
                    "cancelledOrderIds"
                ][0]
            elif local_order_id is not None:
                orderData = self.get_order(
                    symbol=symbol, local_order_id=local_order_id, futures=True
                )
                cancelledOrderId = self.futuresTrade.cancel_order(
                    orderId=orderData["orderId"]
                )["cancelledOrderIds"][0]
            else:
                raise ValueError(self.noOrderIdsErrorString)
            return self.get_order(symbol, order_id=cancelledOrderId, futures=True)
        else:
            if order_id is not None:
                cancelledOrderId = self.spotTrade.cancel_order(order_id)[
                    "cancelledOrderIds"
                ][0]
            elif local_order_id is not None:
                cancelledOrderId = self.spotTrade.cancel_client_order(local_order_id)[
                    "cancelledOrderId"
                ]
            else:
                raise ValueError(self.noOrderIdsErrorString)
            return self.get_order(symbol, order_id=cancelledOrderId, futures=False)

    def get_order(self, symbol, order_id=None, local_order_id=None, futures=False):
        if futures:
            if order_id is not None:
                orderData = self.futuresTrade.get_order_details(order_id)
            elif local_order_id is not None:
                orderData = self.futuresTrade.get_client_order_details(local_order_id)
            else:
                raise ValueError(self.noOrderIdsErrorString)

            lotSize = self.get_symbol_min_trade(symbol=symbol, futures=True)[
                "precisionStep"
            ]
            return KuCoinHelpers.unify_get_order(
                orderData, futures=True, lot_size=lotSize
            )
        else:
            if order_id is not None:
                orderData = self.spotTrade.get_order_details(order_id)
            elif local_order_id is not None:
                orderData = self.spotTrade.get_client_order_details(local_order_id)
            else:
                raise ValueError(self.noOrderIdsErrorString)

            return KuCoinHelpers.unify_get_order(orderData)

    def get_trading_fees(self, symbol=None, futures=False):
        if futures:
            if symbol is None:
                raise ValueError("Must specify futures contract symbol name.")
            contractInfo = self.futuresMarket.get_contract_detail(symbol=symbol)
            return {
                "symbol": contractInfo["symbol"],
                "takerCommission": contractInfo["takerFeeRate"],
                "makerCommission": contractInfo["makerFeeRate"],
            }
        else:
            if symbol is None:
                return self.spotUser.get_base_fee()
            else:
                feeData = self.spotUser.get_actual_fee(symbols=symbol)[0]

                return {
                    "symbol": feeData["symbol"],
                    "takerCommission": feeData["takerFeeRate"],
                    "makerCommission": feeData["makerFeeRate"],
                }

    def get_symbol_ticker_price(self, symbol, futures=False):
        if futures:
            return float(self.futuresMarket.get_ticker(symbol=symbol)["price"])
        else:
            return float(self.spotMarket.get_ticker(symbol=symbol)["price"])

    def get_symbol_klines(
        self,
        symbol,
        interval,
        start_time=None,
        end_time=None,
        limit=500,
        futures=False,
        blvtnav=False,
        convert_date_time=False,
        do_clean=False,
        to_clean_dataframe=False,
    ):
        if interval not in KuCoinExchange.timeIntervals:
            if interval in KuCoinExchange.timeIntervalTranslate.keys():
                timeInterval = KuCoinExchange.timeIntervalTranslate[interval]
            else:
                raise ValueError("Time interval is not valid.")
        else:
            timeInterval = interval

        if start_time is not None and not isinstance(start_time, int):
            start_time = int(
                datetime.timestamp(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
            )
        if end_time is not None and not isinstance(end_time, int):
            end_time = int(
                datetime.timestamp(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
            )

        if futures:
            data = self._getFuturesSymbolKlines(
                end_time, timeInterval, limit, start_time, symbol
            )
        else:
            if start_time is not None:
                start_time = int(str(start_time)[:-3])

            if end_time is not None:
                end_time = int(str(end_time)[:-3])

            data = self._getSpotSymbolKlines(
                end_time, timeInterval, limit, start_time, symbol
            )

        if convert_date_time or to_clean_dataframe:
            if futures:
                for datum in data:
                    datum.append(datum[-1])
                    datum[-1] = datetime.fromtimestamp((float(datum[0]) - 1) / 1000)
                    datum[0] = datetime.fromtimestamp(float(datum[0]) / 1000)
                    datum.append(None)
            else:
                for datum in data:
                    datum.append(datum[-1])
                    datum[-2] = datetime.fromtimestamp(float(datum[0]) - 1)
                    datum[0] = datetime.fromtimestamp(float(datum[0]))

        if do_clean or to_clean_dataframe:
            if to_clean_dataframe:
                if futures:
                    cleanDataFrame = pd.DataFrame(
                        data,
                        columns=[
                            "date",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                            "closeDate",
                            "tradesNum",
                        ],
                    )
                else:
                    cleanDataFrame = pd.DataFrame(
                        data,
                        columns=[
                            "date",
                            "open",
                            "close",
                            "high",
                            "low",
                            "volume",
                            "closeDate",
                            "tradesNum",
                        ],
                    )
                cleanDataFrame.set_index("date", inplace=True)
                cleanDataFrame[cleanDataFrame.columns[:5]] = cleanDataFrame[
                    cleanDataFrame.columns[:5]
                ].apply(pd.to_numeric, errors="coerce")
                cleanDataFrame[cleanDataFrame.columns[-1]] = cleanDataFrame[
                    cleanDataFrame.columns[-1]
                ].apply(pd.to_numeric, errors="coerce")
                return cleanDataFrame
            return data
        else:
            return data

    def _getSpotSymbolKlines(self, endTime, timeInterval, limit, startTime, symbol):
        if limit is None:
            if startTime is None:
                if endTime is None:
                    data = self.spotMarket.get_kline(
                        symbol=symbol, kline_type=timeInterval
                    )
                else:
                    raise ValueError("Can't use endTime without limit.")
            else:
                if endTime is None:
                    data = self.spotMarket.get_kline(
                        symbol=symbol, kline_type=timeInterval, startAt=startTime
                    )
                else:
                    data = self.spotMarket.get_kline(
                        symbol=symbol,
                        kline_type=timeInterval,
                        startAt=startTime,
                        endAt=endTime,
                    )
        else:
            if startTime is None:
                if endTime is None:
                    startAt = int(time.time()) - limit * self._getTimeIntervalInSeconds(
                        timeInterval
                    )
                    data = self.spotMarket.get_kline(
                        symbol=symbol,
                        kline_type=timeInterval,
                        startAt=startAt,
                        endAt=int(time.time()),
                    )
                else:
                    startAt = endTime - limit * self._getTimeIntervalInSeconds(
                        timeInterval
                    )
                    data = self.spotMarket.get_kline(
                        symbol=symbol,
                        kline_type=timeInterval,
                        startAt=startAt,
                        endAt=endTime,
                    )
            else:
                if endTime is None:
                    endAt = startTime + limit * self._getTimeIntervalInSeconds(
                        timeInterval
                    )
                    data = self.spotMarket.get_kline(
                        symbol=symbol,
                        kline_type=timeInterval,
                        startAt=startTime,
                        endAt=endAt,
                    )
                else:
                    data = self.spotMarket.get_kline(
                        symbol=symbol,
                        kline_type=timeInterval,
                        startAt=startTime,
                        endAt=endTime,
                    )
        return data[::-1]

    def _getFuturesSymbolKlines(self, endTime, timeInterval, limit, startTime, symbol):
        granularity = int(self._getTimeIntervalInSeconds(timeInterval) / 60)
        if limit is None:
            if startTime is None:
                if endTime is None:
                    data = self.futuresMarket.get_kline_data(
                        symbol=symbol, granularity=granularity
                    )
                else:
                    endTime = endTime - endTime % (granularity * 60)
                    data = self.futuresMarket.get_kline_data(
                        symbol=symbol, granularity=granularity, end_t=endTime
                    )
            else:
                if endTime is None:
                    startTime = startTime - startTime % (granularity * 60)
                    data = self.futuresMarket.get_kline_data(
                        symbol=symbol, granularity=granularity, begin_t=startTime
                    )
                else:
                    endTime = endTime - endTime % (granularity * 60)
                    startTime = startTime - startTime % (granularity * 60)

                    data = self.futuresMarket.get_kline_data(
                        symbol=symbol,
                        granularity=granularity,
                        begin_t=startTime,
                        end_t=endTime,
                    )
        else:
            if startTime is None:
                if endTime is None:
                    endTime = int(time.time()) * 1000
                    endTime = endTime - endTime % (granularity * 60 * 1000)

                    startAt = endTime - limit * granularity * 60 * 1000
                    startAt = startAt - startAt % (granularity * 60 * 1000)

                    data = self.futuresMarket.get_kline_data(
                        symbol=symbol, granularity=granularity, begin_t=startAt
                    )
                else:
                    endTime = endTime - endTime % (granularity * 60 * 1000)

                    startTime = endTime - limit * granularity * 60 * 1000
                    startTime = startTime - startTime % (granularity * 60 * 1000)

                    data = self.futuresMarket.get_kline_data(
                        symbol=symbol,
                        granularity=granularity,
                        begin_t=startTime,
                        end_t=endTime,
                    )
            else:
                if endTime is None:
                    startTime = startTime - startTime % (granularity * 60 * 1000)

                    endTime = startTime + limit * granularity * 60 * 1000
                    endTime = endTime - endTime % (granularity * 60 * 1000)

                    data = self.futuresMarket.get_kline_data(
                        symbol=symbol,
                        granularity=granularity,
                        begin_t=startTime,
                        end_t=endTime,
                    )
                else:
                    startTime = startTime - startTime % (granularity * 60 * 1000)
                    endTime = endTime - endTime % (granularity * 60 * 1000)

                    data = self.futuresMarket.get_kline_data(
                        symbol=symbol,
                        granularity=granularity,
                        begin_t=startTime,
                        end_t=endTime,
                    )
        return data

    def _getTimeIntervalInSeconds(self, timeInterval):
        if timeInterval not in self.timeIntervals:
            raise ValueError("Time interval is not valid.")

        if timeInterval == "1min":
            return 60
        elif timeInterval == "3min":
            return 3 * 60
        elif timeInterval == "5min":
            return 5 * 60
        elif timeInterval == "15min":
            return 15 * 60
        elif timeInterval == "30min":
            return 40 * 60
        elif timeInterval == "1hour":
            return 3600
        elif timeInterval == "2hour":
            return 2 * 3600
        elif timeInterval == "4hour":
            return 4 * 3600
        elif timeInterval == "6hour":
            return 6 * 3600
        elif timeInterval == "8hour":
            return 8 * 3600
        elif timeInterval == "12hour":
            return 12 * 3600
        elif timeInterval == "1day":
            return 24 * 3600
        elif timeInterval == "1week":
            return 7 * 24 * 3600

    def get_exchange_time(self, futures=False):
        if futures:
            return self.futuresMarket.get_server_timestamp()
        else:
            return self.spotMarket.get_server_timestamp()

    def get_symbol_24h_ticker(self, symbol):
        return self.spotMarket.get_24h_stats(symbol)

    def test_futures_order(self, futures_order_data):
        checkFuturesOrderDataValid(futures_order_data)

    def make_futures_order(self, futures_order_data):
        if futures_order_data.quantity is None:
            if futures_order_data.quote_quantity is not None:
                lotSize = self.get_symbol_min_trade(
                    symbol=futures_order_data.symbol, futures=True
                )["precisionStep"]
                if futures_order_data.price is None:
                    currPrice = self.get_symbol_ticker_price(
                        futures_order_data.symbol, futures=True
                    )
                    futures_order_data.quantity = int(
                        round(futures_order_data.quote_quantity / currPrice / lotSize)
                    )
                else:
                    futures_order_data.quantity = int(
                        round(
                            futures_order_data.quote_quantity
                            / futures_order_data.price
                            / lotSize
                        )
                    )

        params = KuCoinHelpers.get_futures_order_as_dict(futures_order_data)

        symbol = params["symbol"]
        del params["symbol"]

        side = params["side"]
        del params["side"]

        if "leverage" in params.keys():
            leverage = params["leverage"]
            del params["leverage"]
        else:
            leverage = None
        if params["type"] == "market":
            result = self.futuresTrade.create_market_order(
                symbol, side, leverage, **params
            )
        elif params["type"] == "limit":
            size = params["size"]
            del params["size"]

            price = params["price"]
            del params["price"]

            result = self.futuresTrade.create_limit_order(
                symbol, side, leverage, size, price, **params
            )
        else:
            result = None
        return self.get_order(symbol, order_id=result["orderId"], futures=True)

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
        quoteQuantity=None,
    ):
        currOrder = DataHelpers.set_futures_order_data(
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
            quoteQuantity,
        )

        lotSize = self.get_symbol_min_trade(symbol=symbol, futures=True)[
            "precisionStep"
        ]
        if currOrder.quantity is not None:
            currOrder.quantity /= lotSize

        self.test_futures_order(currOrder)

        return currOrder

    def make_batch_futures_order(self, futures_order_datas):
        raise NotImplementedError(self.unavailableErrorText)

    def change_initial_leverage(self, symbol, leverage):
        raise NotImplementedError(self.unavailableErrorText)

    def change_margin_type(self, symbol, margin_type, params=None):
        if margin_type.upper() == "CROSSED":
            autoAdd = True
        elif margin_type.upper() == "ISOLATED":
            autoAdd = False
        else:
            raise ValueError(
                "Invalid value specified for 'marginType'. Must be either 'ISOLATED' or 'CROSSED'."
            )
        return self.futuresTrade.modify_auto_deposit_margin(symbol, autoAdd)["data"]

    def change_position_margin(self, symbol, amount):
        newPosition = self.futuresTrade.add_margin_manually(
            symbol=symbol, margin=amount, bizNo=str(time.time())
        )

        return True

    def get_position(self):
        return self.futuresTrade.get_all_position()

    def spot_best_bid_asks(self, symbol):
        tickerData = self.spotMarket.get_ticker(symbol)
        return KuCoinHelpers.unify_get_best_bid_asks(tickerData, symbol)

    def get_symbol_order_book(self, symbol, limit=None, futures=False):
        if futures:
            orderBook = self.futuresMarket.l2_order_book(symbol)
            return orderBook
        else:
            orderBook = self.spotMarket.get_aggregated_order(symbol)
            return orderBook

    def get_symbol_recent_trades(self, symbol, limit=None, futures=False):
        if futures:
            tradeHistory = self.futuresMarket.get_trade_history(symbol=symbol)
            return pd.DataFrame(
                KuCoinHelpers.unify_recent_trades(tradeHistory, futures=True)
            )
        else:
            tradeHistory = self.spotMarket.get_trade_histories(symbol=symbol)
            return pd.DataFrame(KuCoinHelpers.unify_recent_trades(tradeHistory))

    def get_position_info(self, symbol=None):
        if symbol is None:
            positionInfos = self.futuresTrade.get_all_position()
            return KuCoinHelpers.unify_get_position_infos(positionInfos)
        else:
            positionInfo = self.futuresTrade.get_position_details(symbol=symbol)
            return [KuCoinHelpers.unify_get_position_info(positionInfo)]

    def get_symbol_min_trade(self, symbol, futures=False):
        if futures:
            contractInfos = self.futuresMarket.get_contract_detail(symbol)
            return KuCoinHelpers.unify_min_trade(contractInfos, futures=True)
        else:
            symbolInfoList = self.spotMarket.get_symbol_list()

            symbolInfo = None
            for info in symbolInfoList:
                if info["symbol"] == symbol:
                    symbolInfo = info
            return KuCoinHelpers.unify_min_trade(symbolInfo)

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
        symbolInfo = self.get_symbol_min_trade(symbol=symbol, futures=True)

        if quantity is None:
            if quote_quantity is None:
                raise ValueError("Specify either quantity or quoteQuantity")
            quantity = (
                int(quote_quantity / enter_price / symbolInfo["precisionStep"])
                * symbolInfo["precisionStep"]
            )

        if quantity < symbolInfo["minQuantity"]:
            raise ValueError("Quantity is lower than minimum quantity allowed.")

        mainOrder = self.create_and_test_futures_order(
            symbol,
            order_side.upper(),
            "LIMIT",
            quantity=quantity,
            price=enter_price,
            time_in_force="GTC",
            extra_params={"leverage": leverage},
        )

        tpSlSide = "sell" if order_side.upper() == "BUY" else "buy"

        slExtraParams = {
            "stop": "down" if order_side.upper() == "BUY" else "up",
            "stopPriceType": "TP",
        }
        stopLossOrder = self.create_and_test_futures_order(
            symbol=symbol,
            side=tpSlSide,
            order_type="MARKET",
            stop_price=stop_loss,
            close_position=True,
            time_in_force="GTC",
            extra_params=slExtraParams,
        )

        tpExtraParams = {
            "stop": "up" if order_side.upper() == "BUY" else "down",
            "stopPriceType": "TP",
        }
        takeProfitOrder = self.create_and_test_futures_order(
            symbol=symbol,
            side=tpSlSide,
            order_type="MARKET",
            stop_price=take_profit,
            close_position=True,
            time_in_force="GTC",
            extra_params=tpExtraParams,
        )

        mainOrderRes = self.make_futures_order(mainOrder)
        slOrderRes = self.make_futures_order(stopLossOrder)
        tpOrderRes = self.make_futures_order(takeProfitOrder)

        orderIds = {
            "mainOrder": mainOrderRes["orderId"],
            "stopLoss": slOrderRes["orderId"],
            "takeProfit": tpOrderRes["orderId"],
        }

        return orderIds

    def makeSlTpMarketFuturesOrder(
        self,
        symbol,
        orderSide,
        quantity=None,
        quoteQuantity=None,
        takeProfit=None,
        stopLoss=None,
        leverage=None,
        marginType=None,
    ):
        symbolInfo = self.get_symbol_min_trade(symbol=symbol, futures=True)
        marketPrice = self.get_symbol_ticker_price(symbol=symbol, futures=True)

        if leverage is None:
            raise ValueError("Must specify 'leverage' parameter for KuCoin orders.")

        if quantity is None:
            if quoteQuantity is None:
                raise ValueError("Specify either quantity or quoteQuantity")
            quantity = (
                int(quoteQuantity / marketPrice / symbolInfo["precisionStep"])
                * symbolInfo["precisionStep"]
            )

        if quantity < symbolInfo["minQuantity"]:
            raise ValueError("Quantity is lower than minimum quantity allowed.")

        mainOrder = self.create_and_test_futures_order(
            symbol,
            orderSide.upper(),
            "MARKET",
            quantity=quantity,
            extra_params={"leverage": leverage},
        )

        tpSlSide = "sell" if orderSide.upper() == "BUY" else "buy"

        slExtraParams = {
            "stop": "down" if orderSide.upper() == "BUY" else "up",
            "stopPriceType": "TP",
        }
        stopLossOrder = self.create_and_test_futures_order(
            symbol=symbol,
            side=tpSlSide,
            order_type="MARKET",
            stop_price=stopLoss,
            close_position=True,
            time_in_force="GTC",
            extra_params=slExtraParams,
        )

        tpExtraParams = {
            "stop": "up" if orderSide.upper() == "BUY" else "down",
            "stopPriceType": "TP",
        }
        takeProfitOrder = self.create_and_test_futures_order(
            symbol=symbol,
            side=tpSlSide,
            order_type="MARKET",
            stop_price=takeProfit,
            close_position=True,
            time_in_force="GTC",
            extra_params=tpExtraParams,
        )

        mainOrderRes = self.make_futures_order(mainOrder)
        slOrderRes = self.make_futures_order(stopLossOrder)
        tpOrderRes = self.make_futures_order(takeProfitOrder)

        orderIds = {
            "mainOrder": mainOrderRes["orderId"],
            "stopLoss": slOrderRes["orderId"],
            "takeProfit": tpOrderRes["orderId"],
        }

        return orderIds

    def getSymbol24hChanges(self, futures=False):
        changesList = []
        if futures:
            for ticker in self.futuresMarket.get_contracts_list():
                if ticker["status"] == "Open":
                    changesList.append(
                        (ticker["symbol"], float(ticker["priceChgPct"]) * 100)
                    )
        else:
            symbolInfos = self.spotMarket.get_symbol_list()
            for ticker in self.spotMarket.get_all_tickers()["ticker"]:
                if is_symbol_status_valid(ticker["symbol"], symbolInfos, futures=False):
                    changesList.append(
                        (ticker["symbol"], float(ticker["changeRate"]) * 100)
                    )

        return sorted(changesList, key=lambda x: x[1], reverse=True)

    def getSymbolList(self, futures=False):
        symbolNames = []
        if futures:
            for ticker in self.futuresMarket.get_contracts_list():
                symbolNames.append(ticker["symbol"])
        else:
            for ticker in self.spotMarket.get_all_tickers()["ticker"]:
                symbolNames.append(ticker["symbol"])

        return symbolNames

    def getLatestSymbolNames(self, numOfSymbols=None, futures=False):
        symbolDatas = []
        if futures:
            for symbolInfo in self.futuresMarket.get_contracts_list():
                symbolDatas.append(
                    (
                        symbolInfo["symbol"],
                        datetime.fromtimestamp(
                            float(symbolInfo["firstOpenDate"]) / 1000
                        ),
                    )
                )
                symbolDatas.sort(key=lambda x: x[1], reverse=True)
            if numOfSymbols is not None and numOfSymbols > len(symbolDatas):
                numOfSymbols = len(symbolDatas)
        else:
            raise NotImplementedError()
        return symbolDatas[:numOfSymbols]

    def getIncomeHistory(
        self, currency, incomeType=None, startTime=None, endTime=None, limit=None
    ):
        args = {
            "beginAt": startTime,
            "endAt": endTime,
            "type": incomeType,
            "maxCount": limit,
            "currency": currency,
        }
        args = {k: v for k, v in args.items() if v is not None}

        return KuCoinHelpers.unify_get_income(
            self.futuresUser.get_transaction_history(**args)["dataList"]
        )

    def get_long_short_ratios(
        self, symbol, period, limit=None, start_time=None, end_time=None
    ):
        pass

    def get_deposit_address(self, coin, network=None):
        pass
