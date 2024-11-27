# scheduler.py
import requests
import logging
from config import Config
import json

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResourceBooker:
  def __init__(self):
      self.config = Config()
      self.session = requests.Session()
      self.headers = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Accept': 'application/json, text/javascript, */*; q=0.01',
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'X-Requested-With': 'XMLHttpRequest'
      }

  def authenticate(self):
      try:
          self.session.get(self.config.auth_url)

          auth_data = {
              'username': self.config.username,
              'password': self.config.password,
              'submit': 'Login'
          }

          response = self.session.post(
              self.config.auth_url,
              data=auth_data,
              headers=self.headers,
              allow_redirects=True
          )

          if response.status_code == 200:
              logger.info("Authentication successful")
              return True
          else:
              logger.error(f"Authentication failed: {response.status_code}")
              return False

      except Exception as e:
          logger.error(f"Authentication error: {str(e)}")
          return False

  def reserve(self, resource_id):
      try:
          target_date = self.config.get_target_date()

          booking_data = {
              'reservableResourceId': resource_id,
              'facilityId': self.config.booking_config['facility'],
              'reservationDate': target_date,
              'startTimeId': self.config.booking_config['start'],
              'reservationTypeId': self.config.booking_config['type'],
              'duration': self.config.booking_config['duration']
          }

          logger.info(f"Attempting reservation for {target_date}")

          response = self.session.post(
              self.config.booking_url,
              data=booking_data,
              headers=self.headers
          )

          if response.status_code == 200:
              if "Good Job" in response.text:
                  logger.info(f"Reservation successful for {target_date}")
                  return True
              else:
                  logger.error("Reservation failed - confirmation not received")
                  logger.debug(f"Response: {response.text}")
                  return False
          else:
              logger.error(f"Reservation failed: {response.status_code}")
              return False

      except Exception as e:
          logger.error(f"Reservation error: {str(e)}")
          return False

def main():
  booker = ResourceBooker()

  if not booker.authenticate():
      logger.error("Authentication failed")
      return

  if booker.reserve(booker.config.resources['R1']):
      logger.info("Primary reservation successful")
  else:
      logger.info("Attempting backup reservation")
      if booker.reserve(booker.config.resources['R2']):
          logger.info("Backup reservation successful")
      else:
          logger.error("All reservation attempts failed")

if __name__ == "__main__":
  main()