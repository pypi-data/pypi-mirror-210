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

    if order.orderType == "LIMIT":
        check_limit_order_data_validity(order)

    elif order.orderType == "MARKET":
        check_spot_market_order_data_validity(order)

    elif order.orderType in ["STOP_LOSS", "TAKE_PROFIT"]:
        check_spot_stop_market_data_validity(order)

    elif order.orderType in ["STOP_LOSS_LIMIT", "TAKE_PROFIT_LIMIT"]:
        check_spot_stop_limit_order_data_validity(order)

    elif order.orderType == "LIMIT_MAKER":
        check_spot_limit_maker_order_data_validity(order)

    return False


def check_spot_limit_maker_order_data_validity(order):
    if order.quantity is None or order.price is None:
        raise ValueError("For LIMIT_MAKER order quantity and price must be specified.")


def check_spot_stop_limit_order_data_validity(order):
    if (
        order.timeInForce is None
        or order.quantity is None
        or order.price is None
        or order.stopPrice is None
    ):
        raise ValueError(
            "For STOP_LOSS_LIMIT or TAKE_PROFIT_LIMIT orders timeInForce, quantity, price and stopPrice must be specified."
        )


def check_spot_stop_market_data_validity(order):
    if order.quantity is None or order.stopPrice is None:
        raise ValueError(
            "For STOP_LOSS or TAKE_PROFIT orders quantity and stopPrice must be specified."
        )


def check_spot_market_order_data_validity(order):
    if order.quantity is None and order.quoteOrderQty is None:
        raise ValueError(
            "For MARKET order either quantity or quoteOrderQty must be specified."
        )


def check_limit_order_data_validity(order):
    if order.timeInForce is None or order.quantity is None or order.price is None:
        raise ValueError(
            "For LIMIT order timeInForce, quantity and price must be specified"
        )


def check_spot_order_time_in_force(order):
    if order.timeInForce not in [None, "GTC", "IOC", "FOK"]:
        raise ValueError("Order time in force is not valid.")


def check_spot_order_response_type(order):
    if order.newOrderRespType not in [None, "ACK", "RESULT", "FULL"]:
        raise ValueError("Order response type is not valid.")


def check_spot_order_type(order):
    if order.orderType not in BinanceExchange.spotOrderTypes:
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
    if order.callbackRate is None:
        raise ValueError(
            "For futures TRAILING_STOP_MARKET orders callbackRate must be specified."
        )


def check_futures_stop_market_order_data_validity(order):
    if order.stopPrice is None:
        raise ValueError(
            "For futures STOP_MARKET and TAKE_PROFIT_MARKET orders stopPrice must be specified"
        )


def check_futures_stop_limit_order_data_validity(order):
    if order.quantity is None or order.price is None or order.stopPrice is None:
        raise ValueError(
            "For futures STOP or TAKE_PROFIT order quantity, price and stopPrice must be specified."
        )


def check_futures_market_order_data_validity(order):
    if order.quantity is None:
        raise ValueError("For MARKET order quantity must be specified.")


def check_simultaneous_close_position_and_reduce_only(order):
    if order.closePosition is True and order.reduceOnly is True:
        raise ValueError("Can't set both closePosition and reduceOnly to True.")


def check_futures_order_reduce_only(order):
    if order.reduceOnly not in [None, True, False]:
        raise ValueError("Futures order reduceOnly is not valid.")


def check_simultaneous_close_position_and_quantity(order):
    if order.closePosition is True and order.quantity is not None:
        raise ValueError("Must not specify quantity if closePosition is True.")


def check_futures_order_price_protect(order):
    if order.priceProtect not in [None, True, False]:
        raise ValueError("Futures order priceProtect is not valid.")


def check_futures_order_callback_rate(order):
    if order.callbackRate is not None and not (0.1 <= order.callbackRate <= 5):
        raise ValueError("Futures order callbackRate is not valid.")


def check_futures_order_close_position(order):
    if order.closePosition not in [None, True, False]:
        raise ValueError("Futures order closePosition is not valid.")


def check_futures_order_response_type(order):
    if order.newOrderRespType not in [None, "ACK", "RESULT"]:
        raise ValueError("Futures order newOrderRespType is not valid.")


def check_futures_order_working_type(order):
    if order.workingType not in [None, "MARK_PRICE", "CONTRACT_PRICE"]:
        raise ValueError("Futures order workingType is not valid.")


def check_futures_order_time_in_force(order):
    if order.timeInForce not in [None, "GTC", "IOC", "FOK", "GTX"]:
        raise ValueError("Futures order timeInForce is not valid.")


def check_futures_order_side(order):
    if order.positionSide not in [None, "BOTH", "LONG", "SHORT"]:
        raise ValueError("Futures order side is not valid")


def check_futures_order_type(order):
    if order.orderType not in BinanceExchange.futuresOrderTypes:
        raise ValueError("Futures order type is not valid.")


def check_order_side(order):
    if order.side not in ["BUY", "SELL"]:
        raise ValueError("Order side can only be 'BUY' or 'SELL'")


class BinanceExchange(BaseExchange):
    timeIntervals = [
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

    timeIndexesInCandleData = [0, 6]
    desiredCandleDataIndexes = [0, 1, 2, 3, 4, 5, 6, 8]

    spotOrderTypes = [
        "LIMIT",
        "MARKET",
        "STOP_LOSS",
        "STOP_LOSS_LIMIT",
        "TAKE_PROFIT",
        "TAKE_PROFIT_LIMIT",
        "LIMIT_MAKER",
    ]

    futuresOrderTypes = [
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
        self.unifiedInOuts = unified_in_outs

        if sandbox:
            self.client = Spot(
                key=credentials["spot"]["key"],
                secret=credentials["spot"]["secret"],
                base_url="https://testnet.binance.vision",
            )
            self.futuresClient = RequestClient(
                api_key=credentials["futures"]["key"],
                secret_key=credentials["futures"]["secret"],
                url="https://testnet.binancefuture.com",
            )
        else:
            self.client = Spot(
                key=credentials["spot"]["key"], secret=credentials["spot"]["secret"]
            )
            self.futuresClient = RequestClient(
                api_key=credentials["futures"]["key"],
                secret_key=credentials["futures"]["secret"],
                url="https://fapi.binance.com",
            )

        self.subFutureClient = None

    def get_balance(self, asset="", futures=False):
        if not futures:
            try:
                balances = self.client.account()["balances"]
            except Exception as e:
                print(e)
                return None
            if asset == "" or asset is None:
                return balances
            else:
                for balance in balances:
                    if balance["asset"] == asset:
                        return balance
            return None
        else:
            balances = []
            for balance in self.futuresClient.get_balance():
                balances.append(balance.toDict())

            if asset == "" or asset is None:
                return balances
            else:
                for balance in balances:
                    if balance["asset"] == asset:
                        return balance
                return Balance.makeFreeBalance(asset)

    def symbolAccountTradeHistory(self, symbol, futures=False, fromId=None, limit=None):
        try:
            if not futures:
                return self.client.my_trades(symbol, fromId=fromId, limit=limit)
            else:
                trades = []
                for trade in self.futuresClient.get_account_trades(
                    symbol=symbol, fromId=fromId, limit=limit
                ):
                    trades.append(trade.toDict())
                return trades

        except Exception:
            return None

    def testSpotOrder(self, orderData):
        if not is_order_data_valid(orderData):
            raise ValueError("Incomplete data provided.")

        orderData.setTimestamp()
        params = BinanceHelpers.getSpotOrderAsDict(orderData)

        response = self.client.new_order_test(**params)
        return response

    def makeSpotOrder(self, orderData):
        params = BinanceHelpers.getSpotOrderAsDict(orderData)

        response = self.client.new_order(**params)
        logging.info(response)
        return response

    def createAndTestSpotOrder(
        self,
        symbol,
        side,
        orderType,
        quantity=None,
        price=None,
        timeInForce=None,
        stopPrice=None,
        icebergQty=None,
        newOrderRespType=None,
        newClientOrderId=None,
        extraParams=None,
    ):
        currOrder = DataHelpers.setSpotOrderData(
            icebergQty,
            newClientOrderId,
            newOrderRespType,
            orderType,
            price,
            quantity,
            side,
            stopPrice,
            symbol,
            timeInForce,
            extraParams,
        )

        self.testSpotOrder(currOrder)

        return currOrder

    def getSymbolOrders(
        self,
        symbol,
        futures=False,
        orderId=None,
        startTime=None,
        endTime=None,
        limit=None,
    ):
        if not futures:
            return self.client.get_orders(
                symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                timestamp=time.time(),
            )
        else:
            orders = []
            for order in self.futuresClient.get_all_orders(
                symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ):
                orders.append(order.toDict())
            return orders

    def getOpenOrders(self, symbol, futures=False):
        try:
            if not futures:
                return self.client.get_open_orders(symbol, timestamp=time.time())
            else:
                orders = []
                for order in self.futuresClient.get_open_orders(symbol=symbol):
                    orders.append(order.toDict())
                return orders
        except Exception:
            return None

    def cancelAllSymbolOpenOrders(self, symbol, futures=False):
        if not futures:
            openOrders = self.getOpenOrders(symbol)
            if len(openOrders) == 0:
                return []
            else:
                return self.client.cancel_open_orders(symbol, timestamp=time.time())
        else:
            openOrders = self.getOpenOrders(symbol, futures=True)

            if len(openOrders) == 0:
                return []
            else:
                orderIds = [order["orderId"] for order in openOrders]

                results = []
                for res in self.futuresClient.cancel_list_orders(
                    symbol=symbol, orderIdList=orderIds
                ):
                    results.append(res.toDict())

                return results

    def cancelOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        errorMessage = (
            "Specify either order Id in the exchange or local Id sent with the order"
        )
        if not futures:
            if orderId is not None:
                return self.client.cancel_order(
                    symbol, orderId=orderId, timestamp=time.time()
                )
            elif localOrderId is not None:
                return self.client.cancel_order(
                    symbol, origClientOrderId=localOrderId, timestamp=time.time()
                )
            else:
                raise ValueError(errorMessage)
        else:
            if orderId is not None:
                return self.futuresClient.cancel_order(symbol, orderId=orderId).toDict()
            elif localOrderId is not None:
                return self.futuresClient.cancel_order(
                    symbol, origClientOrderId=localOrderId
                ).toDict()
            else:
                raise ValueError(errorMessage)

    def getOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        errorMessage = (
            "Specify either order Id in the exchange or local Id sent with the order"
        )
        if not futures:
            if orderId is not None:
                return self.client.get_order(
                    symbol, orderId=orderId, timestamp=time.time()
                )
            elif localOrderId is not None:
                return self.client.get_order(
                    symbol, origClientOrderId=localOrderId, timestamp=time.time()
                )
            else:
                raise ValueError(errorMessage)
        else:
            if orderId is not None:
                return self.futuresClient.get_order(symbol, orderId=orderId).toDict()
            elif localOrderId is not None:
                return self.futuresClient.get_order(
                    symbol, origClientOrderId=localOrderId
                ).toDict()
            else:
                raise ValueError(errorMessage)

    def getTradingFees(self, symbol=None, futures=False):
        if symbol:
            return self.client.trade_fee(symbol=symbol)[0]
        else:
            return self.client.trade_fee(symbol=symbol)

    def getSymbolTickerPrice(self, symbol, futures=False):
        if futures:
            return self.futuresClient.get_symbol_price_ticker(symbol=symbol)[0].price
        else:
            return float(self.client.ticker_price(symbol)["price"])

    def getSymbolKlines(
        self,
        symbol,
        interval,
        startTime=None,
        endTime=None,
        limit=None,
        futures=False,
        blvtnav=False,
        convertDateTime=False,
        doClean=False,
        toCleanDataframe=False,
    ):
        if interval not in BinanceExchange.timeIntervals:
            raise ValueError("Time interval is not valid.")

        if futures:
            data = self._getFuturesSymbolKlines(
                blvtnav, endTime, interval, limit, startTime, symbol
            )
        else:
            data = self._getSpotSymbolKlines(
                endTime, interval, limit, startTime, symbol
            )

        if convertDateTime or toCleanDataframe:
            BinanceHelpers.klinesConvertDate(data, self.timeIndexesInCandleData)

        if doClean or toCleanDataframe:
            finalDataArray = BinanceHelpers.getKlinesDesiredOnlyCols(
                data, self.desiredCandleDataIndexes
            )

            if toCleanDataframe:
                return BinanceHelpers.klinesConvertToPandas(finalDataArray)
            return finalDataArray
        else:
            return data

    def _getSpotSymbolKlines(self, endTime, interval, limit, startTime, symbol):
        data = self.client.klines(
            symbol, interval, startTime=startTime, endTime=endTime, limit=limit
        )
        for datum in data:
            for idx in range(len(datum)):
                if idx in BinanceExchange.timeIndexesInCandleData:
                    continue
                datum[idx] = float(datum[idx])
        return data

    def _getFuturesSymbolKlines(
        self, blvtnav, endTime, interval, limit, startTime, symbol
    ):
        data = []
        if blvtnav:
            candles = self.futuresClient.get_blvt_nav_candlestick_data(
                symbol=symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            )
        else:
            candles = self.futuresClient.get_candlestick_data(
                symbol=symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            )
        for candle in candles:
            data.append(candle.toArray())
        return data

    def getExchangeTime(self, futures=False):
        try:
            if not futures:
                return self.client.time()["serverTime"]
            else:
                return self.futuresClient.get_servertime()
        except Exception:
            return None

    def getSymbol24hTicker(self, symbol):
        try:
            return self.client.ticker_24hr(symbol)
        except Exception:
            return None

    def testFuturesOrder(self, futuresOrderData):
        if not is_futures_order_data_valid(futuresOrderData):
            raise ValueError("Incomplete data provided.")
        return futuresOrderData

    def makeFuturesOrder(self, futuresOrderData):
        params = BinanceHelpers.getFuturesOrderAsDict(futuresOrderData)

        response = self.futuresClient.post_order(**params)
        return response.toDict()

    def createAndTestFuturesOrder(
        self,
        symbol,
        side,
        orderType,
        positionSide=None,
        timeInForce=None,
        quantity=None,
        reduceOnly=None,
        price=None,
        newClientOrderId=None,
        stopPrice=None,
        closePosition=None,
        activationPrice=None,
        callbackRate=None,
        workingType=None,
        priceProtect=None,
        newOrderRespType=None,
        recvWindow=None,
        extraParams=None,
        quoteQuantity=None,
    ):
        currOrder = DataHelpers.setFuturesOrderData(
            activationPrice,
            callbackRate,
            closePosition,
            extraParams,
            newClientOrderId,
            newOrderRespType,
            orderType,
            positionSide,
            price,
            priceProtect,
            quantity,
            reduceOnly,
            side,
            stopPrice,
            symbol,
            timeInForce,
            workingType,
            quoteQuantity,
        )

        self.testFuturesOrder(currOrder)

        return currOrder

    def makeBatchFuturesOrder(self, futuresOrderDatas):
        batchOrders = BinanceHelpers.makeBatchOrderData(futuresOrderDatas)

        orderResults = self.futuresClient.post_batch_order(batchOrders)

        return [order.toDict() for order in orderResults]

    def cancelAllSymbolFuturesOrdersWithCountDown(self, symbol, countdownTime):
        return self.futuresClient.auto_cancel_all_orders(symbol, countdownTime)

    def changeInitialLeverage(self, symbol, leverage):
        return self.futuresClient.change_initial_leverage(
            symbol=symbol, leverage=leverage
        ).toDict()["leverage"]

    def changeMarginType(self, symbol, marginType, params=None):
        if marginType not in ["ISOLATED", "CROSSED"]:
            raise ValueError("Margin type specified is not acceptable")
        try:
            result = self.futuresClient.change_margin_type(
                symbol=symbol, marginType=marginType
            )
            if result["code"] == 200:
                return True
            else:
                return False
        except BinanceApiException:
            pass

    def changePositionMargin(self, symbol, amount):
        if amount >= 0:
            addOrSub = 1
        else:
            addOrSub = 2
        result = self.futuresClient.change_position_margin(
            symbol=symbol, amount=amount, type=addOrSub
        )
        if result["code"] == 200:
            return True
        else:
            return False

    def getPosition(self):
        return self.futuresClient.get_position()

    def spotBestBidAsks(self, symbol):
        return self.client.book_ticker(symbol=symbol)

    def getSymbolOrderBook(self, symbol, limit=None, futures=False):
        if not futures:
            if limit is None:
                return self.client.depth(symbol)
            else:
                return self.client.depth(symbol, limit=limit)
        else:
            if limit is None:
                return self.futuresClient.get_order_book(symbol=symbol).toDict()
            else:
                return self.futuresClient.get_order_book(
                    symbol=symbol, limit=limit
                ).toDict()

    def getSymbolRecentTrades(self, symbol, limit=None, futures=False):
        if limit is not None:
            if limit > 1000:
                limit = 1000
            elif limit < 1:
                limit = 1
        if not futures:
            if limit is None:
                return pd.DataFrame(self.client.trades(symbol))
            else:
                return pd.DataFrame(self.client.trades(symbol, limit=limit))
        else:
            if limit is None:
                return pd.DataFrame(
                    self.futuresClient.get_recent_trades_list(symbol=symbol)
                )
            else:
                return pd.DataFrame(
                    self.futuresClient.get_recent_trades_list(
                        symbol=symbol, limit=limit
                    )
                )

    def getPositionInfo(self, symbol=None):
        return self.futuresClient.get_position_v2(symbol)

    def getSymbolMinTrade(self, symbol, futures=False):
        tickerPrice = self.getSymbolTickerPrice(symbol, futures=futures)

        if futures:
            exchangeInfo = self.futuresClient.get_exchange_information()

            for sym in exchangeInfo.symbols:
                if sym.symbol == symbol:
                    symbolFilters = sym.filters
                    return BinanceHelpers.extractSymbolInfoFromFilters(
                        symbolFilters, tickerPrice
                    )
            return None
        else:
            exchangeInfo = self.client.exchange_info()

            for sym in exchangeInfo["symbols"]:
                if sym["symbol"] == symbol:
                    symbolFilters = sym["filters"]
                    return BinanceHelpers.extractSymbolInfoFromFilters(
                        symbolFilters, tickerPrice
                    )
            return None

    def getIncomeHistory(
        self, symbol, incomeType=None, startTime=None, endTime=None, limit=None
    ):
        return self.futuresClient.get_income_history(
            symbol=symbol,
            incomeType=incomeType,
            startTime=startTime,
            endTime=endTime,
            limit=limit,
        )

    def makeSlTpLimitFuturesOrder(
        self,
        symbol,
        orderSide,
        quantity=None,
        quoteQuantity=None,
        enterPrice=None,
        takeProfit=None,
        stopLoss=None,
        leverage=None,
        marginType=None,
    ):
        symbolInfo = self.getSymbolMinTrade(symbol=symbol, futures=True)

        quantity = DataHelpers.getQuantity(
            enterPrice, quantity, quoteQuantity, symbolInfo["precisionStep"]
        )
        self._setLeverage(leverage, symbol)
        self.changeMarginType(symbol, marginType)
        tpSlOrderSide = "BUY" if orderSide.upper() == "SELL" else "SELL"

        mainOrder = self.createAndTestFuturesOrder(
            symbol,
            orderSide.upper(),
            "LIMIT",
            quantity=str(quantity),
            price=str(enterPrice),
            timeInForce="GTC",
        )

        stopLossOrder = self.createAndTestFuturesOrder(
            symbol,
            tpSlOrderSide,
            "STOP_MARKET",
            stopPrice=str(stopLoss),
            closePosition=True,
            priceProtect=True,
            workingType="MARK_PRICE",
            timeInForce="GTC",
        )

        takeProfitOrder = self.createAndTestFuturesOrder(
            symbol,
            tpSlOrderSide,
            "TAKE_PROFIT_MARKET",
            stopPrice=str(takeProfit),
            closePosition=True,
            priceProtect=True,
            workingType="MARK_PRICE",
            timeInForce="GTC",
        )

        orderingResult = self.makeBatchFuturesOrder(
            [mainOrder, stopLossOrder, takeProfitOrder]
        )

        orderIds = DataHelpers.getTpSlLimitOrderIds(orderingResult)

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
        symbolInfo = self.getSymbolMinTrade(symbol=symbol, futures=True)
        marketPrice = self.getSymbolTickerPrice(symbol=symbol, futures=True)

        quantity = DataHelpers.getQuantity(
            marketPrice, quantity, quoteQuantity, symbolInfo["precisionStep"]
        )
        self._setLeverage(leverage, symbol)
        self.changeMarginType(symbol, marginType)
        tpSlOrderSide = "BUY" if orderSide.upper() == "SELL" else "SELL"

        ordersList = []
        mainOrder = self.createAndTestFuturesOrder(
            symbol, orderSide.upper(), "MARKET", quantity=str(quantity)
        )

        ordersList.append(mainOrder)
        has_tp = False
        has_sl = False
        if stopLoss is not None:
            stopLossOrder = self.createAndTestFuturesOrder(
                symbol,
                tpSlOrderSide,
                "STOP_MARKET",
                stopPrice=str(stopLoss),
                closePosition=True,
                priceProtect=True,
                workingType="MARK_PRICE",
                timeInForce="GTC",
            )
            ordersList.append(stopLossOrder)
            has_sl = True

        if takeProfit is not None:
            takeProfitOrder = self.createAndTestFuturesOrder(
                symbol,
                tpSlOrderSide,
                "TAKE_PROFIT_MARKET",
                stopPrice=str(takeProfit),
                closePosition=True,
                priceProtect=True,
                workingType="MARK_PRICE",
                timeInForce="GTC",
            )
            ordersList.append(takeProfitOrder)
            has_tp = True

        orderingResult = self.makeBatchFuturesOrder(ordersList)

        orderIds = DataHelpers.getTpSlMarketOrderIds(
            orderingResult, has_sl=has_sl, has_tp=has_tp
        )
        return orderIds

    def _setLeverage(self, leverage, symbol):
        setLeverageResult = self.changeInitialLeverage(symbol, leverage)
        print("Leverage changed.")
        if isinstance(setLeverageResult, dict):
            if setLeverageResult["leverage"] != leverage:
                raise ConnectionError("Could not change leverage.")
        elif isinstance(setLeverageResult, float):
            if setLeverageResult != leverage:
                raise ConnectionError("Could not change leverage.")
        else:
            raise ConnectionError("Could not change leverage.")

    def getSymbolList(self, futures=False):
        if futures:
            symbolNames = []
            for symbolInfo in self.futuresClient.get_exchange_information().symbols:
                if symbolInfo.status == "TRADING":
                    symbolNames.append(symbolInfo.symbol)
            return symbolNames

    def getSymbol24hChanges(self, futures=False):
        symbolDatas = []
        if futures:
            symbolStatus = self.futuresClient.get_exchange_information().symbols
            for symbolInfo in self.futuresClient.get_ticker_price_change_statistics():
                if is_symbol_status_valid(
                    symbolInfo.symbol, symbolStatus, futures=True
                ):
                    symbolDatas.append(
                        (symbolInfo.symbol, symbolInfo.priceChangePercent)
                    )
        else:
            symbolStatus = self.client.exchange_info()["symbols"]
            for symbolInfo in self.client.ticker_24hr():
                if is_symbol_status_valid(
                    symbolInfo["symbol"], symbolStatus, futures=False
                ):
                    symbolDatas.append(
                        (symbolInfo["symbol"], float(symbolInfo["priceChangePercent"]))
                    )
        return sorted(symbolDatas, key=lambda x: x[1], reverse=True)

    def getLatestSymbolNames(self, numOfSymbols=None, futures=False):
        symbolDatas = []
        if futures:
            for symbolInfo in self.futuresClient.get_exchange_information().symbols:
                symbolDatas.append(
                    (
                        symbolInfo.symbol,
                        datetime.fromtimestamp(float(symbolInfo.onboardDate) / 1000),
                    )
                )
                symbolDatas.sort(key=lambda x: x[1], reverse=True)
            if numOfSymbols is not None and numOfSymbols > len(symbolDatas):
                numOfSymbols = len(symbolDatas)
        else:
            raise NotImplementedError("Only available for futures market.")

        return symbolDatas[:numOfSymbols]

    def getLongShortRatios(
        self, symbol, period, limit=None, startTime=None, endTime=None
    ):
        if limit is None:
            limit = 30
        topLongShortAccounts = self.futuresClient.get_top_long_short_accounts(
            symbol=symbol,
            period=period,
            startTime=startTime,
            endTime=endTime,
            limit=limit,
        )
        topLongShortPositions = self.futuresClient.get_top_long_short_positions(
            symbol=symbol,
            period=period,
            startTime=startTime,
            endTime=endTime,
            limit=limit,
        )
        longShortRatio = self.futuresClient.get_global_long_short_accounts(
            symbol=symbol,
            period=period,
            startTime=startTime,
            endTime=endTime,
            limit=limit,
        )

        return {
            "topLongShortAccounts": topLongShortAccounts,
            "topLongShortPositions": topLongShortPositions,
            "longShortRatio": longShortRatio,
        }

    def getDepositAddress(self, coin, network=None):
        return self.client.deposit_address(coin=coin, network=network)
