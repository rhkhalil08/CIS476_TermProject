from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.User import SessionManager
from models.Booking import BookingManager, CarOwner, Renter
from models.UI_Mediator import Mediator  
from models.CarListing import CarBuilder, CarBuilderDirector  
from models.Payment import PaymentProxy
from models.Password import SecurityQuestionHandler
from models.Messages import Message, MessageMediator


app = Flask(__name__)
app.secret_key = 'your_secret_key' 


# OBSERVER PATTERN VARIABLES
booking_manager = BookingManager()
car_owner = CarOwner(email="owner@example.com")
renter = Renter(email="renter@example.com")
booking_manager.attach(car_owner)
booking_manager.attach(renter)


# ----- HOME PAGE ----- #
@app.route('/')
def home():
    user_email = session.get('user_email')
    return render_template('home.html', user_email=user_email)


#  ----- REGISTERATION PAGE ----- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        email = request.form['email']
        security_question_1 = request.form['security_question_1']
        security_question_2 = request.form['security_question_2']
        security_question_3 = request.form['security_question_3']
    
        flash(f'Registration successful for {email}!', 'success')
        return redirect(url_for('home'))
    
    return render_template('registration.html')

#  ----- LOGIN PAGE ----- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # hardcoded email + pass
        if email == "renter@example.com" and password == "password123":
            SessionManager.get_instance().set_user(email) #singleton instance mirros flash session
            session['user_email'] = email  
            
            flash(f'Login successful! Logged in as {email}', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid input, please try again.', 'danger')
    return render_template('login.html')

#  ----- LOGOUT PAGE ----- #
@app.route('/logout')
def logout():
    SessionManager.get_instance().clear_user()
    session.clear()  # Clear all session data
    session.pop('user_email',None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))



#  ----- BOOKING PAGE ----- #
car_bookings = {}

@app.route('/booking/<car_id>', methods=['GET', 'POST'])
def booking(car_id):
    # Retrieve car details from session (which contains car listings the user creates)
    car_listings = session.get('car_listings', [])
    
    # Find the car based on the car_id
    car = next((car for car in car_listings if car['model'] == car_id), None)

    if not car:
        flash(f'Car {car_id} not found.', 'danger')
        return redirect(url_for('car_listings'))

    car_model = car['model']
    car_price = car['price']

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        #avoids overlapping bookings
        bookings = car_bookings.get(car_id, [])
        for booking in bookings:
            if not (end_date < booking['start'] or start_date > booking['end']):
                flash(f"Car {car_id} is already booked for these dates.", 'danger')
                return redirect(url_for('car_listings'))
            
        bookings.append({'start': start_date, 'end': end_date})
        car_bookings[car_id] = bookings
        session['car_price'] = car_price
        session['booking_details'] = {'car_id': car_id, 'start_date': start_date, 'end_date': end_date}

        #SENDING NOTIFICATION TO OBSERVERS
        booking_manager.create_booking(car_model, start_date, end_date)

        flash(f'Booking confirmed for {car_model} from {start_date} to {end_date}!', 'success')
        return redirect(url_for('payment'))

    car_owner_notifications = car_owner.notifications
    renter_notifications = renter.notifications
    all_notifications = car_owner_notifications + renter_notifications

    return render_template('bookings.html', car_id=car_id, notifications=all_notifications)


#  ----- MESSAGE FEATURE ----- #
mediator_msg = MessageMediator()

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    user_email = session.get('user_email')  
    if not user_email:
        return redirect(url_for('login'))  #checks if user is logged in 

    if request.method == 'POST':
        message_content = request.form['message']
        receiver_email = request.form['receiver_email']  
        mediator_msg.send_message(user_email, receiver_email, message_content)

    #mediator pattern helps send message
    messages_to_display = mediator_msg.get_messages_for_user(user_email)
    return render_template('message.html', messages=messages_to_display)


#  ----- ADD CAR LISTING ----- #
mediator = Mediator()
@app.route('/add-car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        car_builder = CarBuilder(mediator) 
        car_director = CarBuilderDirector(car_builder, mediator)  

        car_data = {
            "model": request.form['model'],
            "year": request.form['year'],
            "mileage": request.form['mileage'], 
            "availability": request.form['availability'],
            "location": request.form['location'],
            "price": float(request.form['price'])
        }

        car_director.construct(car_data)
        car_listings = session.get('car_listings', [])
        car_listings.append(car_builder.get_result())
        session['car_listings'] = car_listings
        
        flash(f'Car {car_data["model"]} added successfully!', 'success')
        return redirect(url_for('car_listings')) 

    return render_template('car_listings.html', car_listings=session.get('car_listings', []))

@app.route('/car-listings') #helps display car listings
def car_listings():
    cars = session.get('car_listings', [])
    return render_template('car_listings.html', car_listings=cars)


@app.route('/delete-car/<car_model>', methods=['GET']) #delete listing feature
def delete_car(car_model):
    car_listings = session.get('car_listings', [])
    car_listings = [car for car in car_listings if car['model'] != car_model]
    session['car_listings'] = car_listings
    
    flash(f'Car listing for {car_model} has been removed.', 'success')
    return redirect(url_for('car_listings'))

@app.route('/update-car/<car_model>', methods=['GET', 'POST']) #update car listing feature
def update_car(car_model):
    car_listings = session.get('car_listings', [])
    car_to_update = next((car for car in car_listings if car['model'] == car_model), None)
    
    if not car_to_update:
        flash(f'Car listing for {car_model} not found.', 'danger')
        return redirect(url_for('car_listings'))
    
    if request.method == 'POST':
        car_to_update['model'] = request.form['model']
        car_to_update['year'] = request.form['year']
        car_to_update['price'] = request.form['price']
        car_to_update['availability'] = request.form['availability']
        car_to_update['location'] = request.form['location']
        car_to_update['mileage'] = request.form['mileage']
        
        session['car_listings'] = car_listings
        
        flash(f'Car listing for {car_model} has been updated.', 'success')
        return redirect(url_for('car_listings'))
    
    return render_template('update_car.html', car=car_to_update)


#  ----- PAYMENT PAGE ----- #
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_email' not in session:
        flash("Please log in first to make a payment.", 'warning')
        return redirect(url_for('login'))
    
    car_price = float(session.get('car_price', 0)) 
    booking_details = session.get('booking_details', {})
    car_id = booking_details.get('car_id', 'Unknown car')
    start_date = booking_details.get('start_date', 'Unknown date')
    end_date = booking_details.get('end_date', 'Unknown date')

    from_user = session['user_email']  
    to_user = "owner@example.com"  #sample email !!

    if request.method == 'POST':
        payment_proxy = PaymentProxy()
        payment_successful = payment_proxy.pay(car_price, from_user, to_user)

        if payment_successful:
            flash(f"Payment of ${car_price} for {car_id} from {start_date} to {end_date} was successful!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Payment failed. Please try again.", 'danger')

    return render_template('payment.html', amount=car_price, car_id=car_id, start_date=start_date, end_date=end_date)

#  -----  PASSWORD RECOVERY ----- #
@app.route('/recover-password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        
        correct_answers = {
            'security_answer1': 'Mary',
            'security_answer2': 'Fluffy',
            'security_answer3': 'New York'
        }

        answer1 = request.form.get('security_answer1')
        answer2 = request.form.get('security_answer2')
        answer3 = request.form.get('security_answer3')

        flash("Password recovery successful! Your new password has been sent to your email.", "success")
        session.modified = True
        
        return render_template('password_recover.html', show_button=True)
    return render_template('password_recover.html')


if __name__ == "__main__":
    app.run(debug=True)
