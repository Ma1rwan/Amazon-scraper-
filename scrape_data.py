import json
from bs4 import BeautifulSoup
import time
import difflib
import requests
import os
import cv2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from logger import logger  # Importing the Logger class from logger.py
logger = logger(identifier='AMZN')

def create_driver():
    driver = webdriver.Chrome()

    return driver


def wait_for_element_to_be_clickable(driver, xpath, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )

def calculate_percentages(title_data, image_data):
    results = []

    # Ensure both lists have the same length
    if len(title_data) != len(image_data):
        raise ValueError("The length of title_data and image_data must be the same.")

    for (title, title_percentage), (image, image_percentage) in zip(title_data, image_data):
        new_percentage = (0.8 * image_percentage) + (0.2 * title_percentage)
        results.append(new_percentage)

    return results


def calculate_title_similarity(reference_string, string_list):
    similarity_scores = []

    for string in string_list:
        # Calculate similarity ratio
        similarity_ratio = difflib.SequenceMatcher(None, reference_string, string).ratio()
        # Convert to percentage
        similarity_percentage = similarity_ratio * 100
        similarity_scores.append((string, similarity_percentage))

    return similarity_scores


def download_reference_image(url, download_dir='images\\reference'):
    """Download the reference image to a specified directory."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        image_name = os.path.join(download_dir, url.split("/")[-1])
        with open(image_name, 'wb') as file:
            file.write(response.content)
        return image_name
    except Exception as e:
        logger.log("error", f"Error downloading reference image")
        return None


def clear_temp_images(download_dir='images\\temporary_images'):
    """Clear all images in the temporary images directory."""
    if not os.path.exists(download_dir):
        # Log "directory not found" as info and create the directory
        logger.log("info", f"Directory {download_dir} not found. Creating it now.")
        os.makedirs(download_dir)  # Create the directory

        # Proceed with clearing the directory
    for filename in os.listdir(download_dir):
        file_path = os.path.join(download_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)  # Remove the file
        except Exception as e:
            logger.log("error", f"Error deleting {file_path}: {str(e)}")
    logger.log("info", "Temporary images directory cleared.")



def download_images(image_urls, download_dir='images\\temporary_images'):
    """Download images from the given URLs."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    downloaded_images = []
    for url in image_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            image_name = os.path.join(download_dir, url.split("/")[-1])
            with open(image_name, 'wb') as file:
                file.write(response.content)
            downloaded_images.append(image_name)
        except Exception as e:
            logger.log("error", f"Error downloading {url}:")

    return downloaded_images



def calculate_ssim(img1, img2):
    """Calculate SSIM manually."""
    # Constants to avoid division by zero
    C1 = 6.5025
    C2 = 58.5225

    # Calculate means
    mu1 = np.mean(img1)
    mu2 = np.mean(img2)

    # Calculate variances
    sigma1_sq = np.var(img1)
    sigma2_sq = np.var(img2)
    sigma12 = np.cov(img1.flatten(), img2.flatten())[0][1]

    # SSIM formula
    ssim = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
           ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1_sq + sigma2_sq + C2))

    return ssim


def compare_images(image1_path, image2_path):
    """Compare two images and return similarity percentage using OpenCV."""
    # Read the images
    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)  # Read as grayscale
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)  # Read as grayscale

    # Check if either image failed to load
    if img1 is None or img2 is None:
        logger.log("error", f"Error: One of the images could not be loaded.")
        return 0  # Return 0 if an image could not be loaded

    # Resize images to the same size for comparison
    img1 = cv2.resize(img1, (100, 100))  # Adjust size as necessary
    img2 = cv2.resize(img2, (100, 100))  # Adjust size as necessary

    # Calculate SSIM
    ssim_score = calculate_ssim(img1, img2)

    # Convert to percentage
    similarity_percentage = ssim_score * 100
    return similarity_percentage


def open_sellers_section(amazon_driver):
                other_sellers_button1 = '/html/body/div[2]/div/div[5]/div[4]/div[1]/div[5]/div[2]/div/div[2]/a/span'
                other_sellers_button2 = 'buybox-see-all-buying-choices'
                other_sellers_button3 = "/html/body/div[3]/div/div[8]/div[4]/div[1]/div[5]/div[2]/div/div[2]/a/span/span[1]"
                other_sellers_button_js_path = 'document.querySelector("#dynamic-aod-ingress-box > div > div.a-section.a-spacing-none.daodi-content > a > span > span:nth-child(1)")'

                try:
                    # Wait until the element is clickable
                    WebDriverWait(amazon_driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, other_sellers_button1))
                    )
                    amazon_driver.find_element(By.XPATH, other_sellers_button1).click()

                    time.sleep(1)
                    for i in range(0, 3):
                        try:
                            html_source = amazon_driver.page_source
                            soup = BeautifulSoup(html_source, "html.parser")
                            slider = soup.find(id="all-offers-display-scroller")
                            if slider:
                                return True
                            else:
                                time.sleep(1)
                        except Exception as e:
                            pass
                except Exception as e:
                    time.sleep(0.5)

                

                try:
                    # Use JavaScript to find and click the element
                    amazon_driver.execute_script(f'{other_sellers_button_js_path}.click();')
                    time.sleep(1)

                    for i in range(3):
                        try:
                            html_source = amazon_driver.page_source
                            soup = BeautifulSoup(html_source, "html.parser")
                            slider = soup.find(id="all-offers-display-scroller")
                            if slider:
                                return True
                            else:
                                time.sleep(1)
                        except Exception as e:
                            pass
                except Exception as e:
                    time.sleep(0.5)

                
                try:
                    # Wait until the element is clickable
                    WebDriverWait(amazon_driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, other_sellers_button3))
                    )
                    amazon_driver.find_element(By.XPATH, other_sellers_button3).click()
                    time.sleep(1)
                    for i in range(0, 3):
                        try:
                            html_source = amazon_driver.page_source
                            soup = BeautifulSoup(html_source, "html.parser")
                            slider = soup.find(id="all-offers-display-scroller")
                            if slider:
                                return True
                            else:
                                time.sleep(1)
                        except Exception as e:
                            pass
                except Exception as e:
                    time.sleep(0.5)
                
                try:

                    # Wait until the element is clickable
                    WebDriverWait(amazon_driver, 10).until(
                        EC.element_to_be_clickable((By.ID, other_sellers_button2))
                    )
                    amazon_driver.find_element(By.ID, other_sellers_button2).click()

                    return True
                except Exception:
                    time.sleep(1)
                return False


amazon_driver = create_driver()
tmp_url = f"https://www.amazon.com/Monitor-FreeSync-Premium-Refresh-Support/dp/B0CJQ7V6M8"

for _ in range(0, 5):
    try:
        amazon_driver.get(tmp_url)

        # Check if the page loaded correctly (e.g., by checking the page title or specific element)
        if "Acer Nitro" in amazon_driver.title:  # Replace with expected page title or condition
            logger.log("success", "Page loaded successfully!")
            break  # Exit loop if page loaded successfully
        else:
            logger.log("error", "Error loading page, retrying...")
    except WebDriverException:
        logger.log("error", "Error loading page, retrying...")
        time.sleep(2)  # Wait before retrying (you can adjust the wait time as needed)
if "Acer Nitro" not in amazon_driver.title:  # Replace with expected page title or condition
    logger.log("info", "There might be a captcha in the browser, waiting for the user to solve it.")
time.sleep(15)
try:


    accept_cookies_PATH = '/html/body/div[2]/span/form/div[2]/span[1]/span/input'
    wait_for_element_to_be_clickable(amazon_driver, accept_cookies_PATH).click()


    # Click the "Continue" button
    continue_button_PATH = '/html/body/div[10]/div/div/div[2]/span/span/input'
    # Use JavaScript to find and click the element

    wait_for_element_to_be_clickable(amazon_driver, continue_button_PATH).click()
except Exception:
    pass

with open("all_product_links.txt", "r", encoding="utf-8") as file:
    links1 = file.readlines()
    links = set(links1) # <-- remove any duplicates
links = list(links)
storage_path = "storage.json"
for k in range(0, len(links)):
    link = links[k]
    valid_product = True
    while valid_product == True:        
        try:
            amazon_driver.get(link)
            html_source = amazon_driver.page_source
            soup = BeautifulSoup(html_source, "html.parser")
            product_image_tag = soup.find(id='imgTagWrapperId')
            product_image = product_image_tag.find('img')['src']
            if product_image == 'https://m.media-amazon.com/images/I/01RmK+J4pJL._AC_.gif':
                valid_product = False
                continue
            amazon_price = float(amazon_driver.execute_script("""
                return document.querySelector("#corePrice_feature_div > div > div > span.a-price.aok-align-center > span:nth-child(2)").textContent
            """).strip().split(" ")[-1].replace(",", '').replace("£", "").replace("$", "").replace("+", ""))
            if not amazon_price:

                outofstock = False
                
                

                for i in range(0, 3):
                    try:
                        html_source = amazon_driver.page_source
                        soup = BeautifulSoup(html_source, "html.parser")
                        check_stock = soup.find(id="outOfStock")
                        if check_stock:
                            outofstock = True
                            break
                        else:
                            time.sleep(1)
                    except Exception as e:
                        logger.log("error", f"{e}")
                if outofstock:
                    valid_product = False
                    continue
                section_opened = open_sellers_section(amazon_driver)
                if section_opened:
                    for i in range(0, 5):
                        try:
                            html_source = amazon_driver.page_source
                            soup = BeautifulSoup(html_source, "html.parser")
                            slider = soup.find(id="all-offers-display-scroller")
                            if slider:
                                amazon_sellerstags = slider.find_all(class_="a-size-small a-link-normal")
                                amazon_pricestags = slider.find_all(
                                    class_="a-section a-spacing-none aok-align-center aok-relative")
                                break
                            else:
                                time.sleep(1)
                        except Exception as e:
                            pass
                else:
                    html_source = amazon_driver.page_source
                    soup = BeautifulSoup(html_source, "html.parser")
                    amazon_sellertag = soup.find(id="sellerProfileTriggerId")
                    amazon_pricetag = soup.find(class_="a-size-base a-color-price offer-price a-text-normal")
                    if not amazon_pricetag:
                        amazon_pricetag = soup.find(class_="a-offscreen")
                    if amazon_sellertag:
                        amazon_price = float(amazon_pricetag.text.strip().replace("£", "").replace("$", ""))
            product_title = soup.find(id="productTitle").text.strip()
            reference_image_path = download_reference_image(product_image)
            product_code = link.split("/dp/")[1].split("/")[0]

            new_data = {
                'amazon_title': product_title,
                'amazon_link': link,
                'amazon_image': reference_image_path,
                'product_code': product_code,
                'amazon_price': float(f"{amazon_price:.2f}")
            }
            # Function to load the existing data from the JSON file (or create new lists if file doesn't exist)
            def load_existing_data(storage_path):
                if os.path.exists(storage_path):
                    with open(storage_path, 'r') as file:
                        try:
                            return json.load(file)
                        except json.JSONDecodeError:
                            # If the file is empty or invalid JSON, start with empty lists
                            return {
                                'amazon_titles': [],
                                'amazon_links': [],
                                'amazon_images': [],
                                'product_codes': [],
                                'amazon_prices': []
                            }
                else:
                    # If the file doesn't exist, return empty lists
                    return {
                        'amazon_titles': [],
                        'amazon_links': [],
                        'amazon_images': [],
                        'product_codes': [],
                        'amazon_prices': []
                    }


            # Load the existing data
            existing_data = load_existing_data(storage_path)

            if all([
                new_data['amazon_title'] is not None,
                new_data['amazon_link'] is not None,
                new_data['amazon_image'] is not None,
                new_data['product_code'] is not None,
                new_data['amazon_price'] is not None,
            ]):
                existing_data['amazon_titles'].append(new_data['amazon_title'])
                existing_data['amazon_links'].append(new_data['amazon_link'])
                existing_data['amazon_images'].append(new_data['amazon_image'])
                existing_data['product_codes'].append(new_data['product_code'])
                existing_data['amazon_prices'].append(new_data['amazon_price'])

                # Save updated data back to the JSON file
                with open(storage_path, 'w') as file:
                    json.dump(existing_data, file, indent=4)
                # Save updated data back to the JSON file
                with open(storage_path, 'w') as file:
                    json.dump(existing_data, file, indent=4)
                logger.log("success", f"Data successfully added to {storage_path}!")


            else:
                logger.log("info", "Some data is missing, skipping the product.")
                valid_product = False
                continue
            break
        except Exception:
            valid_product = False
            continue
logger.log("success", "Scraping data is done !")
amazon_driver.quit()
