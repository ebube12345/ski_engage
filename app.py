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



   
@app.route('/')
def land():
    return Response("Hosted")

@app.route('/api', methods=['POST'])
def index():
    # return render_template('landing_page.html')
    data = {'message':'Communication successful'}
    return (data)



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload', methods=['POST'])
def upload():
    global var
    var = request.form['fileId']
    print(request.files)
    if 'files' not in request.files:
        print("No file was uploaded")
        return 'No file was uploaded.'

    pptx_file = request.files['files']
    print(pptx_file)
    if pptx_file.filename == '':
        return 'No file was selected.'
    
    # directory = var + '\\name'
    parent_dir = "C:\\Users\\Al-ghazali\\presentAi_demo\\static\\"
    directory = secure_filename(var)
    app.config['parent_dir'] = parent_dir
    path1 = os.path.join(app.config['parent_dir'], var) # var is the dynamic variable here to create dynamic folders
    os.mkdir(path1)  #path1 is the new folder name
    print(path1)
    
    
    
    
    
    

    if pptx_file:
        print(pptx_file)
        filename = secure_filename(pptx_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pptx_file.save(file_path)
        PPTtoPDF(file_path, f'{path1}\{var}') # folder where pdf is saved
        
        image =[]  #Array for storing images

        # incase of Linux we don't have to provide the popper_path parameter
        new_folder = f'{path1}/{var}.pdf'
        images = convert_from_path(
            new_folder)

        for i in range(len(images)):
            # Save pages as images in the pdf
            images[i].save(f'static\{var}\image_{i+1}.png','PNG')
            slide_folder = path1
            
            
            dir_path = slide_folder #function to count the number of files
            count =0
            # Iterate directory
            for path in os.listdir(dir_path):
           # check if current path is a file
                if os.path.isfile(os.path.join(dir_path, path)):
                    count += 1
        global val            #This variable is declared to count the number of images in the given folder
        val = count
        print(val)

       
        
        
        return jsonify({'message': 'success'})
    else:
        return 'An error occurred while saving the file.'




@app.route('/count', methods=['POST'])
def slide_count():
    print(request.json)
    add = request.json['data']
    try:
        my_list = []
        # print("slide count is", size)
        
        for i in range(1,val):
            v = str(i)
            Src =  f'https://brave-equally-gar.ngrok-free.app/static/{add}/image_{v}.png'
            my_list.append(
                {
                    "id": i,
                    "Src": Src
                }
                )
        print(my_list)
    except Exception as e:
        print (e)
    
    return my_list
    
    
@app.route('/delete', methods=['POST'])
def delete():
    print(request.json['data'])
    rem = request.json['data']
    
    print("Will delete")
    slide_folder = f'C:\\Users\\Al-ghazali\\presentAi_demo\\static\\{rem}'
    if os.path.exists(slide_folder):
        shutil.rmtree(slide_folder)
        print("Deleted", rem)
        
        return jsonify({'message':'deleted'})
   
    else:
        print("Failed to delete")
        return "file not exist"
            
        
   
        
            



if __name__ == '__main__':
    app.run(debug=True)
