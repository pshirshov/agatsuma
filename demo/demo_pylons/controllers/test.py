from agatsuma.web.pylons import BaseController

class TestController(BaseController):
    """
    """
    
    def __init__(self, ):
        """
        """
        BaseController.__init__(self)
        
    def example(self):
        return "Pylons are working!"
