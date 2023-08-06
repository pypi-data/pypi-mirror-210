import cv2
from pyzbar.pyzbar import decode
import os

def getBarcode(filename):
    # print('FN: ', filename)
    image = cv2.imread(filename)
    height, width = image.shape[:2]
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(grey, (5, 5), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    barcodedata = decode(th3)
    # print(barcodedata)
    if barcodedata == []:
        # Otsu's thresholding
        ret2, th2 = cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        barcodedata = decode(th2)
        # Convert_Barcode_Move_File(barcodedata)
        if barcodedata == []:
            # Threshing on greyscale image
            # print('NA')
            return 'NA'
    res = str(barcodedata[0].data)[2:-1]
    return res
