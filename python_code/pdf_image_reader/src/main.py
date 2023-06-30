# import module
from pdf2image import convert_from_path
from PIL import Image
import pytesseract


def convert_pdf():
    # Store Pdf with convert_from_path function
    images = convert_from_path("../pdfs/necrons.pdf")

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save("./output/necrons/page" + str(i) + ".jpg", "JPEG")


print(pytesseract.image_to_string(Image.open("./output/necrons/page24.jpg")))
