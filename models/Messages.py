# MESSAGE UI + MEDIATOR PATTERN 

class Message:
    def __init__(self, sender, receiver, message_content):
        self.sender = sender
        self.receiver = receiver
        self.message_content = message_content


class MessageMediator:
    def __init__(self):
        self.messages = []

    def send_message(self, sender, receiver, message_content):
        message = Message(sender, receiver, message_content)
        self.messages.append(message)

    def get_messages_for_user(self, user_email):
        return [msg for msg in self.messages if msg.receiver == user_email or msg.sender == user_email]
