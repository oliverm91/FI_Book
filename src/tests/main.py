from typing import Any
from json import loads

from OrderBook.OrderBook import FI_Book
from OrderBook.warning_logger import BookLogger

from .get_fix_messages import get_messages
from .book_updating import update_book


fix_messages = get_messages(exclude=b'lvalgorf', include=b'\x0135=X')

book_logger = BookLogger('testing_logfile.log', verbose=True)
fi_book = FI_Book(logger=book_logger)
for fix_message in fix_messages:
    try:
        update_book(fix_message, fi_book)        
    except Exception as e:
        print(fi_book)
        print('\n\t\t'+fix_message.original_message.decode())
        raise e
    
print('\n\nBook built successfully')
for book_line in loads(fi_book.to_json()):
    nemo = book_line[0]
    sett_condition = book_line[1]
    orders_data: dict[str, list[dict[str, Any]]] = book_line[2]
    for side, orders in orders_data.items():
        for order in orders:
            notional = order['notional']
            irr = order['irr']
            all_amount = order['all_amount']
            print(f'{side}, {nemo}, {sett_condition}, {notional}, {irr}, {all_amount}')
