class VkError(Exception):
    def __init__(self, error:dict):
        self.error_code:int = int(error['error_code'])
        self.error_msg:str = error['error_msg']
        self.error_params:list = error['request_params']

    def __str__(self):
        return f"{self.error_code}. {self.error_msg}\nrequest_params: {self.error_params}"

__all__ = ('VkError')
