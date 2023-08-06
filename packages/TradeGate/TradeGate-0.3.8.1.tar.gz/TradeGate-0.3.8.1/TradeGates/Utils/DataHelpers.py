import time


class OrderData:
    def __init__(self, symbol, side, order_type):
        self.symbol = symbol
        self.side = side
        self.order_type = order_type

        self.time_in_force = None
        self.quantity = None
        self.quote_order_qty = None
        self.price = None
        self.new_client_order_id = None
        self.stop_price = None
        self.iceberg_qty = None
        self.new_order_resp_type = None
        self.timestamp = None
        self.extra_params = None
        self.recv_window = None

    def set_time_in_force(self, time_in_force):
        self.time_in_force = time_in_force

    def set_quantity(self, quantity):
        self.quantity = quantity

    def set_quote_order_qty(self, quote_order_qty):
        self.quote_order_qty = quote_order_qty

    def set_price(self, price):
        self.price = price

    def set_new_client_order_id(self, new_client_order_id):
        self.new_client_order_id = new_client_order_id

    def set_stop_price(self, stop_price):
        self.stop_price = stop_price

    def set_iceberg_qty(self, iceberg_qty):
        self.iceberg_qty = iceberg_qty

    def set_new_order_resp_type(self, new_order_resp_type):
        self.new_order_resp_type = new_order_resp_type

    def set_timestamp(self):
        self.timestamp = time.time()

    def set_extra_params(self, extra_params):
        self.extra_params = extra_params


class FuturesOrderData:
    def __init__(self, symbol, side=None, order_type=None):
        self.symbol = symbol
        self.side = side
        self.orderType = order_type

        self.position_side = None
        self.time_in_force = None
        self.quantity = None
        self.quote_quantity = None
        self.reduce_only = None
        self.price = None
        self.new_client_order_id = None
        self.stop_price = None
        self.close_position = None
        self.activation_price = None
        self.callback_rate = None
        self.working_type = None
        self.price_protect = None
        self.new_order_resp_type = None
        self.extra_params = None
        self.leverage = None

    def set_order_side(self, order_side):
        self.side = order_side

    def set_position_side(self, position_side):
        self.position_side = position_side

    def set_time_in_force(self, time_in_force):
        self.time_in_force = time_in_force

    def set_quantity(self, quantity):
        self.quantity = quantity

    def set_reduce_only(self, reduce_only):
        self.reduce_only = reduce_only

    def set_price(self, price):
        self.price = price

    def set_new_client_order_id(self, new_client_order_id):
        self.new_client_order_id = new_client_order_id

    def set_stop_price(self, stop_price):
        self.stop_price = stop_price

    def set_close_position(self, close_position):
        self.close_position = close_position

    def set_activation_price(self, activation_price):
        self.activation_price = activation_price

    def set_callback_rate(self, callback_rate):
        self.callback_rate = callback_rate

    def set_working_type(self, working_type):
        self.working_type = working_type

    def set_price_protect(self, price_protect):
        self.price_protect = price_protect

    def set_new_order_resp_type(self, new_order_resp_type):
        self.new_order_resp_type = new_order_resp_type

    def set_extra_params(self, extra_params):
        self.extra_params = extra_params

    def set_leverage(self, leverage):
        self.leverage = leverage

    def set_quote_quantity(self, quote_quantity):
        self.quote_quantity = quote_quantity


def set_spot_order_data(
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
    extra_params=None,
):
    curr_order = OrderData(symbol.upper(), side.upper(), order_type.upper())
    if quantity is not None:
        curr_order.set_quantity(quantity)
    if price is not None:
        curr_order.set_price(price)
    if time_in_force is not None:
        curr_order.set_time_in_force(time_in_force)
    if stop_price is not None:
        curr_order.set_stop_price(stop_price)
    if iceberg_qty is not None:
        curr_order.set_iceberg_qty(iceberg_qty)
    if new_order_resp_type is not None:
        curr_order.set_new_order_resp_type(new_order_resp_type)
    if new_client_order_id is not None:
        curr_order.set_new_client_order_id(new_client_order_id)
    if extra_params is not None:
        curr_order.set_extra_params(extra_params)
    return curr_order


def set_futures_order_data(
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
    quote_quantity,
):
    if extra_params is None:
        extra_params = {}
    curr_order = FuturesOrderData(symbol=symbol.upper(), order_type=order_type.upper())
    if side is not None:
        curr_order.set_order_side(side)
    if position_side is not None:
        curr_order.set_position_side(position_side)
    if time_in_force is not None:
        curr_order.set_time_in_force(time_in_force)
    if quantity is not None:
        curr_order.set_quantity(quantity)
    if quote_quantity is not None:
        curr_order.set_quote_quantity(quote_quantity)
    if reduce_only is not None:
        curr_order.set_reduce_only(reduce_only)
    if price is not None:
        curr_order.set_price(price)
    if new_client_order_id is not None:
        curr_order.set_new_client_order_id(new_client_order_id)
    if stop_price is not None:
        curr_order.set_stop_price(stop_price)
    if close_position is not None:
        curr_order.set_close_position(close_position)
    if activation_price is not None:
        curr_order.set_activation_price(activation_price)
    if callback_rate is not None:
        curr_order.set_callback_rate(callback_rate)
    if working_type is not None:
        curr_order.set_working_type(working_type)
    if price_protect is not None:
        curr_order.set_price_protect(price_protect)
    if new_order_resp_type is not None:
        curr_order.set_new_order_resp_type(new_order_resp_type)
    if "leverage" in extra_params.keys():
        curr_order.set_leverage(extra_params["leverage"])
    if extra_params is not None:
        curr_order.set_extra_params(extra_params)
    return curr_order


def get_quantity(enter_price, quantity, quote_quantity, step_precision):
    if (quantity is not None and quote_quantity is not None) or (
        quantity is None and quote_quantity is None
    ):
        raise ValueError("Specify either quantity or quoteQuantity and not both")
    if quantity is None:
        if float(step_precision) > 0.5:
            quantity = round(
                quote_quantity / enter_price, len(str(float(step_precision))) - 3
            )
        else:
            quantity = round(
                quote_quantity / enter_price, len(str(float(step_precision))) - 2
            )
    return quantity


def get_tp_sl_limit_order_ids(ordering_result):
    order_ids = {}
    for order in ordering_result:
        if order["type"] == "LIMIT":
            order_ids["mainOrder"] = order["orderId"]
        elif order["type"] == "STOP_MARKET":
            order_ids["stopLoss"] = order["orderId"]
        elif order["type"] == "TAKE_PROFIT_MARKET":
            order_ids["takeProfit"] = order["orderId"]
    return order_ids


def get_tp_sl_market_order_ids(ordering_result, has_sl, has_tp):
    order_ids = {}
    for order in ordering_result:
        if order["type"] == "MARKET":
            order_ids["mainOrder"] = order["orderId"]
        elif order["type"] == "STOP_MARKET":
            order_ids["stopLoss"] = order["orderId"]
        elif order["type"] == "TAKE_PROFIT_MARKET":
            order_ids["takeProfit"] = order["orderId"]

    if "mainOrder" not in order_ids.keys():
        raise RuntimeError("Problem in main order")

    if has_sl and "stopLoss" not in order_ids.keys():
        raise RuntimeError("Problem in stop loss order")

    if has_tp and "takeProfit" not in order_ids.keys():
        raise RuntimeError("Problem in take profit order")
    return order_ids
