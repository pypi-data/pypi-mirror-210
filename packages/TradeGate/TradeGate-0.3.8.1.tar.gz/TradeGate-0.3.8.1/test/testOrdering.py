import json
import logging
import time

import pytest

from TradeGates.TradeGate import TradeGate

loglevel = logging.INFO
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)


@pytest.fixture
def getGatesAndSymbolNames():
    gates = []
    symbolNames = {}
    with open("../../config.json") as f:
        config = json.load(f)

    for key in config.keys():
        gates.append(TradeGate(config[key], sandbox=True))
        if gates[-1].exchangeName.lower() == "kucoin":
            symbolNames[gates[-1].exchangeName] = "BTC-USDT"
        else:
            symbolNames[gates[-1].exchangeName] = "BTCUSDT"

    return gates, symbolNames


def testNewTestOrder(getGatesAndSymbolNames):
    gates, symbolNamesDict = getGatesAndSymbolNames
    for gate in gates:
        symbolName = symbolNamesDict[gate.exchangeName]
        try:
            res = gate.create_and_test_spot_order(
                symbolName,
                "SELL",
                "LIMIT",
                time_in_force="GTC",
                quantity=0.002,
                price=20000,
            )
            assert (
                res is not None
            ), "Problem in testing making order from {} exchange".format(
                gate.exchangeName
            )
        except Exception as e:
            assert False, "From {} exchange : {}".format(gate.exchangeName, str(e))


def testNewTestOrderBadOrderType(getGatesAndSymbolNames):
    gates, symbolNamesDict = getGatesAndSymbolNames
    for gate in gates:
        symbolName = symbolNamesDict[gate.exchangeName]
        try:
            res = gate.create_and_test_spot_order(
                symbolName,
                "SELL",
                "LINIT",
                time_in_force="GTC",
                quantity=0.002,
                price=30000,
            )
            assert (
                res is None
            ), "Bad order type and information provided. Must fail (Exchange: {})".format(
                gate.exchangeName
            )
        except Exception as e:
            assert (
                True
            ), "Bad order type and information provided. Must fail (Exchange: {})".format(
                gate.exchangeName
            )


def testNewOrder(getGatesAndSymbolNames):
    gates, symbolNamesDict = getGatesAndSymbolNames
    for gate in gates:
        symbolName = symbolNamesDict[gate.exchangeName]
        try:
            verifiedOrder = gate.create_and_test_spot_order(
                symbolName,
                "BUY",
                "LIMIT",
                quantity=0.002,
                price=20000,
                time_in_force="GTC",
            )
            result = gate.make_spot_order(verifiedOrder)
            print(result)
            assert (
                result is not None
            ), "Problem in making new order in {} exchange".format(gate.exchangeName)
        except Exception:
            assert False, "Problem in making new order in {} exchange".format(
                gate.exchangeName
            )


def testGetOrders(getGatesAndSymbolNames):
    gates, symbolNamesDict = getGatesAndSymbolNames
    for gate in gates:
        if gate.exchangeName.lower() == "binance":
            continue
        symbolName = symbolNamesDict[gate.exchangeName]
        orders = gate.get_symbol_orders(symbolName, futures=False)
        # print('\nGetting order history for BTCUSDT symbol from {}: {}'.format(gate.exchangeName, orders[0]))

        assert (
            orders is not None
        ), "Problem in getting list of all orders from {} exchange.".format(
            gate.exchangeName
        )


def testGetOpenOrders(getGatesAndSymbolNames):
    gates, symbolNamesDict = getGatesAndSymbolNames
    for gate in gates:
        if gate.exchangeName.lower() == "binance":
            continue
        symbolName = symbolNamesDict[gate.exchangeName]
        symbolOpenOrders = gate.get_open_orders(symbolName)
        # print('\nGetting BTCUSDT open orders list from {} exchange: {}'.format(gate.exchangeName, symbolOpenOrders))
        assert (
            symbolOpenOrders is not None
        ), "Problem in getting list of open orders with symbol from {} exchange.".format(
            gate.exchangeName
        )


def testGetOrder(getGatesAndSymbolNames):
    gates, symbolNamesDict = getGatesAndSymbolNames
    for gate in gates:
        if gate.exchangeName.lower() == "binance":
            continue
        symbolName = symbolNamesDict[gate.exchangeName]
        try:
            verifiedOrder = gate.create_and_test_spot_order(
                symbolName,
                "BUY",
                "LIMIT",
                quantity=0.02,
                price=30000,
                time_in_force="GTC",
                new_client_order_id=str(int(time.time())),
            )
            result = gate.make_spot_order(verifiedOrder)
        except Exception as e:
            assert False, "Problem in making order from {} exchange: {}".format(
                gate.exchangeName, str(e)
            )

        # print('Submitted order on {} exchange: {}'.format(gate.exchangeName, result))

        order = gate.get_order(symbolName, order_id=result["orderId"])
        assert (
            order["clientOrderId"] == result["clientOrderId"]
        ), "Fetch client orderID is not equal to the actual client orderID from {} exchange.".format(
            gate.exchangeName
        )
        # print('Correct \'clientOrderId\'.')

        order = gate.get_order(symbolName, local_order_id=result["clientOrderId"])
        assert (
            order["orderId"] == result["orderId"]
        ), "Fetch orderID is not equal to the actual orderID from {} exchange.".format(
            gate.exchangeName
        )
        # print('Correct \'orderId\'.')

        gate.cancel_order("BTCUSDT", order_id=result["orderId"])


def testCancelingAllOpenOrders(getGatesAndSymbolNames):
    gates, symbolNamesDict = getGatesAndSymbolNames
    for gate in gates:
        symbolName = symbolNamesDict[gate.exchangeName]
        result = gate.cancel_all_symbol_open_orders(symbolName)

        openOrders = gate.get_open_orders(symbolName)
        assert (
            len(openOrders) == 0
        ), "Problem in canceling all Open Orders in {} exchange.".format(
            gate.exchangeName
        )


def testCancelingOrder(getGatesAndSymbolNames):
    gates, symbolNamesDict = getGatesAndSymbolNames
    for gate in gates:
        symbolName = symbolNamesDict[gate.exchangeName]
        try:
            verifiedOrder = gate.create_and_test_spot_order(
                symbolName,
                "BUY",
                "LIMIT",
                quantity=0.002,
                price=28000,
                time_in_force="GTC",
                new_client_order_id=str(int(time.time())),
            )
            result = gate.make_spot_order(verifiedOrder)
        except Exception as e:
            assert False, "Problem in making order in {} exchange: {}".format(
                gate.exchangeName, str(e)
            )

        result = gate.cancel_order(symbol=symbolName, order_id=result["orderId"])
        result = gate.get_order(symbol=symbolName, order_id=result["orderId"])

        assert result["status"].upper() in [
            "CANCELED",
            "CANCELLED",
        ], "Problem in canceling specified Open Orders in {} exchange.".format(
            gate.exchangeName
        )

        try:
            verifiedOrder = gate.create_and_test_spot_order(
                symbolName,
                "BUY",
                "LIMIT",
                quantity=0.002,
                price=28000,
                time_in_force="GTC",
                new_client_order_id=str(int(time.time())),
            )
            result = gate.make_spot_order(verifiedOrder)
        except Exception as e:
            assert False, "Problem in making order in {} exchange: {}".format(
                gate.exchangeName, str(e)
            )

        result = gate.cancel_order(
            symbol=symbolName, local_order_id=result["clientOrderId"]
        )
        result = gate.get_order(symbol=symbolName, order_id=result["orderId"])

        assert result["status"].upper() in [
            "CANCELED",
            "CANCELLED",
        ], "Problem in canceling specified Open Orders in {} exchange.".format(
            gate.exchangeName
        )
