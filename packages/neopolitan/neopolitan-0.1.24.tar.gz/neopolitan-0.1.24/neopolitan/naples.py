"""
Main application code for displaying a board

Why is this file named 'naples.py'?
    To reduce the confusion of naming it 'neopolitan.py', I tried to find a synonym.
    Neopolitan/Neapolitan is a resident of Naples, Italy.
"""

import time

# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes

from neopolitan.board_functions.board import Board
from neopolitan.writing.data_transformation import str_to_data
from neopolitan.board_functions.board_data import default_board_data
from neopolitan.log import get_logger
from neopolitan.const import WIDTH, HEIGHT


def process_board_data_events(board_data, event_list):
    """Manipulate board data according to events"""

    logger = get_logger()

    first = event_list[0]
    if first == 'speed':
        try:
            speed = event_list[1]
        # pylint: disable=broad-except
        except Exception as err:
            # todo: better explanation
            logger.warning('No second value provided, %s', err)
        if speed == 'slow':
            board_data.scroll_slow()
            logger.info('set speed: slow')
        elif speed == 'medium':
            board_data.scroll_medium()
            logger.info('set speed: medium')
        elif speed == 'fast':
            board_data.scroll_fast()
            logger.info('set speed: fast')
        else:
            try:
                speed = float(speed)
                board_data.set_scroll_wait(speed)
                logger.info('set speed: %s', speed)
            except ValueError:
                logger.warning('Cannot parse speed: %s', speed)
    elif first == 'wrap':
        try:
            wrap = event_list[1]
        # pylint: disable=broad-except
        except Exception as err:
            # todo: better explanation
            logger.warning('No second value provided, %s', err)
        if wrap in ('True', '1'):
            board_data.should_wrap = True
            logger.info('set wrap: True')
        elif wrap in ('False', '0'):
            board_data.should_wrap = False
            logger.info('set wrap: False')
        else:
            logger.warning('Cannot parse wrap: %s', wrap)

    return board_data


class Neopolitan:
    """Main application class for displaying a board"""
    def __init__(self, board_data=None, events=None):
        self.board_data = default_board_data if board_data is None else board_data
        self.width = WIDTH
        self.height = HEIGHT
        self.size = WIDTH*HEIGHT
        self.board = None
        self.display = None
        self.board_display = None

        self.events = events

        self.init_board()
        self.board.set_data(str_to_data(board_data.message))

    def __del__(self):
        del self.display

    def init_board(self):
        """Initialize board data"""
        # todo: make better
        if self.board_data.graphical:
            get_logger().info('Initializing graphical display')
            # pylint: disable=import-outside-toplevel
            from neopolitan.display.graphical_display import GraphicalDisplay
            self.board = Board(self.size)
            self.display = GraphicalDisplay(board=self.board)
        else:
            get_logger().info('Initializing hardware display')
            # pylint: disable=import-outside-toplevel
            from neopolitan.display.hardware_display import HardwareDisplay
            self.display = HardwareDisplay(WIDTH*HEIGHT)
            self.board_display = self.display.board_display
            self.board = self.board_display.board

    def loop(self):
        """Main display loop"""
        logger = get_logger()
        while not self.display.should_exit:
            # process events
            # todo: make better
            while self.events and not self.events.empty():
                event = self.events.get()
                logger.info('event: %s', event)
                event_list = event.split()
                first = event_list[0]
                if first == 'exit':
                    return
                if first == 'say':
                    logger.info('say: %s', event)
                    # todo: better handling: this is unintuitive
                    message = ' '
                    for word in event_list[1:]:
                        message += word + ' '
                    logger.info(message)
                    self.board.set_data(str_to_data(message))
                    logger.info('set message: %s', message)
                else: # try board data events
                    self.board_data = process_board_data_events(self.board_data, event_list)
                # todo: error handling
            self.display.loop()
            if self.board_data.scroll_speed:
                self.board.scroll(wrap=self.board_data.should_wrap)

            time.sleep(self.board_data.scroll_wait)
