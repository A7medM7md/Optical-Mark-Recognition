import cv2
import numpy as np
import utlis  # Utility functions like contour detection, splitting boxes, etc.

########################################################################
webCamFeed = False
pathImage = "assets/1.jpg"  # Path to the image to be scanned
heightImg = 700
widthImg = 700
questions = 5
choices = 5
ans = [1, 2, 0, 2, 4]  # Correct answers for each question
########################################################################


if webCamFeed:
    cap = cv2.VideoCapture(0)
    cap.set(10, 160)

while True:
    # Read image from webcam or file
    if webCamFeed:
        success, img = cap.read()
        if not success:
            print("Error: Couldn't read from the webcam.")
            break
    else:
        img = cv2.imread(pathImage)
        if img is None:
            print(f"Error: Couldn't read the image at path {pathImage}")
            break

    img = cv2.resize(img, (widthImg, heightImg))  # Resize image to standard dimensions
    imgFinal = img.copy()  # Copy of original image to draw final output
    imgBlank = np.zeros((heightImg, widthImg, 3), np.uint8)  # Empty image for error handling
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # Apply Gaussian Blur
    imgCanny = cv2.Canny(imgBlur, 10, 70)  # Edge detection using Canny

    try:
        # Find contours on edge image
        imgContours = img.copy()
        imgBigContour = img.copy()
        contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)

        # Get the biggest rectangular contours: answer sheet and grade area
        rectCon = utlis.rectContour(contours)
        biggestPoints = utlis.getCornerPoints(rectCon[0])  # Main sheet
        gradePoints = utlis.getCornerPoints(rectCon[1])    # Grade box

        if biggestPoints.size != 0 and gradePoints.size != 0:
            biggestPoints = utlis.reorder(biggestPoints)
            cv2.drawContours(imgBigContour, biggestPoints, -1, (0, 255, 0), 20)

            # Perspective transform to get top-down view of answer sheet
            pts1 = np.float32(biggestPoints)
            pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

            # Perspective transform for grade display area
            gradePoints = utlis.reorder(gradePoints)
            cv2.drawContours(imgBigContour, gradePoints, -1, (255, 0, 0), 20)
            ptsG1 = np.float32(gradePoints)
            ptsG2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])
            matrixG = cv2.getPerspectiveTransform(ptsG1, ptsG2)
            imgGradeDisplay = cv2.warpPerspective(img, matrixG, (325, 150))

            # Threshold the warped image to get binary image
            imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
            imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]

            # Split threshold image into boxes for each question
            boxes = utlis.splitBoxes(imgThresh)
            countR = 0
            countC = 0
            myPixelVal = np.zeros((questions, choices))  # Store pixel count per choice

            # Count white pixels in each box
            for image in boxes:
                totalPixels = cv2.countNonZero(image)
                myPixelVal[countR][countC] = totalPixels
                countC += 1
                if countC == choices:
                    countC = 0
                    countR += 1

            # Determine selected answer (box with most white pixels)
            myIndex = []
            for x in range(0, questions):
                arr = myPixelVal[x]
                myIndexVal = np.where(arr == np.amax(arr))
                myIndex.append(myIndexVal[0][0])

            # Grade student answers
            grading = []
            for x in range(0, questions):
                if ans[x] == myIndex[x]:
                    grading.append(1)  # Correct
                else:
                    grading.append(0)  # Incorrect

            score = (sum(grading) / questions) * 100  # Calculate percentage

            # Draw answer results on the warped image
            utlis.showAnswers(imgWarpColored, myIndex, grading, ans)
            utlis.drawGrid(imgWarpColored)

            # Create blank image and draw results
            imgRawDrawings = np.zeros_like(imgWarpColored)
            utlis.showAnswers(imgRawDrawings, myIndex, grading, ans)

            # Warp the result drawings back to original image perspective
            invMatrix = cv2.getPerspectiveTransform(pts2, pts1)
            imgInvWarp = cv2.warpPerspective(imgRawDrawings, invMatrix, (widthImg, heightImg))

            # Create grade image and write score on it
            imgRawGrade = np.zeros_like(imgGradeDisplay, np.uint8)
            cv2.putText(imgRawGrade, str(int(score)) + "%", (70, 100),
                        cv2.FONT_HERSHEY_COMPLEX, 3, (0, 255, 255), 3)

            # Warp grade image back to original position
            invMatrixG = cv2.getPerspectiveTransform(ptsG2, ptsG1)
            imgInvGradeDisplay = cv2.warpPerspective(imgRawGrade, invMatrixG, (widthImg, heightImg))

            # Overlay drawings and grade onto original image
            imgFinal = cv2.addWeighted(imgFinal, 1, imgInvWarp, 1, 0)
            imgFinal = cv2.addWeighted(imgFinal, 1, imgInvGradeDisplay, 1, 0)

            # Stack all steps to display process
            imageArray = ([img, imgGray, imgCanny, imgContours],
                        [imgBigContour, imgThresh, imgWarpColored, imgFinal])
            cv2.imshow("Final Result", imgFinal)

    except Exception as e:
        print(f"Error during processing: {e}")
        imageArray = ([img, imgGray, imgCanny, imgContours],
                        [imgBlank, imgBlank, imgBlank, imgBlank])

    # Label names for each image in the display
    lables = [["Original", "Gray", "Edges", "Contours"],
                ["Biggest Contour", "Threshold", "Warped", "Final"]]

    # Stack images into a single display window
    stackedImage = utlis.stackImages(imageArray, 0.5, lables)
    cv2.imshow("Result", stackedImage)

    # Press 's' to save final result
    key = cv2.waitKey(1)
    if key == ord('s'):
        cv2.imwrite(f"Scanned/ResultImage.jpg", imgFinal)
        print(f"Image Saved as Scanned/ResultImage.jpg")
    # Press 'q' to quit
    if key == ord('q'):
        print("Good bye")
        break

cv2.destroyAllWindows()
