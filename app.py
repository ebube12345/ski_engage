from flask import Flask, render_template, Response ,request, jsonify
import os
import shutil
from werkzeug.utils import secure_filename
import comtypes.client
from pdf2image import convert_from_path
import flask_cors
from flask_cors import CORS, cross_origin

UPLOAD_FOLDER = "C:\\Users\\Al-ghazali\\PycharmProjects\\ppt_to_pdf"

from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

app = Flask(__name__)
# CORS(app)
flask_cors.CORS(app, expose_headers='Authorization')

def PPTtoPDF(inputFileName, outputFileName, formatType = 32):
    comtypes.CoInitialize()
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1

    if outputFileName[-3:] != 'pdf':
        outputFileName = outputFileName + ".pdf"
        deck = powerpoint.Presentations.Open(inputFileName)
        deck.SaveAs(outputFileName, formatType) # formatType = 32 for ppt to pdf
        deck.Close()
        powerpoint.Quit()


   

@app.route('/api', methods=['POST'])
def index():
    # return render_template('landing_page.html')
    data = {'message':'Communication successful'}
    return (data)



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        print("No file was uploaded")
        return 'No file was uploaded.'

    pptx_file = request.files['file']
    print(pptx_file)
    if pptx_file.filename == '':
        return 'No file was selected.'

    if pptx_file:
        print(pptx_file)
        filename = secure_filename(pptx_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pptx_file.save(file_path)
        PPTtoPDF(file_path,'C:\\Users\\Al-ghazali\\presentAi_demo\\static\\name')
        
        image =[]  #Array for storing images

        # incase of Linux we don't have to provide the popper_path parameter
        images = convert_from_path(
            "C:\\Users\\Al-ghazali\\presentAi_demo\\static\\name.pdf")

        for i in range(len(images)):
            # Save pages as images in the pdf
            images[i].save(f'static\image_{i+1}.png','PNG')
            slide_folder = 'C:\\Users\\Al-ghazali\\presentAi_demo\\static\\'
            
            
            dir_path = slide_folder #function to count the number of files
            count =0
            # Iterate directory
            for path in os.listdir(dir_path):
           # check if current path is a file
                if os.path.isfile(os.path.join(dir_path, path)):
                    count += 1
        
        size=count

       
        
        
        return render_template("tensorflow.html",size=size)
    else:
        return 'An error occurred while saving the file.'



@app.route('/delete', methods=['POST'])
def delete():
    if request.method == "POST":
        print("Will delete")
        slide_folder = 'C:\\Users\\Al-ghazali\\presentAi_demo\\static\\'
        if os.path.exists(slide_folder):
            dir_path = slide_folder #function to count the number of files
            count = 0
            v=0
            # Iterate directory
            for path in os.listdir(dir_path):
           # check if current path is a file
                if os.path.isfile(os.path.join(dir_path, path)):
                    count += 1
            for i in range(1,count-1):
              v+=1
              s =  str(v)
              os.remove(slide_folder+ "image_" + s+ ".png")
            return render_template('index.html')
        else:
            return "Slide folder does not exist."
        
    else:
        return "Invalid request method"
        
            



if __name__ == '__main__':
    app.run(debug=True)
    
