from EasyFIX.definitions.market_data.tags import MDTags
from EasyFIX.definitions.market_data.values import MDEntryType, MDUpdateAction

from OrderBook.OrderBook import FI_Book
from OrderBook.warning_logger import BookLogger

from .get_fix_messages import get_messages
from .book_updating import update_book


fix_messages = get_messages()

book_logger = BookLogger('testing_logfile.log', verbose=True)
fi_book = FI_Book(logger=book_logger)
for fix_message in fix_messages:
    update_book(fix_message, fi_book)