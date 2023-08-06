import json
from datetime import datetime

import pandas as pd

from Utils import DataHelpers


def get_spot_order_as_dict(order: DataHelpers.OrderData):
    if order.timestamp is None:
        raise ValueError("Timestamp must be set")

    params = {
        "symbol": order.symbol,
        "side": order.side,
        "type": order.order_type,
        "timestamp": order.timestamp,
    }

    if order.time_in_force is not None:
        params["timeInForce"] = order.time_in_force

    if order.quantity is not None:
        params["quantity"] = order.quantity

    if order.quote_order_qty is not None:
        params["quoteOrderQty"] = order.quote_order_qty

    if order.price is not None:
        params["price"] = order.price

    if order.new_order_resp_type is not None:
        params["newOrderRespType"] = order.new_order_resp_type

    if order.stop_price is not None:
        params["stopPrice"] = order.stop_price

    if order.iceberg_qty is not None:
        params["icebergQty"] = order.iceberg_qty

    if order.new_client_order_id is not None:
        params["newClientOrderId"] = order.new_client_order_id

    if order.recv_window is not None:
        params["recvWindow"] = order.recv_window

    return params


def get_futures_order_as_dict(order: DataHelpers.FuturesOrderData, all_str=False):
    params = {"symbol": order.symbol, "side": order.side, "ordertype": order.orderType}

    if order.position_side is not None:
        params["positionSide"] = order.position_side

    if order.time_in_force is not None:
        params["timeInForce"] = order.time_in_force

    if order.quantity is not None:
        params["quantity"] = order.quantity

    if order.reduce_only is not None:
        params["reduceOnly"] = order.reduce_only

    if order.price is not None:
        params["price"] = order.price

    if order.new_client_order_id is not None:
        params["newClientOrderId"] = order.new_client_order_id

    if order.stop_price is not None:
        params["stopPrice"] = order.stop_price

    if order.close_position is not None:
        params["closePosition"] = order.close_position

    if order.activation_price is not None:
        params["activationPrice"] = order.activation_price

    if order.callback_rate is not None:
        params["callbackRate"] = order.callback_rate

    if order.working_type is not None:
        params["workingType"] = order.working_type

    if order.price_protect is not None:
        params["priceProtect"] = order.price_protect

    if order.new_order_resp_type is not None:
        params["newOrderRespType"] = order.new_order_resp_type

    if all_str:
        for key, value in params.items():
            params[key] = str(value)

    return params


def get_klines_desired_only_cols(data, desired_indexes):
    return [[datum[index] for index in desired_indexes] for datum in data]


def klines_convert_to_pandas(out_array):
    df = pd.DataFrame(
        out_array,
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


def klines_convert_date(data, time_col_idxs):
    for datum in data:
        for idx in time_col_idxs:
            datum[idx] = datetime.fromtimestamp(float(datum[idx]) / 1000)


def extract_symbol_info_from_filters(symbol_filters, ticker_price):
    params = {}
    for symbolFilter in symbol_filters:
        if symbolFilter["filterType"] == "LOT_SIZE":
            params["minQuantity"] = float(symbolFilter["minQty"])
            params["precisionStep"] = float(symbolFilter["stepSize"])
            params["minQuoteQuantity"] = ticker_price * params["minQuantity"]

        if symbolFilter["filterType"] == "PRICE_FILTER":
            params["stepPrice"] = float(symbolFilter["tickSize"])
    return params


def make_batch_order_data(futures_order_datas):
    batch_orders = []
    for order in futures_order_datas:
        order_as_dict = get_futures_order_as_dict(order, all_str=True)
        order_as_dict["type"] = order_as_dict.pop("ordertype")

        order_json = json.dumps(order_as_dict)

        batch_orders.append(order_json)
    return batch_orders
