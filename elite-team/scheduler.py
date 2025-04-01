# book_tennis_court.py (Based on tennis_booking_automation.py, using config.py)

import time
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import configuration from config.py
try:
    from config import config
except ModuleNotFoundError:
    print("Error: config.py not found. Make sure it's in the same directory.")
    sys.exit(1) # Exit if config cannot be imported

def book_tennis_court(booking_date, booking_time, duration_hours, court_name):
    """
    Automates booking a tennis court 

    Parameters:
    - booking_date: Date for booking in format 'YYYY-MM-DD'
    - booking_time: Time for booking in 12-hour format with AM/PM (e.g., '7:00 PM')
    - duration_hours: Duration in hours (1, 1.5, 2, etc.)
    - court_name: Name of the court (e.g., 'Towns Sq 1')
    """
    # Setup Chrome options
    chrome_options = Options()
    # Uncomment the line below to run in headless mode (no browser UI)
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080") # Added for consistency

    # Initialize the Chrome driver using webdriver-manager
    driver = None # Initialize driver to None for finally block
    try:
        print("Setting up WebDriver...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("WebDriver setup complete.")

        # Navigate to the login page using URL from config
        print(f"Navigating to login page: {config.login_url}")
        driver.get(config.login_url)

        # Wait for the page to load
        print("Waiting for login form...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'username')))

        # Login using credentials from config
        print("Entering credentials...")
        driver.find_element(By.ID, 'username').send_keys(config.username)
        driver.find_element(By.ID, 'password').send_keys(config.password)
        print("Clicking Log In button...")
        driver.find_element(By.XPATH, '//button[text()="Log In"]').click()

        # Wait for the dashboard/home page to load by checking for the "Reservations" link
        print("Waiting for login confirmation (Reservations link)...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(),"Reservations")]')))
        print("Login successful.")

        # Navigate to the reservations page
        print("Navigating to Reservations page...")
        driver.find_element(By.XPATH, '//a[contains(text(),"Reservations")]').click()

        # Wait for the schedule page to load
        print("Waiting for schedule container...")
        schedule_container_locator = (By.XPATH, '//div[contains(@class,"schedule-container")]')
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(schedule_container_locator))
        print("Schedule container loaded.")

        # --- Date Handling ---
        target_date_obj = datetime.strptime(booking_date, '%Y-%m-%d')
        target_date_str_input = target_date_obj.strftime('%Y-%m-%d')
        target_date_str_display = target_date_obj.strftime('%A, %B %d') # Format for comparison

        # Find the date input element
        date_input_locator = (By.XPATH, '//input[@type="date"]')
        date_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(date_input_locator)
        )

        # Find the date display element (adjust locator if needed)
        date_display_locator = (By.XPATH, '//div[contains(@class,"date-display")] | //h2[contains(@class,"current-date")] | //span[contains(@class,"schedule-date")]')
        current_date_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(date_display_locator)
        )
        current_date_text = current_date_element.text
        print(f"Currently displayed date: {current_date_text}")
        print(f"Target date: {target_date_str_display}")

        # Compare dates and change if necessary
        if target_date_str_display not in current_date_text:
            print("Target date differs. Attempting to change date...")
            try:
                old_schedule_container = driver.find_element(*schedule_container_locator)
                print(f"Setting date input to: {target_date_str_input}")
                # Use JavaScript to set the date
                driver.execute_script(f"arguments[0].value = '{target_date_str_input}'; arguments[0].dispatchEvent(new Event('change'));", date_input_element)

                print("Waiting for schedule to refresh...")
                WebDriverWait(driver, 15).until(EC.staleness_of(old_schedule_container))
                WebDriverWait(driver, 15).until(EC.presence_of_element_located(schedule_container_locator))
                print(f"Successfully navigated to date {target_date_str_input}")
            except Exception as date_e:
                 print(f"Error changing date: {str(date_e)}")
                 # Consider adding screenshot here if needed
                 raise # Re-raise the exception to stop the script
        else:
            print("Target date is already displayed.")

        # --- Find the correct time slot and court ---
        print(f"Looking for court '{court_name}'...")
        court_columns = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//th[contains(@class,"court-header")]'))
        )
        court_index = None
        for i, column in enumerate(court_columns):
            if court_name.strip() in column.text.strip():
                court_index = i + 1  # +1 because XPath indices start at 1
                print(f"Found court '{court_name}' at column index: {court_index}")
                break

        if court_index is None:
            raise ValueError(f"Court '{court_name}' not found in the schedule headers.")

        # Find the time row (using exact match for booking_time)
        print(f"Looking for time slot '{booking_time}'...")
        time_rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//tr[contains(@class,"time-slot")]'))
        )
        target_row = None
        for row in time_rows:
            try:
                # Assuming the first cell contains the time text
                time_cell = row.find_element(By.XPATH, './/td[1]')
                if booking_time.strip() == time_cell.text.strip():
                    target_row = row
                    print(f"Found time slot row for '{booking_time}'")
                    break
            except NoSuchElementException:
                continue # Skip rows that don't match the expected structure

        if target_row is None:
            raise ValueError(f"Time slot '{booking_time}' not found in the schedule table.")

        # Click on the cell that corresponds to the court and time
        print(f"Checking availability for court column {court_index} in the target row...")
        court_cell = WebDriverWait(target_row, 5).until(
            EC.presence_of_element_located((By.XPATH, f'.//td[{court_index}]'))
        )

        if "Open" in court_cell.text:
            print(f"Slot is Open. Clicking cell for {court_name} at {booking_time}.")
            # Scroll into view before clicking
            driver.execute_script("arguments[0].scrollIntoView(true);", court_cell)
            time.sleep(0.5) # Brief pause
            court_cell.click()

            # Wait for the reservation form/modal to load (wait for duration dropdown)
            print("Waiting for booking form (duration dropdown)...")
            duration_dropdown_locator = (By.XPATH, '//select[contains(@id,"duration")]')
            duration_dropdown = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(duration_dropdown_locator)
            )

            # Select the duration
            print(f"Selecting duration...")
            duration_select = Select(duration_dropdown)
            # Map duration hours to visible text (adjust if needed based on actual dropdown values)
            duration_options = {
                1: "1 Hour",
                1.5: "90 Minutes",
                2: "2 Hours"
            }
            if duration_hours not in duration_options:
                 raise ValueError(f"Unsupported duration: {duration_hours} hours. Supported: {list(duration_options.keys())}")

            selected_duration_text = duration_options[duration_hours]
            duration_select.select_by_visible_text(selected_duration_text)
            print(f"Selected duration: {selected_duration_text}")

            # Click the Reserve button
            print("Clicking Reserve button...")
            reserve_button_locator = (By.XPATH, '//button[text()="Reserve"]')
            reserve_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(reserve_button_locator)
            )
            reserve_button.click()

            # Wait for confirmation message (adjust locator if needed)
            print("Waiting for booking confirmation message...")
            confirmation_locator = (By.XPATH, "//div[contains(@class, 'alert-success')]" \
                                              " | //div[contains(text(), 'successfully booked')]" \
                                              " | //div[contains(text(), 'Good Job')]")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(confirmation_locator)
            )

            print(f"Successfully booked {court_name} on {booking_date} at {booking_time} for {selected_duration_text}!")
            return True # Indicate success
        else:
            print(f"The court {court_name} is not available at {booking_time} on {booking_date}. Cell text: '{court_cell.text}'")
            return False # Indicate failure

    except TimeoutException as e:
        print(f"A timeout occurred: {str(e)}")
        # Consider adding screenshot saving here
        # driver.save_screenshot("timeout_error.png")
        return False # Indicate failure
    except NoSuchElementException as e:
        print(f"An element was not found: {str(e)}")
        # driver.save_screenshot("element_not_found_error.png")
        return False # Indicate failure
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        # driver.save_screenshot("unexpected_error.png")
        return False # Indicate failure

    finally:
        # Close the browser
        if driver:
            print("Closing browser.")
            driver.quit()

# Example usage
if __name__ == "__main__":
    # --- Configuration for the booking ---
    # Calculate the target date (e.g., 3 days from today)
    TARGET_DAYS_AHEAD = 3
    target_date = (datetime.now() + timedelta(days=TARGET_DAYS_AHEAD)).strftime('%Y-%m-%d')

    # Define booking details
    BOOKING_TIME = "7:00 PM"   # Use the exact format shown on the schedule (e.g., "7:00 PM")
    DURATION_HOURS = 2       # Duration in hours (e.g., 1, 1.5, 2)
    COURT_NAME = "Towns Sq 1" # Exact court name as shown on the schedule

    print(f"--- Starting Tennis Booking ---")
    print(f"Target Date: {target_date}")
    print(f"Time: {BOOKING_TIME}")
    print(f"Duration: {DURATION_HOURS} hours")
    print(f"Court: {COURT_NAME}")
    print(f"-----------------------------")

    # Check if config was loaded successfully
    if 'config' not in globals():
        print("Exiting due to config load failure.")
        sys.exit(1)

    # Check if essential config values are present
    if not all([config.login_url, config.username, config.password]):
         print("Error: LOGIN_URL, ELITE_USERNAME, or ELITE_PASSWORD not found in config or environment variables.")
         sys.exit(1)

    # Run the booking function
    success = book_tennis_court(
        booking_date=target_date,
        booking_time=BOOKING_TIME,
        duration_hours=DURATION_HOURS,
        court_name=COURT_NAME
    )

    if success:
        print("--- Booking Process Completed Successfully ---")
        sys.exit(0)
    else:
        print("--- Booking Process Failed ---")
        sys.exit(1)
