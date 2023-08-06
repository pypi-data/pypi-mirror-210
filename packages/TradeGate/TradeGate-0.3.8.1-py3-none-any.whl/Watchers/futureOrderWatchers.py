import time


def watchFuturesLimitTrigger(
    gate, symbol, orderId, doPutTpSl, cancelIfNotOpened, params
):
    if doPutTpSl:
        if (
            "tpSlOrderSide" not in params.keys()
            or "stopLoss" not in params.keys()
            or "takeProfit" not in params.keys()
        ):
            raise ValueError(
                "Must specify 'tpSlOrderSide' and 'stopLoss' and 'takeProfit'"
            )

    if cancelIfNotOpened:
        if "cancelDelaySec" not in params.keys():
            raise ValueError("Must specify 'cancelDelaySec'")
        delayTimeSec = float(params["cancelDelaySec"])
        startDelayTime = time.time()

    print("Watching order")
    while True:
        time.sleep(0.1)
        order = gate.get_order(symbol=symbol, order_id=orderId, futures=True)

        if cancelIfNotOpened:
            if time.time() - startDelayTime > delayTimeSec:
                gate.cancel_order(symbol=symbol, order_id=orderId, futures=True)
                break

        if order["status"] == "NEW":
            continue
        elif order["status"] == "FILLED":
            if doPutTpSl:
                orderSide = params["tpSlOrderSide"]
                stopLoss = params["stopLoss"]
                takeProfit = params["takeProfit"]

                stopLossOrder = gate.create_and_test_futures_order(
                    symbol,
                    orderSide,
                    "STOP_MARKET",
                    stop_price=str(stopLoss),
                    close_position=True,
                    price_protect=True,
                    working_type="MARK_PRICE",
                    time_in_force="GTC",
                )

                takeProfitOrder = gate.create_and_test_futures_order(
                    symbol,
                    orderSide,
                    "TAKE_PROFIT_MARKET",
                    stop_price=str(takeProfit),
                    close_position=True,
                    price_protect=True,
                    working_type="MARK_PRICE",
                    time_in_force="GTC",
                )
                result = gate.make_batch_futures_order([stopLossOrder, takeProfitOrder])
                # print(result)
                break
        elif order["status"] == "CANCELED":
            break

    print("Watching position")
    while True:
        time.sleep(0.1)
        position = gate.get_position_info(symbol)[0]

        if float(position["entryPrice"]) == 0.0:
            gate.cancel_all_symbol_open_orders(symbol, futures=True)
            break


# if __name__ == '__main__':
#     print(sys.argv)
#     time.sleep(3)
#     with open('helloWorld.txt')
