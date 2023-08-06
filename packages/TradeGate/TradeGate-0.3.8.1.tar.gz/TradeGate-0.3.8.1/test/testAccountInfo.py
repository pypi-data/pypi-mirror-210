import json
import logging

import pytest

from TradeGates.TradeGate import TradeGate

loglevel = logging.INFO
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)


@pytest.fixture
def get_gates():
    with open("../../config.json") as f:
        config = json.load(f)

    return [TradeGate(config[key], sandbox=True) for key in config.keys()]


def testFullBalance(get_gates):
    for gate in get_gates:
        balance = gate.getBalance()
        print("\nFull Balance from {} exchange: {}".format(gate.exchangeName, balance))
        assert (
            balance is not None
        ), "Problem in fetching balance from {} exchange.".format(gate.exchangeName)

        errorMessage = "Bad fetch balance interface for {} exchange,".format(
            gate.exchangeName
        )
        try:
            if gate.exchangeName != "Binance":
                if sorted(list(balance[0].keys())) != sorted(
                    ["asset", "free", "locked", "exchangeSpecific"]
                ):
                    assert False, errorMessage
            else:
                if sorted(list(balance[0].keys())) != sorted(
                    ["asset", "free", "locked"]
                ):
                    assert False, errorMessage
        except Exception:
            assert False, errorMessage


def testSingleCoinBalance(get_gates):
    for gate in get_gates:
        balance = gate.get_balance("BTC")
        print(
            "\nSingle coin balance from {} exchange: {}".format(
                gate.exchangeName, balance
            )
        )
        assert (
            balance is not None
        ), "Problem in fetching single coin balance from {} exchange.".format(
            gate.exchangeName
        )

        errorMessage = (
            "Bad fetch single coin balance interface for {} exchange,".format(
                gate.exchangeName
            )
        )
        try:
            if gate.exchangeName != "Binance":
                if sorted(list(balance.keys())) != sorted(
                    ["asset", "free", "locked", "exchangeSpecific"]
                ):
                    assert False, errorMessage
            else:
                if sorted(list(balance.keys())) != sorted(["asset", "free", "locked"]):
                    assert False, errorMessage
        except Exception:
            assert False, errorMessage


def testTradeHistory(get_gates):
    for gate in get_gates:
        if gate.exchangeName.lower() == "kucoin":
            tradeHistory = gate.symbol_account_trade_history("BTC-USDT", futures=False)
        else:
            tradeHistory = gate.symbol_account_trade_history("BTCUSDT", futures=False)
        # print('\nTrade history from {} exchange: {}'.format(gate.exchangeName, tradeHistory))

        assert (
            tradeHistory is not None
        ), "Problem in fetching trade history from {} exchange.".format(
            gate.exchangeName
        )

        interface = [
            "symbol",
            "id",
            "orderId",
            "orderListId",
            "price",
            "qty",
            "quoteQty",
            "commission",
            "commissionAsset",
            "time",
            "isBuyer",
            "isMaker",
            "isBestMatch",
        ]

        errorMessage = "Bad fetch trade history interface for {} exchange,".format(
            gate.exchangeName
        )
        try:
            if not gate.exchangeName == "Binance":
                interface.append("exchangeSpecific")
                if not sorted(list(tradeHistory[0].keys())) == sorted(interface):
                    assert False, errorMessage
            else:
                if not sorted(list(tradeHistory[0].keys())) == sorted(interface):
                    assert False, errorMessage
        except Exception:
            assert False, errorMessage
