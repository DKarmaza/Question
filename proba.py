from collections import UserDict
import re
from datetime import datetime, timedelta, date

def input_error(func): # Обробка помилок

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            if func.__name__ == "add_contact":
                return "Give me name and phone please."
            elif func.__name__ == "change_contact":
                return "Give me name and changes please."
            elif func.__name__ == "add_birthday":
                return "Give me name and date(DD.MM.YYYY) please."
        except IndexError:
            return "Give me name please."

    return inner

def parse_input(user_input): # Введення команд юзера
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, contacts): # Додавання контакту
    name, phone = args
    contacts[name] = phone
    return "Contact added."

@input_error
def change_contact(args, contacts): # Зміна данних контакту
    name, new_phone = args
    if name in contacts:
        contacts[name] = new_phone
        return "Contact updated."
    else:
        return "Contact not found."

@input_error
def show_phone(args, contacts): # Показ номеру телефона за именем
    name = args[0]
    if name in contacts:
        return contacts[name]
    else:
        return "Contact not found."
    
@input_error
def add_birthday(args, book):
    name, birthday_date = args
    if name in book:
        book[name].add_birthday(birthday_date)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    if name in book:
        return f"{name}'s birthday is {book[name].birthday}"
    else:
        return "Contact not found."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    return "\n".join(f"{record['name']}: {record['congratulation_date']}" for record in upcoming_birthdays)

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field): # клас ім'я
    def __init__(self, value):
        if not value:
            raise ValueError("Ім'я обов'язкове.")
        super().__init__(value)

class Phone(Field): # клас телефон
    def __init__(self, value):
        if not self.is_valid_phone(value):
            raise ValueError("Номер повинен мати 10 цифр")
        super().__init__(value)

    @staticmethod
    def is_valid_phone(value):
        return bool(re.match(r'^\d{10}$', value))

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Не правильний запис дати, він має бути: DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone_number): # додавання телефону
        self.phones.append(Phone(phone_number))

    def remove_phone (self, phone_number): # видалення телефону
        phone_to_remove = None
        for phone in self.phones:
            if phone.value == phone_number:
                phone_to_remove = phone
                break
        
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError("Телефон не знайдено.")

    def edit_phone(self, old_number, new_number): # зміна телефону
        if not self.find_phone(old_number):
            raise ValueError("Старий номер телефону не знайдено.")
        if not Phone.is_valid_phone(new_number): # Перевірка на правильність нового номера
            raise ValueError("Новий номер телефону повинен мати 10 цифр.")
        self.remove_phone(old_number)
        self.add_phone(new_number)

    def find_phone(self, phone_number): # знайти телефон
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday_date):  # додавання дати народження
        self.birthday = Birthday(birthday_date)

    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict): # клас сама книжка
    def add_record(self, record): # додавання телефону у книзі
        self.data[record.name.value] = record

    def find(self, name): # знаходження телефону у книзі
        return self.data.get(name)

    def delete(self, name): # видалення телефону у книзі
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Запис не знайдено.")

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())
    
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                adjusted_birthday = self.adjust_for_weekend(birthday_this_year)
                
                if 0 <= (adjusted_birthday - today).days <= days:
                    congratulation_date_str = adjusted_birthday.strftime("%d.%m.%Y")
                    upcoming_birthdays.append({"name": record.name.value, "congratulation_date": congratulation_date_str})

    def adjust_for_weekend(self, birthday):  # Корекція днів народження
        if birthday.weekday() == 5:  # Якщо субота
            birthday += timedelta(days=2)  # Переносимо на понеділок
        elif birthday.weekday() == 6:  # Якщо неділя
            birthday += timedelta(days=1)  # Переносимо на понеділок
        return birthday

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!") # Вітання
    while True:
        user_input = input("Enter a command: ") # Введення команд
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]: # Закриття программи
            print("Good bye!")
            break
        
        elif command in ["hello", "hi"]: # Початок роботи
            print("How can I help you?")
        
        elif command == "add": # Додати контакт
            print(add_contact(args, book))
        
        elif command == "change": # Змінити контакт
            print(change_contact(args, book))

        elif command == "phone": # Знайти за ім'ям 
            print(show_phone(args, book))

        elif command == "all": # Всі контакти 
            print(book)
        
        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()