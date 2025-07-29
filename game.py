'''
the game module reads an input simulating the game turn by turn
'''
from yogi import read
from board import *
from player import *
from places import * 

class Game:
    _turns: int
    _path_price: int
    _city_price: int
    _destruction_price: int
    _cash: int
    _max_cities: int
    _players_info: list[Player]
    _board_info: Board 
    _num_players: int
    
    _current_turn: int
    _player_num: int
    
    def __init__(self):
        self._current_turn = 1
        self._player_num = 0

        try:
            read(str)
            self._turns = read(int)
            assert self._turns > 0

            read(str)
            self._path_price = read(int)
            assert self._path_price > 0

            read(str)
            self._city_price = read(int)
            assert self._city_price > 0

            read(str)
            self._destruction_price = read(int)
            assert self._destruction_price > 0

            read(str)
            self._cash = read(int) #initial cash for each player

            read(str)
            self._max_cities = read(int) 
            assert self._max_cities > 0 #NO 0 -> game starts with 1 house/player

            read(str)
            board_size = (read(int), read(int)) #boxsize
            assert board_size[0] > 0 and board_size[1] > 0

            resources = [[read(int) for _ in range (board_size[1])] for _ in range (board_size[0])]
            
            read(str)
            self._num_players = read(int)
            self._players_info: list[Player] = []

            for i in range(self._num_players):
                assert read(str) == 'player_color'
                self._players_info.append(Player(i + 1, self._cash, read(str)))
                        
            self._board_info =  Board(board_size, resources) 
            
            for player in self._players_info:
                assert read(str) == 'player_city'
                city = (read(int), read(int))
                if self._coordinates_in_board(city) and not self._already_cities(city):
                    self._board_info.add_city(player, city) #entrada ciutats 
                else:
                    raise AssertionError #assert: coordinates in board and not existing city

        except AssertionError:
            print('Incorrect input; try again :)')
            exit(1) #program exits due to an error       
        
    def get_board(self) -> Board:
        '''returns board info: size, resources, cities and paths'''
        return self._board_info
    
    def get_players(self) -> list[Player]:
        '''returns the list of this game Players'''
        return self._players_info
    
    def get_current_player(self) -> Player:
        '''returns the current turn's player information'''
        return self._players_info[self._player_num]

    def is_game_over(self) -> bool:
        '''checks if the number of turns has reached the maximum'''
        return self._current_turn > self._turns
    
    def next_turn(self) -> None:
        if not self.is_game_over(): 
            
            #1  SUBSTRACT RESOURCES 
            current_player = self.get_current_player() #avoid repetitive function call
            for player, city in self._board_info.get_cities(): 
                if player == current_player: #city belongs to current plaeyer
                    money = 0
                    for neighbour in self._neighbours(city): 
                        if self._neighbour_in_board(neighbour) and self._not_empty(neighbour):
                            self._board_info.substract_resource(neighbour)
                            money += 1 # -1 resource/cell -> +1 money/substracted resource
                    current_player.update_cash(money)
            
            #2 ACTIONS
            action = read(str)
            if action == 'build_path':
                player = read(int)
                path = ((read(int), read(int)), (read(int), read(int)))
                
                if player != current_player.get_id(): 
                    print(self._playeridError())
                
                else:
                    if (self._can_afford_path(current_player.get_cash()) and self._module_1(path) and 
                        all(self._coordinates_in_board(coord) for coord in path) and self._legal(path)):

                        self._board_info.add_path(self.get_current_player(), path)
                        self.get_current_player().update_cash(- self._path_price) #cash_update
                    else:
                        print(self._illegalPath())
             
            elif action == 'build_city':
                player = read(int)
                city = (read(int), read(int))
                if player != current_player.get_id():
                    print(self._playeridError())
                else:
                    if (self._can_afford_city(current_player.get_cash()) and self._coordinates_in_board(city) and
                        self._city_building_valid(city)):
                    
                        cp_path, adjacent = self._adj_path(city)
                        if (cp_path and adjacent):
                            self._board_info.add_city(current_player, city)
                            current_player.update_cash(- self._city_price)
                        else:
                            print(self._illegalCity())
                    else:
                        print(self._illegalCity())
            else: 
                player = read(int)
                city = (read(int), read(int))
                
                if action != 'destroy_city':
                    print(self._wronginput())
                
                elif player != current_player.get_id():
                    print(self._playeridError())
                
                else:
                    if self._can_afford_destruction(current_player.get_cash()):
                        correct_player, existing_city = self._cityowner_and_coinciding(city)
                        if (correct_player and existing_city):
                            self._board_info.remove_city(city)
                            current_player.update_cash(- self._destruction_price)
                        else:
                            print(self._illegalDest())
                    else:
                        print(self._not_enough_money())

            self._current_turn += 1
            self._num_player_update()
        
        else:
            print(f'Game over! Congratulations player number {self._winner()}! You are the conqueror of Camins i Ciutats!')
            exit()
            
    #INITIAL CITIES CONDITIONS
    def _already_cities(self, coord: Coord) -> bool:
        '''check if there is already a city in the given coordinate'''
        for city in self._board_info.get_cities():
            if city[1] == coord:
                return True   
        return False
    
    #PLAYER UPDATE NUM:
    def _num_player_update(self) -> None:
        '''updates the current player number according to the number of players'''
        if (self._player_num + 1) == self._num_players: #restart the round for players
            self._player_num = 0
        else:
            self._player_num += 1

    #ILLEGAL ACTIONS MESSAGES
    def _playeridError(self) -> str:
        return (f"You've entered a wrong identification! Sorry, you'll have to skip your turn!")
    
    def _illegalPath(self) -> str:
        return (f"You can't build a path! Taking illegal actions has consequences; you lose your turn!")
    
    def _illegalCity(self) -> str:
        return (f"You can't build a city, and you know it! There are consequences for breaking the rules; you'll have to skip your turn!")
    
    def _wronginput(self) -> str:
        return (f"Oops! This action doesn't exist! Looks like you'll have to skip this turn.")
    
    def _not_enough_money(self) -> str:
        return (f"You don't have enough money to destroy a city right now. You'll have to pass your turn.")
    
    def _illegalDest(self) -> str:
        return(f"Hey! Trying to destroy a city that doesn't even belong to you? Nice try, but rules are rules! You'll have to skip your turn!")

    #CONDITIONS FOR ACTIONS#

    #PRICE CONDITIONS
    def _can_afford_path(self, cash: int) -> bool:
        '''checks if a player has enough cash to build a path'''
        return cash >= self._path_price
    
    def _can_afford_city(self, cash: int) -> bool:
        '''checks if a player has enough cash to build a house'''
        return cash >= self._city_price
    
    def _can_afford_destruction(self, cash: int) -> bool:
        '''checks if a player has enough cash to destroy a house'''
        return cash >= self._destruction_price

    #PATH AND CITIES COORDINATES
    def _coordinates_in_board(self, coord: Coord) -> bool:
        '''checks whether a given coordinate of path/city fits in the board'''
        return 0 <= coord[0] <= self._board_info.get_size()[0] + 1 and 0 <= coord[1] <= self._board_info.get_size()[1] + 1    
    
    #PATH length
    def _module_1(self, path: Path) -> bool:
        '''checks path length == 1'''
        return (path[1][0] - path[0][0]) ** 2 + (path[1][1] - path[0][1]) ** 2 == 1

    #PATH and CITY usage
    def _adj_path(self, coord: Coord) -> tuple[bool, bool]:
        '''
        checks if a coordinate is adjacent to a path belonging to the current player
        returns(T/F: adj to path from the current player, T/F: coord adj to a path)
        '''
        for path in self._board_info.get_paths():
            if path[0] == self.get_current_player() and (path[1][0] == coord or path[1][1] == coord):
                return (True, True)
            elif path[0] != self.get_current_player() and (path[1][0] == coord or path[1][1] == coord):
                return (False, True)
        return (False, False) #(False: default, False: NO ADJ TO PATH)

    def _cityowner_and_coinciding(self, coord: Coord) -> tuple[bool, bool]:
        '''
        checks if the coordinate belongs to a city and whether it belongs to the current player
        returns (T/F: current player's house, T/F: is an existing house
        '''    
        for city in self._board_info.get_cities():
            if city[1] == coord:
                if city[0] == self.get_current_player():
                    return (True, True)
                else:
                    return (False, True)
        return (False, False)  #(False: default, False: NO HOUSE)
    
    #PATH exclusive
    def _legal(self, path: Path) -> bool:
        '''
        checks if a path is legal: 
        1. unexisting path
        2. one endpoint is adjacent to path or city from the current player
        3. NONE of the endpoints has another player's adjacent path, EXCEPT if the coord is a city 
        '''
        if self._not_existing_path(path): 
            adj_city_1 = self._cityowner_and_coinciding(path[0])
            adj_city_2 = self._cityowner_and_coinciding(path[1])

            if adj_city_1[1]: #coord 1 adj to city
                if adj_city_1[0]: #adj to current player city
                    return adj_city_2[1] or self._adj_path(path[1])[0] or not self._adj_path(path[1])[1] #not adj to anything
                else: #adj to other player's city
                    return adj_city_2[0] or self._adj_path(path[1])[0]
            else:
                if adj_city_2[1]: #coord2 adj to city
                    if adj_city_2[0]: #to current player city
                        return self._adj_path(path[0])[0] or not self._adj_path(path[1])[1] #not adj to anything
                    else:
                        return self._adj_path(path[0])[0]
                else: #NONE of the coords is adj to a city
                    if self._adj_path(path[0])[0]: #coord1 adj to current player path
                        return self._adj_path(path[1])[0] or not self._adj_path(path[1])[1] #coord2 adj to current player path or solo
                    elif self._adj_path(path[1])[0]: #coord2 adj to current player path
                        return self._adj_path(path[0])[0] or not self._adj_path(path[0])[1]  #coord1 adj to current player path or solo
                    else:
                        return False
        return False

    def _not_existing_path(self, path: Path) -> bool:
        '''checks that the path doesn't already exists'''
        for _, path_coord in self._board_info.get_paths():
            if path_coord == path:
                return False
        return True

    #FOR CITIES
    def _city_building_valid(self, coord: Coord) -> bool:
        '''check that the city is not already a city
        and that the player hasn't exceeded the limit of cities allowed'''
        cities = 0
        for player, city in self._board_info.get_cities():
            if player == self.get_current_player():
                cities += 1
            if city == coord:
                return False    
        return cities < self._max_cities
    
    #NEIGHBOURS COORDINATES:
    def _neighbours(self, coord: Coord) -> list[Coord]:
        '''returns the 4 cells that surround the city'''
        return[(coord[0], coord[1]), (coord[0], coord[1] - 1), (coord[0] - 1, coord[1] - 1), (coord[0] - 1, coord[1])]
        #return: down-right cell, down-left cell, up-left cell, up-right cell
    
    def _neighbour_in_board(self, coord: Coord) -> bool:
        '''checks whether the coordinates are inside the board'''
        return ((0 <= coord[0] < self._board_info.get_size()[0]) and (0 <= coord[1] < self._board_info.get_size()[1])) 
    
    def _not_empty(self, coord: Coord) -> bool:
        '''checks that the resource cell is not empty'''
        return self._board_info.get_resources(coord) > 0
    
    #MAX CASH -> WINNER
    def _winner(self) -> int:
        '''
        checks the player with the max cash, in case of a tie it returns
        the player with the maximum ID
        '''
        max_cash = float('-inf') #inicialize value at min
        winners = []

        for player in self._players_info:
            cash = player.get_cash()
            
            if cash > max_cash:
                max_cash = cash
                winners = [player.get_id()]
            elif cash == max_cash:
                winners.append(player.get_id())
        
        return winners.pop() #in case of a tie, the player with max id of the winners
