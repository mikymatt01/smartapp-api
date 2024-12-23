

class UserNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ReportNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class KPINotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class AlarmNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MachineNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)