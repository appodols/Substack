# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import csv
# import os


# def parse_medicine(file_path):
#     print(f"Parsing file: {file_path}")
#     # Set up Selenium WebDriver with headless mode
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     driver = webdriver.Chrome(options=options)
#     file_url = f"file://{os.path.abspath(file_path)}"
#     print(f"File URL: {file_url}")

#     try:
#         driver.get(file_url)
#         print("Loaded HTML file successfully in Selenium.")

#         # Extract primary key (medication name) from the <h1> tag
#         try:
#             medication_name = (
#                 WebDriverWait(driver, 10)
#                 .until(
#                     EC.presence_of_element_located(
#                         (By.CSS_SELECTOR, "h1[data-qa='drug-price-header-title']")
#                     )
#                 )
#                 .text
#             )
#             print(f"Extracted Medication Name (Primary Key): {medication_name}")
#         except:
#             print("Medication name not found.")
#             medication_name = "N/A"

#         # Click button to open the modal
#         try:
#             button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable(
#                     (By.CSS_SELECTOR, "button[data-qa='prescription-editor-button']")
#                 )
#             )
#             button.click()
#             print("Clicked the prescription editor button.")
#         except:
#             print("Prescription editor button not found.")
#             return

#         # Wait for the modal to appear
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-13oi5ev-0.knKVvD"))
#         )
#         print("Modal appeared.")

#         # Extract options for each dropdown in the modal
#         medication_options = extract_options(
#             driver, "select[data-qa='drug-configuration-label-selector']"
#         )
#         form_options = extract_options(
#             driver, "select[data-qa='drug-configuration-form-selector']"
#         )
#         dosage_options = extract_options(
#             driver, "select[data-qa='drug-configuration-dosage-selector']"
#         )
#         quantity_options = extract_options(
#             driver, "select[data-qa='drug-configuration-quantity-selector']"
#         )

#         # Write data to CSV files for each database
#         write_medicine_csv(medication_name, medication_options)
#         write_dosage_csv(medication_name, dosage_options)
#         write_form_csv(medication_name, form_options)
#         write_quantity_csv(medication_name, quantity_options)

#         print(f"Completed parsing file: {file_path}")

#     except Exception as e:
#         print(f"Failed to parse file: {file_path}. Error: {e}")
#     finally:
#         driver.quit()


# def extract_options(driver, selector):
#     """Helper function to extract options from a dropdown given a CSS selector."""
#     try:
#         select_element = driver.find_element(By.CSS_SELECTOR, selector)
#         options = [
#             option.text
#             for option in select_element.find_elements(By.TAG_NAME, "option")
#         ]
#         print(f"Options for {selector}: {options}")
#         return options
#     except:
#         print(f"No options found for {selector}")
#         return []


# def write_medicine_csv(medication_name, medication_options):
#     file_exists = os.path.isfile("medicine.csv")
#     with open("medicine.csv", mode="a", newline="") as file:
#         writer = csv.writer(file)
#         if not file_exists:
#             writer.writerow(
#                 ["ID", "Name", "Brand", "Associated Medicines"]
#             )  # CSV header
#         writer.writerow(
#             [medication_name, medication_name, "Yes", ", ".join(medication_options)]
#         )


# def write_dosage_csv(medication_name, dosage_options):
#     file_exists = os.path.isfile("dosage.csv")
#     with open("dosage.csv", mode="a", newline="") as file:
#         writer = csv.writer(file)
#         if not file_exists:
#             writer.writerow(
#                 ["ID", "Amount", "TempMedicineName"]
#             )  # CSV header with TempMedicineName
#         for i, dosage in enumerate(dosage_options, start=1):
#             # Extract only the numeric part from the dosage (e.g., "10mg" -> "10")
#             numeric_dosage = "".join(filter(str.isdigit, dosage))
#             if numeric_dosage:  # Ensure we have a valid number
#                 numeric_dosage = int(
#                     numeric_dosage
#                 )  # Convert to integer for Bubble if needed
#             writer.writerow(
#                 [
#                     f"{medication_name}_dosage_{i}",
#                     numeric_dosage,
#                     medication_name,  # Use medication_name as TempMedicineName
#                 ]
#             )


# def write_form_csv(medication_name, form_options):
#     file_exists = os.path.isfile("form.csv")
#     with open("form.csv", mode="a", newline="") as file:
#         writer = csv.writer(file)
#         if not file_exists:
#             writer.writerow(
#                 ["ID", "Name", "TempMedicineName"]
#             )  # CSV header with TempMedicineName
#         for i, form in enumerate(form_options, start=1):
#             writer.writerow(
#                 [
#                     f"{medication_name}_form_{i}",
#                     form,
#                     medication_name,
#                 ]  # Populate TempMedicineName with medication_name
#             )


# def write_quantity_csv(medication_name, quantity_options):
#     file_exists = os.path.isfile("quantity.csv")
#     with open("quantity.csv", mode="a", newline="") as file:
#         writer = csv.writer(file)
#         if not file_exists:
#             writer.writerow(
#                 ["ID", "Amount", "TempMedName"]
#             )  # Added TempMedName to CSV header
#         for i, quantity in enumerate(quantity_options, start=1):
#             writer.writerow(
#                 [
#                     f"{medication_name}_quantity_{i}",
#                     quantity,
#                     medication_name,  # Populate TempMedName with medication_name
#                 ]
#             )


# def process_folder_recursively(path):
#     """
#     Recursively processes all HTML files in a folder and its subfolders.
#     """
#     if os.path.isdir(path):
#         for root, _, files in os.walk(path):
#             for filename in files:
#                 if filename.endswith(".html"):
#                     file_path = os.path.join(root, filename)
#                     parse_medicine(file_path)
#     elif os.path.isfile(path):
#         parse_medicine(path)
#     else:
#         print("Invalid path provided. Please provide a valid file or directory.")


# if __name__ == "__main__":
#     # Specify either a single file or a directory
#     path = input("Enter the path to the file or folder: ")
#     process_folder_recursively(path)

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os
import time


def parse_medicine(file_path):
    print(f"Parsing file: {file_path}")

    # Set up Selenium WebDriver (not headless for debugging)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Open browser maximized
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    file_url = f"file://{os.path.abspath(file_path)}"
    print(f"File URL: {file_url}")

    try:
        driver.get(file_url)
        print("Loaded HTML file successfully in Selenium.")
        time.sleep(2)  # Pause to ensure page loads

        # Extract medication name
        try:
            medication_name = (
                WebDriverWait(driver, 10)
                .until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "h1[data-qa='drug-price-header-title']")
                    )
                )
                .text
            )
            print(f"Extracted Medication Name: {medication_name}")
        except:
            print("Medication name not found.")
            medication_name = "N/A"

        # Click the prescription editor button
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[data-qa='rx-editor-button']")
                )
            )
            driver.execute_script(
                "arguments[0].click();", button
            )  # JS click for reliability
            print("Clicked the prescription editor button.")
        except:
            print("Prescription editor button not found.")
            return

        # **Wait for Modal - Light Checking**
        time.sleep(2)  # Small delay instead of strict check
        print("Assuming modal is open... extracting fields.")

        # **Extract options dynamically**
        fields = {
            "Medication options": "label_override",
            "Form": "form",
            "Dosage": "dosage",
            "Quantity": "quantity",
        }

        extracted_data = {}

        for field_name, field_id in fields.items():
            extracted_data[field_name] = extract_dropdown_options(driver, field_id)

        # Debugging - print extracted info
        print(f"Available Medications: {extracted_data['Medication options']}")
        print(f"Available Forms: {extracted_data['Form']}")
        print(f"Available Dosages: {extracted_data['Dosage']}")
        print(f"Available Quantities: {extracted_data['Quantity']}")

        # Write data to a single CSV file
        write_medicine_csv(
            medication_name,
            extracted_data["Medication options"],
            extracted_data["Form"],
            extracted_data["Dosage"],
            extracted_data["Quantity"],
        )

        print(f"Completed parsing file: {file_path}")

    except Exception as e:
        print(f"Failed to parse file: {file_path}. Error: {e}")
    finally:
        driver.quit()


def extract_dropdown_options(driver, field_id):
    """Extracts all dropdown options for a given field_id"""
    try:
        select_element = driver.find_element(By.ID, field_id)
        options = [
            option.text
            for option in select_element.find_elements(By.TAG_NAME, "option")
        ]
        return ", ".join(options)  # Return options as a comma-separated string for CSV
    except:
        print(f"Could not find options for {field_id}")
        return "N/A"


def write_medicine_csv(
    medication_name, medication_options, form_options, dosage_options, quantity_options
):
    """Writes all extracted data into a **single CSV file**"""
    file_exists = os.path.isfile("medicine_data.csv")
    with open("medicine_data.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(
                ["ID", "Name", "Medication Options", "Forms", "Dosages", "Quantities"]
            )  # CSV Headers
        writer.writerow(
            [
                medication_name,
                medication_name,
                medication_options,
                form_options,
                dosage_options,
                quantity_options,
            ]
        )


def process_folder_recursively(path):
    """Recursively processes all HTML files in a folder and its subfolders."""
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for filename in files:
                if filename.endswith(".html"):
                    file_path = os.path.join(root, filename)
                    parse_medicine(file_path)
    elif os.path.isfile(path):
        parse_medicine(path)
    else:
        print("Invalid path provided. Please provide a valid file or directory.")


if __name__ == "__main__":
    path = input("Enter the path to the file or folder: ")
    process_folder_recursively(path)
