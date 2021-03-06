from xdrlib import ConversionError
from PIL import Image, ImageFile, UnidentifiedImageError
import os
import time
from KFS import log


def convert_jpg_to_pdf(h_ID: int, title: str, pages: int, conversion_fails: list([int])) -> None:
    pdf=[]                  #images converted for saving as pdf


    if type(h_ID)!=int:
        raise TypeError("Error in \"convert_jpg_to_pdf(...)\": h_ID must be of type int.")
    if type(title)!=str:
        raise TypeError("Error in \"convert_jpg_to_pdf(...)\": title must be of type str.")
    if type(pages)!=int:
        raise TypeError("Error in \"convert_jpg_to_pdf(...)\": pages must be of type int.")


    ImageFile.LOAD_TRUNCATED_IMAGES=True    #set true or raises unnecessary exception sometimes

    for page_nr in range(1, pages+1):   #convert all saved images
        log.write(f"\rConverting {h_ID}-{page_nr}.jpg to pdf...")
        try:
            with Image.open(f"./{h_ID}/{h_ID}-{page_nr}.jpg") as img_file:  #open image
                pdf.append(img_file.convert("RGBA").convert("RGB"))         #convert, append to pdf
        except UnidentifiedImageError:                  #download failed earlier, image is corrupted
            
            conversion_fails[page_nr-1]+=1  #increment fail counter
            if conversion_fails[page_nr-1]<10:
                log.write(f"Converting {h_ID}-{page_nr}.jpg to pdf failed.")
            else:   #if page failed to convert 10 times or more: give up on hentai
                log.write(f"Converting {h_ID}-{page_nr}.jpg to pdf failed at least 10 times. Giving up hentai {h_ID}...")
                raise RuntimeError
                
            for i in range(10):
                log.write(f"Removing corrupted image {h_ID}-{page_nr}.jpg to redownload later...")
                try:
                    os.remove(f"./{h_ID}/{h_ID}-{page_nr}.jpg") #remove image, redownload later
                except PermissionError: #if could not be removed: try again, give up after 10th try
                    if i<9:
                        log.write(f"Removing corrupted image {h_ID}-{page_nr}.jpg failed. Retrying after waiting 1s...")
                        time.sleep(1)
                        continue
                    else:   #if removing corrupted image failed after 10th try: give hentai up
                        log.write(f"Removing corrupted image {h_ID}-{page_nr}.jpg failed 10 times. Giving up hentai {h_ID}...")
                        raise PermissionError
                log.write(f"\rRemoved corrupted image {h_ID}-{page_nr}.jpg to redownload later.")
                break
            raise UnidentifiedImageError
        except FileNotFoundError:
            log.write(f"{h_ID}-{page_nr}.jpg not found, converting to pdf failed. Redownloading later.")
            raise FileNotFoundError

    
    log.write(f"\rSaving {h_ID}.pdf...")
    if os.path.isdir("./hentai/")==True:
        pdf[0].save(f"./hentai/{h_ID} {title}.pdf", save_all=True, append_images=pdf[1:])  #if exists: save in extra folder
    else:
        pdf[0].save(f"./{h_ID} {title}.pdf", save_all=True, append_images=pdf[1:])  #save
    return