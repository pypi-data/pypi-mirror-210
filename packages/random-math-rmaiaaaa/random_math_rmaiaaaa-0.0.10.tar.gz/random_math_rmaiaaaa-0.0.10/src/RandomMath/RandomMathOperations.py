import math
import random

class RandomMath:
    def __init__(self) -> None:
        pass

    def random_sum(self, number:int = 0) -> int:
        '''
        Realiza a soma de um número de entrada com um número aleatório
        '''
        random_int = random.randint(1, number)
        return number + random_int