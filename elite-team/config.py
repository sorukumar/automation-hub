import os

class Config:
    def __init__(self):
        # URLs
        self.login_url = os.environ.get('LOGIN_URL')
        self.schedule_url = os.environ.get('SCHEDULE_URL')
        
        # Credentials
        self.username = os.environ.get('ELITE_USERNAME')
        self.password = os.environ.get('ELITE_PASSWORD')

# Create a singleton instance
config = Config()
