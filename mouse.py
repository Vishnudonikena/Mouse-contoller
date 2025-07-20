import cv2
import mediapipe as mp
import pyautogui
import math
import time

# --- Configuration (These will be auto-tuned) ---
SMOOTHING_FACTOR = 0.7
CONTROL_BOX_SCALE = 0.35
ACTION_COOLDOWN = 0.5

# --- Setup ---
WINDOW_NAME = 'Eye Controlled Mouse (Calibration)'
pyautogui.FAILSAFE = True

def map_value(x, in_min, in_max, out_min, out_max):
    if (in_max - in_min) == 0: return out_min
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def calculate_ear(eye_points, landmarks):
    try:
        p1 = landmarks[eye_points[0]]
        p2 = landmarks[eye_points[1]]
        p3 = landmarks[eye_points[2]]
        p4 = landmarks[eye_points[3]]
        
        hor_dist = math.dist((p1.x, p1.y), (p2.x, p2.y))
        ver_dist = math.dist((p3.x, p3.y), (p4.x, p4.y))

        if hor_dist == 0: return 0.0
        return ver_dist / hor_dist
    except IndexError:
        return 0.0

def put_text(frame, text, position=(50, 50)):
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

# --- Initialization ---
face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("FATAL ERROR: Cannot open camera.")
    exit()

screen_w, screen_h = pyautogui.size()

# --- Calibration Phase ---
ear_values = []
calibration_frames = 100
is_calibrated = False
ear_sensitivity = 0.0

while not is_calibrated:
    success, frame = cam.read()
    if not success: continue
    frame = cv2.flip(frame, 1)
    
    put_text(frame, "CALIBRATING: Keep eyes open, then blink a few times.")
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)

    if output.multi_face_landmarks:
        landmarks = output.multi_face_landmarks[0].landmark
        left_ear = calculate_ear([33, 133, 159, 145], landmarks)
        right_ear = calculate_ear([362, 263, 386, 374], landmarks)
        
        if left_ear > 0.01 and right_ear > 0.01: # Filter out bad frames
            avg_ear = (left_ear + right_ear) / 2.0
            ear_values.append(avg_ear)
    
    cv2.imshow(WINDOW_NAME, frame)
    if cv2.waitKey(1) & 0xFF == ord('q') or len(ear_values) >= calibration_frames:
        is_calibrated = True

if len(ear_values) > 20:
    ear_values.sort()
    # Calculate sensitivity based on the lowest 10% of EAR values (blinks)
    blink_threshold_index = len(ear_values) // 10
    ear_sensitivity = ear_values[blink_threshold_index] * 1.1 # Add a small buffer
    print(f"Calibration complete. EAR Sensitivity set to: {ear_sensitivity:.2f}")
else:
    print("Calibration failed. Using default sensitivity.")
    ear_sensitivity = 0.18 # Fallback to default

# --- Main Control Loop ---
cv2.destroyAllWindows()
WINDOW_NAME = 'Eye Controlled Mouse (Active)'
smooth_x, smooth_y = screen_w / 2, screen_h / 2
last_action_time = 0
is_blinking = False

while True:
    success, frame = cam.read()
    if not success:
        time.sleep(0.1)
        continue

    frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape
    
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        current_time = time.time()

        if output.multi_face_landmarks:
            put_text(frame, "Status: ACTIVE", (frame_w - 200, 50))
            landmarks = output.multi_face_landmarks[0].landmark

            left_iris = landmarks[473]
            right_iris = landmarks[468]
            avg_iris_x = (left_iris.x + right_iris.x) / 2
            avg_iris_y = (left_iris.y + right_iris.y) / 2
            
            box_w = frame_w * CONTROL_BOX_SCALE
            box_h = frame_h * CONTROL_BOX_SCALE
            box_x_min = (frame_w / 2) - (box_w / 2)
            box_y_min = (frame_h / 2) - (box_h / 2)

            target_x = map_value(avg_iris_x * frame_w, box_x_min, box_x_min + box_w, 0, screen_w)
            target_y = map_value(avg_iris_y * frame_h, box_y_min, box_y_min + box_h, 0, screen_h)
            
            smooth_x = smooth_x * SMOOTHING_FACTOR + target_x * (1 - SMOOTHING_FACTOR)
            smooth_y = smooth_y * SMOOTHING_FACTOR + target_y * (1 - SMOOTHING_FACTOR)

            pyautogui.moveTo(max(0, min(screen_w - 1, smooth_x)), max(0, min(screen_h - 1, smooth_y)))

            left_ear = calculate_ear([33, 133, 159, 145], landmarks)
            right_ear = calculate_ear([362, 263, 386, 374], landmarks)
            avg_ear = (left_ear + right_ear) / 2.0

            if avg_ear < ear_sensitivity and avg_ear > 0.01:
                if not is_blinking and (current_time - last_action_time) > ACTION_COOLDOWN:
                    pyautogui.click()
                    last_action_time = current_time
                    is_blinking = True
            else:
                is_blinking = False
        else:
            put_text(frame, "Status: Searching for face...", (frame_w - 300, 50))

        cv2.imshow(WINDOW_NAME, frame)

    except Exception as e:
        print(f"An error occurred: {e}")
        break

    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
        break

# --- Cleanup ---
cam.release()
cv2.destroyAllWindows()
print("Script terminated.")
