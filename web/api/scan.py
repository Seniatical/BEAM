import numpy as np
import cv2
from skimage.morphology import extrema
from skimage.morphology import watershed as skwater
import numpy as np
from keras.preprocessing import image
from io import BytesIO
from PIL import Image

def get_tumour(stream: BytesIO):
    file_bytes = np.asarray(bytearray(stream.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    scan = image
    cv2.waitKey(1)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    
    ret, markers = cv2.connectedComponents(thresh)
    marker_area = [np.sum(markers == m) for m in range(np.max(markers)) if m != 0] 
    largest_component = np.argmax(marker_area) + 1
    brain_mask = markers == largest_component
    brain_out = image.copy()
    brain_out[brain_mask == False] = (0,0,0)
    img = scan
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 2)
    sure_bg = cv2.dilate(opening, kernel,iterations = 3)
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv2.watershed(img, markers)
    img[markers == -1] = [255, 0, 0]
    im1 = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)

    image = Image.fromarray(im1)
    new_stream = BytesIO()

    image.save(new_stream, 'PNG')
    new_stream.seek(0)

    return new_stream
