"""
Template file for store.py module.
"""

from dataclasses import dataclass
from turtle import width
from typing import Optional, TextIO, List, Tuple, Dict
import curses
import time


TimeStamp = int


Position = int


Location = Tuple[int, int]


@dataclass
class TimeRange:
    start: TimeStamp
    end: TimeStamp


@dataclass
class Container:
    identifier: int
    size: int
    value: int
    arrival: TimeRange
    delivery: TimeRange


class Store:
    ''' Welcome to the Store class! 

        Structure for function documentation:
        Preconditions:
        Requirements for the execution of the function, omitted if there are none.

        Input:
        [Storage unit], Function_argument_1 (type(Function_argument_1)), Function_argument_2 (type(Function_argument_2)), ...
        Output/work:
        Description of what the function does or returns: type(return)

        All functions raise TypeError if the type given does not match the one demanded by the description,
        and assert preconditions to the execution of the function.
        '''

    def __init__(self, width: int):
        '''Input:
        width (int): amount of columns of the storage unit
        Attributes initialized:
        _width: integer, amount of columns of the storage unit (rows of the matrix)
        cash: integer that keeps track of the benefit gained from storing containers (initially empty)
        _storage: matrix of containers represting the store, width is the number of rows of the matrix (initiated at 0)
        _map: dictionary containing containers as key and location as value. (initially empty)
        _containers: list of containers in the store.
        '''
        if not isinstance(width, int):
            raise TypeError("The width is not an integer")
        self._storage: List[List[Container]] = [[]for i in range(width)]
        self._width = width
        self._cash = 0
        self._containers = []
        # keys are c.identifier and value is location
        self._map: Dict[int, Location] = {}

    def width(self) -> int:
        '''Input:
        [Storage unit]
        Output/work:
        Returns the width of the store '''
        return self._width

# unused.
    def empty_store(self) -> bool:
        '''Input:
        [Storage unit], position (int)
        Output/work:
        Returns whether the store is empty: Bool'''
        return len(self._containers == 0)

    def height(self) -> int:
        '''Input:
        [Storage unit]
        Output/work:
        Returns the maximum height of container piles in the store (maximum row length of the storage matrix): int'''
        height = 0
        for l in self._storage:
            height = max(height, len(l))
        return height

    def height_column(self, p: Position):
        '''Pre:
        p is a valid position.
        Input:
        [Storage unit], position (int)
        Output/work:
        Returns the height of the column at position p: int'''
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
        assert(self.valid_position(p))
        return len(self._storage[p])

    def cash(self) -> int:
        '''Input:
        [Storage unit]
        Output/work:
        Returns the cash obtained from storing containers: int'''
        return self._cash

    def valid_position(self, p: Position) -> bool:
        '''Input:
        [Storage unit], position (int)
        Output/work:
        Returns whether the position is valid in the store'''
        return p < self._width

    def add_cash(self, amount: int) -> None:
        '''Input:
        [Storage unit], amount (int)
        Output/work:
        Adds the cash to the current amount in the store: int'''
        if not isinstance(amount, int):
            raise TypeError("Invalid cash amount")
        self._cash += amount

    def add(self, c: Container, p: Position) -> None:
        '''Pre:
        Container can be added to position p.
        Input:
        [Storage unit], container (Container), position (int)
        Output/work:
        Adds a container in the position if possible: None'''
        if not isinstance(c, Container):
            raise TypeError("You are not adding a container")
        if not isinstance(p, Position):
            raise TypeError("The position is incorrect")
        assert(self.can_add(c, p))
        # here storage[loc[1]][loc[0]]=c, but len(storage[loc[1]][loc[0]])=loc[0]+1 as the position
        # in the storage unit starts at 0.
        self._map[c.identifier] = (self.height_column(p), p)
        self._containers.append(c)
        for i in range(p, p+c.size):
            self._storage[i].append(c)

    def remove(self, c: Container) -> None:
        '''Pre:
        Container is in the store and can be removed.
        Input:
        [Storage unit], container (Container)
        Output/work:
        Removes (if possible) the container at indicated position from the storage unit: None'''
        if not isinstance(c, Container):
            raise TypeError("You are not removing a container")
        # Implement a dictionary to find containers easily.
        assert(c.identifier in self._map and self.can_remove(c))
        loc = self.location(c)
        self._map.pop(c.identifier)
        self._containers.remove(c)
        # remove element in map
        for i in range(loc[1], loc[1]+c.size):
            del(self._storage[i][loc[0]])
            # remove the container piece by piece, has as many pieces as its size. (discretization)

    def can_move(self, c: Container, p: Position):
        '''Pre: c is in the store
        Input:
        [Storage unit], container (Container), position (int)
        Output/work:
        Returns whether the container can be moved to position p'''
        if not isinstance(c, Container):
            raise TypeError("This is not a container")
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
        return self.can_remove(c) and self.can_add(c, p)

    def move(self, c: Container, p: Position) -> None:
        ''' Pre:
        Container can be removed and the position is valid for the container.
        Input:
        [Storage unit], container (Container), position (int)
        Output/work:
        Moves a container (if possible) to the position indicated (if available): None'''
        if not isinstance(c, Container):
            raise TypeError("You are not adding a container")
        if not isinstance(p, Position):
            raise TypeError("The position is incorrect")
        if self.can_move(c, p):
            self.remove(c)
            self.add(c, p)
            self._map[c.identifier] = self.location(c)

    def containers(self) -> List[Container]:
        '''Input:
        [Storage unit]
        Output/work:
        Returns a list of all containers in the store: List'''
        return self._containers

    def removable_containers(self) -> List[Container]:
        '''Input:
        [Storage unit]
        Output/work:
        Returns a list of all removable containers in the store: List'''
        removables_list = []
        for c in self.containers():
            if self.can_remove(c):
                removables_list.append(c)
        return removables_list

    def empty(self, p: Position):
        '''Input:
        [Storage unit], position (int)
        Output/work:
        Returns whether there are containers in this position: Bool'''
        if not isinstance(p, Position):
            raise TypeError("Incorrect position")
        return len(self._storage[p]) == 0

    def top_container(self, p: Position) -> Optional[Container]:
        '''Input:
        [Storage unit], position (int)
        Output/work:
        Returns the top container in the position (if it exists): Container or None'''
        if not isinstance(p, Position):
            raise TypeError("Incorrect position")
        if self.empty(p):
            return None
        return self._storage[p][-1]

    # loc[0] is the column in the store, loc[1] is the height/row.
    def location(self, c: Container) -> Optional[Location]:
        '''Input:
        [Storage unit], container (Container)
        Output/work:
        Returns the location of your container, none if it isn't in the storage unit: Location or None'''
        if not isinstance(c, Container):
            raise TypeError("You are not adding a container")
        # location[0] is the row of the store, column of the matrix.
        # location[1] is the column of the store, row of the matrix
        return self._map.get(c.identifier)

    def can_add(self, c: Container, p: Position) -> bool:
        '''Input:
        [Storage unit], container (Container), position (int)
        Output/work:
        Adds a container in given position (if possible): Bool'''
        if not isinstance(c, Container):
            raise TypeError("You are not adding a container")
        if not isinstance(p, Position):
            raise TypeError("The position is incorrect")
        assert(self.valid_position(p))  # position has to be inside the store
        # to add a container, we need a flat surface, i.e. all columns need same height.
        l = self.height_column(p)
        for i in range(p, p+c.size):
            if self.height_column(i) != l:
                return False
        return True

    def can_remove(self, c: Container) -> bool:
        '''Input:
        [Storage unit], container (Container)
        Output/work:
        Returns whether you can remove the container: Bool'''
        if not isinstance(c, Container):
            raise TypeError("You are not adding a container")
        loc = self.location(c)
        # we check if the height of the pile corresponds to the height of the container,
        # otherwise there is one on top
        container_height = loc[0]+1
        if loc is not None and container_height == self.height_column(loc[1]):
            return True
        return False

    def write(self, stdscr: curses.window, caption: str = ''):

        maximum = 15  # maximum number of rows to write
        delay = 0.05  # delay after writing the state

        # start: clear screen
        stdscr.clear()

        # write caption
        stdscr.addstr(0, 0, caption)
        # write floor
        stdscr.addstr(maximum + 3, 0, '—' * 2 * self.width())
        # write cash
        stdscr.addstr(maximum + 4, 0, '$: ' + str(self.cash()))

        # write containers
        for c in self.containers():
            row, column = self.location(c)
            if row < maximum:
                # some random color depending on the identifier of the container
                p = 1 + c.identifier * 764351 % 250
                stdscr.addstr(maximum - row + 2, 2 * column,
                              '  ' * c.size, curses.color_pair(p))
                stdscr.addstr(maximum - row + 2, 2 * column,
                              str(c.identifier % 100), curses.color_pair(p))

        # done
        stdscr.refresh()
        time.sleep(delay)


class Logger:

    """Class to log store actions to a file."""

    _file: TextIO

    def __init__(self, path: str, name: str, width: int):
        self._file = open(path, 'w')
        print(0, 'START', name, width, file=self._file)

    def add(self, t: TimeStamp, c: Container, p: Position):
        print(t, 'ADD', c.identifier, p, file=self._file)

    def remove(self, t: TimeStamp, c: Container):
        print(t, 'REMOVE', c.identifier, file=self._file)

    def move(self, t: TimeStamp, c: Container, p: Position):
        print(t, 'MOVE', c.identifier, p, file=self._file)

    def cash(self, t: TimeStamp, cash: int):
        print(t, 'CASH', cash, file=self._file)


def read_containers(path: str) -> List[Container]:
    """Returns a list of containers read from a file at path."""

    with open(path, 'r') as file:
        containers: List[Container] = []
        for line in file:
            identifier, size, value, arrival_start, arrival_end, delivery_start, delivery_end = map(
                int, line.split())
            container = Container(identifier, size, value, TimeRange(
                arrival_start, arrival_end), TimeRange(delivery_start, delivery_end))
            containers.append(container)
        return containers


def check_and_show(containers_path: str, log_path: str, stdscr: Optional[curses.window] = None):
    """
    Check that the actions stored in the log at log_path with the containers at containers_path are legal.
    Raise an exception if not.
    In the case that stdscr is not None, the store is written after each action.
    """

    # get the data
    containers_list = read_containers(containers_path)
    containers_map = {c.identifier: c for c in containers_list}
    log = open(log_path, 'r')
    lines = log.readlines()

    # process first line
    tokens = lines[0].split()
    assert len(tokens) == 4
    assert tokens[0] == "0"
    assert tokens[1] == "START"
    name = tokens[2]
    width = int(tokens[3])
    last = 0
    store = Store(width)
    if stdscr:
        store.write(stdscr)

    # process remaining lines
    for line in lines[1:]:
        tokens = line.split()
        time = int(tokens[0])
        what = tokens[1]
        assert time >= last
        last = time

        if what == "CASH":
            cash = int(tokens[2])
            assert cash == store.cash()

        elif what == "ADD":
            identifier, position = int(tokens[2]), int(tokens[3])
            store.add(containers_map[identifier], position)

        elif what == "REMOVE":
            identifier = int(tokens[2])
            container = containers_map[identifier]
            store.remove(container)
            if container.delivery.start <= time < container.delivery.end:
                store.add_cash(container.value)

        elif what == "MOVE":
            identifier, position = int(tokens[2]), int(tokens[3])
            store.move(containers_map[identifier], position)

        else:
            assert False

        if stdscr:
            store.write(stdscr, f'{name} t: {time}')
