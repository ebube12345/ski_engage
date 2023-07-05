from flask import Flask, render_template, Response ,request
from cvzone.HandTrackingModule import HandDetector
import cv2
import os
import numpy as np
import comtypes.client
from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

app = Flask(__name__)

def PPTtoPDF(inputFileName, outputFileName, formatType = 32):
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1

    if outputFileName[-3:] != 'pdf':
        outputFileName = outputFileName + ".pdf"
        deck = powerpoint.Presentations.Open(inputFileName)
        deck.SaveAs(outputFileName, formatType) # formatType = 32 for ppt to pdf
        deck.Close()
        powerpoint.Quit()

def gen_frames():
    # Parameters
    width, height = 1920, 1080
    gestureThreshold = 300
    #put the presentation folder path here
    folderPath = "presentation1"

    # Camera Setup
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)

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


    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
        imgCurrent = cv2.imread(pathFullImage)
        # Find the hand and its landmarks
        hands, img = detectorHand.findHands(img)  # with draw
        # Draw Gesture Threshold line
        cv2.line(img, (0, gestureThreshold),(width, gestureThreshold), (0, 255, 0), 10)

        if hands and buttonPressed is False:  # If hand is detected

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
                    if imgNumber < len(pathImages) - 1:
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

        #this is where the datatype conversion goes on so that the computer can be able to understand the feed so its converted to jpg
        ret, buffers = cv2.imencode('.jpg', imgSmall)
        frame1 = buffers.tobytes()
        yield (b'--frame1\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n')

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        ret, image_byte = cv2.imencode('.jpg', imgCurrent)
        frames = image_byte.tobytes()
        yield (b'--frames\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frames + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Define the app route to stream the camera frames to the web
@app.route('/slides_feed')
def slides_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frames')

@app.route('/upload', methods=['POST'])

def upload():
    pptx_file = request.files['pptx_file']
    if pptx_file:
        # Save the uploaded file to a folder
        if pptx_file.save('C:\\Users\\g\\Documents\\dev\\test\\ppt_file'):
           PPTtoPDF('C:\\Users\\g\\Documents\\dev\\test\\ppt_file',"C:\\Users\\g\\Documents\\dev\\test\\name")
        else:
            return "ppt not saved at all"
        
        return 'File uploaded and saved successfully!'
    else:
        return 'file not uploaded succesfully'
       
        # Process the uploaded file here (e.g., save it to a folder, extract data, etc.)
        # You can access the file name using pptx_file.filename
    
      


if __name__ == '__main__':
    app.run(debug=True)
