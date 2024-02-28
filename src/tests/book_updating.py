from EasyFIX.Messages import MDMessage
from EasyFIX.Body import MDEntry
from EasyFIX.definitions.market_data.values import MDUpdateAction, MDEntryType, Side
from EasyFIX.definitions.market_data.tags import MDTags

from OrderBook.OrderBook import FI_Book
from OrderBook.NemoOrderBook import Settlement_Condition
from OrderBook.Order import Order, OrderSide


def get_settlement_condition(md_booking_ref_ID_value: str) -> Settlement_Condition:
    if 'PH' in md_booking_ref_ID_value:
        return Settlement_Condition.PH
    elif 'PM' in md_booking_ref_ID_value:
        return Settlement_Condition.PM
    return Settlement_Condition.CN

_side_mapper = {
    MDEntryType.Bid: OrderSide.BID,
    MDEntryType.Offer: OrderSide.OFFER
}
def add_order(md_entry: MDEntry, fi_book: FI_Book):
    nemo = md_entry.get_tag_value(MDTags.Symbol)
    settlement_condition = get_settlement_condition(md_entry.get_tag_value(MDTags.BookingRefID))
    side = md_entry.get_tag_value(MDTags.MDEntryType)
    side = _side_mapper[side]
    notional = int(md_entry.get_tag_value(MDTags.MDEntrySize))
    irr = float(md_entry.get_tag_value(MDTags.MDEntryPx))
    amount = float(md_entry.get_tag_value(MDTags.ValuedAmount))
    order_id = md_entry.get_tag_value(MDTags.OrderID)
    order = Order(notional, irr, order_id, 1, all_amount=amount)
    
    fi_book.add_order(nemo, order, side, settlement_condition)
    pass

_update_action_mapper = {
    MDUpdateAction.New: add_order
}
_skipped_entry_types = set([MDEntryType.Duration, MDEntryType.ClosingPrice])
def update_book(fix_message: MDMessage, fi_book: FI_Book):
    body = fix_message.body
    entries = body.entries
    for entry in entries:
        entry_type = entry.get_tag_value(MDTags.MDEntryType)
        if entry_type in _skipped_entry_types:
            continue
        func = _update_action_mapper[entry.get_tag_value(MDTags.MDUpdateAction)]
        func(entry, fi_book)