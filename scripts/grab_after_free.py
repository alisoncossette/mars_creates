#!/usr/bin/env python3
"""Grab one frame from whatever /dev/video* is now free, save upright to ~/mars_view.jpg."""
import cv2

saved = False
for d in range(6):
    c = cv2.VideoCapture(d)
    if c.isOpened():
        for _ in range(6):
            c.read()
        r, f = c.read()
        if r and f is not None:
            ff = f[:, : f.shape[1] // 2] if f.shape[1] >= 2 * f.shape[0] else f
            cv2.imwrite("/home/jetson1/mars_view.jpg", cv2.rotate(ff, cv2.ROTATE_90_CLOCKWISE))
            print("SAVED from /dev/video%d" % d, f.shape)
            saved = True
            c.release()
            break
    c.release()
print("done" if saved else "NONE_GRABBABLE")
