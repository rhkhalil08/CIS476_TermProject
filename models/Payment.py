# PAYMENT AND PROXY PATTERN

class RealPayment:
    def pay(self, amount, from_user, to_user):
        print(f"Processing payment of ${amount} from {from_user} to {to_user}")
        return True


class PaymentProxy:
    def __init__(self):
        self.real_payment = RealPayment()

    def pay(self, amount, from_user, to_user):
        print(f"Validating transaction for ${amount} payment from {from_user} to {to_user}.")
        
        if amount <= 10000:  #hardcoded balance
            print("Payment successful!")
            return self.real_payment.pay(amount, from_user, to_user)
        else:
            print(f"Insufficient balance for {from_user}.")
            return False
