from app.utils import add

class TestUtils():
    def test_add_two_positive(self):
        
        # A A A
        '''
        Arrange
        Action
        Assert
        '''
        
        result = add(1, 2)
        expected = 3
        assert result == expected
        
    