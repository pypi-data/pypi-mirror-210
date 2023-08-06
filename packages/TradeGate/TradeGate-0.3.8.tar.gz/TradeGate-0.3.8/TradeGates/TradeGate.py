"""
TradeGate - An algorithmic trading library to use as a gateway to different exchanges.
"""

__version__ = "0.3.2"

from Exchanges import BinanceExchange, BybitExchange, KuCoinExchange


def getCorrectExchange(exchangeName):
    if exchangeName.lower() == "binance":
        return BinanceExchange.BinanceExchange
    if exchangeName.lower() == "bybit":
        return BybitExchange.BybitExchange
    if exchangeName.lower() == "kucoin":
        return KuCoinExchange.KuCoinExchange


class TradeGate:
    def __init__(self, configDict, sandbox=False):
        self.exchangeName = configDict["exchangeName"]
        exchangeClass = getCorrectExchange(self.exchangeName)
        if sandbox:
            self.apiKey = configDict["credentials"]["test"]["spot"]["key"]
            self.apiSecret = configDict["credentials"]["test"]["spot"]["secret"]

            self.exchange = exchangeClass(
                configDict["credentials"]["test"], sandbox=True
            )
        else:
            self.apiKey = configDict["credentials"]["main"]["spot"]["key"]
            self.apiSecret = configDict["credentials"]["main"]["spot"]["secret"]

            self.exchange = exchangeClass(
                configDict["credentials"]["main"], sandbox=False
            )

    def getBalance(self, asset=None, futures=False):
        """Returns account balance of all assets or a single asset

        :param asset: a valid asset name, defaults to None
        :type asset: str , optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: Returns a single asset balance or list of assets if no asset was specified.
        :rtype: dict or list(dict)
        :Output with asset specified:

            .. code-block:: python

                {
                    'asset': 'BNB',
                    'free': '1000.00000000',
                    'locked': '0.00000000'
                }

        :Output without asset specified:

            .. code-block:: python

                [
                    {
                        'asset': 'BNB',
                        'free': '1000.00000000',
                        'locked': '0.00000000'
                    },
                    {
                        'asset': 'BTC',
                        'free': '1.02000000',
                        'locked': '0.00000000'
                    },
                    ...
                ]

        """
        return self.exchange.get_balance(asset, futures)

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
        """ Create a OrderData object and test the given parameters for validity. The object returned is then used \
        to send an order to the exchange by :func:`makeSpotOrder() <TradeGate.TradeGate.makeSpotOrder>`

        :param symbol: Symbol of the order
        :type symbol: str
        :param side: Side of the order. Either '**BUY**' or '**SELL**'
        :type side: str
        :param orderType: Type of the order. can be '**MARKET**', '**LIMIT**' or others (Check exchange's API documentation)
        :type orderType: str
        :param quantity: The amount of base asset of the order.
        :type quantity: float , optional
        :param price: Order price
        :type price: float , optional
        :param timeInForce: Order's time in force. Can be '**GTC**', '**IOC**', '**FOK**' or specific to the exchange. \
        Check the exchange's API documentation for more options.
        :type timeInForce: str , optional
        :param stopPrice: Price condition to trigger the order. Only for stop order type.
        :type stopPrice: float , optional
        :param icebergQty: Only for Binance. Amount of the base asset to be hide on the exchange.
        :type icebergQty: float , optional
        :param newOrderRespType: Only for Binance. Response of the order, either '**ACK**' or '**RESULT**'.
        :type newOrderRespType: str , optional
        :param newClientOrderId: Custom string to identify your order for yourself.
        :type newClientOrderId: str , optional
        :param extraParams: Extra parameters for other exchanges than Binance.
        :type extraParams: dict , optional
        :return: An orderData object of the created order, ready to be submitted using \
        :func:`makeSpotOrder() <TradeGate.TradeGate.makeSpotOrder>`
        :rtype: OrderData

        :Notes:

            * Input parameters are based on Binance API. We map the appropriate parameters from input to the exchange \
            requirements, but other parameters must be inside the '**extraParams**' dictionary.
            * Some parameters have values that are only valid for some exchanges. See each exchange's documentation for\
             these values.
            * ValueError exception is raised when wrong combination of parameters are sent. Check the exception's \
            message for guidance.
            * Do not send '**price**' with '**MARKET**' orders.
            * You must specify '**price**' for '**LIMIT**' orders.
            * For **ByBit**:

                * Order type can only be '**MARKET**', '**LIMIT**' or '**LIMIT_MAKER**'

            * For **KuCoin**:

                * To send a stop order, set '**orderType**' to **STOP_MARKET** or **STOP_LIMIT**.
                * Send '**stop**' (either **loss** or **entry**) in the '**extraParams**' when specifying '**stopPrice**'.
                * You can send '**cancelAfter**' parameter inside '**extraParams**' to cancel order after **n** seconds \
                only if '**timeInForce**' value is **GTT**
                * You can send '**postOnly**', '**hidden**', '**iceberg**' (bool) and '**visibleSize**' parameters inside \
                '**extraParams**'.
                * Valid values for the '**timeInForce**' variable: **GTC** (Good Till Cancel), **IOC** \
                (Immediate Or Cancel), **GTT** (Good Till Time) and **FOK** (Fill Or Kill)

        """
        return self.exchange.createAndTestSpotOrder(
            symbol,
            side,
            orderType,
            quantity,
            price,
            timeInForce,
            stopPrice,
            icebergQty,
            newOrderRespType,
            newClientOrderId,
            extraParams,
        )

    def makeSpotOrder(self, orderData):
        """Make a spot order

        :param orderData: OrderData created using :func:`makeSpotOrder() <TradeGate.TradeGate.makeSpotOrder>`
        :type orderData: OrderData
        :return: submitted order information
        :rtype: dict
        :Output:

            .. code-block:: python

                {
                    'symbol': 'BTCUSDT',
                    'orderId': 7048832,
                    'orderListId': -1,
                    'clientOrderId': 'Jes2sprMLHxEUXHyJOUEAr',
                    'transactTime': 1656343106986,
                    'price': '20000.00000000',
                    'origQty': '0.00200000',
                    'executedQty': '0.00000000',
                    'cummulativeQuoteQty': '0.00000000',
                    'status': 'NEW',
                    'timeInForce': 'GTC',
                    'type': 'LIMIT',
                    'side': 'BUY',
                    'fills': []
                }

        """
        return self.exchange.makeSpotOrder(orderData)

    def getSymbolOrders(
        self,
        symbol,
        futures=False,
        orderId=None,
        startTime=None,
        endTime=None,
        limit=None,
    ):
        """Get History of orders submitted

        :param symbol: The order's symbol
        :type symbol: str
        :param orderId: Only return orders from the order with this orderId onwards.
        :type orderId: long, optional
        :param startTime: Timestamp for the start of the data
        :type startTime: long, optional
        :param endTime: Timestamp for the end of the data
        :type endTime: long, optional
        :param limit: Maximum number of order datas to return
        :type limit: int, optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: A list of orders datas
        :rtype: list(dict)
        :Output:

            .. code-block:: python

                [
                    {
                        'symbol': 'BTCUSDT',
                        'orderId': 7020578,
                        'orderListId': -1,
                        'clientOrderId': 'tI8wxMsbaUk6hcf5QpC8zx',
                        'price': '20000.00000000',
                        'origQty': '0.00200000',
                        'executedQty': '0.00000000',
                        'cummulativeQuoteQty': '0.00000000',
                        'status': 'NEW',
                        'timeInForce': 'GTC',
                        'type': 'LIMIT',
                        'side': 'BUY',
                        'stopPrice': '0.00000000',
                        'icebergQty': '0.00000000',
                        'time': 1656338254295,
                        'updateTime': 1656338254295,
                        'isWorking': True,
                        'origQuoteOrderQty': '0.00000000'
                    },
                    {
                        'symbol': 'BTCUSDT',
                        'orderId': 7048832,
                        'orderListId': -1,
                        'clientOrderId': 'Jes2sprMLHxEUXHyJOUEAr',
                        'price': '20000.00000000',
                        'origQty': '0.00200000',
                        'executedQty': '0.00000000',
                        'cummulativeQuoteQty': '0.00000000',
                        'status': 'NEW',
                        'timeInForce': 'GTC',
                        'type': 'LIMIT',
                        'side': 'BUY',
                        'stopPrice': '0.00000000',
                        'icebergQty': '0.00000000',
                        'time': 1656343106986,
                        'updateTime': 1656343106986,
                        'isWorking': True,
                        'origQuoteOrderQty': '0.00000000'
                    }
                ]

        :Notes:

            * Specify the symbol for better output.

        """
        return self.exchange.getSymbolOrders(
            symbol=symbol,
            futures=futures,
            orderId=orderId,
            startTime=startTime,
            endTime=endTime,
            limit=limit,
        )

    def getOpenOrders(self, symbol, futures=False):
        """Get order datas of all open orders for a symbol

        :param symbol: The symbol
        :type symbol: str
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: Order datas of the open orders
        :rtype: list(dict)
        :Output:

            .. code-block:: python

                [
                    {
                        'symbol': 'BTCUSDT',
                        'orderId': 3051997664,
                        'clientOrderId': 'VhxN3SezOKgpvACYe2qhO6',
                        'transactTime': 1656337589565,
                        'price': 20000.0,
                        'origQty': 0.002,
                        'executedQty': 0.0,
                        'cummulativeQuoteQty': 0.0,
                        'status': 'NEW',
                        'timeInForce': 'GTC',
                        'type': 'LIMIT',
                        'side': 'BUY',
                        'extraData':
                        {
                            'reduceOnly': False,
                            'stopPrice': 0.0,
                            'workingType': 'CONTRACT_PRICE',
                            'avgPrice': 0.0,
                            'origType': 'LIMIT',
                            'positionSide': 'BOTH',
                            'activatePrice': None,
                            'priceRate': None,
                            'closePosition': False
                        }
                    },
                    {
                        'symbol': 'BTCUSDT',
                        'orderId': 3051997723,
                        'clientOrderId': 'v1nT9fQjDGVRqHBtDYotTh',
                        'transactTime': 1656337600701,
                        'price': 20000.0,
                        'origQty': 0.002,
                        'executedQty': 0.0,
                        'cummulativeQuoteQty': 0.0,
                        'status': 'NEW',
                        'timeInForce': 'GTC',
                        'type': 'LIMIT',
                        'side': 'BUY',
                        'extraData':
                        {
                            'reduceOnly': False,
                            'stopPrice': 0.0,
                            'workingType':
                            'CONTRACT_PRICE',
                            'avgPrice': 0.0,
                            'origType': 'LIMIT',
                            'positionSide': 'BOTH',
                            'activatePrice': None,
                            'priceRate': None,
                            'closePosition': False
                        }
                    }
                ]

        """
        return self.exchange.getOpenOrders(symbol, futures)

    def getOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        """Get an order's data

        :param symbol: The Order's symbol
        :type symbol: str
        :param orderId: Exchange assigned '**orderId**' of the order.
        :type orderId: long, optional
        :param localOrderId: User assigned '**clientOrderId**' of the order.
        :type localOrderId: long, optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: The order data
        :rtype: dict
        :Output:

            .. code-block:: python

                {
                    'symbol': 'BTCUSDT',
                    'orderId': 3051988035,
                    'clientOrderId': '1656335100',
                    'transactTime': 1656335103251,
                    'price': 20000.0,
                    'origQty': 0.002,
                    'executedQty': 0.0,
                    'cummulativeQuoteQty': 0.0,
                    'status': 'CANCELED',
                    'timeInForce': 'GTC',
                    'type': 'LIMIT',
                    'side': 'BUY',
                    'extraData':
                    {
                        'reduceOnly': False,
                        'stopPrice': 0.0,
                        'workingType': 'CONTRACT_PRICE',
                        'avgPrice': 0.0,
                        'origType': 'LIMIT',
                        'positionSide': 'BOTH',
                        'activatePrice': None,
                        'priceRate': None,
                        'closePosition': False
                    }
                }

        :Notes:

            * Must specify either '**orderId**' or '**localOrderId**'

        """
        return self.exchange.getOrder(symbol, orderId, localOrderId, futures=futures)

    def cancelAllSymbolOpenOrders(self, symbol, futures=False):
        """Cancel all active orders of a symbol

        :param symbol: The symbol
        :type symbol: str
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: Order datas of the cancelled orders
        :rtype: list(dict)
        :Output:

            .. code-block:: python

                [
                    {
                        'symbol': 'BTCUSDT',
                        'orderId': 3051990476,
                        'clientOrderId': 'sDAclHSkWaO5R3fHYwI9IQ',
                        'transactTime': 1656335835113,
                        'price': 20000.0,
                        'origQty': 0.002,
                        'executedQty': 0.0,
                        'cummulativeQuoteQty': 0.0,
                        'status': 'CANCELED',
                        'timeInForce': 'GTC',
                        'type': 'LIMIT',
                        'side': 'BUY',
                        'extraData':
                        {
                            'reduceOnly': False,
                            'stopPrice': 0.0,
                            'workingType': 'CONTRACT_PRICE',
                            'avgPrice': 0.0,
                            'origType': 'LIMIT',
                            'positionSide': 'BOTH',
                            'activatePrice': None,
                            'priceRate': None,
                            'closePosition': False
                        }
                    },
                    {
                        'symbol': 'BTCUSDT',
                        'orderId': 3051990465,
                        'clientOrderId': 'SxyPikUE9ysMSZ8jbKGQAZ',
                        'transactTime': 1656335835113,
                        'price': 20000.0,
                        'origQty': 0.002,
                        'executedQty': 0.0,
                        'cummulativeQuoteQty': 0.0,
                        'status': 'CANCELED',
                        'timeInForce': 'GTC',
                        'type': 'LIMIT',
                        'side': 'BUY',
                        'extraData':
                        {
                            'reduceOnly': False,
                            'stopPrice': 0.0,
                            'workingType': 'CONTRACT_PRICE',
                            'avgPrice': 0.0,
                            'origType': 'LIMIT',
                            'positionSide': 'BOTH',
                            'activatePrice': None,
                            'priceRate': None,
                            'closePosition': False
                        }
                    }
                ]

        """
        return self.exchange.cancelAllSymbolOpenOrders(symbol, futures)

    def cancelOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        """Cancel an active order

        :param symbol: The Order's symbol
        :type symbol: str
        :param orderId: Exchange assigned '**orderId**' of the order.
        :type orderId: long, optional
        :param localOrderId: User assigned '**clientOrderId**' of the order.
        :type localOrderId: long, optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: The order data of the canceled order
        :rtype: dict
        :Output:

            .. code-block:: python

                {
                    'symbol': 'BTCUSDT',
                    'orderId': 3051988035,
                    'clientOrderId': '1656335100',
                    'transactTime': 1656335103251,
                    'price': 20000.0,
                    'origQty': 0.002,
                    'executedQty': 0.0,
                    'cummulativeQuoteQty': 0.0,
                    'status': 'CANCELED',
                    'timeInForce': 'GTC',
                    'type': 'LIMIT',
                    'side': 'BUY',
                    'extraData':
                    {
                        'reduceOnly': False,
                        'stopPrice': 0.0,
                        'workingType': 'CONTRACT_PRICE',
                        'avgPrice': 0.0,
                        'origType': 'LIMIT',
                        'positionSide': 'BOTH',
                        'activatePrice': None,
                        'priceRate': None,
                        'closePosition': False
                    }
                }

        :Notes:

            * Must specify either '**orderId**' or '**localOrderId**'

        """
        return self.exchange.cancelOrder(symbol, orderId, localOrderId, futures)

    def getTradingFees(self, symbol=None, futures=None):
        """Get the fee structure of the exchange

        :param symbol: Trading fee for a specific symbol
        :type symbol: str, optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: The fee structure of the exchange
        :rtype: dict
        :Output:

            .. code-block:: python

                {
                    'symbol': 'BTCUSDT',
                    'makerCommission': '0.001',
                    'takerCommission': '0.001'
                }

        :Notes:

            * Specify the symbol for better output.
        """
        return self.exchange.getTradingFees(symbol=symbol, futures=futures)

    def getSymbolTickerPrice(self, symbol, futures=False):
        """Get the latest price of a symbol

        :param symbol: Symbol
        :type symbol: str
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: The latest price of the symbol specified as a float number
        :rtype: float
        :Output:

            .. code-block:: python

                21275.84

        """
        return self.exchange.getSymbolTickerPrice(symbol, futures)

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
        """ Get a symbol's Klines (candlestick) data

        :param symbol: The symbol to fetch the klines
        :type symbol: str
        :param interval: The interval of klines data
        :type interval: str
        :param startTime: Timestamp for the start time of the data
        :type startTime: long , optional
        :param endTime: Timestamp for the end time of the data
        :type endTime: long , optional
        :param limit: Number of klines data (candlesticks) to be returned
        :type limit: int , optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :param blvtnav: Only for **Binance**. Return the blvtnav data.
        :type blvtnav: bool , optional
        :param convertDateTime: Convert the timestamps to datetime objects in the returned data
        :type convertDateTime: bool , optional
        :param doClean: Only return desired columns of the data
        :type doClean: bool , optional
        :param toCleanDataframe: Returned Pandas dataframe object of the data with desired columns
        :type toCleanDataframe: bool , optional
        :return: Either a 2D array containing the data or a pandas dataframe object of the data
        :rtype: list(list)) or pandas.DataFrame
        :Output as list:

            .. code-block:: python

                [
                    [
                        1656327600000,
                        21437.18,
                        21445.56,
                        21380.02,
                        21428.66,
                        525.2881,
                        1656328499999,
                        11246729.6314567,
                        9626.0, 277.31647,
                        5936870.8288083,
                        0.0
                    ],
                    [
                        1656328500000,
                        21428.66,
                        21450.0,
                        21339.83,
                        21376.49,
                        477.24441,
                        1656329399999,
                        10206890.129678,
                        9503.0, 208.56099,
                        4459849.0304778,
                        0.0
                    ]
                ]

        :Output as DataFrame:

            .. code-block:: python

                                         open      high       low     close   \

                date
                2022-06-27 16:15:00  21367.67  21376.00  21285.48  21304.55
                2022-06-27 16:30:00  21304.56  21329.91  21301.24  21308.73

                                        volume            closeDate  tradesNum
                date
                2022-06-27 16:15:00  470.24040  2022-06-27 16:29:59     8980.0
                2022-06-27 16:30:00  113.05128  2022-06-27 16:44:59     2693.0

        :Notes:

            * '**startTime**' and '**endTime**' variables must be timestamps. If neither are sent, will return the \
            latest data.
            * '**limit**' parameter has a maximum value (usually 1000). if the given limit number is bigger than that, \
            only the maximum number will be fetched.
            * Desired columns are: **open** - **high** - **low** - **close** - **volume** - **closeDate** \
            - **tradesNum**

        """
        return self.exchange.getSymbolKlines(
            symbol,
            interval,
            startTime,
            endTime,
            limit,
            futures,
            blvtnav,
            convertDateTime,
            doClean,
            toCleanDataframe,
        )

    def getExchangeTime(self, futures=False):
        """Get time of the exchange

        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: Timestamp of the current time on the server
        :rtype: int
        :Output:

            .. code-block:: python

                1656330049381

        """
        return self.exchange.getExchangeTime(futures)

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
        extraParams=None,
        quoteQuantity=None,
    ):
        """ Create a FuturesOrderData object and test the given parameters for validity. The object returned is then used \
        to send an order to the exchange by :func:`makeFuturesOrder() <TradeGate.TradeGate.makeFuturesOrder>`

        :param symbol: Symbol of the order
        :type symbol: str
        :param side: Side of the order. Either '**BUY**' or '**SELL**'
        :type side: str
        :param orderType: Type of the order. can be '**MARKET**', '**LIMIT**' or others (Check exchange's API documentation)
        :type orderType: str
        :param positionSide: Only for binance. '**BOTH**' for One-way Mode and '**LONG**' or '**SHORT**' for Hedge Mode.\
         It must be sent in Hedge Mode.
        :type positionSide: str , optional
        :param timeInForce: Order's time in force. Can be '**GTC**', '**IOC**', '**FOK**' or specific to the exchange. \
        Check the exchange's API documentation for more options.
        :type timeInForce: str , optional
        :param quantity: The amount of base asset of the order.
        :type quantity: float , optional
        :param reduceOnly: A flag to reduce the position size only.
        :type reduceOnly: bool , optional
        :param price: Order price
        :type price: float , optional
        :param newClientOrderId: Custom string to identify your order for yourself.
        :type newClientOrderId: str , optional
        :param stopPrice: Price condition to trigger the order. Only for stop order type.
        :type stopPrice: float , optional
        :param closePosition: Whether to close the current open position or not.
        :type closePosition: bool , optional
        :param activationPrice: Only for Binance. Used with '**TRAILING_STOP_MARKET**' order type.
        :type activationPrice: float , optional
        :param callbackRate: Only for Binance. Used with TRAILING_STOP_MARKET orders and specifies callback percentage.
        :type callbackRate: float , optional
        :param workingType: With what price the stop order is triggered: '**MARK_PRICE**' or '**CONTRACT_PRICE**'
        :type workingType: str , optional
        :param priceProtect: Only for Binance. Whether to protect the stop order from large difference of mark price \
        and contract price.
        :type priceProtect: bool , optional
        :param newOrderRespType: Only for Binance. Response of the order, either '**ACK**' or '**RESULT**'.
        :type newOrderRespType: str , optional
        :param extraParams: Extra parameters for other exchanges than Binance.
        :type extraParams: dict , optional
        :param quoteQuantity: The amount of quote asset of the order.
        :type quoteQuantity: float , optional
        :return: An orderData object of the created order, ready to be submitted using \
        :func:`makeFuturesOrder() <TradeGate.TradeGate.makeFuturesOrder>`
        :rtype: OrderData

        :Notes:

            * Input parameters are based on Binance API. We map the appropriate parameters from input to the exchange \
            requirements, but other parameters must be inside the '**extraParams**' dictionary.
            * Preferably use '**quantity**' instead of '**quoteQuantity**'. Some exchanges don't accept this parameter \
            and we convert it to the quantity based on the price (if provided) or current market price.
            * Some parameters have values that are only valid for some exchanges. See each exchange's documentation for\
             these values.
            * ValueError exception is raised when wrong combination of parameters are sent. Check the exception's \
            message for guidance.
            * Do not send '**price**' with '**MARKET**' orders.
            * You must specify '**price**' for '**LIMIT**' orders.
            * Other than **ByBit**, \
            use :func:`makeSlTpLimitFuturesOrder() <TradeGate.TradeGate.makeSlTpLimitFuturesOrder>` or \
            :func:`makeSlTpMarketFuturesOrder() <TradeGate.TradeGate.makeSlTpMarketFuturesOrder>` to send take profit \
            and stop loss.
            * if '**closePosition**' is used, do not specify '**quantity**' or '**quoteQuantity**'.
            * For **ByBit**:

                * You can send take profit by specifying '**take_profit**' (price) and '**tp_trigger_by**' \
                ('**LastPrice**', '**IndexPrice**' or '**MarkPrice**') in '**extraParams**'.
                * You can send take profit by specifying '**stop_loss**' (price) and '**sl_trigger_by**' \
                ('**LastPrice**', '**IndexPrice**' or '**MarkPrice**') in '**extraParams**'.

            * For **KuCoin**:

                * You must send '**leverage**' parameter inside '**extraParams**' for the **KuCoin** exchange.
                * Send '**stop**' (either '**down**' or '**up**') and '**stopPriceType**' (either '**TP**', '**IP**' \
                or '**MP**') in the '**extraParams**' when specifying '**stopPrice**'.
                * You can send '**postOnly**', '**hidden**', '**iceberg**' and '**visibleSize**' parameters inside \
                '**extraParams**'.
                * There are two values for the '**timeInForce**' variable: '**GTC**' (Good Till Cancel) and '**IOC**' \
                (Immediate Or Cancel)


        """
        return self.exchange.createAndTestFuturesOrder(
            symbol,
            side,
            orderType,
            positionSide,
            timeInForce,
            quantity,
            reduceOnly,
            price,
            newClientOrderId,
            stopPrice,
            closePosition,
            activationPrice,
            callbackRate,
            workingType,
            priceProtect,
            newOrderRespType,
            extraParams,
        )

    def makeFuturesOrder(self, futuresOrderData):
        """Make a futures order

        :param futuresOrderData: OrderData created using :func:`makeFuturesOrder() <TradeGate.TradeGate.makeFuturesOrder>`
        :type futuresOrderData: OrderData
        :return: submitted order information
        :rtype: dict
        :Output:

            .. code-block:: python

                {
                    'symbol': 'BTCUSDT',
                    'orderId': 3049327900,
                    'clientOrderId': 'aLHt4lEJzO2Xeh21GebGCz0',
                    'transactTime': 1655704960910,
                    'price': 0.0,
                    'origQty': 0.003,
                    'executedQty': 0.0,
                    'cummulativeQuoteQty': 0.0,
                    'status': 'NEW',
                    'timeInForce': 'GTC',
                    'type': 'MARKET',
                    'side': 'BUY',
                    'extraData':
                        {
                            'reduceOnly': False,
                            'stopPrice': 0.0,
                            'workingType':
                            'CONTRACT_PRICE',
                            'avgPrice': 0.0,
                            'origType': 'MARKET',
                            'positionSide': 'BOTH',
                            'activatePrice': None,
                            'priceRate': None,
                            'closePosition': False
                        }
                    }

        """
        return self.exchange.makeFuturesOrder(futuresOrderData)

    def makeBatchFuturesOrder(self, batchOrders):
        """ Make multiple futures order with single request

        :param batchOrders: list of OrderDatas created using :func:`makeFuturesOrder() <TradeGate.TradeGate.makeFuturesOrder>`
        :type batchOrders: list(OrderData)
        :return: List of order information submitted
        :rtype: list(dict)
        :Output:

            .. code-block:: python

                [
                    {
                        'symbol': 'BTCUSDT',
                        'orderId': 3049327900,
                        'clientOrderId': 'aLHt4lEJzO2Xeh21GebGCz0',
                        'transactTime': 1655704960910,
                        'price': 0.0,
                        'origQty': 0.003,
                        'executedQty': 0.0,
                        'cummulativeQuoteQty': 0.0,
                        'status': 'NEW',
                        'timeInForce': 'GTC',
                        'type': 'MARKET',
                        'side': 'BUY',
                        'extraData':
                        {
                            'reduceOnly': False,
                            'stopPrice': 0.0,
                            'workingType':
                            'CONTRACT_PRICE',
                            'avgPrice': 0.0,
                            'origType': 'MARKET',
                            'positionSide': 'BOTH',
                            'activatePrice': None,
                            'priceRate': None,
                            'closePosition': False
                        }
                    },
                    {
                        'symbol': 'BTCUSDT',
                        'orderId': 3049327901,
                        'clientOrderId': 'hUacgz6xW3Vp71sc8yztxK1',
                        'transactTime': 1655704960910,
                        'price': 0.0,
                        'origQty': 0.005,
                        'executedQty': 0.0,
                        'cummulativeQuoteQty': 0.0,
                        'status': 'NEW',
                        'timeInForce': 'GTC',
                        'type': 'MARKET',
                        'side': 'BUY',
                        'extraData':
                        {
                            'reduceOnly': False,
                            'stopPrice': 0.0,
                            'workingType':
                            'CONTRACT_PRICE',
                            'avgPrice': 0.0,
                            'origType': 'MARKET',
                            'positionSide': 'BOTH',
                            'activatePrice': None,
                            'priceRate': None,
                            'closePosition': False
                        }
                    }
                ]

        :Notes:

            * Not available for **KuCoin** exchange.
            * The execution of orders in the batch are not dependent on each other, so be careful if orders depend on \
            one another.

        """
        return self.exchange.makeBatchFuturesOrder(batchOrders)

    def changeInitialLeverage(self, symbol, leverage):
        """Change initial leverage for a symbol

        :param symbol: Futures symbol
        :type symbol: str
        :param leverage: Initial leverage number.
        :type leverage: int
        :return: The number of leverage
        :rtype: int
        :Output:

            .. code-block:: python

                10

        :Notes:

            * Not available for **KuCoin** exchange. You must specify leverage when sending an order for this exchange.

        """
        return self.exchange.changeInitialLeverage(symbol, leverage)

    def changeMarginType(self, symbol, marginType, params=None):
        """ Change position margin of a symbol

        :param symbol: Symbol of the position
        :type symbol: str
        :param marginType: Type of the margin. Either '**ISOLATED**' or '**CROSSED**'.
        :type marginType: str
        :param params: Extra data needed for some exchanges.
        :type params: dict , optional
        :return: True if changing was successful or False if unsuccessful
        :rtype: bool
        :Output:

            .. code-block:: python

                True

        :Notes:

            * For **KuCoin**, '**CROSSED**' means enabling '**auto_add_margin**', and '**ISOLATED**' means disabling it.
            * For **ByBit**, you must specify '**buyLeverage**' and '**sellLeverage**' inside params. If switching from \
            '**CROSSED**' to '**ISOLATED**', theses two numbers must be equal.

        """
        return self.exchange.changeMarginType(symbol, marginType, params)

    def changePositionMargin(self, symbol, amount):
        """ Change position margin of a symbol

        :param symbol: Symbol of the position
        :type symbol: str
        :param amount: Amount to be added (or subtracted)
        :type amount: float
        :return: True if changing was successful or False if unsuccessful
        :rtype: bool
        :Output:

            .. code-block:: python

                True

        :Notes:

            * The amount can be positive or negative for **Binance** exchange but it must be positive for other exchanges.
            * Use :func:`changeMarginType() <TradeGate.TradeGate.changeMarginType>` to make current position available \
            for changing amount.

        """
        return self.exchange.changePositionMargin(symbol, amount)

    def spotBestBidAsks(self, symbol=None):
        """Returns best bid and best ask price with their quantities

        :param symbol: Symbol name of the orders
        :type symbol: str
        :return: A dictionary with best bid and ask with their quantity
        :rtype: dict
        :Output:

            .. code-block:: python

                {
                    'symbol': 'BTC-USDT',
                    'bidPrice': '18125.7',
                    'bidQty': '0.00839998',
                    'askPrice': '18126',
                    'askQty': '0.00496777'
                }

        """
        return self.exchange.spotBestBidAsks(symbol)

    def getSymbolOrderBook(self, symbol, limit=None, futures=False):
        """Returns list of current orders in the orderbook of the exchange

        :param symbol: Symbol name of the orders
        :type symbol: str
        :param limit: Maximum number of returned bids and asks
        :type limit: int , Optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: A dictionary with bids and asks. Each bid and ask is a tuple of price and quantity.
        :rtype: dict
        :Output (limit=5):

            .. code-block:: python

                {
                    'lastUpdateId': 1630819351623,
                    'bids': [
                        ['18009.90', '0.557'],
                        ['18009.80', '0.076'],
                        ['18009.30', '0.002'],
                        ['18009.20', '0.004'],
                        ['18008.20', '0.038']
                    ],
                    'asks': [
                        ['18010.00', '0.464'],
                        ['18010.50', '0.101'],
                        ['18010.70', '0.099'],
                        ['18010.90', '0.017'],
                        ['18011.20', '0.206']
                    ]
                }

        """
        return self.exchange.getSymbolOrderBook(symbol, limit, futures)

    def getSymbolRecentTrades(self, symbol, limit=None, futures=False):
        """Returns list of the recent trades for a symbol

        :param symbol: Symbol name of the trades
        :type symbol: str
        :param limit: Maximum number of returned trade datas
        :type limit: int , Optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: A data frame of the trade infos
        :rtype: pandas.DataFrame
        :Output columns:

            * **id** (:py:class:`int`) - ID of the trade
            * **price** (:py:class:`float`) - Price of the trade
            * **qty** (:py:class:`float`) - Amount of the base asset
            * **quoteQty** (:py:class:`float`) - Amount of the quote asset
            * **time** (:py:class:`int`) - Timestamp of the trade
            * **isBuyerMaker** (:py:class:`bool`) - If trade is buyer-maker

        """
        return self.exchange.getSymbolRecentTrades(symbol, limit, futures)

    def symbolAccountTradeHistory(self, symbol, fromId=None, limit=None, futures=False):
        """Returns list of the trade history for user orders

        :param symbol: Symbol name of the trades
        :type symbol: str
        :param fromId: Only return trades from the specified id forward.
        :type fromId: str , Optional
        :param limit: Maximum number of returned trade datas
        :type limit: int , Optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: A list of trade datas
        :rtype: list(dict)
        :Output:

            .. code-block:: python

                [
                    {
                        'symbol': 'BTCUSDT',
                        'id': 233453846,
                        'orderId': 3046255912,
                        'orderListId': None,
                        'price': 27426.7,
                        'qty': 0.61,
                        'quoteQty': 16730.287,
                        'commission': 0.0,
                        'commissionAsset': 'USDT',
                        'time': 1655001759033,
                        'isBuyer': False,
                        'isMaker': False,
                        'isBestMatch': None
                    },
                    {
                        'symbol': 'BTCUSDT',
                        'id': 233480351,
                        'orderId': 3046360099,
                        'orderListId': None,
                        'price': 27300.0,
                        'qty': 0.002,
                        'quoteQty': 54.6,
                        'commission': 0.02184,
                        'commissionAsset': 'USDT',
                        'time': 1655027380068,
                        'isBuyer': True,
                        'isMaker': False,
                        'isBestMatch': None
                    },
                    ...
                ]

        :Notes:

            * The **orderListId** returned parameter is either None or -1 if order was made with API.
            * The **isBestMatch** returned parameter is not reliable and not available on most of the exchanges.
        """
        return self.exchange.symbolAccountTradeHistory(
            symbol=symbol, futures=futures, fromId=fromId, limit=limit
        )

    def makeSlTpLimitFuturesOrder(
        self,
        symbol,
        orderSide,
        enterPrice,
        quantity=None,
        quoteQuantity=None,
        takeProfit=None,
        stopLoss=None,
        leverage=None,
        marginType=None,
    ):
        """Make market price futures order with take profit and stop loss.

        :param symbol: Name of the symbol
        :type symbol: str
        :param orderSide: Side of the order.
        :type orderSide: str
        :param enterPrice: Limit price of the order
        :type enterPrice: float , optional
        :param quantity: Amount of the base asset
        :type quantity: float , optional
        :param quoteQuantity: Amount of the quote asset
        :type quoteQuantity: float , optional
        :param takeProfit: Take profit price
        :type takeProfit: float , optional
        :param stopLoss: Stop loss price
        :type stopLoss: float , optional
        :param leverage: Desired leverage for the order.
        :type leverage: int , optional
        :param marginType: Margin type of the order
        :type marginType: str , optional
        :return: Returns orderID's of the orders submitted.
        :rtype: dict
        :Output:

            .. code-block:: python

                {
                    'mainOrder': 3048448085,
                    'stopLoss': 3048448086,
                    'takeProfit': 3048448087
                }

        :Notes:

            * The **orderSide** parameter can either be **BUY** or **SELL**.
            * Should specify either **quantity** or **quoteQuantity**.
            * The **leverage** parameter is mandatory for the following exchanges:

                * KuCoin

            * The **marginType** is currently only valid for **Binance** exchange.
            * Be careful with the **takeProfit** and **stopLoss** prices, if they would trigger immidietly, there will be an error.
            * Use with a try catch block preferably.

        """
        return self.exchange.makeSlTpLimitFuturesOrder(
            symbol,
            orderSide,
            quantity,
            quoteQuantity,
            enterPrice,
            takeProfit,
            stopLoss,
            leverage,
            marginType,
        )

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
        """Make market price futures order with take profit and stop loss.

        :param symbol: Name of the symbol
        :type symbol: str
        :param orderSide: Side of the order.
        :type orderSide: str
        :param quantity: Amount of the base asset
        :type quantity: float , optional
        :param quoteQuantity: Amount of the quote asset
        :type quoteQuantity: float , optional
        :param takeProfit: Take profit price
        :type takeProfit: float , optional
        :param stopLoss: Stop loss price
        :type stopLoss: float , optional
        :param leverage: Desired leverage for the order.
        :type leverage: int , optional
        :param marginType: Margin type of the order
        :type marginType: str , optional
        :return: Returns orderID's of the orders submitted.
        :rtype: dict
        :Output:

            .. code-block:: python

                {
                    'mainOrder': 3048424829,
                    'stopLoss': 3048424830,
                    'takeProfit': 3048424828
                }

        :Notes:

            * The **orderSide** parameter can either be **BUY** or **SELL**.
            * Should specify either **quantity** or **quoteQuantity**.
            * The **leverage** parameter is mandatory for the following exchanges:

                * KuCoin
            * The **marginType** is currently only valid for **Binance** exchange.
            * Be careful with the **takeProfit** and **stopLoss** prices, if they would trigger immidietly, there will be an error.
            * Use with a try catch block preferably.

        """
        return self.exchange.makeSlTpMarketFuturesOrder(
            symbol,
            orderSide,
            quantity,
            quoteQuantity,
            takeProfit,
            stopLoss,
            leverage,
            marginType,
        )

    def getPositionInfo(self, symbol=None):
        """Returns information of  position or positions. (Only for futures accounts)

        :param symbol: The symbol of the position
        :type symbol: str , optional
        :return: A list of position information. If the symbol parameter is given, the list will contain only one element.
        :rtype: list(dict)
        :Output with symbol specified:

            .. code-block:: python

                [
                    {
                        'entryPrice': 19229.6,
                        'isAutoAddMargin': True,
                        'leverage': 10.0,
                        'maxNotionalValue': 1000000.0,
                        'liquidationPrice': 20935.5130297,
                        'markPrice': 19222.55166016,
                        'positionAmt': -0.01,
                        'symbol': 'BTCUSDT',
                        'unrealizedProfit': 0.07048339,
                        'marginType': 'isolated',
                        'isolatedMargin': 19.22316499,
                        'positionSide': 'BOTH'
                    }
                ]

        :Output without symbol specified:

            .. code-block:: python

                [
                    {
                        'entryPrice': 0.0,
                        'isAutoAddMargin': True,
                        'leverage': 20.0,
                        'maxNotionalValue': 25000.0,
                        'liquidationPrice': 0.0,
                        'markPrice': 0.0,
                        'positionAmt': 0.0,
                        'symbol': 'RAYUSDT',
                        'unrealizedProfit': 0.0,
                        'marginType': 'cross',
                        'isolatedMargin': 0.0,
                        'positionSide': 'BOTH'
                    },
                    {
                        'entryPrice': 0.0,
                        'isAutoAddMargin': True,
                        'leverage': 20.0,
                        'maxNotionalValue': 25000.0,
                        'liquidationPrice': 0.0,
                        'markPrice': 0.0,
                        'positionAmt': 0.0,
                        'symbol': 'API3USDT',
                        'unrealizedProfit': 0.0,
                        'marginType': 'cross',
                        'isolatedMargin': 0.0,
                        'positionSide': 'BOTH'
                    },
                    ...
                ]

        """
        return self.exchange.getPositionInfo(symbol)

    def getSymbolMinTrade(self, symbol, futures=False):
        """Returns information of valid minimum quantity, quote quantity and price precision.

        :param symbol: The symbol which the information is for.
        :type symbol: str
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: A dictionary containing information about the minimum valid values of the specified symbol
        :rtype: dict
        :Output parameters:

            .. list-table::
               :widths: 10 50
               :header-rows: 0

               * - **stepPrice**
                 - Price's maximum precision
               * - **minQuantity**
                 - Minimum valid quantity
               * - **precisionStep**
                 - Quantity's maximum precision
               * - **minQuoteQuantity**
                 - Minimum valid quote quantity

        :Output:

            .. code-block:: python

                {
                    'stepPrice': 0.01,
                    'minQuantity': 1e-05,
                    'precisionStep': 1e-05,
                    'minQuoteQuantity': 0.19279200000000002
                }

        """
        return self.exchange.getSymbolMinTrade(symbol, futures)

    def getIncomeHistory(
        self, symbol, incomeType=None, startTime=None, endTime=None, limit=None
    ):
        """Returns list of changes to the account balance. (Only for futures accounts)

        :param symbol: The symbol which the incomes are related to
        :type symbol: str
        :param incomeType: Type of income. For options visit the exchange's API documentation.
        :type incomeType: str , Optional
        :param startTime: If specified, incomes will be fetched from that time forward. (Time string format : '%Y-%m-%d %H:%M:%S')
        :type startTime: str , Optional
        :param endTime: If specified, incomes will be fetched until that time. (Time string format : '%Y-%m-%d %H:%M:%S')
        :type endTime: str , Optional
        :param limit: Maximum number of entries returned. For available options visit the exchange's API documentation.
        :type limit: int
        :return: A list of incomes
        :rtype: list(dict)
        :Output:

            .. code-block:: python

                [
                    {
                        'symbol': 'BTCUSDT',
                        'incomeType': 'FUNDING_FEE',
                        'income': 0.26403463,
                        'asset': 'USDT',
                        'time': 1655280000000
                    },
                    {
                        'symbol': 'BTCUSDT',
                        'incomeType': 'REALIZED_PNL',
                        'income': 26.0335,
                        'asset': 'USDT',
                        'time': 1655281638000
                    },
                    {
                        'symbol': 'BTCUSDT',
                        'incomeType': 'COMMISSION',
                        'income': -0.08219559,
                        'asset': 'USDT',
                        'time': 1655281638000
                    },
                    ...
                ]

        """

        return self.exchange.getIncomeHistory(
            symbol, incomeType, startTime, endTime, limit
        )

    def getSymbolList(self, futures=False):
        """Returns list of symbol names available for trade

        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: Returns a list of strings
        :rtype: list(str)
        :Output:

            .. code-block:: python

                [
                    'BTCUSDT',
                    'ETHUSDT',
                    'BCHUSDT',
                    'XRPUSDT',
                    'EOSUSDT',
                    'LTCUSDT',
                    'TRXUSDT',
                    ...
                ]

        """
        return self.exchange.getSymbolList(futures=futures)

    def getSymbol24hChanges(self, futures=False):
        """Returns all symbols 24-hour change percentages

        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: Returns a list of tuples containing asset names and percentage of change in 24-hour
        :rtype: list(tuple)
        :Output:

            .. code-block:: python

                [
                    ('PONDUSDT', 28.45),
                    ('PONDBTC', 28.261),
                    ('PONDBUSD', 28.162),
                    ('NULSBTC', 24.321),
                    ('NULSUSDT', 23.975),
                    ('NULSBUSD', 23.244),
                    ('CTXCBTC', 20.551),
                    ('CTXCUSDT', 19.959),
                    ('CTXCBUSD', 19.776),
                    ...
                ]

        """
        return self.exchange.getSymbol24hChanges(futures=futures)

    def getLatestSymbolNames(self, numOfSymbols=None, futures=True):
        """Returns list of newly added symbols to the exchange. Currently, only working for futures market.

        :param numOfSymbols: Number of symbols returned, sorted for the newest to oldest.
        :type numOfSymbols: int, optional
        :param futures: False for spot market and True for futures market, defaults to False
        :type futures: bool , optional
        :return: Returns a list of tuples containing asset names and a datetime object specifying its listed date.
        :rtype: list(tuple)
        :Output:

            .. code-block:: python

                [
                    ('DOTBUSD', datetime.datetime(2022, 6, 7, 11, 30)),
                    ('TLMBUSD', datetime.datetime(2022, 6, 7, 11, 30)),
                    ('ICPBUSD', datetime.datetime(2022, 6, 7, 11, 30)),
                    ('OPUSDT', datetime.datetime(2022, 6, 1, 11, 30)),
                    ('LUNA2BUSD', datetime.datetime(2022, 5, 31, 11, 30)),
                    ('1000LUNCBUSD', datetime.datetime(2022, 5, 30, 11, 30)),
                    ('GALABUSD', datetime.datetime(2022, 5, 25, 11, 30)),
                    ('TRXBUSD', datetime.datetime(2022, 5, 25, 11, 30)),
                    ('DODOBUSD', datetime.datetime(2022, 5, 24, 11, 30)),
                    ('ANCBUSD', datetime.datetime(2022, 5, 24, 11, 30))
                ]

        """
        return self.exchange.getLatestSymbolNames(
            numOfSymbols=numOfSymbols, futures=futures
        )

    def getLongShortRatios(
        self, symbol, period, limit=None, startTime=None, endTime=None
    ):
        print(self.exchange)
        return self.exchange.getLongShortRatios(
            symbol, period, limit, startTime, endTime
        )

    def getDepositAddress(self, coin, network=None):
        return self.exchange.getDepositAddress(coin, network)
