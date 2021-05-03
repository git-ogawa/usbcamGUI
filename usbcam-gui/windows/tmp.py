#!/usr/bin/env python3
import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    cv2.imshow("window", frame)
    key = cv2.waitKey(27)
    if key == ord('s'):
        cv2.imwrite("tmp.png", frame)
        print("tmp.png")
    elif key == ord('q'):
        break

cv2.destroyAllWindows()