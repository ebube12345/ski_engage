import comtypes.client

from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

def PPTtoPDF(inputFileName, outputFileName, formatType = 32):
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1

    if outputFileName[-3:] != 'pdf':
        outputFileName = outputFileName + ".pdf"
    deck = powerpoint.Presentations.Open(inputFileName)
    deck.SaveAs(outputFileName, formatType) # formatType = 32 for ppt to pdf
    deck.Close()
    powerpoint.Quit()




PPTtoPDF("C:\\Users\\Al-ghazali\\PycharmProjects\\ppt_to_pdf\\pitch_desk_format.pptx","C:\\Users\\Al-ghazali\\PycharmProjects\\ppt_to_pdf\\pitch_desk_format.pptx")


image =[]  #Array for storing images

# incase of Linux we don't have to provide the popper_path parameter
images = convert_from_path(
	"C:\\Users\\Al-ghazali\\PycharmProjects\\ppt_to_pdf\\pitch_desk_format.pptx.pdf")

for i in range(len(images)):
	# Save pages as images in the pdf
    images[i].save(f'image_{i+1}.png','PNG')
    image.append(images[i])


print(image)
