"""
Template file for simple.py module.
"""


from shutil import move
import sys
import curses
from typing_extensions import Self

from store import *


class Strategy:

    """ Welcome to the Strategy class!

        Structure for function documentation:
        Preconditions:
        Requirements for the execution of the function, omitted if there are none.

        Input:
        [Strategy], Function_argument_1 (
            type(Function_argument_1)), Function_argument_2 (type(Function_argument_2)), ...
        Output/work:
        Description of what the function does or returns: type(return)

        All functions raise TypeError if the type given does not match the one demanded by the description,
        and assert preconditions to the execution of the function."""

    def __init__(self, width: int, log_path: str):
        '''Input:
        [Strategy], width (int), log_path (str)
        _store: storage unit (Store)
        _time: time passed since the beginning of the strategy: increases by 1 everytime we add, move, or remove a container.
        '''
        if not isinstance(width, int):
            raise TypeError("The width is not an integer")
        if not isinstance(log_path, str):
            raise TypeError("Incorrect log_path")
        self._store = Store(width)
        self._logger = Logger(log_path, "my_strategy", width)
        self._time = 0

    def valid_container(self, c: Container) -> bool:
        '''Input:
        [Strategy], container (Container)
            Output/work:
            Checks if the container is good to go, if we can make profit by removing it from the store'''
        if not isinstance(c, Container):
            raise TypeError("This is not a container")
        return self._time >= c.delivery.start and not self.expired_container(c)

    def valid_position(self, p: Position) -> bool:
        '''Input:
            [Strategy], position (int)
            Output/work:
            Returns whether the position is valid'''
        return p < self._store._width

    def expired_container(self, c: Container) -> bool:
        '''Input:
            [Strategy], container (Container)
            Output/work:
            Returns whether a container is expired, that is if it isn't within delivery range anymore'''
        if not isinstance(c, Container):
            raise TypeError("This is not a container")
        return self._time >= c.delivery.end

    def stack_position(self, n: int, size: int) -> Position:
        '''Input:
            [Strategy], container (Container), n (int)
            Output/work:
            Returns the position in which the most left part of the container should be according to its size,
            in the 1s or 2nd pile (n)'''
        if not isinstance(n, int):
            raise TypeError("The number is not an integer")
        if not isinstance(size, int):
            raise TypeError("This is not a valid size")
        assert(n <= 2 and n >= 1)
        # As we have to put containers from size 1 to m, we leave room for 2 piles each.
        # Therefore, if we want to know where the kth pile starts, we have to make room for all
        # piles from 1 to k-1. Now that would be 1+2+3+...+(k-1), but as there are 2 piles for each
        # size we have 2(1+2+3+...+(k-1))=k*(k-1)
        # the second pile is k positions after that, so k**2-k+k=k**2
        if n == 1:
            return size*(size-1)
        else:  # n=2
            return size**2

    def lose_container(self, c: Container) -> None:
        '''Pre:
        container can be removed
        Input:
            [Strategy], container (Container)
            Output/work:
            Removes expired container and gives log notice'''
        if not isinstance(c, Container):
            raise TypeError("Invalid container")
        assert(self._store.can_remove(c))
        self._store.remove(c)
        self._logger.remove(self._time, c)
        self.update_time()

    def sold_container(self, c: Container) -> None:
        '''Pre:
        container can be removed
        Input:
            [Strategy], container (Container)
            Output/work:
            Removes valid container, adding the cash gained and gives log notice'''
        if not isinstance(c, Container):
            raise TypeError("Invalid container")
        assert(self._store.can_remove(c))
        self._store.add_cash(c.value)
        self._store.remove(c)
        self._logger.remove(self._time, c)
        self.update_time()

    def move_container(self, c: Container, p: Position) -> None:
        '''Pre:
            container can be moved to position p
        Input:
            [Strategy], container (Container)
            Output/work:
            Moves container to position p and gives log notice'''
        assert(self._store.can_move(c, p))
        self._store.move(c, p)
        self._logger.move(self._time, c, p)
        self.update_time()

    def empty_store(self) -> bool:
        '''Input:
            [Strategy]
            Output/work:
            Returns whether the store is empty'''
        return len(self._store.containers()) == 0

    def evaluate_container(self, c: Container, p_2: Position) -> None:
        '''Input:
            [Strategy], c (Container), p_2 (Position)
            Output/work:
            Evaluates a container and acts accordingly: removes if expired, sold if valid
            and moved to p_2 else. Can always be moved to p_2 strategically speaking.
        '''
        if not isinstance(p_2, Position):
            raise TypeError("Invalid position")
        if not isinstance(c, Container):
            raise TypeError("Invalid container")
        if self._store.can_add(c, p_2) and self._store.can_remove(c):
            if self.expired_container(c):
                self.lose_container(c)
            elif self.valid_container(c):
                self.sold_container(c)
            else:
                self.move_container(c, p_2)

    # Transfers everything on p_1 to p_2.
    def transfer(self, p_1: Position, p_2: Position, time_limit: int) -> None:
        '''Input:
            [Strategy], p_1 (Position), p_2 (Position), time_limit (int)
            Output/work:
            Transfers all containers if possible from pile p_1 to pile p_2,
            whilst removing expired ones and ones that are within delivery range.
        '''
        if not isinstance(p_1, Position):
            raise TypeError("Incorrect position")
        if not isinstance(p_2, Position):
            raise TypeError("Incorrect position")
        assert(self.valid_position(p_1) and self.valid_position(p_2))
        if self.empty_store():
            self.update_time()
        while not self._store.empty(p_1) and time_limit > self._time:
            c = self._store._storage[p_1][-1]
            self.evaluate_container(c, p_2)

    def update_time(self) -> None:
        '''Input:
            [Strategy]
            Output/work:
            Adds a time unit to the strategy "clock"
        '''
        self._time += 1

    def cash(self) -> int:
        '''Input:
            [Strategy]
            Output/work:
            Returns the current cash amount gained from the Strategy
        '''
        return self._store.cash

    def add_container(self, c: Container, p: Position) -> None:
        '''Pre:
            container can be added to given position
        Input:
            [Strategy], container (Container), position (int)
            Output/work:
            Adds container to the store, while updating time and giving log notice
        '''
        self._store.add(c, p)
        self._logger.add(self._time, c, p)
        self.update_time()

    def exec(self, c: Container):
        '''Input:
            [Strategy], container (Container)
            Output/work:
            Executes one iteration of the simple strategy, corresponding to the intake of the container
            and the actions within timerange
        '''
        if not isinstance(c, Container):
            raise TypeError("This is not a container")
        pos_1 = self.stack_position(1, c.size)
        if self._store.can_add(c, pos_1) and not self.expired_container(c):
            self.add_container(c, pos_1)
        while self._time < c.arrival.end:
            for width_pile in range(1, 5):
                pos_1 = self.stack_position(1, width_pile)
                pos_2 = self.stack_position(2, width_pile)
                self.transfer(pos_1, pos_2, c.arrival.end)
                self.transfer(pos_2, pos_1, c.arrival.end)
            # for each width possible (1 to 4), we transfer the containers from the first to the second pile,
            # of their respective width, then from the second to the first.
            # asking if can_add is a formality here, we can always add as we are following a homogenous
            # structure.


def init_curses():
    """Initializes the curses library to get fancy colors and whatnots."""

    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, curses.COLOR_WHITE, i)


def execute_strategy(containers_path: str, log_path: str, width: int):
    """Execute the strategy on an empty store of a certain width reading containers from containers_path and logging to log_path."""

    containers = read_containers(containers_path)
    strategy = Strategy(width, log_path)
    for container in containers:
        strategy.exec(container)


def main(stdscr: curses.window):
    """main script"""

    init_curses()

    containers_path = sys.argv[1]
    log_path = sys.argv[2]
    width = int(sys.argv[3])

    execute_strategy(containers_path, log_path, width)
    check_and_show(containers_path, log_path, stdscr)


# start main script when program executed
if __name__ == '__main__':
    curses.wrapper(main)
