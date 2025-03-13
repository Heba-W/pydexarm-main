import cv2
import numpy as np
import os

def close_camera_app():
    os.system("taskkill /IM WindowsCamera.exe /F 2>nul")  # Closes Camera app without printing errors

def detect_colors(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    height, width, _ = frame.shape
    total_pixels = height * width

    # Define improved color ranges in HSV
    colors = {
        "Red": [(0, 120, 70), (10, 255, 255)],  # First range for red
        "Red2": [(170, 120, 70), (180, 255, 255)],  # Second range for red
        "Green": [(35, 50, 50), (85, 255, 255)],
        "Blue": [(90, 50, 50), (130, 255, 255)],
        "Black": [(0, 0, 0), (180, 50, 50)]   # Adjusted black range
    }

    detected_any = False
    color_percentages = {}

    for color, (lower, upper) in colors.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        color_pixels = cv2.countNonZero(mask)
        percentage = (color_pixels / total_pixels) * 100
    
        if percentage > 1:  # Only show colors with significant presence
            color_percentages[color.replace("2", "")] = round(percentage, 2)
    
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        for contour in contours:
            if cv2.contourArea(contour) > 2000:  # Increased threshold for stability
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, color.replace("2", ""), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                detected_any = True

    if detected_any:
        close_camera_app()  # Close camera app when detection happens

    # Display color percentages on screen
    y_offset = 30
    for color, percentage in color_percentages.items():
        cv2.putText(frame, f"{color}: {percentage}%", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    detect_colors(frame)

    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("Camera Feed", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()