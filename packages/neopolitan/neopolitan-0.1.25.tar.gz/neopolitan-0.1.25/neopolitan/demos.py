"""Demo some functionalities of the board"""

from neopolitan.log import init_logger
from neopolitan.naples import Neopolitan
from neopolitan.board_functions.board_data import default_board_data

# pylint: disable=anomalous-backslash-in-string

LOWER = 'abcdefghijklmnopqrstuvwxyz'
UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS = '0123456789'
SYMBOLS = '$ % ↑ ↓ ( ) - . , : = ~ ! @ & * ? < > ; | \{ \} " \''

def display(msg):
    """Display a message on the board"""

    init_logger()

    board_data = default_board_data
    board_data.message = msg

    board_data.scroll_fast()

    neop = Neopolitan(board_data=board_data)
    neop.loop()
    del neop

def display_all():
    """Display all defined characters"""
    display(f'    {LOWER} {UPPER} {NUMBERS} {SYMBOLS}')

def display_all_lowercase_letters():
    """Display all lowercase letters"""
    display(LOWER)

def display_all_uppercase_letters():
    """Display all uppercase letters"""
    display(UPPER)

def display_all_numbers():
    """Display all numbers"""
    display(NUMBERS)

def display_all_symbols():
    """Display all symbols"""
    display(SYMBOLS)
