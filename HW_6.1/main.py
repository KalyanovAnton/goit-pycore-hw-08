from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # Клас для зберігання імені контакту. Є обов'язковим полем.
		pass

class Phone(Field):
    def __init__(self, value):
         self.value = None
         self.set_value(value)

    def set_value(self, value):
        # Клас для зберігання номера телефону. Має валідацію формату (10 цифр).
        if re.fullmatch(r'\d{10}', value):
            self.value = value
        else:
             raise ValueError("Телефон повинен містити рівно 10 цифр.")
        
    def __str__(self):
         return self.value 

class Birthday(Field):
    def __init__(self, value):
        try:
        #    перевіркa коректності даних
           self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")         

class Record:
    # Клас для зберігання інформації про контакт.
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday  = None

    def add_phone(self, phone):
         self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
             if p.value == phone:
                  self.phones.remove(p)
                  return
        raise ValueError(f"Телефон {phone} не знайдено у списку контактів {self.name.value}.")
    
    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f"Телефон {old_phone} не знайдено у списку контактів {self.name.value}.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        raise ValueError(f"Телефон {phone} не знайдено у списку контактів {self.name.value}.")     

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


class AddressBook(UserDict):
    # Клас для зберігання та управління записами контактів.
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
            return self.data[name] 
        raise KeyError(f"Контакт з ім'ям {name} не знайдено.")



    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return
        raise KeyError(f"Контакт з ім'ям {name} не знайдено.")
    
    
    def get_upcoming_birthdays(self, days=7):
        # Повертає список контактів, у яких день народження буде в найближчі 'days' днів.
        date_today = datetime.today().date()
        list_birthdays = []
        
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.date()
                birthday_this_year = birthday.replace(year=date_today.year)
                
                if date_today > birthday_this_year:
                    birthday_this_year = birthday_this_year.replace(year=date_today.year + 1)

                difference_days = (birthday_this_year - date_today).days

                if 0 <= difference_days <= days:
                    if birthday_this_year.weekday() == 5:  # Saturday
                        congratulation_date = birthday_this_year + timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:  # Sunday
                        congratulation_date = birthday_this_year + timedelta(days=1)
                    else:
                        congratulation_date = birthday_this_year

                    list_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%Y.%m.%d")
                    })

        return list_birthdays
    




        
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return"ПОМИЛКА: Неправильний формат. Будь ласка, введіть ім'я і номер телефону."
        except IndexError:
            return "ПОМИЛКА: Недостатньо аргументів для команди."
        except KeyError:
            return "ПОМИЛКА: Контакт не знайдено."
    return inner



def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено        


@input_error
def get_or_create_contact(name, book):
    try:
        # Якщо контакт вже є, повертаємо існуючий запис
        return book.find(name)
    except KeyError:
        # Якщо контакту немає, створюємо новий запис і додаємо до книги
        new_record = Record(name)
        book.add_record(new_record)
        return new_record



@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = get_or_create_contact(name, book)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        raise KeyError

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"Мобільний телефон для {name}: {', '.join(str(phone) for phone in record.phones)}"
    else:
        raise KeyError
    
    
@input_error
def show_all(args, book):
    if not book:
        return "Немає збережених контактів"
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"День народження {name}: {record.birthday}"
    else:
        return f"День народження для {name} не додано."

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "Немає контактів з днями народження на наступному тижні."
    return "\n".join(f"Ім'я: {user['name']}, дата привітання: {user['congratulation_date']}" for user in upcoming_birthdays)
 
    

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))  
        elif command == "phone":
            print(show_phone(args, book))  
        elif command == "all":
            print(show_all(args, book))
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