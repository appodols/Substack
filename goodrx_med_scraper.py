from bs4 import BeautifulSoup
import csv
import os
import requests

# Commented out to use a hardcoded URL instead
# def generate_file_names():
#     folder_path = "./urls"
#     file_name = "urls.txt"
#     full_path = os.path.join(folder_path, file_name)
#     print(f"Looking for file at: {full_path}")
#     return full_path

# Commented out to use a hardcoded URL instead
# def parse_medicines():
#     file_name = generate_file_names()
#     if not os.path.isfile(file_name):
#         print(f"File not found: {file_name}")
#         return
#
#     with open(file_name, "r", encoding="utf-8") as file:
#         urls = file.readlines()
#
#     for url in urls:
#         url = url.strip()
#         if url:
#             parse_medicine(url)


def parse_medicine(url):
    print(f"Parsing URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Failed to fetch URL: {url}. Error: {e}")
        return

    medication_details = get_medication_details(soup)
    append_medicine(medication_details)
    print(f"Completed parsing URL: {url}")


def get_medication_details(soup):
    medication_details = {}

    # Extracting data for medication options
    medication_options = []
    medication_select = soup.find("select", {"id": "MDS-component-id-:r4:"})
    if medication_select:
        for option in medication_select.find_all("option"):
            medication_options.append(option.text)

    # Extracting data for form
    form_options = []
    form_select = soup.find("select", {"id": "MDS-component-id-:r5:"})
    if form_select:
        for option in form_select.find_all("option"):
            form_options.append(option.text)

    # Extracting data for dosage
    dosage_options = []
    dosage_select = soup.find("select", {"id": "MDS-component-id-:r6:"})
    if dosage_select:
        for option in dosage_select.find_all("option"):
            dosage_options.append(option.text)

    # Extracting data for quantity
    quantity_options = []
    quantity_select = soup.find("select", {"id": "MDS-component-id-:r7:"})
    if quantity_select:
        for option in quantity_select.find_all("option"):
            quantity_options.append(option.text)

    medication_details = {
        "url": soup.title.string,
        "medication_options": medication_options,
        "form_options": form_options,
        "dosage_options": dosage_options,
        "quantity_options": quantity_options,
    }
    return medication_details


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
    print(f"Appended medication details for URL: {medication_details['url']}")


if __name__ == "__main__":
    # Hardcoded URL for testing
    url = "https://www.goodrx.com/vyvanse"
    parse_medicine(url)
