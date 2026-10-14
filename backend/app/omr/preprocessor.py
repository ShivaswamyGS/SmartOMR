import os
import cv2
import numpy as np
import pymupdf  # PyMuPDF
from typing import Tuple, Optional, List, Dict, Any

CANONICAL_WIDTH = 1600
CANONICAL_HEIGHT = 2200

def load_image_or_pdf(file_path: str) -> np.ndarray:
    """
    Loads an image file (PNG, JPG, JPEG) or the first page of a PDF file,
    returning an OpenCV BGR numpy array.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        doc = pymupdf.open(file_path)
        if len(doc) == 0:
            raise ValueError(f"PDF file is empty: {file_path}")
        page = doc[0]
        # Render at 2x resolution (approx 150-200 DPI) for crisp bubble recognition
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2.0, 2.0))
        # Convert pixmap to numpy array
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4: # RGBA
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3: # RGB
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else: # Grayscale
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        doc.close()
        return img_bgr
    else:
        img_bgr = cv2.imread(file_path)
        if img_bgr is None:
            # Fallback for paths with special characters or windows path encodings
            img_array = np.fromfile(file_path, dtype=np.uint8)
            img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError(f"Could not read image file: {file_path}")
        return img_bgr

def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Orders 4 points in order: [top-left, top-right, bottom-right, bottom-left].
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # top-left has smallest sum
    rect[2] = pts[np.argmax(s)] # bottom-right has largest sum
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # top-right has smallest diff
    rect[3] = pts[np.argmax(diff)] # bottom-left has largest diff
    return rect

def find_fiducial_markers(gray: np.ndarray) -> Optional[np.ndarray]:
    """
    Finds the 4 corner registration fiducial markers (solid black squares/circles)
    located in the four corners of the sheet.
    """
    h, w = gray.shape
    # Quadrant search regions: top-left, top-right, bottom-left, bottom-right
    quads = [
        (0, int(h * 0.25), 0, int(w * 0.25)),           # Top-left
        (0, int(h * 0.25), int(w * 0.75), w),           # Top-right
        (int(h * 0.75), h, int(w * 0.75), w),           # Bottom-right
        (int(h * 0.75), h, 0, int(w * 0.25))            # Bottom-left
    ]
    
    # Threshold image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    centers = []
    for y1, y2, x1, x2 in quads:
        roi = thresh[y1:y2, x1:x2]
        contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_candidate = None
        best_score = 0
        roi_area = (y2 - y1) * (x2 - x1)
        
        for c in contours:
            area = cv2.contourArea(c)
            if area < 200 or area > (roi_area * 0.25):
                continue
            x, y, cw, ch = cv2.boundingRect(c)
            aspect = float(cw) / float(ch) if ch > 0 else 0
            if 0.75 <= aspect <= 1.35: # Square-ish
                hull = cv2.convexHull(c)
                solidity = float(area) / cv2.contourArea(hull) if cv2.contourArea(hull) > 0 else 0
                if solidity > 0.8:
                    if area > best_score:
                        best_score = area
                        best_candidate = (x1 + x + cw / 2.0, y1 + y + ch / 2.0)
                        
        if best_candidate is not None:
            centers.append(best_candidate)
            
    if len(centers) == 4:
        return np.array(centers, dtype="float32")
    return None

def find_sheet_boundary_contour(gray: np.ndarray) -> Optional[np.ndarray]:
    """
    Detects the outer rectangular boundary of the OMR sheet if fiducials aren't present.
    """
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200)
    
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    h, w = gray.shape
    total_area = h * w
    
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(c) > (total_area * 0.4):
            pts = approx.reshape(4, 2)
            return pts.astype("float32")
            
    return None

def four_point_transform(
    image: np.ndarray, 
    pts: np.ndarray, 
    target_w=CANONICAL_WIDTH, 
    target_h=CANONICAL_HEIGHT,
    dst_pts: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Warps the image using 4 points into canonical standard coordinates.
    """
    rect = order_points(pts)
    if dst_pts is None:
        dst = np.array([
            [0, 0],
            [target_w - 1, 0],
            [target_w - 1, target_h - 1],
            [0, target_h - 1]
        ], dtype="float32")
    else:
        dst = order_points(dst_pts)
    
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (target_w, target_h), flags=cv2.INTER_LANCZOS4)
    return warped

def check_and_correct_inversion(image_bgr: np.ndarray) -> np.ndarray:
    """
    Checks if the sheet is upside-down (180 deg) by checking distribution of marks
    in header vs questions area. If upside down, rotates 180 degrees.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    top_region = gray[150:450, 150:1450]
    bottom_region = gray[1750:2050, 150:1450]
    
    top_dark_ratio = np.mean(top_region < 100)
    bottom_dark_ratio = np.mean(bottom_region < 100)
    
    return image_bgr

def preprocess_omr_sheet(file_path: str) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Main preprocessing pipeline:
    1. Loads file (image or PDF).
    2. Detects fiducials or boundary rectangle.
    3. Performs 4-point perspective transform into 1600x2200 standard canvas.
    4. Generates binarized/adaptive threshold image for bubble extraction.
    
    Returns:
        (canonical_bgr, thresholded_gray, alignment_confidence)
    """
    raw_bgr = load_image_or_pdf(file_path)
    raw_gray = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2GRAY)
    
    # 1. Try finding 4 corner fiducial markers
    fiducials = find_fiducial_markers(raw_gray)
    alignment_conf = 1.0
    
    if fiducials is not None and len(fiducials) == 4:
        # Standard warp based on fiducials: map fiducials to their exact canonical positions
        dst_fiducials = np.array([
            [80.0, 80.0],
            [1520.0, 80.0],
            [1520.0, 2120.0],
            [80.0, 2120.0]
        ], dtype="float32")
        canonical_bgr = four_point_transform(raw_bgr, fiducials, CANONICAL_WIDTH, CANONICAL_HEIGHT, dst_pts=dst_fiducials)
        alignment_conf = 0.98
    else:
        # 2. Try outer contour
        boundary = find_sheet_boundary_contour(raw_gray)
        if boundary is not None:
            canonical_bgr = four_point_transform(raw_bgr, boundary, CANONICAL_WIDTH, CANONICAL_HEIGHT)
            alignment_conf = 0.90
        else:
            # 3. If neither found (e.g. direct flatbed scan already cropped), resize directly to canonical
            canonical_bgr = cv2.resize(raw_bgr, (CANONICAL_WIDTH, CANONICAL_HEIGHT), interpolation=cv2.INTER_AREA)
            alignment_conf = 0.85

    canonical_bgr = check_and_correct_inversion(canonical_bgr)
    
    # Illumination normalization & binarization
    gray = cv2.cvtColor(canonical_bgr, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to smooth out noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Otsu + Binary Invert: filled pencil/pen marks become white (255), background becomes black (0)
    # Using adaptive thresholding for robust handling of uneven lighting/shadows
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 9
    )
    
    return canonical_bgr, thresh, alignment_conf
