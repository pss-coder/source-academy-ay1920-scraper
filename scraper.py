from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementNotInteractableException
from getpass import getpass
import time
import os

URL = "https://sourceacademy.nus.edu.sg"
IMPLICIT_WAIT = 5
LOGIN_WAIT = 3
SCROLL_INTERVAL = 0.1

def process_page(ext, folder):
    # Load page
    driver.get(URL + ext)
    # Extract list of items
    collapse_button = driver.find_element_by_xpath("//button[contains(., 'Closed')]")
    collapse_button.click()
    titles = [item.text for item in driver.find_elements_by_xpath("//h4[@class='bp3-heading listing-title']")]
    urls = [item.get_attribute("href") for item in driver.find_elements_by_xpath("//a[contains(@href, '" + ext + "')]")]
    # Create main folder
    if not os.path.exists(folder):
        os.mkdir(folder)
    for title, url in zip(titles[::-1], urls[::-1]):
        # File names cannot have ":"
        subfolder = (folder + "/" + title).replace(":", "")
        # Create subfolder
        if not os.path.exists(subfolder):
            os.mkdir(subfolder)
        driver.get(url)
        question_number = 1
        while True:
            try:
                # Skip if question is MCQ
                if len(driver.find_elements_by_xpath("//div[@class='ace_line']")) > 1:
                    file = subfolder + "/Task " + str(question_number) + " Solution.js"
                    f = open(file, "w", encoding="utf-8")
                    lines = []
                    # Click on the text editor
                    driver.find_elements_by_xpath("//div[@class='ace_scroller']")[0].click()
                    while True:
                        # StaleElementReferenceException randomly occurs unpredictably
                        # Keep trying to read the lines until success
                        while True:
                            try:
                                lines_new = [item.get_attribute("innerText") for item in driver.find_elements_by_xpath("//div[@class='ace_line']")[:-2]]
                            except StaleElementReferenceException:
                                continue
                            break
                        # Append lists without the overlapping lines
                        temp = (i for i in range(len(lines_new), 0, -1) if lines_new[:i] == lines[-i:])
                        temp2 = next(temp, 0)
                        lines += lines_new[temp2:]
                        if len(lines_new[temp2:]) == 0:
                            break
                        # Scroll down
                        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                        time.sleep(SCROLL_INTERVAL)
                    for line in lines:
                        f.write(line + "\n")
                    # Handle the last line separately
                    while True:
                        try:
                            f.write(driver.find_elements_by_xpath("//div[@class='ace_line']")[-2].get_attribute("innerText"))
                        except StaleElementReferenceException:
                            continue
                        break
                    f.close()
            except ElementNotInteractableException:
                pass # Probably an MCQ question; skip
            finally:
                # Go to the next question if applicable
                try:
                    driver.implicitly_wait(1)
                    next_button = driver.find_element_by_xpath("//button[contains(., 'Next')]")
                    next_button.click()
                    question_number += 1
                except NoSuchElementException:
                    break
                finally:
                    driver.implicitly_wait(IMPLICIT_WAIT)

# Get login credentials
print("Enter your user ID:")
user_id = input()
password = getpass("Enter your password:\n")
# Load webpage
driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(IMPLICIT_WAIT)
driver.get(URL)
# Login
login_button = driver.find_element_by_xpath("//*[@class='bp3-button bp3-large']")
login_button.click()
user_id_input = driver.find_element_by_id("userNameInput")
user_id_input.send_keys(user_id)
password_input = driver.find_element_by_id("passwordInput")
password_input.send_keys(password)
signin_button = driver.find_element_by_id("submitButton")
signin_button.click()
# Selenium does not implicitly wait for login to be done
time.sleep(LOGIN_WAIT)
# Missions
process_page("/academy/missions/", "Missions")
# Quests
process_page("/academy/quests/", "Quests")
# Paths
process_page("/academy/paths/", "Paths")
# Contests
process_page("/academy/contests/", "Contests")
# Practicals
process_page("/academy/practicals/", "Practicals")
