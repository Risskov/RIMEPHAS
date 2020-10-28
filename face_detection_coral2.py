import cv2
from edgetpu.detection.engine import DetectionEngine
from PIL import Image

engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
#engine = DetectionEngine("face-detector-quantized_edgetpu.tflite")
cap = cv2.VideoCapture(-1)
cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
"""
cv2.namedWindow('imageL', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('imageR', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('imageBL', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('imageBR', cv2.WINDOW_AUTOSIZE)
"""
term = False

def frameCutout(frame, vOff, hOff):
    frameRGB = frame[vOff:320+vOff, hOff:320+hOff]
    framePIL = Image.fromarray(frameRGB)
    faces = engine.detect_with_image(framePIL,
                                     threshold=0.05,
                                     keep_aspect_ratio=True,
                                     relative_coord=False,
                                     top_k=10,
                                     resample=4)
    for face in faces:
        (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
        #print(x, x2)
        w = x2-x
        h = y2-y
        x = x+hOff
        y = y+vOff
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        print(h/w)
        
    return frame

while not term:
    _, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    frameRGB = frameCutout(frameRGB, 0, 0)
    frameRGB = frameCutout(frameRGB, 0, 320)
    frameRGB = frameCutout(frameRGB, 160, 0)
    frameRGB = frameCutout(frameRGB, 160, 320)
    
    cv2.imshow("image", frameRGB)
    """
    cv2.imshow("imageL", frameL)
    cv2.imshow("imageR", frameR)
    cv2.imshow("imageBL", frameBL)
    cv2.imshow("imageBR", frameBR)
    """
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()    
cv2.destroyAllWindows()
exit(0)

"""
frameL = frame[0:320, 0:320]
frameRGB = cv2.cvtColor(frameL, cv2.COLOR_BGR2RGB)
framePIL = Image.fromarray(frameRGB)
faces = engine.detect_with_image(framePIL,
                                 threshold=0.05,
                                 keep_aspect_ratio=True,
                                 relative_coord=False,
                                 top_k=10,
                                 resample=4)
for face in faces:
    (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
    w = x2-x
    h = y2-y
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    
frameR = frame[0:320, 320:640]
frameRGB = cv2.cvtColor(frameR, cv2.COLOR_BGR2RGB)
framePIL = Image.fromarray(frameRGB)
faces = engine.detect_with_image(framePIL,
                                 threshold=0.05,
                                 keep_aspect_ratio=True,
                                 relative_coord=False,
                                 top_k=10,
                                 resample=4)
for face in faces:
    (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
    w = x2-x
    h = y2-y
    x = x+320
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    
vOff = 480-320

frameBL = frame[vOff:480, 0:320]
frameRGB = cv2.cvtColor(frameBL, cv2.COLOR_BGR2RGB)
framePIL = Image.fromarray(frameRGB)
faces = engine.detect_with_image(framePIL,
                                 threshold=0.05,
                                 keep_aspect_ratio=True,
                                 relative_coord=False,
                                 top_k=10,
                                 resample=4)
for face in faces:
    (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
    w = x2-x
    h = y2-y
    y = y+vOff
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

frameBR = frame[vOff:480, 320:640]
frameRGB = cv2.cvtColor(frameBR, cv2.COLOR_BGR2RGB)
framePIL = Image.fromarray(frameRGB)
faces = engine.detect_with_image(framePIL,
                                 threshold=0.05,
                                 keep_aspect_ratio=True,
                                 relative_coord=False,
                                 top_k=10,
                                 resample=4)
for face in faces:
    (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
    w = x2-x
    h = y2-y
    x = x+320
    y = y+vOff
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
"""
