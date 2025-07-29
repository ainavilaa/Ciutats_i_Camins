'''
info about a player (id num, cash, color)
'''
class Player:
    _id: int
    _cash: int
    _color: str

    def __init__(self, id: int, cash: int, color: str):
        '''constructor with ID number, cash and color parameters'''
        self._id, self._cash, self._color = id, cash, color

    def get_id(self) -> int:
        '''returns the number of player (ID num)'''
        return self._id
    
    def get_cash(self) -> int: 
        '''returns the player's cash'''
        return self._cash
    
    def get_color(self) -> str:
        '''returns the player's colour'''
        return self._color
    
    def update_cash(self, value: int) -> None:
        '''given a negative or positive value, it updates the player's cash'''
        self._cash += value
