class Dummy:
    """
    Some useful information about this class
    
    Attributes
    ----------
    Dummy.attr_a : of type str
        Default is 'Hello'
    Dummy.attr_b : of type int

    """

    attr_a: str = "Hello"
    attr_b: int

    def __init__(self):
        pass

    def some_method(self, param_a: int):
        """
        Lorem ipsum dolor some_method
        
        Parameters
        ----------
        param_a : argument of type int
        
        """

        return self.attr_b

    @classmethod
    def some_classmethod(cls):
        """
        Lorem ipsum dolor some_classmethod
        """

        return cls.attr_b
