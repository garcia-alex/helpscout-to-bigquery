import os.path
from configparser import ConfigParser


class Config:
    def __init__(self, section):
        """
        Get the ids, passwords and credentials for your application
        """

        self.__parser = ConfigParser()
        self.__parser.read(os.path.dirname(__file__) +
                           os.path.sep + 'config.ini')
        self.__section = section

    def get(self, param):
        return self.__parser.get(self.__section, param)
