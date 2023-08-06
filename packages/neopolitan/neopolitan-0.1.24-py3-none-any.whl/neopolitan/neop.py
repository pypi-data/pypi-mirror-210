"""Main application function"""

# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-branches

import getopt
import sys

from neopolitan.os_detection import log_os
from neopolitan.log import init_logger, get_logger
from neopolitan.naples import Neopolitan
from neopolitan.os_detection import on_pi
from neopolitan.board_functions.board_data import default_board_data
from neopolitan.const import SCROLL_SLOW, SCROLL_MED, SCROLL_FAST

def process_arguments():
    """Process the command line arguments and return them as a BoardData object"""
    logger = get_logger()
    board_data = default_board_data

    argument_list = sys.argv[1:]
    options = 'm:g:s:w:'
    long_options = ['message=', 'graphical=', 'scroll=', 'wrap=']
    try:
        # args, vals
        args = getopt.getopt(argument_list, options, long_options)
        if len(args[0]) > 0:
            for arg, val in args[0]:
                if arg in ('-m', '--message'):
                    board_data.message = val
                elif arg in ('-g', '--graphical'):
                    if val == 'True':
                        board_data.graphical = True
                    elif val == 'False':
                        board_data.graphical = False
                    else:
                        logger.warning('Could not parse "graphical" argument: %s', val)
                elif arg in ('-s', 'scroll'):
                    if val in ('slow', 'medium', 'fast'):
                        board_data.scroll_speed = val
                        if val == 'slow':
                            board_data.scroll_wait = SCROLL_FAST
                        elif val == 'medium':
                            board_data.scroll_wait = SCROLL_MED
                        else: # fast
                            board_data.scroll_wait = SCROLL_SLOW
                    else:
                        logger.warning('Invalid scroll speed: %s', val)
                elif arg in ('-w', 'wrap'):
                    if val == 'True':
                        board_data.should_wrap = True
                    elif val == 'False':
                        board_data.should_wrap = False
                    else:
                        logger.warning('Could not parse "wrap" argument: %s', val)
        # --- Verify OS for graphical/hardware
        if on_pi() and board_data.graphical:
            logger.warning('This code cannot be run in graphical' \
                            ' mode on a Raspberry Pi, setting graphical to False')
            board_data.graphical = False
        if not on_pi() and not board_data.graphical:
            logger.warning('This code cannot be run in hardware mode when not run'\
            ' on a Raspberry Pi, setting graphical to True')
            board_data.graphical = True
        # --- Done verifying
        logger.info('message set to: %s', board_data.message)
        logger.info('graphical set to: %s', board_data.graphical)
        logger.info('scroll speed set to: %s (%s)', board_data.scroll_speed, board_data.scroll_wait)
        logger.info('wrap set to: %s', {board_data.should_wrap})

    except getopt.error as err:
        logger.error('getopt error: %s', err)

    return board_data


def main(events=None, initialize_logger=False):
    """Make a very simple display"""

    if initialize_logger:
        init_logger()
    log_os()

    neopolitan = Neopolitan(board_data=process_arguments(), events=events)
    neopolitan.loop()
    del neopolitan

if __name__ == '__main__': # todo: is this still true when running from the thread?
    main(initialize_logger=True) # try False maybe? for testing
