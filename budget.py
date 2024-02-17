from collections import namedtuple
from datetime import datetime
from email.policy import default
from sqlite3 import Date
from tracemalloc import start
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as parse_date
import click
from daterangeparser import parse as dr_parse

class DateRange:
    def __init__(self, start_date: datetime, end_date: datetime=None, year_interval:int=0, month_interval:int=0, week_interval:int=0, day_interval:int=1) -> None:
        self.start_date = start_date
        if end_date:
            self.end_date = end_date
        else: 
            self.end_date = self.start_date + relativedelta(days=10)
        self.years = year_interval
        self.months = month_interval
        self.weeks = week_interval
        self.days = day_interval
        self.current_date = self.start_date

        print(start_date, end_date)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_date < self.end_date:
            ret = self.current_date
            self.current_date += relativedelta(year=self.years, months=self.months, weeks=self.weeks, days=self.days)
            return ret
        else:
            raise StopIteration

class Monthly:
    def __init__(self, start_date: datetime=None, end_date: datetime=None, day: int=None) -> None:
        if start_date and end_date:
            self.set_range(start_date, end_date)
        if day:
            self.day = day

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_date < self.end_date:
            ret = self.current_date

            self.current_date = self.current_date.replace(month=(self.current_date.month + 1) % 12)

            return ret
        else:
            raise StopIteration    

    def set_day(self, day:int):
        # bump the start date to nearest
        if day:
            self.day = day
            if self.start_date.day > self.day:
                self.start_date = self.start_date.replace(month=(self.start_date.month + 1) % 12)
            else:
                self.start_date = self.start_date.replace(day=self.day)

            self.current_date = self.start_date

    def set_range(self, start:datetime, end:datetime):
        self.start_date = start
        self.end_date = end
        self.set_day(self.day)



class BiMonthly:
    def __init__(self, start_date: datetime=None, end_date: datetime=None, days: list[int]=[1,15]) -> None:
        if start_date and end_date:
            self.set_range(start_date, end_date)

        if days:
            self.days = days
            for i in self.days:
                if self.start_date.day > i:
                    self.start_date = self.start_date
                
                self.current_date = self.start_date  

    def __call__(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_date < self.end_date:
            ret = self.current_date

            # if current date is the last,
            if self.current_date.day == self.days[-1]:
                # reset the index to 0
                self.days_idx = 0
                self.current_date = self.current_date.replace(month=(self.current_date.month + 1) % 12)
            else:
                self.occurrence_idx += 1

            self.current_date = self.current_date.replace(day=self.occurrence[self.occurrence_idx])

            return ret
        else:
            raise StopIteration

    def set_day(self, day):
        # bump start date to next nearest

    def set_range(self, start:datetime, end:datetime):
        self.start_date = start
        self.end_date = end

months = {
    "January":1,
    "February":2,
    "March":3,
    "April":4,
    "May":5,
    "June":6,
    "July":7,
    "August":8,
    "September":9,
    "October":10,
    "November":11,
    "December":12
}

monthly = relativedelta(months=+1)
daily = relativedelta(day=1)

class Budget:
    def __init__(self, entries=None) -> None:
        self.budget_entries = entries
        self.now = datetime.now()
        pass

    def generate_budget(self, datestr: str=None):
        print(dr_parse(datestr))
        for entry in self.budget_entries:
            for date_instance in entry.interval().set_range(*dr_parse(datestr)):
                print(budgetEntryString(date_instance, entry.name, entry.amount, entry.payer_account, entry.payee_account))

BudgetEntry = namedtuple("BudgetEntry", "name amount interval payer_account payee_account")
budgetEntryString = lambda date, name, amount, payer_account, payee_account: f"{date.date()} {name}\n  {payer_account}  {amount}\n  {payee_account}\n"

entries = [
    BudgetEntry(name="paycheck", amount=1700.0, interval=BiMonthly(), payer_account="Income:SkySync", payee_account="Assets:USAA:Checking"),
    BudgetEntry(name="rent", amount=1300.0, interval=Monthly(day=3), payer_account="Assets:USAA:Checking", payee_account="Expenses:Housing:Rent")
]

@click.command()
@click.option('-d', '--date', '_date', default=datetime.now())
def main(_date):
    myBudget = Budget(entries)
    myBudget.generate_budget(_date)

if __name__ == '__main__':
    main()