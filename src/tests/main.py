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
    
print(fi_book)
print('\n\nBook built successfully')