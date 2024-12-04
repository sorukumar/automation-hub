# config.py
import os
from datetime import datetime, timedelta

class Config:
  def __init__(self):
      self.username = os.environ.get('ELITE_USERNAME')
      self.password = os.environ.get('ELITE_PASSWORD')
      self.base_url = os.environ.get('BASE_URL')
      self.base = os.environ.get('BASE')

      self.booking_config = {
          "type": "1",
          "duration": "120",
          "facility": 1530,
          "start": 13
      }

      self.resources = {
          'R1': 7318,
          'R2': 7319,
          'R3': 7320,
          'R4': 7321
      }

      self.auth_url = f"{self.base_url}/security/showLogin"
      self.booking_url = f"{self.base_url}/{self.base}/reservation/newreservation"

  @staticmethod
  def get_target_date():
      target = datetime.now() + timedelta(days=3)
      return target.strftime("%m/%d/%Y")
