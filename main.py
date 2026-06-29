from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import os
import time

# =====================================================================
# 1. Configuration & Credentials
# =====================================================================
ACCOUNT_EMAIL = "vek@test.com"
ACCOUNT_PASSWORD = "Testw0rd"
GYM_URL = "https://appbrewery.github.io/gym/"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=chrome_options)
driver.get(GYM_URL)

# Snappy wait window for our inner loop checks
wait = WebDriverWait(driver, 2)


# =====================================================================
# 2. The Network Resilience Retry Wrapper
# =====================================================================
def retry(func, retries=7, description=None):
    """
    Runs a function. If a network glitch happens, catches the error,
    waits 1 second, and retries up to the limit.
    """
    label = description if description else func.__name__
    for attempt in range(1, retries + 1):
        try:
            print(f"🔄 [Attempt {attempt}/{retries}] Starting: {label}...")
            result = func()
            print(f"✅ Success: {label} completed.")
            return result
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException, Exception) as error:
            print(f"⚠️ Network glitch during '{label}': {type(error).__name__}")
            if attempt == retries:
                print(f"❌ CRITICAL: '{label}' failed completely after {retries} attempts.")
                raise error
            time.sleep(1)


# =====================================================================
# 3. Modular Core Functions
# =====================================================================

def login():
    """Handles checking and executing the login process."""
    try:
        # If cookies kept us logged in, skip form steps immediately
        driver.find_element(By.ID, "schedule-page")
        return True
    except NoSuchElementException:
        login_btn = wait.until(ec.element_to_be_clickable((By.ID, "login-button")))
        login_btn.click()

        email_input = wait.until(ec.presence_of_element_located((By.ID, "email-input")))
        email_input.clear()
        email_input.send_keys(ACCOUNT_EMAIL)

        password_input = driver.find_element(By.ID, "password-input")
        password_input.clear()
        password_input.send_keys(ACCOUNT_PASSWORD)

        submit_btn = driver.find_element(By.ID, "submit-button")
        submit_btn.click()

        # Confirm landing layout loaded
        wait.until(ec.presence_of_element_located((By.ID, "schedule-page")))
        return True


def book_classes():
    """Scans grid elements and processes booking requirements."""
    class_cards = driver.find_elements(By.CSS_SELECTOR, "div[id^='class-card-']")
    
    booked_count = 0
    waitlist_count = 0
    already_booked_count = 0

    for card in class_cards:
        day_group = card.find_element(By.XPATH, "./ancestor::div[contains(@id, 'day-group-')]")
        day_title = day_group.find_element(By.TAG_NAME, "h2").text
        
        if "Tue" in day_title or "Thu" in day_title:
            time_text = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text
            
            if "6:00 PM" in time_text:
                class_name = card.find_element(By.CSS_SELECTOR, "h3[id^='class-name-']").text
                button = card.find_element(By.CSS_SELECTOR, "button[id^='book-button-']")
                class_info = f"{class_name} on {day_title}"
                
                initial_text = button.text.strip()

                if initial_text == "Booked":
                    print(f"✓ Already booked: {class_info}")
                    already_booked_count += 1
                elif initial_text == "Waitlisted":
                    print(f"✓ Already on waitlist: {class_info}")
                    already_booked_count += 1
                elif initial_text in ["Book Class", "Join Waitlist"]:
                    # Action block execution function wrapped individually
                    def click_and_verify():
                        button.click()
                        time.sleep(0.5)
                        if button.text.strip() == initial_text:
                            raise Exception("Click dropped by network simulation.")
                        return button.text.strip()

                    final_state = retry(click_and_verify, retries=4, description=f"Booking click for {class_name}")
                    
                    if "Booked" in final_state:
                        print(f"✓ Successfully booked: {class_info}")
                        booked_count += 1
                    else:
                        print(f"✓ Joined waitlist for: {class_info}")
                        waitlist_count += 1
                    time.sleep(0.5)

    return already_booked_count + booked_count + waitlist_count


def get_my_bookings():
    """Navigates to bookings tab ledger view and counts rows."""
    my_bookings_link = driver.find_element(By.ID, "my-bookings-link")
    my_bookings_link.click()

    wait.until(ec.presence_of_element_located((By.ID, "my-bookings-page")))

    verified_count = 0
    all_cards = driver.find_elements(By.CSS_SELECTOR, "div[id*='card-']")
    
    for card in all_cards:
        try:
            when_paragraph = card.find_element(By.XPATH, ".//p[strong[text()='When:']]")
            when_text = when_paragraph.text
            if ("Tue" in when_text or "Thu" in when_text) and "6:00 PM" in when_text:
                class_name = card.find_element(By.TAG_NAME, "h3").text
                print(f"  ✓ Verified: {class_name}")
                verified_count += 1
        except NoSuchElementException:
            pass
            
    return verified_count


# =====================================================================
# 4. Orchestration Pipeline
# =====================================================================

# Step 1: Resilient Portal Login
retry(login, retries=7, description="User Portal Login Authentication")

# Step 2: Resilient Booking Processing
total_booked = retry(book_classes, retries=5, description="Schedule Booking Engine")
print(f"\n--- Total Tuesday/Thursday 6pm classes tracked: {total_booked} ---")

# Step 3: Resilient Verification Page Extraction
print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")
verified_count = retry(get_my_bookings, retries=5, description="My Bookings Page Verification Lookup")

# Final Comparison Panel metrics display
print(f"\n--- VERIFICATION RESULT ---")
print(f"Expected: {total_booked} bookings")
print(f"Found: {verified_count} bookings")

if total_booked == verified_count:
    print("✅ SUCCESS: All bookings verified despite the network chaos! 🦾🏆")
else:
    print(f"❌ MISMATCH: Missing {total_booked - verified_count} bookings")