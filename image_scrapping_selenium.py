import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Function to fetch image URLs
def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 2):
    # Function to scroll to the end of the page
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    wd.get(search_url.format(q=query))

    image_urls = set()
    results_start = 0
    
    while len(image_urls) < max_links_to_fetch:
        scroll_to_end(wd)
        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
        number_results = len(thumbnail_results)

        for img in thumbnail_results[results_start:number_results]:
            try:
                image_url = img.get_attribute('src')
                if image_url and 'http' in image_url:
                    image_urls.add(image_url)
                    if len(image_urls) >= max_links_to_fetch:
                        return image_urls
            except Exception as e:
                continue

        results_start = len(image_urls)

        if results_start == number_results:
            break

    return image_urls

# Function to persist image to disk
def persist_image(folder_path:str,url:str, counter):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        return

    try:
        f = open(os.path.join(folder_path, 'jpg' + "_" + str(counter) + ".jpg"), 'wb')
        f.write(image_content)
        f.close()
    except Exception as e:
        return

# Function to search and download images
def search_and_download(search_term: str, target_path='./images', number_images=150):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    res = fetch_image_urls(search_term, number_images, wd=driver, sleep_between_interactions=0.5)

    counter = 0
    for elem in res:
        persist_image(target_folder, elem, counter)
        counter += 1

# Get user input for search term and number of images
search_term = input("Enter Search Term: ")
number_images = int(input("Enter Number of Images: "))
# Execute search and download function
search_and_download(search_term=search_term, number_images=number_images)
