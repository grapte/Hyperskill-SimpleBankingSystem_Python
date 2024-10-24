import random
import sqlite3
from dataclasses import dataclass, astuple


@dataclass
class Account:
    acc_id: int
    no: str
    balance: int
    pin: str


def luhn_checksum(no: str) -> int:
    if len(no) == 16:
        no = no[:15]
    if len(no) == 15:
        luhn = [int(c) * 2 if i % 2 == 1 else int(c) for i, c in enumerate(no, start=1)]  # multiply odd digits by 2
        luhn = [i - 9 if i > 9 else i for i in luhn]  # sub 9 from nums over 9
        tot = sum(luhn)  # add all numbers
        chk = 0 if (tot % 10) == 0 else 10 - (tot % 10)
        return chk


def create_account():
    acc_id = random.randint(0, 999999999)
    mii_bin = 400000
    pin = random.randint(0, 9999)
    # Making checksum
    no = f'{mii_bin:06d}{acc_id:09d}'  # no last digit
    chk = luhn_checksum(no)
    no = f'{mii_bin:06d}{acc_id:09d}{chk:01d}'
    a = Account(int(no), no, 0, f'{pin:04d}')
    cx.execute('INSERT INTO card VALUES (?,?,?,?)', astuple(a))
    print(f'Your card has been created')
    print('Your card number:')
    print(f'{a.no}')
    print('Your card PIN:')
    print(f'{a.pin}')


def login_account():
    print('Enter your card number:')
    line_no = input()
    print('Enter your PIN:')
    line_pin = input()
    # select card no and pin
    cu = cx.execute('SELECT * FROM card WHERE number = ? AND pin = ?', (line_no, line_pin))
    acc = cu.fetchone()
    cu.close()

    if acc:
        acc = Account(*acc)
        print(f'You have successfully logged in!')
        account_operation(acc)
        print('You have successfully logged out!')
    else:
        print('Wrong card number or PIN!')


def account_operation(a: Account):
    while True:
        print('''1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit''')
        choice = int(input())
        match choice:
            case 1:
                print(f'Balance: {a.balance}')
            case 2:
                print('Enter income:')
                val = int(input())
                a.balance += val
                cx.execute('UPDATE card SET balance = ? WHERE number = ?', (a.balance, a.no))
                print('Income was added!')
            case 3:
                print('Transfer\nEnter card number:')
                line_no = input()
                if luhn_checksum(line_no) != int(line_no[-1]):
                    print('Probably you made a mistake in the card number. Please try again!')
                else:
                    cu = cx.execute('SELECT * FROM card WHERE number = ?', (line_no,))
                    other_a = cu.fetchone()
                    cu.close()

                    if other_a:
                        other_a = Account(*other_a)
                        print('Enter how much money you want to transfer:')
                        val = int(input())
                        if val > a.balance:
                            print('Not enough money!')
                        else:
                            a.balance -= val
                            other_a.balance += val
                            cx.execute('UPDATE card SET balance = ? WHERE number = ?', (a.balance, a.no))
                            cx.execute('UPDATE card SET balance = ? WHERE number = ?', (other_a.balance, other_a.no))
                            print('Success!')
                    else:

                        print('Such a card does not exist.')
            case 4:
                cx.execute('DELETE * FROM card WHERE number = ?', (a.no,))
                print('The account has been closed!')
                break
            case 5:
                break
            case 0:
                exit_program()
        print()


def exit_program():
    print()
    print('Bye!')
    cx.close()
    exit()


db_file = 'card.s3db'
cx = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
cx.autocommit = True
# Unable to pass test #8 in part 4/4
# Found in unit test that the check code has hard coded the field orders, but wasn't specified in Description.
cx.execute('CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, balance INTEGER DEFAULT 0, pin TEXT)')

while True:
    print('''1. Create an account
2. Log into account
0. Exit''')
    line = int(input())
    match line:
        case 1:
            create_account()
        case 2:
            login_account()
        case 0:
            exit_program()
    print()
