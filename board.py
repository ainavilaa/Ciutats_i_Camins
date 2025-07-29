'''
info about a board game (size, resources, cities and paths)
'''
from places import *
from player import *

class Board:
    _size: BoxSize
    _initial_resources: list[list[int]]
    _cities: list[tuple[Player, Coord]] = []
    _paths: list[tuple[Player, Path]] = []

    def __init__(self, size: BoxSize, initial_resources: list[list[int]]):
        '''board constructor depending on the size and initial resources'''
        self._size, self._initial_resources = size, initial_resources
    
    def get_size(self) -> BoxSize:
        '''returns the board size'''
        return self._size
    
    def get_resources(self, coord: Coord) -> int:
        '''returns the number of resources a cell of the board has'''
        return self._initial_resources[coord[0]][coord[1]]
   
    def get_cities(self) -> list[tuple[Player, Coord]]:
        '''returns a list of tuples with the name of a player and the coordinate (location) of its city'''
        return self._cities
            
    def get_paths(self) -> list[tuple[Player, Path]]:
        '''returns a list of players and their respective paths'''
        return self._paths
    
    def add_city(self, player: Player, coord: Coord) -> None:
        '''adds a city in the city list: with the player and location (coordinate) info'''
        self._cities.append((player, coord))
    
    def add_path(self, player: Player, path: Path) -> None: 
        '''adds a path in the path list: with the player and path coordinates info'''
        self._paths.append((player, path))

    def remove_city(self, coord: Coord) -> None:
        '''delates a city (Player, Coord) from the city list'''
        for city in self._cities:
            if city[1] == coord:
                self._cities.remove(city)
                break

    def substract_resource(self, coord: Coord) -> None:
        '''substracts 1 unit of resource from the given cell'''
        self._initial_resources[coord[0]][coord[1]] -= 1