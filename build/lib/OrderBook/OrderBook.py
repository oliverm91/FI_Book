from collections import deque
import json
from .warning_logger import BookLogger
from .Order import Order, OrderSide
from .NemoOrderBook import NemoSettlementOrderBook, NemoSettlementOrderBookSide, Settlement_Condition, NemoOrderBook


class FI_Book:
    def __init__(self, nemo_curr_dict: dict[str, str]=None, nemo_it_dict: dict[str, str]=None, logger: BookLogger=None):
        self.nemo_curr_dict = nemo_curr_dict if nemo_curr_dict is not None else {}
        self.nemo_it_dict = nemo_it_dict if nemo_it_dict is not None else {}
        
        self.nemo_order_books_dict: dict[str, NemoOrderBook] = {}
        self.last_impacted_nemos = deque(maxlen=10)

        self.logger = logger

        self._order_id_nemo_settlement_order_book_side: dict[str, NemoSettlementOrderBookSide] = {}

    def add_order(self, nemo: str, order: Order, order_side: OrderSide, settlement_condition: Settlement_Condition):
        nemo_settlement_order_book = self.get_nemo_settlement_order_book(nemo, settlement_condition)
        nemo_settlement_order_book.add_order(order, order_side)
        self.last_impacted_nemos.append(nemo)

        self._order_id_nemo_settlement_order_book_side[order._order_id] = nemo_settlement_order_book.bid_order_book_side if order_side==OrderSide.BID else nemo_settlement_order_book.offer_order_book_side

    def delete_order(self, order_id: str):
        if order_id not in self._order_id_nemo_settlement_order_book_side:
            raise LookupError(f'Trying to delete order_id {order_id}, but is not registered.')
        self._order_id_nemo_settlement_order_book_side[order_id].delete_order()
        del self._order_id_nemo_settlement_order_book_side[order_id]
    
    def get_nemo_settlement_order_book(self, nemo: str, settlement_condition: Settlement_Condition) -> NemoSettlementOrderBook:
        if nemo not in self.nemo_order_books_dict:
            self.nemo_order_books_dict[nemo] = NemoOrderBook(nemo, self.nemo_curr_dict[nemo], self.nemo_it_dict[nemo], {}, logger=self.logger)

        nemo_order_book = self.nemo_order_books_dict[nemo]
        nemo_settlement_order_book = nemo_order_book.get_nemo_settlement_order_book(settlement_condition)
        return nemo_settlement_order_book
    
    def to_json(self, nemos: list[str]=None) -> str:
        pre_nemos = list(self.nemo_order_books_dict.keys())
        if nemos is not None:
            nemos = [nemo for nemo in pre_nemos if nemo in nemos]

        settlement_condition_dict = {Settlement_Condition.PH: 'PH', Settlement_Condition.PM: 'PM', Settlement_Condition.CN: 'CN'}

        nemo_settlement_lines = []
        for nemo in nemos:
            nemo_order_book = self.nemo_order_books_dict[nemo]
            for settlement_condition, nemo_settlement_order_book in nemo_order_book.settlement_order_book_dict.items():
                if nemo_settlement_order_book.bid_order_book_side.total_orders + nemo_settlement_order_book.offer_order_book_side.total_orders > 0:
                    bid_orders = [vars(bid_order) for bid_order in nemo_settlement_order_book.bid_order_book_side.orders]
                    offer_orders = [vars(offer_order) for offer_order in nemo_settlement_order_book.offer_order_book_side.orders]
                    nemo_settlement_line = [nemo, settlement_condition_dict[settlement_condition], bid_orders, offer_orders]
                    nemo_settlement_lines.append(nemo_settlement_line)

        return json.dumps(nemo_settlement_lines, indent=4)