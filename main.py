import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

# 1. Credentials & Configuration
ACCOUNT_EMAIL = "vek@test.com"
ACCOUNT_PASSWORD = "Testw0rd"
GYM_URL = "https://appbrewery.github.io/gym/"

# 2. Automated Lock Cleaner
user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")
lock_file = os.path.join(user_data_dir, "SingletonLock")
if os.path.exists(lock_file):
    try:
        os.remove(lock_file)
    except Exception:
        shutil.rmtree(user_data_dir, ignore_errors=True)

# 3. Browser Setup
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=chrome_options)
driver.get(GYM_URL)

wait = WebDriverWait(driver, 10)

# 4. Direct Login Sequence
try:
    print("Checking if we need to log in...")
    login_btn = wait.until(ec.element_to_be_clickable((By.ID, "login-button")))
    print("Landing page loaded. Clicking login button...")
    login_btn.click()

    print("Waiting for login form fields to render...")
    email_input = wait.until(ec.visibility_of_element_located((By.ID, "email-input")))
    print("Form loaded! Filling details...")
    
    email_input.clear()
    email_input.send_keys(ACCOUNT_EMAIL)

    password_input = driver.find_element(By.ID, "password-input")
    password_input.clear()
    password_input.send_keys(ACCOUNT_PASSWORD)

    submit_btn = driver.find_element(By.ID, "submit-button")
    submit_btn.click()
    print("Submit clicked. Waiting for dashboard...")
    
    # Allow simulated network lag to pass
    time.sleep(2)

    # Wait for dashboard
    wait.until(ec.presence_of_element_located((By.ID, "schedule-page")))
    print("Login sequence complete! Dashboard loaded successfully.")

except TimeoutException:
    print("\n--- Diagnostic Check ---") 
    print("Could not load dashboard immediately. Checking if you were already logged in...")
    try:
        driver.find_element(By.ID, "schedule-page")
        print("Confirmed: Already logged into the dashboard via active cookies!")
    except Exception:
        print("⚠️ Login Failed! The account details were likely rejected by the website.")
        print("Please click on the browser window, register the account manually again, and then re-run.")

print("\nReady for gym booking automation tasks!")


booked_count = 0
waitlisted_count = 0
already_registered_count = 0
target_days = ["sun", "thu"]
# Smart gym booking automatiion

for day in target_days:
    day_name_capitalized = day.capitalize()
    try:
        # Line 1: Let yourself know in the terminal that the script has moved onto Step 3
        print(f"\nScanning schedule for upcoming {day_name_capitalized} at 6:00 PM...")


        # Line 2 The string now dynamically plugs in '{day}' on each pass
        target_xpath = f"//h2[contains(@id, '{day}')]/following::div[contains(., '6:00 PM') or contains(., '6:00pm')][1]//button"

        #3 Wait until the target button is visible on the screen
        booking_btn = wait.until(ec.visibility_of_element_located((By.XPATH, target_xpath)))

        #4 Capture the clean text on the button to check its status
        button_text = booking_btn.text.strip()
        print(f"Current button state detected: '{button_text}'")

        # Line 4 (ULTRA-ROBUST): Looks forward from the Sunday header to get the text of that exact 6:00 PM class wrapper block
        card_element = booking_btn.find_element(By.XPATH, "./ancestor::div[1]")
        card_text = card_element.text

        #5 Identify workout type
        workout_type = "Class"
        if "Spin" in card_text:
            workout_type = "Spin Class"
        elif "Yoga" in card_text:
            workout_type = "Yoga Class"
        elif "HIIT" in card_text:
            workout_type = "HIIT Class"


        #-----SMART DECISION ENGINE--------

        # Condition A: Already Booked
        if button_text == "Booked":
            already_registered_count += 1
            print(f"\nℹ️ Skip: You have already booked this {workout_type} on {day_name_capitalized} 😎")

        # Condition B: Already on Waitlist
        elif button_text == "Waitlisted":
            already_registered_count += 1
            print(f"\nℹ️ Skip: You are already on the waitlist for this {workout_type} on {day_name_capitalized} ⏳")

        # Condition C: Class is Full -> Join Waitlist
        elif button_text == "Join Waitlist":
            booking_btn.click()
            waitlisted_count += 1
            print(f"\n⚠️ Full: {workout_type} was full, but you successfully joined the Waitlist! ⏳🤗")

        # Condition D: Open to Book
        elif button_text == "Book Class":
            booking_btn.click()
            booked_count +=1
            print(f"\n✓ Booked: Fresh spot secured for {workout_type} on {day_name_capitalized} at 6:00 PM! 📅 🤗")

        # Fallback default condition
        else:
            print(f"\n❓ Unknown button state ('{button_text}'). Clicking anyway...")
            booking_btn.click()

    # Catch the error if Selenium searches for 10 seconds but the Sunday 6pm class isn't loaded on the DOM
    except TimeoutException:
        print(f"\n❌ Error: Could not locate an open {day_name_capitalized} class at 6:00 PM on the schedule panel.")

    # Catch any other random runtime exception safely without crashing your terminal window
    except Exception as error_message:
        print(f"\n❌ Automation runtime error while booking: {error_message}")

# ==========================================
# ADDED: STEP 5 - PRINT BOOKING SUMMARY PANEL
# ==========================================
print("\n--- BOOKING SUMMARY ---")
print(f"Classes booked: {booked_count}")
print(f"Waitlists joined: {waitlisted_count}")
print(f"Already booked/waitlisted: {already_registered_count}")

total_processed = booked_count + waitlisted_count + already_registered_count
print(f"Total targeted 6pm classes processed: {total_processed}\n")