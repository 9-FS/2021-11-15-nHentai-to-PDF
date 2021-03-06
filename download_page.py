from lxml import html   #HTML parsing
import requests
import time


def download_page(h_ID, page_nr):
    image=""

    for i in range(10): #repeat if no image because access denied (rate limit)
        try:
            page=requests.get(f'https://nhentai.net/g/{h_ID}/{page_nr}/', timeout=5)    #page gallery
        except requests.exceptions.ReadTimeout: #if timeout: try again
            continue
        except requests.exceptions.ConnectionError:
            continue
        page=html.fromstring(page.text) 
        
        img_link=page.xpath('//section[@id="image-container"]/a/img/@src')  #parse direct image link
        try:
            image=requests.get(img_link[0], timeout=5)  #download image
        except(requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):   #if connection error or timeout: try again
            continue
        
        if len(image.content)==0 or image.status_code==404:   #if image download failed: try again in 1s, maximum 10 times
            time.sleep(1)
        else:               #downloaded successfully
            break
    else:   #no image afer 10 tries: return immediatly, save nothing
        return

    with open(f"./{h_ID}/{h_ID}-{page_nr}.jpg", "wb") as img_file:  #save image
        img_file.write(image.content)