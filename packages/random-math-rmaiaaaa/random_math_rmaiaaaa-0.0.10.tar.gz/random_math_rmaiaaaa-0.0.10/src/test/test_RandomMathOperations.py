import re
from RandomMath.RandomMathOperations import RandomMath

class TestJustSomeMath:

    def test_random_sum(self):
        
        #Arrange
        randomMath = RandomMath()
        number = 1

        #Act
        result = randomMath.random_sum(number)
        
        #Assert
        assert result > number

        pass