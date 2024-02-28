from EasyFIX.parser import create_fix_message
from EasyFIX.Messages import MDMessage


def clean_lines(raw_lines: list[bytes], exclude: bytes=None, include: bytes=None) ->  list[bytes]:
    if exclude is None:
        return [raw_line[raw_line.find(b'8=FIX.4.4'):][:-2] + b'\x01' for raw_line in raw_lines if include in raw_line]
    else:
        return [raw_line[raw_line.find(b'8=FIX.4.4'):][:-2] + b'\x01' for raw_line in raw_lines if (include in raw_line) and (exclude not in raw_line)]

def get_messages(exclude: bytes=None, include: bytes=None) -> list[MDMessage]:
    with open('tests/mdbcsrf_tr-fix-messages.log', 'rb') as f:
        log_lines = f.readlines()
        cleaned_lines = clean_lines(log_lines, exclude=exclude, include=include)
        return [create_fix_message(cleaned_line) for cleaned_line in cleaned_lines]