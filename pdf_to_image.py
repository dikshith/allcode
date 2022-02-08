# PDF TO IMAGE CONVERSION
import pdf2image
from pdf2image 
import convert_from_path
from PIL import Image
import time

# DECLARE CONSTANTS
PDF_PATH = "1.pdf"
DPI = 200
OUTPUT_FOLDER = None
FIRST_PAGE = 3
LAST_PAGE = 25
FORMAT = 'jpg'
THREAD_COUNT = 1
USERPWD = None
USE_CROPBOX = False
STRICT = False


def pdftopil():

    start_time = time.time()
    pil_images = pdf2image.convert_from_path(PDF_PATH, dpi=DPI, output_folder=OUTPUT_FOLDER, first_page=FIRST_PAGE,
                                             last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD,
                                             use_cropbox=USE_CROPBOX, strict=STRICT)
    print("Time taken : " + str(time.time() - start_time))
    return pil_images


def save_images(pil_images):
    index = FIRST_PAGE
    for image in pil_images:
        image.save('pdf_page_img/pdf_page_' + str(index) + '.jpg', "JPEG")
        index += 1


if __name__ == "__main__":
    pil_images = pdftopil()
    save_images(pil_images)