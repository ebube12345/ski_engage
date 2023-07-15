import comtypes.client
import PIL
from PIL import Image
from flask import Flask, render_template, Response ,request
from cvzone.HandTrackingModule import HandDetector
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed', methods=['POST'])
def video_feed():
    frame_data = request.form['frame']
    frame = gen_frames(frame_data)
    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()

    return Response(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n', mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/process_frame', methods=['POST'])
def process_frame():
    frame_data = request.form['frame']

    # Decode the Base64 image data
    frame_bytes = base64.b64decode(frame_data)
    print(type(frame_bytes))
    response = 'Frame processed successfully'
    # Convert the decoded frame data into a numpy array
    frame_arr = np.frombuffer(frame_bytes, np.uint8)

    # Create PIL Image from numpy array
    img = Image.fromarray(frame_arr.astype(np.uint8))
    np_image = np.array(img)


    # Convert RGB to BGR (if needed)
    img = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    print(type(img))

    width, height = 640, 480

# Resize the image
    img= cv2.resize(img, (width, height))
    
    gestureThreshold = 300

   
    detectorHand = HandDetector(detectionCon=0.5, maxHands=1)
    hands, img = detectorHand.findHands(img)  # with draw
    print("hand detected")
    # # Draw Gesture Threshold line
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    # # Rest of the code...
    # # ...

   
    return response

# Define the app route to stream the camera frames to the web
@app.route('/slides_feed')
def slides_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frames')

@app.route('/delete_slide', methods=['POST'])
def delete_slide():
    slide_id = request.json.get('slide_id')
    slide_folder = os.path.join(app.config['UPLOAD_FOLDER'], slide_id)
    if os.path.exists(slide_folder):
        # Use the os module to remove the slide folder recursively
        shutil.rmtree(slide_folder)
        return f"Slide with ID {slide_id} has been deleted."
    else:
        return f"Slide with ID {slide_id} does not exist."

@app.route('/upload', methods=['POST'])
def upload():
    if 'pptx_file' not in request.files:
        return 'No file was uploaded.'

    pptx_file = request.files['pptx_file']
    print(pptx_file)
    if pptx_file.filename == '':
        return 'No file was selected.'

    if pptx_file:
        filename = secure_filename(pptx_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        PPTtoPDF(file_path,'C:\\Users\\g\\Documents\\dev\\test\\name')

                
        image =[]  #Array for storing images

        # incase of Linux we don't have to provide the popper_path parameter
        images = convert_from_path(
            "C:\\Users\\g\\Documents\\dev\\test\\name.pdf")

        for i in range(len(images)):
            # Save pages as images in the pdf
            images[i].save(f'image_{i+1}.png','PNG')
            image.append(images[i])
            print('-------------------------')

        print(image)
        
        return 'File uploaded and saved successfully!'
    else:
        return 'An error occurred while saving the file.'


UPLOAD_FOLDER = 'C:\\Users\\g\\Documents\\dev\\test'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
image =[]  #Array for storing images

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

    # incase of Linux we don't have to provide the popper_path parameter
    images = convert_from_path(
        "C:\\Users\\g\\Documents\\dev\\test\\name.pdf")

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(f'image_{i+1}.png','PNG')
        image.append(images[i])

    print(image)

def gen_frames(frame_data):
    # Parameters
    width, height = 640, 480  # Change the resolution according to your camera
    gestureThreshold = 300
    folderPath = "presentation1"

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.85, maxHands=1)

    # Variables
    imgList = []
    delay = 15
    buttonPressed = False
    counter = 0
    drawMode = False
    imgNumber = 0
    delayCounter = 0
    annotations = [[]]
    annotationNumber = -1
    annotationStart = False
    hs, ws = int(120 * 1), int(213 * 1)  # width and height of small image

    # Get list of presentation images
    pathImages = sorted(os.listdir(folderPath), key=len)
    print(pathImages)

    # Process the received frame data
    frame_bytes = base64.b64decode(frame_data)
    frame_arr = np.frombuffer(frame_bytes, np.uint8)
    img = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)

    img = cv2.flip(img, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    
    # Find the hand and its landmarks
    hands, img = detectorHand.findHands(img)  # with draw
    # Draw Gesture Threshold line
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    # Rest of the code...
    # ...

    if hands and buttonPressed is False:  # If hand is detected
        print("------------ working")

        hand = hands[0]
        cx, cy = hand["center"]
        lmList = hand["lmList"]  # List of 21 Landmark points
        fingers = detectorHand.fingersUp(hand)  # List of which fingers are up

        # Constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [200, height-200], [0, height]))
        indexFinger = xVal, yVal

        if cy <= gestureThreshold:  # If hand is at the height of the face
            if fingers == [0, 1, 1, 1, 1]:
                print("Left")
                buttonPressed = True
                if imgNumber > 0:
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    # # Display a notification icon
                    # icon = cv2.imread("arrow-left.png")
                    # icon = cv2.resize(icon, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                    # imgCurrent[20:20+icon.shape[0], 20:20+icon.shape[1]] = icon
                    # cv2.imshow("Slides", imgCurrent)
                    # cv2.imshow("Image", img)
                    # cv2.waitKey(800)  # Wait for 3 seconds
            if fingers == [0, 0, 0, 0, 0]:
                print("Right")
                buttonPressed = True
                if imgNumber < len(image) - 1:
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    # # Display a notification icon
                    # icon = cv2.imread("right-arrow.png")
                    # icon = cv2.resize(icon, (0, 0), fx=0.8, fy=0.8)
                    # imgCurrent[30:30+icon.shape[0], 30:30+icon.shape[1]] = icon
                    # cv2.imshow("Slides", imgCurrent)
                    # cv2.imshow("Image", img)
                    # cv2.waitKey(800)  # Wait for 3 seconds

        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 255, 255), cv2.FILLED)

        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            print(annotationNumber)
            annotations[annotationNumber].append(indexFinger)
            cv2.circle(imgCurrent, indexFinger, 12, (255, 0, 255), cv2.FILLED)

        else:
            annotationStart = False
        

        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True

    else:
        annotationStart = False

    if buttonPressed:
        counter += 1
        if counter > delay:
            counter = 0
            buttonPressed = False

    for i, annotation in enumerate(annotations):
        for j in range(len(annotation)):
            if j != 0:
                cv2.line(imgCurrent, annotation[j - 1],annotation[j], (0, 0, 200), 12)
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w - ws: w] = imgSmall

    # Convert the frame to JPEG format
    ret, frame_buffer = cv2.imencode('.jpg', img)
    frame_bytes = frame_buffer.tobytes()

    # Yield the frame bytes as a response
    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


if __name__ == '__main__':
    app.run(debug=True)
