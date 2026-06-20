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