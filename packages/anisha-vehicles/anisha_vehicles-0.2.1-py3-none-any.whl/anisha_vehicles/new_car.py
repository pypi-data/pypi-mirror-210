import logging

LOGGER: logging.Logger = logging.getLogger(__name__)

class NewCar:

    def __init__(self,colour,year_of_manufacture): #this is a constructor, just learn the format
        self.colour=colour
        self.year_of_manufacture=year_of_manufacture

    def press_horn(self):   # all functions within the class must have the (self) defined
        LOGGER.info(f"Beep! I am a {self.colour} {type(self).__name__}, made in the year {self.year_of_manufacture}")
