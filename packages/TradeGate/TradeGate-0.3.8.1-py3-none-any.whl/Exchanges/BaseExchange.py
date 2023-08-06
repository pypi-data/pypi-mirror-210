from abc import ABC, abstractmethod


class BaseExchange(ABC):
    @abstractmethod
    def __init__(self, credentials, sandbox=False, unified_in_outs=True):
        pass

    @abstractmethod
    def get_balance(self, asset="", futures=False):
        pass

    @abstractmethod
    def symbol_account_trade_history(
        self, symbol, futures=False, from_id=None, limit=None
    ):
        pass

    @abstractmethod
    def test_spot_order(self, order_data):
        pass

    @abstractmethod
    def make_spot_order(self, order_data):
        pass

    @abstractmethod
    def create_and_test_spot_order(
        self,
        symbol,
        side,
        order_type,
        quantity=None,
        price=None,
        time_in_force=None,
        stop_price=None,
        iceberg_qty=None,
        new_order_resp_type=None,
        new_client_order_id=None,
        extra_params=None,
    ):
        pass

    @abstractmethod
    def get_symbol_orders(
        self,
        symbol,
        futures=False,
        order_id=None,
        start_time=None,
        end_time=None,
        limit=None,
    ):
        pass

    @abstractmethod
    def get_open_orders(self, symbol, futures=False):
        pass

    @abstractmethod
    def cancel_all_symbol_open_orders(self, symbol, futures=False):
        pass

    @abstractmethod
    def cancel_order(self, symbol, order_id=None, local_order_id=None, futures=False):
        pass

    @abstractmethod
    def get_order(self, symbol, order_id=None, local_order_id=None, futures=False):
        pass

    @abstractmethod
    def get_trading_fees(self, futures=False):
        pass

    @abstractmethod
    def get_symbol_ticker_price(self, symbol, futures=False):
        pass

    @abstractmethod
    def get_symbol_klines(
        self,
        symbol,
        interval,
        start_time=None,
        end_time=None,
        limit=None,
        futures=False,
        blvtnav=False,
        convert_date_time=False,
        do_clean=False,
        to_clean_dataframe=False,
    ):
        pass

    @abstractmethod
    def get_exchange_time(self, futures=False):
        pass

    @abstractmethod
    def get_symbol_24h_ticker(self, symbol):
        pass

    @abstractmethod
    def test_futures_order(self, futures_order_data):
        pass

    @abstractmethod
    def make_futures_order(self, futures_order_data):
        pass

    @abstractmethod
    def create_and_test_futures_order(
        self,
        symbol,
        side,
        order_type,
        position_side=None,
        time_in_force=None,
        quantity=None,
        reduce_only=None,
        price=None,
        new_client_order_id=None,
        stop_price=None,
        close_position=None,
        activation_price=None,
        callback_rate=None,
        working_type=None,
        price_protect=None,
        new_order_resp_type=None,
        recv_window=None,
        extra_params=None,
    ):
        pass

    @abstractmethod
    def make_batch_futures_order(self, futures_order_datas):
        pass

    @abstractmethod
    def change_initial_leverage(self, symbol, leverage):
        pass

    @abstractmethod
    def change_margin_type(self, symbol, margin_type, params):
        pass

    @abstractmethod
    def change_position_margin(self, symbol, amount):
        pass

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def spot_best_bid_asks(self, symbol):
        pass

    @abstractmethod
    def get_symbol_order_book(self, symbol, limit=None, futures=False):
        pass

    @abstractmethod
    def get_symbol_recent_trades(self, symbol, limit=None, futures=False):
        pass

    @abstractmethod
    def get_position_info(self, symbol=None):
        pass

    @abstractmethod
    def get_symbol_min_trade(self, symbol, futures=False):
        pass

    @abstractmethod
    def make_sl_tp_limit_futures_order(
        self,
        symbol,
        order_side,
        quantity=None,
        quote_quantity=None,
        enter_price=None,
        take_profit=None,
        stop_loss=None,
        leverage=None,
        margin_type=None,
    ):
        pass

    @abstractmethod
    def get_long_short_ratios(
        self, symbol, period, limit=None, start_time=None, end_time=None
    ):
        pass

    @abstractmethod
    def get_deposit_address(self, coin, network=None):
        pass
