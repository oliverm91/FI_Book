from enum import Enum

from .Order import Order, OrderSide
from .warning_logger import BookLogger


class Settlement_Condition(Enum):
    PH = 0
    PM = 1
    CN = 2


class NemoSettlementOrderBookSide:
    def __init__(self, orders: list[Order], logger: BookLogger=None):
        self.orders = orders
        self.logger = logger

        self.total_orders = len(orders)

        self._order_id_order_dict: dict[str, Order] = {order._order_id: order for order in self.orders}

    @property
    def total_orders(self):
        return self._total_orders

    @total_orders.setter
    def total_orders(self, value):
        if value < 0:
            raise ValueError("Total orders cannot be less than zero.")
        self._total_orders = value

    def add_order(self, new_order: Order, raise_on_already_added_id: bool=True):
        if new_order._order_id in self._order_id_order_dict:
            msg = f'Trying to add Order ID {new_order._order_id} but already added.'
            if raise_on_already_added_id:                
                raise ValueError(msg)
            else:
                warning_msg = f'Warning: {msg}. Proceeding to modify old one for new one.'
                self.logger.log(warning_msg)
        self.orders.insert(new_order._position - 1, new_order)
        self.total_orders += 1
        self._order_id_order_dict[new_order._order_id] = new_order
        following_orders = self.orders[new_order._position:]
        for following_order in following_orders:
            following_order._position += 1

    def delete_order(self, order_id: str, raise_on_id_not_found: bool=True, raise_on_negative_position: bool=True, log_warning: bool=True):
        if order_id not in self._order_id_order_dict:
            msg = f'Trying to delete Order ID {order_id}. ID not found.'
            if raise_on_id_not_found:                
                raise LookupError(msg)
            elif log_warning:
                warning_msg = f'Warning: {msg}. Skipping delete order...'
                self.logger.log(warning_msg)

        order_to_delete = self._order_id_order_dict[order_id]
        self.orders.remove(order_to_delete)
        try:
            self.total_orders -= 1
        except ValueError as ve:
            msg = f'{ve}\nError trying to delete order with ID {order_id}. Total orders is 0.\nOrders:\n{self.orders}'
            if raise_on_negative_position:
                raise ValueError(msg)
            elif log_warning:
                self.logger(f'Warning: {msg}. Skipping delete order...')

        deleted_position = order_to_delete._position
        del self._order_id_order_dict[order_id]
        following_orders = self.orders[deleted_position:]
        for following_order in following_orders:
            following_order._position -= 1

    def get_order(self, order_id: str) -> Order:
        return self._order_id_order_dict[order_id]


class NemoSettlementOrderBook:
    def __init__(self, bid_order_book_side: NemoSettlementOrderBookSide, offer_order_book_side: NemoSettlementOrderBookSide, settlement_condition: Settlement_Condition):
        self.bid_order_book_side = bid_order_book_side
        self.offer_order_book_side = offer_order_book_side
        self.settlement = settlement_condition

    def add_order(self, new_order: Order, order_side: OrderSide):
        order_book_side = self.get_order_book_side(order_side)
        order_book_side.add_order(new_order)

    def delete_order(self, order_id: str, order_side: OrderSide):
        order_book_side = self.get_order_book_side(order_side)
        order_book_side.delete_order(order_id)      

    def get_order_book_side(self, order_side: OrderSide) -> NemoSettlementOrderBookSide:
        if order_side == OrderSide.BID:
            return self.bid_order_book_side
        else:
            return self.offer_order_book_side
        

class NemoOrderBook:
    def __init__(self, nemo: str, currency: str, instrument_type: str, settlement_order_book_dict: dict[Settlement_Condition, NemoSettlementOrderBook], logger: BookLogger=None):
        self.nemo = nemo
        self.currency = currency
        self.instrument_type = instrument_type
        self.settlement_order_book_dict = settlement_order_book_dict
        self.logger = logger
        
        for settlement_condition in Settlement_Condition:
            if settlement_condition not in self.settlement_order_book_dict:
                self.settlement_order_book_dict[settlement_condition] = NemoSettlementOrderBook(NemoSettlementOrderBookSide([], logger=self.logger), NemoSettlementOrderBookSide([], logger=self.logger), settlement_condition)

    def get_nemo_settlement_order_book(self, settlement_condition: Settlement_Condition) -> NemoSettlementOrderBook:
        return self.settlement_order_book_dict[settlement_condition]

        