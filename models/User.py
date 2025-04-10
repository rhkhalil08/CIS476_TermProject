class SessionManager:
    _instance = None  #Singleton instance
    
    @staticmethod
    def get_instance():
        if SessionManager._instance is None:
            SessionManager._instance = SessionManager()
        return SessionManager._instance

    def __init__(self):
        if SessionManager._instance is not None:
            raise Exception("Needs to be single instance")
        self.user_email = None  

    def set_user(self, email):
        self.user_email = email  

    def get_user(self):
        return self.user_email  

    def clear_user(self):
        self.user_email = None  
