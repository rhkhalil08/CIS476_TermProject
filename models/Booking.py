# BOOKING + OBSERVER PATTERN #

class Observer:
    def update(self, car_model, start_date, end_date):
        pass


class CarOwner(Observer):
    def __init__(self, email):
        self.email = email
        self.notifications = [] 

    def update(self, car_model, start_date, end_date):
        message = f"[Owner {self.email}] New booking for {car_model} from {start_date} to {end_date}."
        self.notifications.append(message)

class Renter(Observer):
    def __init__(self, email):
        self.email = email
        self.notifications = []  

    def update(self, car_model, start_date, end_date):
        message = f"[Renter {self.email}] Booking confirmed for {car_model} from {start_date} to {end_date}."
        self.notifications.append(message)


class BookingManager:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self, car_model, start_date, end_date):
        for observer in self.observers:
            observer.update(car_model, start_date, end_date)

    def create_booking(self, car_model, start_date, end_date):
        print(f"Booking created for {car_model} from {start_date} to {end_date}.")
        self.notify(car_model, start_date, end_date)
