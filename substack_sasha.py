
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re

# Set up Chrome WebDriver with options
options = webdriver.ChromeOptions()
# Disable the first run dialog and other similar popups
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-gpu")

# Uncomment these lines if needed
# options.add_argument("--incognito")
# options.add_argument("--headless")  # Uncomment this line to run in headless mode
# options.add_argument("--user-data-dir=/Users/alexanderpodolsky/Library/Application Support/Google/Chrome")
# options.add_argument("--profile-directory=Profile 8")

driver = webdriver.Chrome(options=options)
driver.maximize_window()

# Open a new tab and switch to the first tab
driver.execute_script("window.open('about:blank','secondtab');")
window_handles = driver.window_handles
driver.switch_to.window(window_handles[0])

# Navigate to the target website
driver.get("https://chamath.substack.com/archive?sort=new")
time.sleep(2)

# Handle popups
def handle_popup(xpath):
    try:
        button = driver.find_element(By.XPATH, xpath)
        button.click()
    except NoSuchElementException:
        print(f"Popup not found: {xpath}")

# Define the XPaths for the popups
popup_xpaths = [
    '/html/body/div/div[1]/div[2]/div[5]/div/div/div/a/button',
    '/html/body/div/div[1]/div[2]/div[3]/div[2]/div[2]/button'
]

for xpath in popup_xpaths:
    handle_popup(xpath)
    time.sleep(2)

# Click on the Sign In button using the exact class attribute from the screenshot
try:
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'buttonBase_kqk6u1 buttonNew_kqk6u83 button2_kqk6u2')]"))
    )
    button.click()
except (NoSuchElementException, TimeoutException):
    print("Sign In button not found or not clickable")
time.sleep(2)

# Click on the "Continue with Email" button
try:
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[2]/div[2]/form/div[2]/div')))
    button.click()
except (NoSuchElementException, TimeoutException):
    print("Continue with Email button not found or not clickable")
time.sleep(2)

# Enter email and password
try:
    email = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="substack-login"]/div[2]/div[2]/form/div[1]/input')))
    email.send_keys("sasha.p.podolsky@gmail.com")
except (NoSuchElementException, TimeoutException):
    print("Email input not found")
time.sleep(0.5)

try:
    password = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="substack-login"]/div[2]/div[2]/form/input[3]')))
    password.send_keys("rpa5AEB-zbq6jbr5uqe")
except (NoSuchElementException, TimeoutException):
    print("Password input not found")
time.sleep(5)

try:
    continue_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="substack-login"]/div[2]/div[2]/form/button[@class="button primary"]')))
    continue_button.click()
except (NoSuchElementException, TimeoutException):
    print("Continue button not found")
time.sleep(4)

# Scroll down the page multiple times to load more content
for _ in range(400):
    element = driver.find_element(By.XPATH, '/html/body')
    element.send_keys(Keys.END)
    time.sleep(1)

# Extract links to individual posts
parent_element = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div/div/div[2]')
link_elements = parent_element.find_elements(By.CSS_SELECTOR, '[data-testid="post-preview-title"]')

href = [link.get_attribute("href") for link in link_elements]
print(href)

# Loop through the extracted links
for i, url in enumerate(href, start=1):
    driver.switch_to.window(window_handles[1])
    driver.get(url)
    time.sleep(4)

    # Handle popups in the post pages
    post_popup_xpaths = [
        '/html/body/div/div[1]/div[2]/div[1]/div/div/div/a/button',
        '/html/body/div/div[1]/div[2]/div/div[1]/div/article/div[2]/div[4]/div'
    ]
    
    for xpath in post_popup_xpaths:
        handle_popup(xpath)
        time.sleep(2)

    # Extract inner HTML content
    try:
        element = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]')
        inner_html = element.get_attribute("innerHTML")

        # Use regular expressions to clean up inner HTML content
        patterns = [
            r'<div inert="" role="dialog".*?Other</div></button></div></div></div></div></div></div></div></div>',
            r'<div class="pencraft frontend-pencraft-Box-module__reset.*?frontend-pencraft-Box-module__padding-bottom-16--KVxKv"><div class="pencraft frontend-pencraft-Box-module__reset.*?</circle></svg></a></div></div></div>',
            r'<div class="pencraft frontend-pencraft-Box-module__reset--VfQY8 frontend-pencraft-Box-module__display-flex.*?</line></svg></a></div></div></div></div></div>',
            r'<div class="like-button-container post-ufi-button style-compressed"><a role="button" class="post-ufi-button style-compressed.*?</div></button></div></div></div></div></div></div></div></div>'
        ]

        for pattern in patterns:
            inner_html = re.sub(pattern, '', inner_html, flags=re.DOTALL)

        try:
            element = driver.find_element(By.CSS_SELECTOR, ".post-title.unpublished")
            filename = re.sub(r'[^\w\s-]', '', element.text)
        except NoSuchElementException:
            element = driver.find_element(By.CSS_SELECTOR, ".tw-mt-0.tw-mb-2.tw-leading-tight.sm\\:tw-mb-1.tw-text-3xl.sm\\:tw-text-3xl")
            filename = re.sub(r'[^\w\s-]', '', element.text)

        with open(f'{i} {filename}.html', 'w', encoding='utf-8') as file:
            file.write(inner_html)
    except NoSuchElementException:
        print("No title found or content extraction failed")

# Switch back to the first tab
driver.switch_to.window(window_handles[0])
# Uncomment this line to close the WebDriver
# driver.quit()










# Uncomment this line to close the WebDriver
# driver.quit()












# # Import necessary libraries
# from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys

# import time
# import re

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Set up Chrome WebDriver with options
# # options = webdriver.ChromeOptions()
# # options.add_argument("--incognito")
# # options.add_argument("--headless")  # Uncomment this line to run in headless mode

# # chrome_directory = "/Users/alexanderpodolsky/Library/Application Support/Google/Chrome"
# # profile_name = "Profile 8"
# # options.add_argument(f"--user-data-dir={chrome_directory}")
# # options.add_argument(f"--profile-directory={profile_name}")
# options = webdriver.ChromeOptions()
# # options.add_argument(f"--user-data-dir=/Users/alexanderpodolsky/Library/Application Support/Google/Chrome")
# # options.add_argument("--profile-directory=Profile 8")

# driver = webdriver.Chrome(options=options)
# driver.maximize_window()

# # Open a new tab and switch to the first tab
# driver.execute_script("window.open('about:blank','secondtab');")
# window_handles = driver.window_handles
# driver.switch_to.window(window_handles[0])

# # Navigate to the target website
# # driver.get("https://www.news.aakashg.com/archive")
# driver.get("https://chamath.substack.com/archive?sort=new")

# # Wait for 2 seconds
# time.sleep(2)

# # Try clicking buttons to turn off popup, handle NoSuchElementException if not found
# try:
#     button = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div[5]/div/div/div/a/button')
#     button.click()
# except NoSuchElementException:
#     print("Skip")
# time.sleep(2)

# try:
#     button = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div[3]/div[2]/div[2]/button')
#     button.click()
# except NoSuchElementException:
#     print("Skip")
# time.sleep(2)

# # Click on the Sign In button
# try:
#     # Wait for the Sign In button to be clickable
#     button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'button.sign-in-link')))
#     button.click()
# except NoSuchElementException:
#     print("Sign In button not found or not clickable")

# time.sleep(2)

# # Click on the "Continue with Email" button
# try:
#     button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[2]/div[2]/form/div[2]/div')))
#     button.click()
# except NoSuchElementException:
#     print("Continue with Email button not found or not clickable")

# time.sleep(2)

# # Enter email and password
# try:
#     email = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="substack-login"]/div[2]/div[2]/form/div[1]/input')))
#     email.send_keys("sasha.p.podolsky@gmail.com")
# except NoSuchElementException:
#     print("Email input not found")

# time.sleep(0.5)

# try:
#     password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="substack-login"]/div[2]/div[2]/form/input[3]')))
#     password.send_keys("CNA2kvf0pky5rne.zpg")
# except NoSuchElementException:
#     print("Password input not found")
# time.sleep(5)

# try:
#     continue_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="substack-login"]/div[2]/div[2]/form/button[@class="button primary"]')))
#     continue_button.click()
# except NoSuchElementException:
#     print("Continue button not found")

# time.sleep(4)

# ################################################################

# # Scroll down the page multiple times to load more content
# for i in range(1, 400, 1):
#     element = driver.find_element(By.XPATH, '/html/body')
#     element.send_keys(Keys.END)
#     time.sleep(1)

# # Extract links to individual posts
# parent_element = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div/div/div[2]')
# link_elements = parent_element.find_elements(By.CSS_SELECTOR, '[data-testid="post-preview-title"]')

# href = []

# # Store the href attributes of the links in a list
# for link in link_elements:
#     href.append(link.get_attribute("href"))

# # Print the list of extracted links
# print(href)

# # Loop through the extracted links
# t = len(href)

# for i in range(1, t + 1, 1):

#     url = href[i - 1]

#     # Switch to the second tab and visit the link
#     driver.switch_to.window(window_handles[1])
#     driver.get(url)
#     time.sleep(4)

#     # Try clicking buttons to turn off popup, handle NoSuchElementException if not found
#     try:
#         button = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div[1]/div/div/div/a/button')
#         button.click()
#     except NoSuchElementException:
#         print("Skip")

#     time.sleep(2)

#     # Try finding and clicking a button to turn off popup, handle NoSuchElementException if not found
#     try:
#         button = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div/div[1]/div/article/div[2]/div[4]/div')
#         button.click()
#     except NoSuchElementException:
#         print("Skip")

#     time.sleep(0.5)

#     # Extract inner HTML content
#     # element = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div/div[1]')
#     element = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]')
#     print(element.text)
#     inner_html = element.get_attribute("innerHTML")

#     # Use regular expressions to clean up inner HTML content

#     inner_html = re.sub(
#         r'<div inert="" role="dialog" class="modal typography out gone share-dialog popup"><div class="modal-table"><div class="modal-row"><div class="modal-cell modal-content no-fullscreen"><div class="container">.*?Other</div></button></div></div></div></div></div></div></div>',
#         '', inner_html, flags=re.DOTALL)
#     inner_html = re.sub(
#         r'<div class="pencraft frontend-pencraft-Box-module__reset--VfQY8 frontend-pencraft-Box-module__display-flex--ZqeZt frontend-pencraft-Box-module__flex-direction-column--Rq7pk frontend-pencraft-Box-module__padding-bottom-16--KVxKv"><div class="pencraft frontend-pencraft-Box-module__reset--VfQY8 frontend-pencraft-Box-module__display-flex--ZqeZt frontend-pencraft-Box-module__flex-direction-column--Rq7pk frontend-pencraft-Box-module__padding-y-16--ohCEm">.*?<div class="label">Share</div></a></div></div>',
#         '', inner_html, flags=re.DOTALL)
#     inner_html = re.sub(
#         r'<div class="pencraft frontend-pencraft-Box-module__flexGrow--mx4xz frontend-pencraft-Box-module__reset--VfQY8 frontend-pencraft-Box-module__display-flex--ZqeZt frontend-pencraft-Box-module__flex-justify-space-between--NvIcg frontend-pencraft-Box-module__flex-align-center--rSd6h frontend-pencraft-Box-module__flex-gap-16--TpblU frontend-pencraft-Box-module__padding-y-16--ohCEm frontend-pencraft-Box-module__border-top-detail-themed--e17yZ frontend-pencraft-Box-module__border-bottom-detail-themed--eVwFY post-ufi">.*?<div class="label">Share</div></a></div></div>',
#         '', inner_html, flags=re.DOTALL)
#     inner_html = re.sub(
#         r'<div class="pencraft frontend-pencraft-Box-module__reset--VfQY8 frontend-pencraft-Box-module__display-flex--ZqeZt frontend-pencraft-Box-module__flex-direction-column--Rq7pk frontend-pencraft-Box-module__padding-bottom-16--KVxKv"><div class="pencraft frontend-pencraft-Box-module__reset--VfQY8 frontend-pencraft-Box-module__display-flex--ZqeZt frontend-pencraft-Box-module__flex-direction-column--Rq7pk frontend-pencraft-Box-module__padding-y-16--ohCEm">.*?</circle></svg></a></div></div></div>',
#         '', inner_html, flags=re.DOTALL)
#     inner_html = re.sub(
#         r'<div class="frontend-main-home-PostsLayout-module__container--ZMlBv frontend-main-home-PostsLayout-module__two-column-list--dzbTj"><div class="pencraft frontend-pencraft-Box-module__reset--VfQY8 frontend-pencraft-Box-module__display-flex--ZqeZt frontend-pencraft-Box-module__flex-direction-column--Rq7pk frontend-pencraft-Box-module__border-radius-6--lsyIU frontend-main-home-PostPreview-index-module__container--gXuU1">.*?</line></svg></a></div></div></div></div></div>',
#         '', inner_html, flags=re.DOTALL)
#     inner_html = re.sub(
#         r'<div class="like-button-container post-ufi-button style-compressed"><a role="button" class="post-ufi-button style-compressed has-label with-border">.*?</div></button></div></div></div></div></div></div></div></div>',
#         '', inner_html, flags=re.DOTALL)

#     try:
#         # Try finding and saving the post title, then save the cleaned HTML content to a file
#         element = driver.find_element(By.CSS_SELECTOR, ".post-title.unpublished")
#         filename = re.sub(r'[^\w\s-]', '', element.text)
#         print(filename)

#         with open(f'{i} {filename}.html', 'w', encoding='utf-8') as file:
#             file.write(inner_html)
#     except NoSuchElementException:
#         try:
#             element = driver.find_element(By.CSS_SELECTOR, ".tw-mt-0.tw-mb-2.tw-leading-tight.sm\\:tw-mb-1.tw-text-3xl.sm\\:tw-text-3xl")
#             filename = re.sub(r'[^\w\s-]', '', element.text)
#             print(filename)

#             with open(f'{i} {filename}.html', 'w', encoding='utf-8') as file:
#                 file.write(inner_html)
#         except NoSuchElementException:
#             print("No title found")

# # Switch back to the first tab
# driver.switch_to.window(window_handles[0])
# # driver.quit()  # Uncomment this line to close the WebDriver
