# PyTraffic - People Detection

''' This is the "PeopleDetection" module. '''

# Imports
import cv2
import mimetypes
import os
import imutils

# The Directory
directory = os.path.dirname(os.path.realpath(__file__)).replace(os.sep, "/")

# Initializing the HOG Descriptor
detector = cv2.HOGDescriptor()
detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Function 1 - Detect
def detect(frame, function):
    # Setting the Box Coordinates & Styles
    bounding_box_cordinates, weights =  detector.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)

    # Detecting the People
    person = 1

    for x,y,w,h in bounding_box_cordinates:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(frame, f"Person {person}", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

        person += 1

        # Perform the User Function
        if ((function is not None) and (callable(function))):
            function()

    # Text on the Output
    cv2.putText(frame, f"Total People: {person-1}", (40, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)

    # Showing the Output
    cv2.imshow("People Detection", frame)
    return frame

# Function 2 - Detect By Video
def detectByVideo(path, function):
    # Initializing the Video
    video = cv2.VideoCapture(path)
    check, frame = video.read()

    # Checking if Video is Null
    if (check == False):
        raise Exception("There's something wrong with the video. Try again with another one.")

    # Opening the Video and Sending Video Data to the "detect()" Function
    while video.isOpened():
        check, frame = video.read()

        if (check):
            frame = imutils.resize(frame, width=min(800, frame.shape[1]))
            frame = detect(frame, function)

            # Clicking "q" Closes the Video
            if (cv2.waitKey(1) == ord("q")):
                break
        else:
            raise Exception("There's something wrong with the video. Try again with another one.")
            break

    # Stopping OpenCV
    video.release()
    cv2.destroyAllWindows()

# Function 3 - Detect People
def detectPeople(path, show=False, function=None):
    # Checking if Path Exists
    if (os.path.exists(path)):
        # Checking the File Type
        mimetypes.init()

        mimestart = mimetypes.guess_type(path)[0]
        mimestart = mimestart.split("/")[0]

        if (mimestart == "image"): # Image
            # Reading the Image
            image = cv2.imread(path)

            # Detecting the Humans
            (humans, _) = detector.detectMultiScale(image, winStride=(10, 10), padding=(32, 32), scale=1.1)

            for (x, y, w, h) in humans:
                pad_w, pad_h = int(0.15 * w), int(0.01 * h)
                cv2.rectangle(image, (x + pad_w, y + pad_h), (x + w - pad_w, y + h - pad_h), (0, 255, 0), 2)

                # Performing the User Function
                if ((function is not None) and (callable(function))):
                    function()

            # Returning the Image
            if (show):
                cv2.imshow("People Detection", image)
                cv2.waitKey(0)

            # Returning the Count
            return len(humans)
        elif (mimestart == "video"): # Video
            # Sending the Video to the "detectByVideo()" Function
            detectByVideo(path, function)
        else:
            raise Exception("The file provided must be an image or a video.")
    else:
        raise Exception("The image or video file path does not exist.")