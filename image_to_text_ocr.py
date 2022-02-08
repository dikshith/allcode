# # Python program to extract text from all the images in a folder
# storing the text in corresponding files in a different folder
from PIL import Image
import pytesseract as pt
import os

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def main():
    # path for the folder for getting the raw images
    global imagepath
    input_path = "D:\\sps_documents\\python\\tesseract_OD_pdf\\pdf_page_img"

    # path for the folder for getting the output
    output_path = "D:\\sps_documents\\python\\tesseract_OD_pdf\\text_file"

    # iterating the images inside the folder
    for image_to_convert in os.listdir(input_path):
        inputPath = os.path.join(input_path, image_to_convert)
        img = Image.open(inputPath)

        # applying ocr using pytesseract for python
        text = pt.image_to_string(img, lang="hin+eng")

        from textblob import TextBlob
        text1 = TextBlob(text)

        txt = text1.translate(to='en')
        translated_text = str(txt)
        # print(translated_text)
        # for removing the .jpg from the imagePath
        image_to_convert = image_to_convert[0:-4]

        print(len(translated_text))
        fullPath = os.path.join(output_path, image_to_convert+ ".txt")
        # print(text)

        # saving the  text for every image in a separate .txt file
        import codecs
        f = codecs.open(fullPath, encoding='utf-8', mode="w")
        f.write(translated_text)
        f.close()
        file1 = codecs.open(fullPath, encoding='utf-8', mode="r+")
        file1.seek(0)

if __name__ == '__main__':
    main()
