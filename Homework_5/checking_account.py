from account import Account

class CheckingAccount(Account):
    """Расчетный счет"""
    
    def __init__(self, account_holder, balance=0):
        super().__init__(account_holder, balance)
        self.account_type = "checking"