import time


class OrderData():
    def __init__(self, symbol, side, orderType):
        self.symbol = symbol
        self.side = side
        self.orderType = orderType

        self.timeInForce = None
        self.quantity = None
        self.quoteOrderQty = None
        self.price = None
        self.newClientOrderId = None
        self.stopPrice = None
        self.icebergQty = None
        self.newOrderRespType = None
        self.timestamp = None
        self.extraParams = None

    def setTimeInForce(self, timeInForce):
        self.timeInForce = timeInForce

    def setQuantity(self, quantity):
        self.quantity = quantity

    def setQuoteOrderQty(self, quoteOrderQty):
        self.quoteOrderQty = quoteOrderQty

    def setPrice(self, price):
        self.price = price

    def setNewClientOrderId(self, newClientOrderId):
        self.newClientOrderId = newClientOrderId

    def setStopPrice(self, stopPrice):
        self.stopPrice = stopPrice

    def setIcebergQty(self, icebergQty):
        self.icebergQty = icebergQty

    def setNewOrderRespType(self, newOrderRespType):
        self.newOrderRespType = newOrderRespType

    def setTimestamp(self):
        self.timestamp = time.time()

    def setExtraParams(self, extraParams):
        self.extraParams = extraParams


class FuturesOrderData():
    def __init__(self, symbol, side=None, orderType=None):
        self.symbol = symbol
        self.side = side
        self.orderType = orderType

        self.positionSide = None
        self.timeInForce = None
        self.quantity = None
        self.quoteQuantity = None
        self.reduceOnly = None
        self.price = None
        self.newClientOrderId = None
        self.stopPrice = None
        self.closePosition = None
        self.activationPrice = None
        self.callbackRate = None
        self.workingType = None
        self.priceProtect = None
        self.newOrderRespType = None
        self.extraParams = None
        self.leverage = None

    def setOrderSide(self, orderSide):
        self.side = orderSide

    def setPositionSide(self, positionSide):
        self.positionSide = positionSide

    def setTimeInForce(self, timeInForce):
        self.timeInForce = timeInForce

    def setQuantity(self, quantity):
        self.quantity = quantity

    def setReduceOnly(self, reduceOnly):
        self.reduceOnly = reduceOnly

    def setPrice(self, price):
        self.price = price

    def setNewClientOrderId(self, newClientOrderId):
        self.newClientOrderId = newClientOrderId

    def setStopPrice(self, stopPrice):
        self.stopPrice = stopPrice

    def setClosePosition(self, closePosition):
        self.closePosition = closePosition

    def setActivationPrice(self, activationPrice):
        self.activationPrice = activationPrice

    def setCallbackRate(self, callbackRate):
        self.callbackRate = callbackRate

    def setWorkingType(self, workingType):
        self.workingType = workingType

    def setPriceProtect(self, priceProtect):
        self.priceProtect = priceProtect

    def setNewOrderRespType(self, newOrderRespType):
        self.newOrderRespType = newOrderRespType

    def setExtraParams(self, extraParams):
        self.extraParams = extraParams

    def setLeverage(self, leverage):
        self.leverage = leverage

    def setQuoteQuantity(self, quoteQuantity):
        self.quoteQuantity = quoteQuantity


def setSpotOrderData(icebergQty, newClientOrderId, newOrderRespType, orderType, price, quantity, side,
                     stopPrice, symbol, timeInForce, extraParams=None):
    currOrder = OrderData(symbol.upper(), side.upper(), orderType.upper())
    if quantity is not None:
        currOrder.setQuantity(quantity)
    if price is not None:
        currOrder.setPrice(price)
    if timeInForce is not None:
        currOrder.setTimeInForce(timeInForce)
    if stopPrice is not None:
        currOrder.setStopPrice(stopPrice)
    if icebergQty is not None:
        currOrder.setIcebergQty(icebergQty)
    if newOrderRespType is not None:
        currOrder.setNewOrderRespType(newOrderRespType)
    if newClientOrderId is not None:
        currOrder.setNewClientOrderId(newClientOrderId)
    if extraParams is not None:
        currOrder.setExtraParams(extraParams)
    return currOrder


def setFuturesOrderData(activationPrice, callbackRate, closePosition, extraParams, newClientOrderId,
                        newOrderRespType, orderType, positionSide, price, priceProtect, quantity,
                        reduceOnly, side, stopPrice, symbol, timeInForce, workingType, quoteQuantity):
    if extraParams is None:
        extraParams = {}
    currOrder = FuturesOrderData(symbol=symbol.upper(), orderType=orderType.upper())
    if side is not None:
        currOrder.setOrderSide(side)
    if positionSide is not None:
        currOrder.setPositionSide(positionSide)
    if timeInForce is not None:
        currOrder.setTimeInForce(timeInForce)
    if quantity is not None:
        currOrder.setQuantity(quantity)
    if quoteQuantity is not None:
        currOrder.setQuoteQuantity(quoteQuantity)
    if reduceOnly is not None:
        currOrder.setReduceOnly(reduceOnly)
    if price is not None:
        currOrder.setPrice(price)
    if newClientOrderId is not None:
        currOrder.setNewClientOrderId(newClientOrderId)
    if stopPrice is not None:
        currOrder.setStopPrice(stopPrice)
    if closePosition is not None:
        currOrder.setClosePosition(closePosition)
    if activationPrice is not None:
        currOrder.setActivationPrice(activationPrice)
    if callbackRate is not None:
        currOrder.setCallbackRate(callbackRate)
    if workingType is not None:
        currOrder.setWorkingType(workingType)
    if priceProtect is not None:
        currOrder.setPriceProtect(priceProtect)
    if newOrderRespType is not None:
        currOrder.setNewOrderRespType(newOrderRespType)
    if 'leverage' in extraParams.keys():
        currOrder.setLeverage(extraParams['leverage'])
    if extraParams is not None:
        currOrder.setExtraParams(extraParams)
    return currOrder


def getQuantity(enterPrice, quantity, quoteQuantity, stepPrecision):
    if (quantity is not None and quoteQuantity is not None) or (quantity is None and quoteQuantity is None):
        raise ValueError('Specify either quantity or quoteQuantity and not both')
    if quantity is None:
        if float(stepPrecision) > 0.5:
            quantity = round(quoteQuantity / enterPrice, len(str(float(stepPrecision))) - 3)
        else:
            quantity = round(quoteQuantity / enterPrice, len(str(float(stepPrecision))) - 2)
    return quantity


def getTpSlLimitOrderIds(orderingResult):
    orderIds = {}
    for order in orderingResult:
        if order['type'] == 'LIMIT':
            orderIds['mainOrder'] = order['orderId']
        elif order['type'] == 'STOP_MARKET':
            orderIds['stopLoss'] = order['orderId']
        elif order['type'] == 'TAKE_PROFIT_MARKET':
            orderIds['takeProfit'] = order['orderId']
    return orderIds


def getTpSlMarketOrderIds(orderingResult, has_sl, has_tp):
    orderIds = {}
    for order in orderingResult:
        if order['type'] == 'MARKET':
            orderIds['mainOrder'] = order['orderId']
        elif order['type'] == 'STOP_MARKET':
            orderIds['stopLoss'] = order['orderId']
        elif order['type'] == 'TAKE_PROFIT_MARKET':
            orderIds['takeProfit'] = order['orderId']

    if 'mainOrder' not in orderIds.keys():
        raise Exception('Problem in main order')

    if has_sl and 'stopLoss' not in orderIds.keys():
        raise Exception('Problem in stop loss order')

    if has_tp and 'takeProfit' not in orderIds.keys():
        raise Exception('Problem in take profit order')
    return orderIds
