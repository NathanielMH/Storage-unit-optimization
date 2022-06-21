"""
Template file for expert.py module.
"""

from stats import Stats
import sys
import curses
from unittest import result

from store import *
from typing_extensions import Self

TimeStamp = int


Position = int


Location = Tuple[int, int]


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
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
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
        # the second pile is k positions after that, so (k**2-k)+k=k**2
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

    def sell_container(self, c: Container) -> None:
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
                self.sell_container(c)
            else:
                self.move_container(c, p_2)

    def update_time(self) -> None:
        '''Input:
            [Strategy]
            Output/work:
            Adds a time unit to the strategy "clock"
        '''
        self._time += 1

    def height_column(self, p: Position) -> int:
        '''Pre:
        p is a valid position.
        Input:
        [Storage unit], position (int)
        Output/work:
        Returns the height of the column at position p: int'''
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
        assert(self.valid_position(p))
        return len(self._store._storage[p])

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
        if not isinstance(c, Container):
            raise TypeError("Invalid container")
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
        assert(self._store.can_add(c, p))
        self._store.add(c, p)
        self._logger.add(self._time, c, p)
        self.update_time()

    def valid_container_h(self, c: Container, t: int) -> bool:
        ''' Input:
            [Strategy], container (Container), time (int)
            Output/work:
            Returns if the container is valid at time t: bool
        '''
        if c.delivery.end > t >= c.delivery.start:
            return True
        return False

    def adjacent_stack(self, c: Container) -> Position:
        '''Input:
            [Strategy], container (Container)
            Output/work:
            Returns position of adjacent stack, that is stack_position(c.size)+1 mod(2)
        '''
        loc = self._store._map[c.identifier]
        p = loc[1]
        if p == c.size**2:
            return c.size*(c.size-1)
        return c.size**2

    def containers_from_pile(self, p: Position, depth: int) -> List:
        '''Input:
            [Strategy], position (int), depth (int)
            Output/work:
            Returns amount of containers to be removed (sold or deprecated) while exploring column
            in position p with given depth
        '''
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
        if not isinstance(depth, int):
            raise TypeError("Invalid depth")
        assert(depth >= 0)
        assert(self.valid_position(p))
        remaining_time = depth-self.height_column(p)
        if remaining_time > 0:
            depth = self.height_column(p)
        containers = 0
        for i in range(depth):
            c = self._store._storage[p][depth-i-1]
            if self.valid_container(c) or self.expired_container(c):
                containers += 1
        return containers

    def money_from_pile(self, p: Position, depth: int) -> List:
        '''Input:
            [Strategy], position (int), depth (int)
            Output/work:
            Returns amount of cash evaluating containers in position p with given depth
        '''
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
        if not isinstance(depth, int):
            raise TypeError("Invalid depth")
        assert(depth >= 0)
        assert(self.valid_position(p))
        rem_time = depth-self.height_column(p)
        if rem_time > 0:
            depth = self.height_column(p)
        money = 0
        for i in range(depth):
            c = self._store._storage[p][depth-i-1]
            if self.valid_container_h(c, self._time+i):
                money += c.value
        return money, rem_time

    def money_from_removables(self):
        '''Input:
            [Strategy]
            Output/work:
            Returns the money obtained if we were to remove all removable containers
        '''
        money = 0
        for c in self._store.removable_containers():
            if self.valid_container(c):
                money += c.value
        return money

    def pile_score(self, p: Position, depth: int):
        '''Input:
            [Strategy], position (int), depth (int)
            Output/work:
            Returns pile score, scalar that determines interest in exploring that pile
        '''
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
        if not isinstance(depth, int):
            raise TypeError("Invalid depth")
        assert(depth >= 0)
        assert(self.valid_position(p))
        m = 3
        c = 1
        money = self.money_from_pile(p, depth)
        return [(m*money[0]+c*self.containers_from_pile(p, depth))/(m+c), money[1]]

    # pre: depth is correct.
    def dig_pile(self, p: Position, depth: int) -> None:
        '''Input:
            [Strategy], position (int), depth (int)
            Output/work:
            Treats containers in given position with given depth
        '''
        if not isinstance(p, Position):
            raise TypeError("Invalid position")
        if not isinstance(depth, int):
            raise TypeError("Invalid depth")
        assert(depth >= 0)
        assert(self.valid_position(p))
        while depth > 0 and not self._store.empty(p):
            c = self._store._storage[p][self.height_column(p)-1]
            self.evaluate_container(c, self.adjacent_stack(c))
            depth -= 1

    def better_pile(self, pos: Position, best_pile: List, depth: int) -> List:
        '''Input:
            [Strategy], position (int), depth (int), best_pile (List)
            Output/work:
            Returns the better list between the given best and the one in given position
            according to scoring criteria (c.f. self.pile_score()):
            List have the following format [position,score,remaining_time] and are 
            associated to a column.
        '''
        if not isinstance(pos, Position):
            raise TypeError("Invalid position")
        if not isinstance(depth, int):
            raise TypeError("Invalid depth")
        if not isinstance(best_pile, List):
            raise TypeError("Invalid pile_list")
        assert(self.valid_position(pos))
        assert(depth >= 0)
        pile = [pos, 0, 0]  # pos, score, remaining time.
        pile[1:3] = self.pile_score(pos, depth)
        if best_pile[1] < pile[1] or self._store.empty(best_pile[0]):
            return pile
        else:
            return best_pile

    def best_pile(self, depth: int) -> List:
        '''Input:
            [Strategy], depth (int)
            Output/work:
            Returns the best list associated to a pile from all the store at the given time.
        '''
        if not isinstance(depth, int):
            raise TypeError("Invalid depth")
        assert(depth >= 0)
        best_pile = [0, -1, 0]  # pos, money, remaining time.
        for i in range(1, 5):
            best_pile = self.better_pile(i*i, best_pile, depth)
            best_pile = self.better_pile(i*(i-1), best_pile, depth)
        return best_pile

    def least_full_pile(self, c: Container) -> Position:
        '''Input:
            [Strategy], container (Container)
            Output/work:
            Returns the least full pile from the size of the given container.
        '''
        if not isinstance(c, Container):
            raise TypeError("Invalid container")
        if self.height_column(self.stack_position(1, c.size)) > self.height_column(self.stack_position(2, c.size)):
            return self.stack_position(2, c.size)
        return self.stack_position(1, c.size)

    def least_equilibrated_pile(self) -> List:  # big, small
        '''Input:
            [Strategy]
            Output/work:
            Returns the piles which have the biggest difference in height while hosting same
            size containers. Format: [taller_pile, smaller_pile]
        '''
        max_entropy = -1  # biggest difference
        result = []
        for i in range(1, 5):
            pos_1 = self.stack_position(1, i)
            pos_2 = self.stack_position(2, i)
            if max_entropy < abs(self.height_column(pos_2)-self.height_column(pos_1)):
                if self.height_column(pos_2)-self.height_column(pos_1) > 0:
                    result = [pos_2, pos_1]
                else:
                    result = [pos_1, pos_2]
                max_entropy = abs(self.height_column(
                    pos_2)-self.height_column(pos_1))
        return result

    def by_value(self, c: Container) -> int:
        '''Input:
            [Strategy], container (Container)
            Output/work:
            Returns the size of the container. Necessary to sort containers in sort_by_cost function.
        '''
        return c.value

    def sort_by_cost(self, container_list: List) -> List:
        '''Input: 
        [Strategy], List_of_containers (List)
        Output/Work:
        Returns the list of containers sorted by value in descending order, placing first
        the sellable ones.
        '''
        sell = []
        remove = []
        for x in container_list:
            if self.valid_container(x):
                sell.append(x)
            else:
                remove.append(x)
        sorted(sell, key=self.by_value)
        return sell+remove

    def equilibrate_piles(self, rem_time: int, big_pile: Position, small_pile: Position) -> None:
        '''Input:
            [Strategy], rem_time (int), big_pile (Position), small_pile (Position)
            Output/work:
            Procedure that lasts as long as possible while not lasting more than given time:
            consists in equilibrating piles corresponding to same size containers 
            but with different heights
        '''
        if not isinstance(rem_time, int):
            raise TypeError("Invalid time")
        if not isinstance(big_pile, Position):
            raise TypeError("Invalid big_pile")
        if not isinstance(small_pile, Position):
            raise TypeError("Invalid small_pile")
        assert(rem_time >= 0)
        while rem_time > 0 and self.height_column(big_pile) >= self.height_column(small_pile):
            if not self._store.empty(big_pile):
                self.move_container(
                    self._store._storage[big_pile][-1], small_pile)
            rem_time -= 1
        if self.empty_store():
            rem_time = 0
        return rem_time

    def treat_removables(self, c: Container, before_add: bool) -> None:
        '''Input:
            [Strategy], container (Container), before_add (bool)
            Output/work:
            Treats removable containers while there is time starting with the most expensive ones. 
            before_add is true if we only want to treat containers more expensive than the input one,
            false otherwise.
        '''
        removables = self.sort_by_cost(self._store.removable_containers())
        if before_add == True:
            i = 0
            while i < len(removables) and c.delivery.end > self._time and c.value < removables[i].value:
                if self.expired_container(removables[i]):
                    self.lose_container(removables[i])
                elif self.valid_container(removables[i]):
                    self.sell_container(removables[i])
                i += 1
        else:
            i = 0
            while i < len(removables) and c.delivery.end > self._time:
                if self.expired_container(removables[i]):
                    self.lose_container(removables[i])
                elif self.valid_container(removables[i]):
                    self.sell_container(removables[i])
                i += 1

    def exec(self, c: Container):
        '''Input:
            [Strategy], container (Container)
            Output/work:
            Executes one iteration of the expert strategy, corresponding to the intake of the container 
            and the actions within timerange.
        '''
        min_score = 0.3  # cap from which it is worth to act instead of equilibrating piles.
        self.treat_removables(c, True)
        # first we look to cash out containers that are worth more than the one we can add.
        pos_1 = self.least_full_pile(c)
        if self._store.can_add(c, pos_1) and not self.expired_container(c) and c.delivery.end > self._time:
            self.add_container(c, pos_1)
        self.treat_removables(c, False)
        rem_time = c.arrival.end-self._time
        while rem_time > 0 and not self.empty_store():
            best_p = self.best_pile(rem_time)
            if best_p[1] <= min_score:
                piles = self.least_equilibrated_pile()
                rem_time = self.equilibrate_piles(rem_time, piles[0], piles[1])
            else:
                self.dig_pile(best_p[0], rem_time)
                rem_time = best_p[2]


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
