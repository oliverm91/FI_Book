from enum import Enum

class OrderSide(Enum):
    BID = 'BID'
    OFFER = 'OFFER'

class Order:
    __slots__ = 'notional', 'irr', '_order_id', '_position', 'broker', 'trader', 'all_amount'
    def __init__(self, notional: float, irr: float, order_id: str, position: int, broker: int=None, trader: int=None, all_amount: float=None):
        self.notional = notional
        self.irr = irr
        self._order_id = order_id
        self._position = position
        self.broker = broker
        self.trader = trader
        self.all_amount = all_amount

    def __dict__(self):
        return {
            'notional': self.notional,
            'irr': self.irr,
            'broker': getattr(self, 'broker', ''),
            'trader': getattr(self, 'trader', ''),
            'all_amount': getattr(self, 'all_amount', '')
        }
    
    def __str__(self):
        return f'Order(notional={self.notional}, irr={self.irr}, order_id={self._order_id}, position={self._position}, broker={self.broker})'