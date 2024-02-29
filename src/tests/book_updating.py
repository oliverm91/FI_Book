from collections import defaultdict
from EasyFIX.Messages import MDMessage
from EasyFIX.Body import MDEntry
from EasyFIX.definitions.market_data.values import MDUpdateAction, MDEntryType, Side
from EasyFIX.definitions.market_data.tags import MDTags

from OrderBook.OrderBook import FI_Book
from OrderBook.NemoOrderBook import Settlement_Condition
from OrderBook.Order import Order, OrderSide


def get_settlement_condition(md_booking_ref_ID_value: str) -> Settlement_Condition:
    if 'OD' in md_booking_ref_ID_value:
        return None
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
    settlement_str = md_entry.get_tag_value(MDTags.BookingRefID)
    settlement_condition = get_settlement_condition(settlement_str)
    side = md_entry.get_tag_value(MDTags.MDEntryType)
    side = _side_mapper[side]
    notional = float(md_entry.get_tag_value(MDTags.MDEntrySize))
    irr = float(md_entry.get_tag_value(MDTags.MDEntryPx))
    valued_amount = float(md_entry.get_tag_value(MDTags.ValuedAmount))
    order_id = md_entry.get_tag_value(MDTags.OrderID)
    currency = md_entry.get_tag_value(MDTags.Currency)
    instrument_type = md_entry.get_tag_value(MDTags.SecurityType)
    position = int(md_entry.get_tag_value(MDTags.MDentryPositionNo))
    order = Order(notional, irr, order_id, position, all_amount=valued_amount)
    
    fi_book.add_order(nemo, order, side, settlement_condition, currency, instrument_type)

def delete_order(md_entry: MDEntry, fi_book: FI_Book):
    order_id = md_entry.get_tag_value(MDTags.OrderID)
    fi_book.delete_order(order_id)

def change_order(md_entry: MDEntry, fi_book: FI_Book):
    order_id = md_entry.get_tag_value(MDTags.OrderID)
    new_notional = float(md_entry.get_tag_value(MDTags.MDEntrySize))
    new_valued_amount = float(md_entry.get_tag_value(MDTags.ValuedAmount))
    order_to_modify = fi_book.get_order(order_id)
    order_to_modify.notional = new_notional
    order_to_modify.all_amount = new_valued_amount

_update_action_mapper = {
    MDUpdateAction.New: add_order,
    MDUpdateAction.Delete: delete_order,
    MDUpdateAction.Change: change_order
}
_skipped_entry_types = set([MDEntryType.Duration, MDEntryType.ClosingPrice, MDEntryType.Trade])
_update_action_order = {
        MDUpdateAction.Change: 1,
        MDUpdateAction.Delete: 2,
        MDUpdateAction.New: 3
}    
def update_book(fix_message: MDMessage, fi_book: FI_Book):
    body = fix_message.body
    update_entries = defaultdict(list[MDEntry])
    entries = body.entries
    for md_entry in entries:
        entry_type = md_entry.get_tag_value(MDTags.MDEntryType)
        if entry_type in _skipped_entry_types:
            continue
        settlement_str = md_entry.get_tag_value(MDTags.BookingRefID)
        if 'OD' in settlement_str:
            continue
        order_id = md_entry.get_tag_value(MDTags.OrderID)
        update_entries[order_id].append(md_entry)

    for order_entries_list in update_entries.values():
        order_entries_list.sort(key= lambda e: _update_action_order[e.get_tag_value(MDTags.MDUpdateAction)])

    for sorted_order_entries in update_entries.values():
        for md_entry in sorted_order_entries:
            func = _update_action_mapper[md_entry.get_tag_value(MDTags.MDUpdateAction)]
            func(md_entry, fi_book)