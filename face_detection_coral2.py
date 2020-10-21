import cv2
from edgetpu.detection.engine import DetectionEngine
from PIL import Image

#engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
engine = DetectionEngine("face-detector-quantized_edgetpu.tflite")
cap = cv2.VideoCapture(-1)
cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
term = False
while not term:
    _, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
    
    cv2.imshow("image", frame)
        #now = time.time()
        #print(now-start)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()    
cv2.destroyAllWindows()
exit(0)
    
