class MissingAuthorizationError(Exception):
    def __init__(self, message, url, *args):
        self.message = message
        self.url = url
        super(MissingAuthorizationError, self).__init__(message, url, *args)
