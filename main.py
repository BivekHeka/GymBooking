import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

# 1. Credentials & Configuration
# TIP: You can also use the default built-in account: "student@test.com" / "password123"
ACCOUNT_EMAIL = "vek@test.com"
ACCOUNT_PASSWORD = "Testw0rd"
GYM_URL = "https://appbrewery.github.io/gym/"

# 2. Automated Lock Cleaner
user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
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

# Create a try/except block so if the class isn't on the schedule, the script handles it gracefully
try:
    # Line 1: Let yourself know in the terminal that the script has moved onto Step 3
    print("\nScanning schedule for upcoming Tuesday at 6:00 PM...")

    # Line 2: Define a unique XPath map that isolates the container holding BOTH "Tue" and "6:00 PM", then targets the button inside it
    # Line 2 (FIXED): Finds the 'Tue' header element first, jumps to its class column container, and isolates the 6:00 PM button
    # Line 2 (ULTRA-ROBUST): Finds the Tuesday header by its ID, looks forward for the next 6:00 PM card, and targets its button
    target_xpath = "//h2[contains(@id, 'tue')]/following::div[contains(., '6:00 PM') or contains(., '6:00pm')][1]//button"

    # Line 3: Tell Selenium to wait patiently (up to 10 seconds) until that specific target button becomes clickable on the screen
    booking_btn = wait.until(ec.element_to_be_clickable((By.XPATH, target_xpath)))

    # Line 4: Grab the entire card block text (excluding the button) so we can figure out what type of workout it is
    # Line 4 (FIXED): Selects the specific class card container inside the Tuesday group to extract its readable title text
    # Line 4 (ULTRA-ROBUST): Looks forward from the Tuesday header to get the text of that exact 6:00 PM class wrapper block
    card_element = driver.find_element(By.XPATH, "//h2[contains(@id, 'tue')]/following::div[contains(., '6:00 PM') or contains(., '6:00pm')][1]")
    card_text = card_element.text

    # Line 5: Initialize a default fallback string name for the workout type
    workout_type = "Class"

    # Line 6: Check if the word "Spin" lives anywhere inside the card's readable text layout
    if "Spin" in card_text:
        workout_type = "Spin Class"
    # Line 7: Check if the word "Yoga" lives inside it instead
    elif "Yoga" in card_text:
        workout_type = "Yoga Class"
    # Line 8: Check if the word "HIIT" lives inside it instead
    elif "HIIT" in card_text:
        workout_type = "HIIT Class"

    # Line 9: Command the browser automation to click the targeted "Book Class" or "Join Waitlist" button
    booking_btn.click()

    # Line 10: Output your custom success message directly to the VS Code panel using the string formatting we calculated
    print(f"\n✓ Booked: {workout_type} on Tue at 6:00 PM 📅 🤗")

# Catch the error if Selenium searches for 10 seconds but the Tuesday 6pm class isn't loaded on the DOM
except TimeoutException:
    print("\n❌ Error: Could not locate an open Tuesday class at 6:00 PM on the schedule panel.")

# Catch any other random runtime exception safely without crashing your terminal window
except Exception as error_message:
    print(f"\n❌ Automation runtime error while booking: {error_message}")

