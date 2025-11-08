import pandas as pd
import re
import datetime
import matplotlib.pyplot as plt
from operation import Operation

class Account:
    _account_counter = 1000

    def __init__(self, account_holder, balance=0):
        self._validate_holder_name(account_holder)
        if balance < 0:
            raise ValueError("Начальный баланс не может быть отрицательным")
        
        self.holder = account_holder
        self._balance = balance
        self.account_number = f'ACC-{Account._account_counter}'
        Account._account_counter += 1
        self.operations_history = []

        initial_op = Operation('initial', balance, balance, 'success')
        self.operations_history.append(initial_op)
    
    def _validate_holder_name(self, name):
        # Задание 2 - Этап 4
        pattern = r'^[A-ZА-Я][a-zа-я]+\s+[A-ZА-Я][a-zа-я]+$'
        if not re.match(pattern, name):
            raise ValueError("Имя владельца должно быть в формате 'Имя Фамилия' с заглавных букв")

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        
        self._balance += amount
        operation = Operation('deposit', amount, self._balance, 'success')
        self.operations_history.append(operation)

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        
        if self._balance >= amount:
            self._balance -= amount
            operation = Operation('withdraw', amount, self._balance, 'success')
            self.operations_history.append(operation)
            return True
        else:
            operation = Operation('withdraw', amount, self._balance, 'fail')
            self.operations_history.append(operation)
            return False

    def get_balance(self):
        return self._balance

    def get_history(self):
        return [op.to_dict() for op in self.operations_history]

    def plot_history(self):
        df = pd.DataFrame(self.get_history())
        
        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df['balance_after'], marker='o')
        plt.title(f'История баланса счета {self.account_number}')
        plt.xlabel('Время операции')
        plt.ylabel('Баланс')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def get_large_operations(self, n=5, min_amount=0):
        # Задание 2 - Этап 4
        all_operations = self.get_history()
        
        large_ops = [op for op in all_operations if op['amount'] >= min_amount]
        
        large_ops.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return large_ops[:n]
    
    def analyze_operations_by_date(self, start_date=None, end_date=None):
        all_operations = self.get_history()
        
        if start_date is None:
            start_date = datetime.datetime.min
        if end_date is None:
            end_date = datetime.datetime.max
            
        filtered_ops = [op for op in all_operations 
                       if start_date <= op['timestamp'] <= end_date]
        
        if filtered_ops:
            deposits = [op for op in filtered_ops if op['type'] == 'deposit']
            withdrawals = [op for op in filtered_ops if op['type'] == 'withdraw']
            successful_ops = [op for op in filtered_ops if op['status'] == 'success']
            failed_ops = [op for op in filtered_ops if op['status'] == 'fail']
            
            analysis = {
                'total_operations': len(filtered_ops),
                'total_deposits': len(deposits),
                'total_withdrawals': len(withdrawals),
                'successful_operations': len(successful_ops),
                'failed_operations': len(failed_ops),
                'total_deposit_amount': sum(op['amount'] for op in deposits),
                'total_withdrawal_amount': sum(op['amount'] for op in withdrawals if op['status'] == 'success'),
                'period_start': start_date,
                'period_end': end_date
            }
            return analysis
        else:
            return {"message": "Нет операций за указанный период"}
    