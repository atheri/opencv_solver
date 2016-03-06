import sys
import cv2
import numpy as np

def main():

    print(len(sys.argv))
    if len(sys.argv) != 2:
        print("Usage: python3 sudoku.py [image]")
        sys.exit()

    # Load Image
    img = cv2.imread(sys.argv[1])
    blur = cv2.GaussianBlur(img,(5,5),0) # Tuple level of blur, must be odd
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY) # Grayscale

    # Create a black image to be used as a mask the same dimensions as image
    mask = np.zeros((gray.shape), np.uint8)

    # A circular kernel for the morphologyEx function
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11))  # Tuple adjusts circle size
    # Create a 'background' image with morphologic close
    close = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    
    # Use the closing image to normalize brightness / background 
    div = np.float32(gray)/close
    global adjusted_src
    adjusted_src = np.uint8(cv2.normalize(div, div, 0, 255, cv2.NORM_MINMAX)) # Turn color values back to 0-255 from floats

    thresh = cv2.adaptiveThreshold(adjusted_src, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 7, 2)
    _, contours, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # find Contour with largest area (should be sudoku grid)
    max_area = 0
    best_cnt = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt
    
    cv2.drawContours(mask, [best_cnt], 0, 255, -1)
    #cv2.drawContours(mask, [best_cnt], 0, 0, 2)

    #masked = cv2.bitwise_and(adjusted_src,mask)

    sobelx = cv2.Sobel(adjusted_src,-1,2,0,ksize=5)
    sobely = cv2.Sobel(adjusted_src,-1,0,2,ksize=5)
    
    maskedx = cv2.bitwise_and(sobelx,mask)
    maskedy = cv2.bitwise_and(sobely,mask)

    # Display Image
    #cv2.namedWindow('masked')
    #cv2.namedWindow('res')
    #cv2.createTrackbar('B', 'thresh', 5, 100, remake)
    #cv2.setTrackbarPos('B', 'thresh', 7)
    cv2.imshow('maskedx', maskedx)
    cv2.imshow('maskedy', maskedy)
    cv2.imshow('adjusted_src', adjusted_src)
    cv2.waitKey(0)              # Waits for any keypress
    cv2.destroyAllWindows()               

"""
def remake(x):
    b = cv2.getTrackbarPos('B', 'thresh')
    if b % 2 != 1:
        b = b+1
        cv2.setTrackbarPos('B', 'thresh', b)
    thresh = cv2.adaptiveThreshold(adjusted_src, 255, 0, 1, b, 2)

    cv2.imshow('thresh', thresh)
"""

if __name__ == '__main__':
    main()
