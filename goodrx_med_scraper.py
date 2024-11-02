from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os
import time


def parse_medicine(file_path):
    print(f"Parsing file: {file_path}")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    file_url = f"file://{os.path.abspath(file_path)}"
    print(f"File URL: {file_url}")

    try:
        driver.get(file_url)
        print("Loaded HTML file successfully in Selenium.")

        # Click button to open the modal
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[data-qa='prescription-editor-button']")
                )
            )
            button.click()
            print("Clicked the prescription editor button.")
        except:
            print("Prescription editor button not found.")
            return

        # Wait for the modal to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-13oi5ev-0.knKVvD"))
        )
        print("Modal appeared.")

        # Extract options for each dropdown in the modal
        medication_options = extract_options(
            driver, "select[data-qa='drug-configuration-label-selector']"
        )
        form_options = extract_options(
            driver, "select[data-qa='drug-configuration-form-selector']"
        )
        dosage_options = extract_options(
            driver, "select[data-qa='drug-configuration-dosage-selector']"
        )
        quantity_options = extract_options(
            driver, "select[data-qa='drug-configuration-quantity-selector']"
        )

        # Collect all extracted data
        medication_details = {
            "url": os.path.basename(file_path),  # File name instead of URL
            "medication_options": medication_options,
            "form_options": form_options,
            "dosage_options": dosage_options,
            "quantity_options": quantity_options,
        }

        # Append data to CSV
        append_medicine(medication_details)
        print(f"Completed parsing file: {file_path}")

    except Exception as e:
        print(f"Failed to parse file: {file_path}. Error: {e}")
    finally:
        driver.quit()


def extract_options(driver, selector):
    """
    Helper function to extract options from a dropdown given a CSS selector.
    """
    try:
        select_element = driver.find_element(By.CSS_SELECTOR, selector)
        options = [
            option.text
            for option in select_element.find_elements(By.TAG_NAME, "option")
        ]
        print(f"Options for {selector}: {options}")
        return options
    except:
        print(f"No options found for {selector}")
        return []


def append_medicine(medication_details):
    file_exists = os.path.isfile("medication_details.csv")

    with open("medication_details.csv", mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                [
                    "url",
                    "medication_options",
                    "form_options",
                    "dosage_options",
                    "quantity_options",
                ]
            )

        writer.writerow(
            [
                medication_details["url"],
                ", ".join(medication_details["medication_options"]),
                ", ".join(medication_details["form_options"]),
                ", ".join(medication_details["dosage_options"]),
                ", ".join(medication_details["quantity_options"]),
            ]
        )
    print(f"Appended medication details for file: {medication_details['url']}")


def process_file_or_folder(path):
    """
    Processes a single file or all files in a folder.
    """
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith(".html"):
                file_path = os.path.join(path, filename)
                parse_medicine(file_path)
    elif os.path.isfile(path):
        parse_medicine(path)
    else:
        print("Invalid path provided. Please provide a valid file or directory.")


if __name__ == "__main__":
    # Specify either a single file or a directory
    path = input("Enter the path to the file or folder: ")
    process_file_or_folder(path)
