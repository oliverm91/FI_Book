from enum import Enum

class OrderSide(Enum):
    BID = 'BID'
    OFFER = 'OFFER'

class Order:
    __slots__ = 'notional', 'irr', '_order_id', '_position', 'broker', 'trader', 'all_amount', 'estimated_all_notional'
    def __init__(self, notional: float, irr: float, order_id: str, position: int, broker: int=None, trader: int=None, all_amount: float=None):
        self.notional = notional
        self.irr = irr
        self._order_id = order_id
        self._position = position
        self.broker = broker
        self.trader = trader
        self.all_amount = all_amount
        self.estimated_all_notional = None # To be defined outside library

    def to_dict(self):
        return {
            'notional': self.notional,
            'irr': self.irr,
            'broker': self.broker if self.broker is not None else '',
            'trader': self.trader if self.trader is not None else '',
            'all_amount': self.all_amount if self.all_amount is not None else '',
            'estimated_notional': self.estimated_all_notional if self.estimated_all_notional is not None else ''
        }
    
    def __str__(self):
        return f'Order(notional={self.notional}, irr={self.irr}, order_id={self._order_id}, position={self._position}, broker={self.broker})'