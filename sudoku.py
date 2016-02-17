import cv2
import numpy as np

def main():

    # Load Image
    img = cv2.imread('sudoku.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur to hide noise
    gray = cv2.GaussianBlur(gray,(7,7),0) # Tuple level of blur, must be odd
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

    # Display Image
    cv2.namedWindow('thresh')
    cv2.createTrackbar('B', 'thresh', 0, 50, remake)
    cv2.imshow('thresh', thresh)
    cv2.waitKey(0)              # Waits for any keypress
    cv2.destroyAllWindows()               

def remake(x):
    b = cv2.getTrackbarPos('B', 'thresh')
    if b % 2 != 1:
        b = b+1
    img = cv2.imread('sudoku.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(b,b),0) # Tuple level of blur, must be odd
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    cv2.imshow('thresh', thresh)

if __name__ == '__main__':
    main()
