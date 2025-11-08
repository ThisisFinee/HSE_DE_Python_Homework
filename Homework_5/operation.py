import datetime

class Operation:
    """Банковская операция"""
    
    def __init__(self, op_type, amount, balance_after, status):
        self.timestamp = datetime.datetime.now()
        self.type = op_type
        self.amount = amount
        self.balance_after = balance_after
        self.status = status

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'type': self.type,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'status': self.status
        }