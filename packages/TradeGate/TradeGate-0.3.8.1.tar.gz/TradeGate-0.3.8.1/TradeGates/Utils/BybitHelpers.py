import time
from datetime import datetime

import pandas as pd

from Utils import DataHelpers


def get_balance_out(data, single=False, futures=False):
    if not single:
        out_data = []
        if futures:
            for key, value in data.items():
                coin_data = {
                    "asset": key,
                    "free": value["available_balance"],
                    "locked": value["used_margin"],
                    "exchangeSpecific": value,
                }
                out_data.append(coin_data)
        else:
            for asset in data:
                coin_data = {
                    "asset": asset["coin"],
                    "free": asset["free"],
                    "locked": asset["locked"],
                    "exchangeSpecific": asset,
                }
                out_data.append(coin_data)
    elif futures:
        out_data = set_keys_for_output(data)

    else:
        out_data = {
            "asset": data["coin"],
            "free": data["free"],
            "locked": data["locked"],
            "exchangeSpecific": data,
        }
    return out_data


def set_keys_for_output(data):
    key = list(data.keys())[0]

    return {
        "asset": key,
        "free": data[key]["available_balance"],
        "locked": data[key]["used_margin"],
        "exchangeSpecific": data[key],
    }


def get_my_trade_history_out(data, futures=False):
    out_data = []
    for history in data:
        if futures:
            out_data.append(
                {
                    "symbol": history["symbol"],
                    "id": history["exec_id"],
                    "orderId": history["order_id"],
                    "orderListId": history["order_link_id"],
                    "price": history["price"],
                    "qty": history["order_qty"],
                    "quoteQty": str(
                        float(history["price"]) * float(history["order_qty"])
                    ),
                    "commission": None,
                    "commissionAsset": None,
                    "time": history["trade_time_ms"],
                    "isBuyer": None,
                    "isMaker": None,
                    "isBestMatch": None,
                    "exchangeSpecific": history,
                }
            )
        else:
            out_data.append(
                {
                    "symbol": history["symbol"],
                    "id": history["id"],
                    "orderId": history["orderId"],
                    "orderListId": -1,
                    "price": history["price"],
                    "qty": history["qty"],
                    "quoteQty": str(float(history["price"]) * float(history["qty"])),
                    "commission": history["commission"],
                    "commissionAsset": history["commissionAsset"],
                    "time": history["time"],
                    "isBuyer": history["isBuyer"],
                    "isMaker": history["isMaker"],
                    "isBestMatch": None,
                    "exchangeSpecific": history,
                }
            )
    return out_data


def get_recent_trade_history_out(data, futures=False):
    out_data = []
    for datum in data:
        if futures:
            out_data.append(
                {
                    "id": datum["id"],
                    "price": datum["price"],
                    "qty": datum["qty"],
                    "quoteQty": str(float(datum["qty"] * datum["price"])),
                    "time": datum["trade_time_ms"],
                    "isBuyerMaker": None,
                    "isBestMatch": None,
                    "exchangeSpecific": datum,
                }
            )
        else:
            out_data.append(
                {
                    "id": None,
                    "price": datum["price"],
                    "qty": datum["qty"],
                    "quoteQty": str(float(datum["qty"]) * float(datum["price"])),
                    "time": datum["time"],
                    "isBuyerMaker": datum["isBuyerMaker"],
                    "isBestMatch": None,
                    "exchangeSpecific": datum,
                }
            )
    return out_data


def get_make_spot_order_out(data):
    return {
        "symbol": data["symbol"],
        "orderId": data["orderId"],
        "orderListId": -1,
        "clientOrderId": data["orderLinkId"],
        "transactTime": data["transactTime"],
        "price": data["price"],
        "origQty": data["origQty"],
        "executedQty": data["executedQty"],
        "cummulativeQuoteQty": None,
        "status": data["status"],
        "timeInForce": data["timeInForce"],
        "type": data["type"],
        "side": data["side"],
        "fills": None,
        "exchangeSpecific": data,
    }


def get_order_out(data, futures=False):
    if not futures:
        return {
            "symbol": data["symbol"],
            "orderId": data["orderId"],
            "orderListId": -1,
            "clientOrderId": data["orderLinkId"],
            "price": data["price"],
            "origQty": data["origQty"],
            "executedQty": data["executedQty"],
            "cummulativeQuoteQty": data["cummulativeQuoteQty"],
            "status": data["status"],
            "timeInForce": data["timeInForce"],
            "type": data["type"],
            "side": data["side"],
            "stopPrice": data["stopPrice"],
            "icebergQty": data["icebergQty"],
            "time": data["time"],
            "updateTime": data["updateTime"],
            "isWorking": data["isWorking"],
            "origQuoteOrderQty": None,
            "exchangeSpecific": data,
        }


def get_open_orders_out(data, futures=False):
    out_data = []
    if not futures:
        out_data.extend(
            {
                "symbol": datum["symbol"],
                "orderId": datum["orderId"],
                "orderListId": None,
                "clientOrderId": datum["orderLinkId"],
                "price": datum["price"],
                "origQty": datum["origQty"],
                "executedQty": datum["executedQty"],
                "cummulativeQuoteQty": datum["cummulativeQuoteQty"],
                "status": datum["status"],
                "timeInForce": datum["timeInForce"],
                "type": datum["type"],
                "side": datum["side"],
                "stopPrice": datum["stopPrice"],
                "icebergQty": datum["icebergQty"],
                "time": datum["time"],
                "updateTime": datum["updateTime"],
                "isWorking": datum["isWorking"],
                "origQuoteOrderQty": None,
                "exchangeSpecific": datum,
            }
            for datum in data
        )
    return out_data


def futures_order_out(data, is_conditional=False):
    if is_conditional:
        return {
            "symbol": data["symbol"],
            "orderId": data["stop_order_id"],
            "clientOrderId": data["order_link_id"],
            "transactTime": time.mktime(
                datetime.strptime(
                    data["created_time"], "%Y-%m-%dT%H:%M:%SZ"
                ).timetuple()
            ),
            "price": data["price"],
            "origQty": data["qty"],
            "executedQty": 0.0,
            "cummulativeQuoteQty": 0.0,
            "status": data["order_status"],
            "timeInForce": data["time_in_force"],
            "type": data["order_type"],
            "side": data["side"],
            "extraData": {
                "reduceOnly": data["reduce_only"],
                "stopPrice": data["trigger_price"],
                "workingType": data["trigger_by"],
                "avgPrice": 0.0,
                "origType": data["order_type"],
                "positionSide": None,
                "activatePrice": None,
                "priceRate": None,
                "closePosition": data["close_on_trigger"],
            },
            "exchangeSpecific": data,
        }
    else:
        return {
            "symbol": data["symbol"],
            "orderId": data["order_id"],
            "clientOrderId": data["order_link_id"],
            "transactTime": time.mktime(
                datetime.strptime(
                    data["created_time"], "%Y-%m-%dT%H:%M:%SZ"
                ).timetuple()
            ),
            "price": data["price"],
            "origQty": data["qty"],
            "executedQty": data["cum_exec_qty"],
            "cummulativeQuoteQty": data["cum_exec_value"],
            "status": data["order_status"],
            "timeInForce": data["time_in_force"],
            "type": data["order_type"],
            "side": data["side"],
            "extraData": {
                "reduceOnly": data["reduce_only"],
                "stopPrice": 0.0,
                "workingType": None,
                "avgPrice": 0.0,
                "origType": data["order_type"],
                "positionSide": None,
                "activatePrice": None,
                "priceRate": None,
                "closePosition": data["close_on_trigger"],
            },
            "exchangeSpecific": data,
        }


def make_dummy_balance(asset):
    return {
        "asset": asset,
        "free": str(0.0),
        "locked": str(0.0),
        "exchangeSpecific": {},
    }


def get_spot_order_as_dict(order: DataHelpers.OrderData):
    return {
        "symbol": order.symbol,
        "qty": order.quantity,
        "side": order.side,
        "type": order.order_type,
        "timeInForce": order.time_in_force,
        "price": order.price,
        "orderLinkId": order.new_client_order_id,
    }


def get_futures_order_as_dict(
    order: DataHelpers.FuturesOrderData, time_in_force_translate
):
    if "STOP" in order.orderType:
        params = {
            "side": order.side.lower().title(),
            "symbol": order.symbol,
            "order_type": "Market" if order.orderType == "STOP_MARKET" else "Limit",
            "qty": order.quantity,
            "price": order.price,
            "base_price": order.extra_params["basePrice"],
            "stop_px": order.stop_price,
            "time_in_force": order.time_in_force
            if order.time_in_force in time_in_force_translate.values()
            else time_in_force_translate[order.time_in_force],
            "close_on_trigger": order.close_position,
            "reduce_only": order.reduce_only,
        }

        if "triggerBy" in order.extra_params.keys():
            params["trigger_by"] = order.extra_params["triggerBy"]

    else:
        params = {
            "side": order.side.lower().title(),
            "symbol": order.symbol,
            "order_type": order.orderType.lower().title(),
            "qty": order.quantity,
            "time_in_force": order.time_in_force
            if order.time_in_force in time_in_force_translate.values()
            else time_in_force_translate[order.time_in_force],
            "close_on_trigger": order.close_position,
            "reduce_only": order.reduce_only,
        }

    if order.price is not None:
        params["price"] = order.price

    if order.new_client_order_id is not None:
        params["order_link_id"] = order.new_client_order_id

    if "takeProfit" in order.extra_params.keys():
        params["take_profit"] = order.extra_params["takeProfit"]

    if "stopLoss" in order.extra_params.keys():
        params["stop_loss"] = order.extra_params["stopLoss"]

    if "tpTriggerBy" in order.extra_params.keys():
        params["tp_trigger_by"] = order.extra_params["tpTriggerBy"]

    if "slTriggerBy" in order.extra_params.keys():
        params["sl_trigger_by"] = order.extra_params["slTriggerBy"]

    if "positionIdx" in order.extra_params.keys():
        params["position_idx"] = order.extra_params["positionIdx"]

    return params


def convert_interval_to_futures_klines(interval):
    if interval == "1m":
        return 1
    elif interval == "3m":
        return 3
    elif interval == "5m":
        return 5
    elif interval == "15m":
        return 15
    elif interval == "30m":
        return 30
    elif interval == "1h":
        return 60
    elif interval == "2h":
        return 120
    elif interval == "4h":
        return 240
    elif interval == "6h":
        return 360
    elif interval == "12h":
        return 720
    elif interval == "1d":
        return "D"
    elif interval == "1w":
        return "W"
    elif interval == "1M":
        return "M"


def get_interval_in_seconds(interval, valid_intervals):
    if interval not in valid_intervals:
        raise ValueError("Incorrect time interval specified")
    if interval == "1m":
        return 60
    elif interval == "3m":
        return 3 * 60
    elif interval == "5m":
        return 5 * 60
    elif interval == "15m":
        return 15 * 60
    elif interval == "30m":
        return 30 * 60
    elif interval == "1h":
        return 60 * 60
    elif interval == "2h":
        return 120 * 60
    elif interval == "4h":
        return 240 * 60
    elif interval == "6h":
        return 360 * 60
    elif interval == "12h":
        return 720 * 60
    elif interval == "1d":
        return 86400
    elif interval == "1w":
        return 7 * 86400
    elif interval == "1M":
        return 30 * 86400


def get_klines_desired_only_cols(data, desired_indexes):
    return [[datum[index] for index in desired_indexes] for datum in data]


def klines_convert_to_pandas(final_data_array):
    df = pd.DataFrame(
        final_data_array,
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
    df.set_index("date", inplace=True)
    return df


def klines_convert_date(data, futures, time_col_idxs):
    for datum in data:
        for idx in time_col_idxs:
            if futures:
                datum[idx] = datetime.fromtimestamp(float(datum[idx]))
            else:
                datum[idx] = datetime.fromtimestamp(float(datum[idx]) / 1000)
