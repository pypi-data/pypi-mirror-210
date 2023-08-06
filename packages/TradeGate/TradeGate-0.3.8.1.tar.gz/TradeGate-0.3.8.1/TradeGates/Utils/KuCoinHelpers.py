import pandas as pd


def unify_get_balance_spot_out(data, is_single=False):
    all_assets = []

    for asset in data:
        asset_index = get_asset_index_in_list(asset["currency"], all_assets)
        if asset_index == -1:
            asset_info = new_empty_asset(asset["currency"])
        else:
            asset_info = all_assets[asset_index]

        asset_info["free"] += float(asset["available"])
        asset_info["locked"] += float(asset["holds"])
        asset_info["exchangeSpecific"].append(asset)

        if asset_index == -1:
            all_assets.append(asset_info)

    return all_assets[0] if is_single else all_assets


def new_empty_asset(asset_name):
    return {"asset": asset_name, "free": 0.0, "locked": 0.0, "exchangeSpecific": []}


def get_asset_index_in_list(asset_name, all_assets):
    return next(
        (i for i in range(len(all_assets)) if asset_name == all_assets[i]["asset"]),
        -1,
    )


def unify_trade_history(trade_history, futures=False):
    unified_trade_history = []

    for trade in trade_history:
        is_buyer = trade["liquidity"] == "taker"
        is_maker = trade["liquidity"] == "maker"
        if futures:
            unified_trade_history.append(
                {
                    "symbol": trade["symbol"],
                    "id": trade["tradeId"],
                    "orderId": trade["orderId"],
                    "orderListId": -1,
                    "price": trade["price"],
                    "qty": trade["value"],
                    "quoteQty": trade["size"],
                    "commission": trade["fee"],
                    "commissionAsset": trade["feeCurrency"],
                    "time": trade["tradeTime"],
                    "isBuyer": is_buyer,
                    "isMaker": is_maker,
                    "isBestMatch": None,
                    "exchangeSpecific": trade,
                }
            )
        else:
            unified_trade_history.append(
                {
                    "symbol": trade["symbol"],
                    "id": trade["tradeId"],
                    "orderId": trade["orderId"],
                    "orderListId": -1,
                    "price": trade["price"],
                    "qty": trade["size"],
                    "quoteQty": trade["funds"],
                    "commission": trade["fee"],
                    "commissionAsset": trade["feeCurrency"],
                    "time": trade["createdAt"],
                    "isBuyer": is_buyer,
                    "isMaker": is_maker,
                    "isBestMatch": None,
                    "exchangeSpecific": trade,
                }
            )

    return pd.DataFrame(unified_trade_history)


def unify_recent_trades(trade_history, futures=False):
    unified_trade_history = []

    for trade in trade_history:
        if futures:
            unified_trade_history.append(
                {
                    "id": int(trade["sequence"]),
                    "price": float(trade["price"]),
                    "qty": float(trade["size"]),
                    "quoteQty": float(trade["price"]) * float(trade["size"]),
                    "time": int(trade["ts"] / 1000),
                    "isBuyerMaker": None,
                    "exchangeSpecific": trade,
                }
            )
        else:
            unified_trade_history.append(
                {
                    "id": int(trade["sequence"]),
                    "price": float(trade["price"]),
                    "qty": float(trade["size"]),
                    "quoteQty": float(trade["price"]) * float(trade["size"]),
                    "time": int(trade["time"] / 1000),
                    "isBuyerMaker": None,
                    "isBestMatch": None,
                    "exchangeSpecific": trade,
                }
            )

    return unified_trade_history


def get_spot_order_as_dict(order_data):
    params = {
        "side": order_data.side,
        "symbol": order_data.symbol,
        "type": order_data.order_type,
    }

    if order_data.new_client_order_id is not None:
        params["clientOid"] = order_data.new_client_order_id

    if order_data.price is not None:
        params["price"] = order_data.price

    if order_data.quantity is not None:
        params["size"] = order_data.quantity

    if order_data.time_in_force is not None:
        params["timeInForce"] = order_data.time_in_force

    if order_data.quote_order_qty is not None and "size" not in params.keys():
        params["funds"] = order_data.quote_order_qty

    if order_data.extra_params is not None:
        set_extra_params(order_data, params)

    return params


def set_extra_params(order_data, params):
    if "cancelAfter" in order_data.extra_params.keys():
        params["cancelAfter"] = order_data.extra_params["cancelAfter"]
    if "postOnly" in order_data.extra_params.keys():
        params["postOnly"] = order_data.extra_params["postOnly"]
    if "hidden" in order_data.extra_params.keys():
        params["hidden"] = order_data.extra_params["hidden"]
    if "iceberg" in order_data.extra_params.keys():
        params["iceberg"] = order_data.extra_params["iceberg"]
    if "visibleSize" in order_data.extra_params.keys():
        params["visibleSize"] = order_data.extra_params["visibleSize"]
    if "stopPrice" in order_data.extra_params.keys():
        params["stopPrice"] = order_data.extra_params["stopPrice"]


def unify_get_order(order_data, futures=False, lot_size=None):
    if futures:
        if (
            order_data["value"] is not None
            and order_data["price"] is None
            and float(order_data["size"]) > 0
        ):
            order_data["price"] = float(order_data["value"]) / (
                float(order_data["size"]) * lot_size
            )

        if order_data["cancelExist"]:
            order_status = "CANCELLED"
        elif order_data["isActive"]:
            order_status = "NEW"
        else:
            order_status = "FILLED"

        return {
            "symbol": order_data["symbol"],
            "orderId": order_data["id"],
            "clientOrderId": order_data["clientOid"],
            "transactTime": order_data["createdAt"],
            "price": order_data["price"],
            "origQty": float(order_data["size"]) * lot_size,
            "executedQty": float(order_data["filledSize"]) * lot_size,
            "cummulativeQuoteQty": 0
            if order_data["price"] is None
            else float(order_data["filledSize"])
            * float(order_data["price"])
            * lot_size,
            "status": order_status,
            "timeInForce": order_data["timeInForce"],
            "type": order_data["type"],
            "side": order_data["side"],
            "extraData": {
                "reduceOnly": order_data["reduceOnly"],
                "stopPrice": 0.0
                if order_data["stopPrice"] is None
                else float(order_data["stopPrice"]),
                "workingType": "CONTRACT_PRICE",
                "avgPrice": order_data["price"],
                "origType": order_data["type"],
                "positionSide": "BOTH",
                "activatePrice": None,
                "priceRate": None,
                "closePosition": order_data["closeOrder"],
            },
            "exchangeSpecific": order_data,
        }
    else:
        if order_data["cancelExist"]:
            order_status = "CANCELLED"
        elif order_data["isActive"]:
            order_status = "NEW"
        else:
            order_status = "FILLED"

        return {
            "symbol": order_data["symbol"],
            "orderId": order_data["id"],
            "orderListId": -1,
            "clientOrderId": order_data["clientOid"],
            "price": order_data["price"],
            "origQty": order_data["size"],
            "executedQty": order_data["dealSize"],
            "cummulativeQuoteQty": order_data["dealSize"],
            "status": order_status,
            "timeInForce": order_data["timeInForce"],
            "type": order_data["type"],
            "side": order_data["side"],
            "stopPrice": order_data["stopPrice"],
            "icebergQty": order_data["visibleSize"],
            "time": order_data["createdAt"],
            "updateTime": order_data["createdAt"],
            "isWorking": order_data["isActive"],
            "origQuoteOrderQty": order_data["dealFunds"],
            "exchangeSpecific": order_data,
        }


def unify_get_symbol_orders(orders_list, futures=False, lot_size=None):
    return [unify_get_order(orderData, futures, lot_size) for orderData in orders_list]


def unify_get_best_bid_asks(ticker, symbol):
    return {
        "symbol": symbol,
        "bidPrice": ticker["bestBid"],
        "bidQty": ticker["bestBidSize"],
        "askPrice": ticker["bestAsk"],
        "askQty": ticker["bestAskSize"],
    }


def unify_get_balance_futures_out(data, is_single=False):
    if is_single:
        return {
            "asset": data["currency"],
            "free": data["availableBalance"],
            "locked": data["positionMargin"],
            "exchangeSpecific": data,
        }
    else:
        return [
            {
                "asset": assetData["currency"],
                "free": assetData["availableBalance"],
                "locked": assetData["positionMargin"],
                "exchangeSpecific": assetData,
            }
            for assetData in data
        ]


def get_futures_order_as_dict(order_data):
    params = {
        "side": order_data.side,
        "symbol": order_data.symbol,
        "type": order_data.order_type,
    }

    if "leverage" in order_data.extra_params.keys():
        params["leverage"] = order_data.extra_params["leverage"]

    if order_data.new_client_order_id is not None:
        params["clientOid"] = order_data.new_client_order_id
    else:
        params["clientOid"] = ""

    if order_data.price is not None:
        params["price"] = str(order_data.price)

    if order_data.quantity is not None:
        params["size"] = float(order_data.quantity)

    if order_data.time_in_force is not None:
        params["timeInForce"] = order_data.time_in_force

    if order_data.stop_price is not None:
        params["stopPrice"] = order_data.stop_price
        params["stop"] = order_data.extra_params["stop"]
        params["stopPriceType"] = order_data.extra_params["stopPriceType"]

    if order_data.close_position is not None:
        params["closeOrder"] = order_data.close_position

    if order_data.extra_params is not None:
        set_futures_extra_params(order_data, params)

    return params


def set_futures_extra_params(order_data, params):
    if "postOnly" in order_data.extra_params.keys():
        params["postOnly"] = order_data.extra_params["postOnly"]
    if "hidden" in order_data.extra_params.keys():
        params["hidden"] = order_data.extra_params["hidden"]
    if "iceberg" in order_data.extra_params.keys():
        params["iceberg"] = order_data.extra_params["iceberg"]
    if "visibleSize" in order_data.extra_params.keys():
        params["visibleSize"] = order_data.extra_params["visibleSize"]
    if "reduceOnly" in order_data.extra_params.keys():
        params["reduceOnly"] = order_data.extra_params["reduceOnly"]
    if "forceHold" in order_data.extra_params.keys():
        params["forceHold"] = order_data.extra_params["forceHold"]
    if "postOnly" in order_data.extra_params.keys():
        params["postOnly"] = order_data.extra_params["postOnly"]
    if "hidden" in order_data.extra_params.keys():
        params["hidden"] = order_data.extra_params["hidden"]


def unify_get_position_info(position_info):
    return {
        "entryPrice": position_info["avgEntryPrice"],
        "isAutoAddMargin": position_info["autoDeposit"],
        "leverage": position_info["realLeverage"],
        "maxNotionalValue": None,
        "liquidationPrice": position_info["liquidationPrice"],
        "markPrice": position_info["markPrice"],
        "positionAmt": position_info["currentQty"],
        "symbol": position_info["symbol"],
        "unrealizedProfit": position_info["unrealisedPnl"],
        "marginType": "cross" if position_info["crossMode"] else "isolated",
        "isolatedMargin": position_info["maintMargin"],
        "positionSide": "BOTH",
        "exchangeSpecific": position_info,
    }


def unify_get_position_infos(position_infos):
    return [unify_get_position_info(posInfo) for posInfo in position_infos]


def unify_min_trade(info, futures=False):
    if futures:
        params = {
            "minQuantity": float(info["multiplier"] * info["lotSize"]),
            "precisionStep": float(info["multiplier"] * info["lotSize"]),
            "stepPrice": info["tickSize"],
        }
        params["minQuoteQuantity"] = params["precisionStep"] * info["lastTradePrice"]
    else:
        params = {
            "minQuantity": info["baseMinSize"],
            "minQuoteQuantity": info["quoteMinSize"],
            "precisionStep": info["baseIncrement"],
            "stepPrice": info["priceIncrement"],
        }
    return params


def unify_get_income(income_list):
    return [
        {
            "symbol": income["remark"],
            "incomeType": income["type"],
            "income": income["amount"],
            "asset": income["currency"],
            "time": income["type"],
            "exchangeSpecific": income,
        }
        for income in income_list
    ]
