#PASSWORD RECOVERY + CHAIN OF RESPONSIBILITY PATTERN

class SecurityQuestionHandler:
    def __init__(self, question, correct_answer, next_handler=None):
        self.question = question
        self.correct_answer = correct_answer
        self.next_handler = next_handler

    def handle(self, answer):
        
        if answer != self.correct_answer:
            return False  
        
        if self.next_handler:
            return self.next_handler.handle(answer)
        
        return True  
