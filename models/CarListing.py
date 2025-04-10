
# CAR LISTING + BUILDER PATTERN 

class CarBuilder:
    def __init__(self, mediator):
        self.mediator = mediator
        self.mediator.register(self) 
        self.car = {}

    #SETTING VEHICLE ATTRIBUTES
    def set_model(self, model):
        self.car["model"] = model

    def set_year(self, year):
        self.car["year"] = year

    def set_mileage(self, mileage):
        self.car["mileage"] = mileage

    def set_availability(self, availability):
        self.car["availability"] = availability

    def set_location(self, location):
        self.car["location"] = location

    def set_price(self, price):
        self.car["price"] = price

    def get_result(self):
        return self.car
    
    def update(self, sender, action, data=None):
        """Handle updates from the Mediator."""
        if action == "car_built":
            print(f"Car has been built with the following details: {data}")

    def notify_build_complete(self):
        self.mediator.notify(self, "car_built", self.car)


class CarBuilderDirector:
    def __init__(self, builder, mediator):
        self.builder = builder
        self.mediator = mediator

    def construct(self, data):
        self.builder.set_model(data["model"])
        self.builder.set_year(data["year"])
        self.builder.set_mileage(data["mileage"])
        self.builder.set_availability(data["availability"])
        self.builder.set_location(data["location"])
        self.builder.set_price(data["price"])
        self.builder.notify_build_complete()
