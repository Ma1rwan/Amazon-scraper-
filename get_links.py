import math
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
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from logger import logger
logger = logger(identifier='AMZN')


def create_driver():
    driver = webdriver.Chrome()

    return driver
def clean_url(input_url):
    # Parse the URL
    parsed_url = urlparse(input_url)
    # Parse the query parameters into a dictionary
    query_params = parse_qs(parsed_url.query)

    # Remove any unwanted parameters
    unwanted_params = {'low-price', 'high-price', 'page'}
    for param in unwanted_params:
        query_params.pop(param, None)

    # Rebuild the query string without the unwanted parameters
    cleaned_query = urlencode(query_params, doseq=True)
    # Construct the cleaned URL
    cleaned_url = urlunparse(parsed_url._replace(query=cleaned_query))

    return cleaned_url

low_price = 0
high_price = ""
page = 1




# Ask the user to enter a URL
input_url = input("Please enter the Amazon URL: ")

# Clean the URL of any unwanted parameters
base_url = clean_url(input_url)


# Construct the final URL with desired parameters
url = f"{base_url}&low-price={low_price}&high-price={high_price}&page={page}"
def wait_for_element_to_be_clickable(driver, xpath, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )

def calculate_percentages(title_data, image_data):
    results = []

    # Ensure both lists have the same length
    if len(title_data) != len(image_data):
        pass

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
        logger.log("error", "Error downloading reference image.")
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
time.sleep(5)
try:


    accept_cookies_PATH = '/html/body/div[2]/span/form/div[2]/span[1]/span/input'
    wait_for_element_to_be_clickable(amazon_driver, accept_cookies_PATH).click()


    # Click the "Continue" button
    continue_button_PATH = '/html/body/div[10]/div/div/div[2]/span/span/input'
    # Use JavaScript to find and click the element

    wait_for_element_to_be_clickable(amazon_driver, continue_button_PATH).click()
except Exception:
    pass



amazon_driver.get(url)
max_range = 380
for _ in range(1, 3):
    try:
        max_range = int(amazon_driver.execute_script("""
            return document.querySelector("#p_36\\\\/range-slider > form > div:nth-child(9) > label.a-form-label.sf-range-slider-label.sf-upper-bound-label > span").textContent;
        """).strip().split(" ")[-1].replace(",", '').replace("£", "").replace("$", "").replace("+", ""))
        if max_range:
            break
    except Exception:
        max_range = 380


amazon_product_links =[]
high_price = 5
low_price = 1
page = 1
failed_attempts = 0
while low_price < max_range:
    url = f"{input_url}&low-price={low_price}&high-price={high_price}&page={page}"
    amazon_driver.get(url)

    # Initialize previous range variables
    previous_low_price = low_price
    previous_high_price = high_price
    if failed_attempts > 5:
        break
    while True:
        try:
            # Get the number of products
            Num_of_products = int(amazon_driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/span/div/h1/div/div[1]").text.split("results")[0].strip().split(" ")[-1].replace(",", ''))
            failed_attempts = 0
        except Exception:
            Num_of_products = 0
            failed_attempts += 1
        
        # Check if the number of products is greater than 320
        if Num_of_products > 320:
            try:
                time.sleep(3)

                # If low_price and high_price are the same, increment high_price slightly
                if round(low_price, 2) == round(high_price, 2):
                    high_price += 0.01
                    break

                # Calculate the new high price
                new_high_price = (low_price + high_price) / 2

                # Ensure new_high_price is still greater than low_price
                if new_high_price <= low_price:
                    new_high_price = low_price + 0.01  # Adjust if needed

                # Build the updated URL with the new high_price
                url = f"{input_url}&low-price={low_price}&high-price={high_price}&page={page}"

                # Navigate to the updated URL
                amazon_driver.get(url)

                # Re-fetch the number of products
                Num_of_products = int(amazon_driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/span/div/h1/div/div[1]").text.split("results")[0].strip().split(" ")[-1].replace(",", ''))

                # If no products found, revert to the previous range
                if Num_of_products == 0:
                    low_price = previous_low_price
                    high_price = previous_high_price
                    logger.log("info", "No products found, reverting to previous range.")
                    break  # Exit the inner loop to retry with the previous range
                else:
                    # Update previous range for the next iteration
                    previous_low_price = low_price
                    previous_high_price = high_price
                    high_price = new_high_price  # Update to the new high price

            except Exception as e:
                logger.log("error", f"An error occurred: {e}")
                break  # Exit the inner loop on error
        else:
            break  # If the number of products is 320 or less, exit the loop
    logger.log("info", f"Final high price: {high_price}, Final low price: {low_price}, Number of products: {Num_of_products}")

    # Pagination handling
    pages = 20 if Num_of_products / 16 >= 20 else math.ceil(Num_of_products / 16)
    logger.log("info", f"Number of pages: {pages}")

    for i in range(1, pages + 1):
        if i != 1:
            url = f"{input_url}&low-price={low_price}&high-price={high_price}&page={i}"
            amazon_driver.get(url)

        # Scroll down to load more products
        last_height = amazon_driver.execute_script("return document.body.scrollHeight")
        tries = 20  # Number of tries before stopping

        for j in range(tries):
            try:
                time.sleep(1)  # Wait for page to load
                amazon_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
                new_height = amazon_driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:  # Check if we've reached the end
                    break  # Exit the scrolling loop if no more content is loading
                
                last_height = new_height  # Update the last height
            except Exception as error:
                logger.log("error", f"An error occurred: {error}")

        # Parse the page content
        html_source = amazon_driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        products_link_tags = soup.find_all(class_="a-link-normal s-no-outline")
        amazon_products_links = ["https://www.amazon.com" + products_link['href'] for products_link in products_link_tags]
        
        amazon_product_links.extend(amazon_products_links)  # Append new links to the list
        logger.log("success", f"Page {i} processed. Number of product links found: {len(amazon_products_links)}")
        with open("all_product_links.txt", "a") as file:
            for link in amazon_products_links:
                file.write(link + "\n")
    # Prepare for the next price range
    temp_price = low_price
    low_price = high_price
    high_price += 5  # Increment the high price for the next iteration
    break

# Print or process the gathered product links
logger.log("success", f"Total product links gathered: {len(amazon_product_links)}")

amazon_driver.quit()
