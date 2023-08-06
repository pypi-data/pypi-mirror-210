class VariogramDoesNotCompute(Exception):
    default_message = 'Please calculate the variogram first !'

    def __init__(self, message: str = default_message):
        self.message = message
        super().__init__(self.message)
