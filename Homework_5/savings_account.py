from account import Account
from operation import Operation

class SavingsAccount(Account):
    
    def __init__(self, account_holder, balance=0):
        super().__init__(account_holder, balance)
        self.account_type = "savings"
        self.interest_rate = 0

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        
        if amount > self._balance * 0.5:
            operation = Operation('withdraw', amount, self._balance, 'fail')
            self.operations_history.append(operation)
            raise ValueError(f"Нельзя снять более 50% от текущего баланса. Максимально доступно: {self._balance * 0.5:.2f}")
        
        if self._balance >= amount:
            self._balance -= amount
            operation = Operation('withdraw', amount, self._balance, 'success')
            self.operations_history.append(operation)
            return True
        else:
            operation = Operation('withdraw', amount, self._balance, 'fail')
            self.operations_history.append(operation)
            return False

    def apply_interest(self, rate):
        if rate <= 0:
            raise ValueError("Процентная ставка должна быть положительной")
        
        interest_amount = self._balance * rate
        self._balance += interest_amount
        self.interest_rate = rate
        
        operation = Operation('interest', interest_amount, self._balance, 'success')
        self.operations_history.append(operation)
        
        return interest_amount
