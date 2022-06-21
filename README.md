# Storage-unit-optimization
Python project designed to optimize a storage process given parameters on arrival and delivery timestamps, as well as information on the containers.
Includes a store module where we create a class for the storage unit that processes containers, a simple strategy described later and an expert one.

## Store.py
Includes methods and attributes proper to the reception of containers and cash flow.

## Simple.py
Includes a class for a strategy that is based on the following premise:
the containers have each two different piles depending on their height. At every reception of a container, we add the container to the first pile of its respective
height. With the time remaining until the next container arrives, for every pile we take the container on top and put it in the second pile of its respective height, selling it
if we are in its delivery time parameters or removing it if it is expired.

## Expert.py
Includes a class for a strategy that is more efficient than the simple.py:
We have two piles of container for every possible height. For every container received, we look to add it in its respective pile. Then we evaluate a score for each pile decided
on the amount of removable containers there is and how many cash/space would be obtained/freed. We then check the containers in that pile for removable/sale. 
While we still have time until the next container arrives, we repeat the last process.
