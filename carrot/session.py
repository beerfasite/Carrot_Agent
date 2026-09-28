

class Session:
    def __init__(self):
        self.messages: list = []
        self.active_request: str = "(no active user request)"
