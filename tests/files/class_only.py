class Dummy:
    """
    Some useful information about this class
    """

    attr_a: str = "Hello"
    attr_b: int

    def __init__(self):
        pass

    def some_method(self, param_a: int):
        """
        Lorem ipsum dolor some_method
        """

        return self.attr_b

    @classmethod
    def some_classmethod(cls):
        """
        Lorem ipsum dolor some_classmethod
        """

        return cls.attr_b
