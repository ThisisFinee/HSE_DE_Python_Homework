import pandas as pd
import re
import json
import csv
import datetime
import matplotlib.pyplot as plt
from operation import Operation

class Account:
    _account_counter = 1000

    def __init__(self, account_holder: str, balance: int =0):
        self._validate_holder_name(account_holder)
        if balance < 0:
            raise ValueError("Начальный баланс не может быть отрицательным")
        
        self.holder = account_holder
        self._balance = balance
        self.account_number = f'ACC-{Account._account_counter}'
        self.account_type = "default"
        Account._account_counter += 1
        self.operations_history = []

        initial_op = Operation('initial', balance, balance, 'success')
        self.operations_history.append(initial_op)
    
    def _validate_holder_name(self, name: str):
        # Задание 2 - Этап 4
        pattern = r'^[A-ZА-Я][a-zа-я]+\s+[A-ZА-Я][a-zа-я]+$'
        if not re.match(pattern, name):
            raise ValueError("Имя владельца должно быть в формате 'Имя Фамилия' с заглавных букв")

    def _get_valid_operation_types(self):
        return ["deposit", "withdraw"]
    
    def deposit(self, amount: int):
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        
        self._balance += amount
        operation = Operation('deposit', amount, self._balance, 'success')
        self.operations_history.append(operation)

    def withdraw(self, amount: int):
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
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values('timestamp', inplace=True)
        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df['balance_after'], marker='o')
        plt.title(f'История баланса счета {self.account_number}')
        plt.xlabel('Время операции')
        plt.ylabel('Баланс')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def get_large_operations(self, n: int =5, min_amount: int =0):
        # Задание 2 - Этап 4
        all_operations = self.get_history()
        
        large_ops = [op for op in all_operations if op['amount'] >= min_amount]
        
        large_ops.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return large_ops[:n]
    
    def analyze_operations_by_date(self,
                                   start_date: datetime.datetime=None,
                                   end_date: datetime.datetime=None):
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

### Задание 3 ---------
    def _parse_date(self, date_str):
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d.%m.%Y %H:%M:%S',
            '%d.%m.%Y %H:%M'
        ]
        
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Неизвестный формат даты: {date_str}")
    
    def clean_history(self, transactions: list[dict]) -> list[dict]:
        valid_operations = self._get_valid_operation_types()
        cleaned_transactions = []
        
        for transaction in transactions:
            try:
                if transaction['operation'] not in valid_operations:
                    continue
                
                amount = transaction['amount']
                if amount is None or amount == '' or float(amount) <= 0:
                    continue
                
                self._parse_date(transaction['date'])
                
                if transaction['status'] not in ['success', 'fail']:
                    continue
                
                balance_after = transaction['balance_after']
                if balance_after is None or balance_after == '' or float(balance_after) < 0:
                    continue
                
                transaction['amount'] = float(amount)
                transaction['balance_after'] = float(balance_after)
                
                cleaned_transactions.append(transaction)
                
            except (ValueError, KeyError, TypeError):
                continue
                
        return cleaned_transactions
    
    def load_transactions_from_file(self, file_path: str):
        if file_path.endswith('.csv'):
            transactions = self._load_csv(file_path)
        elif file_path.endswith('.json'):
            transactions = self._load_json(file_path)
        else:
            raise ValueError("Поддерживаются только CSV и JSON файлы")

        filtered_transactions = [
            t for t in transactions 
            if t.get('account_number') == self.account_number 
            and t.get('account_type') == self.account_type
        ]
        
        cleaned_transactions = self.clean_history(filtered_transactions)
        
        for transaction in cleaned_transactions:
            operation = Operation(
                op_type=transaction['operation'],
                amount=transaction['amount'],
                balance_after=transaction['balance_after'],
                status=transaction['status']
            )
            operation.timestamp = self._parse_date(transaction['date'])
            self.operations_history.append(operation)
        
        if self.operations_history:
            self._balance = self.operations_history[-1].balance_after
        
        print(f"Загружено {len(cleaned_transactions)} транзакций из {len(filtered_transactions)}")

    def _load_csv(self, file_path: str) -> list[dict]:
        transactions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    transactions.append(row)
        except Exception as e:
            raise ValueError(f"Ошибка чтения CSV файла: {e}")
        return transactions

    def _load_json(self, file_path: str) -> list[dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                transactions = json.load(file)
        except Exception as e:
            raise ValueError(f"Ошибка чтения JSON файла: {e}")
        return transactions