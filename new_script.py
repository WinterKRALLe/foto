import cv2
import pytesseract
import re
import os
from pdf2image import convert_from_path
from PyPDF3 import PdfFileWriter, PdfFileReader

pdf_dir = "/mnt/nas/foto/sken-in"
new_dir = "/mnt/nas/foto/sken-out"

def Extract_PP_from_PDF(input_file, output_file):
    
    output = PdfFileWriter()
    input1 = PdfFileReader(open(input_file, "rb"))

    output_page = input1.getPage(0)

    x0 = 16.5 * 28.35  # Convert cm to points (1 cm = 28.35 points)
    y0 = (output_page.mediaBox.getHeight() - 1.18 * 28.35)
    x1 = 19.8 * 28.35
    y1 = (output_page.mediaBox.getHeight() - 5.75 * 28.35)

    output_page.mediaBox.lowerLeft = (x0, y0)
    output_page.mediaBox.lowerRight = (x1, y0)
    output_page.mediaBox.upperLeft = (x0, y1)
    output_page.mediaBox.upperRight = (x1, y1)

    output.addPage(output_page)
    outputStream = open(output_file, "wb")
    output.write(outputStream)


def Extract_BN_from_PDF(input_file, output_file):
    
    output = PdfFileWriter()
    input1 = PdfFileReader(open(input_file, "rb"))

    output_page = input1.getPage(0)

    x0 = 10.25 * 28.35  # Convert cm to points (1 cm = 28.35 points)
    y0 = (output_page.mediaBox.getHeight() - 7 * 28.35)
    x1 = 19.75 * 28.35
    y1 = (output_page.mediaBox.getHeight() - 10 * 28.35)

    output_page.mediaBox.lowerLeft = (x0, y0)
    output_page.mediaBox.lowerRight = (x1, y0)
    output_page.mediaBox.upperLeft = (x0, y1)
    output_page.mediaBox.upperRight = (x1, y1)

    output.addPage(output_page)
    outputStream = open(output_file, "wb")
    output.write(outputStream)


def Read_BN(input_file):

    output_file = rf"{pdf_dir}/outputBN.pdf"
    Extract_BN_from_PDF(input_file, output_file)

    pages = convert_from_path(output_file, first_page=0, last_page=0)
    image = pages[0]

    image_path = f"{pdf_dir}/page.png"

    image.save(image_path)

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Repair horizontal table lines 
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,1))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (55,2))
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (255,255,255), 9)

    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,55))
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (255,255,255), 9)

    text = pytesseract.image_to_string(image, lang="ces")
    print(text)

    match = re.search(r"rodné číslo . (.+?)\s", text)
    if match:
        BN = match.group(1)
        print("BN:", BN)
    else:
        print("No BN found in ", input_file)
        BN = None

    #os.remove(image_path)
    os.remove(output_file)

    return BN


def Save_PP(input_file, BN):
    output_file = rf"{pdf_dir}/outputBN.pdf"
    Extract_PP_from_PDF(input_file, output_file)

    pages = convert_from_path(output_file, first_page=0, last_page=0)
    image = pages[0]

    img_resized = image.resize((480, 640))
    new_file_path = os.path.join(os.path.expanduser(new_dir), f"{BN}.png")
    img_resized.save(new_file_path)
    os.remove(output_file)


# Save_PP("/home/winter/Documents/DOC120423-12042023133014-0001.pdf", Read_BN("/home/winter/Documents/DOC120423-12042023133014-0001.pdf"))

for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        file = os.path.join(pdf_dir, filename)
        BN = Read_BN(file)
        if BN is None:
            continue
        Save_PP(file, BN)

