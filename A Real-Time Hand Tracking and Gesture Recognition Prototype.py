import cv2
import mediapipe as mp
import time
import math
import pyodbc

# Function to calculate hand metrics and other utility functions

def calculate_hand_metrics(hand_landmarks):
    # Calculate hand size
    palm_landmarks = hand_landmarks[0:5]  # Landmarks for the palm region
    palm_length = euclidean_distance(palm_landmarks[0], palm_landmarks[4])
    hand_size = 2 * palm_length  # Approximation of hand size

    # Calculate finger lengths
    finger_lengths = []
    finger_landmarks = [hand_landmarks[4:8], hand_landmarks[8:12], hand_landmarks[12:16], hand_landmarks[16:20], hand_landmarks[20:]]
    for landmarks in finger_landmarks:
        if len(landmarks) >= 2:
            finger_length = 0
            for i in range(len(landmarks)-1):
                finger_length += euclidean_distance(landmarks[i], landmarks[i+1])
            finger_lengths.append(finger_length)
        else:
            finger_lengths.append(0)

    return hand_size, finger_lengths

def euclidean_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def detect_hand_poses(hand_landmarks):
    # Detect and classify different hand poses based on the hand landmarks
    # Modify this function based on your hand pose classification approach

    # Example: Hand Pose Classification based on finger count
    finger_count = detect_finger_count(hand_landmarks)

    if finger_count == 0:
        return "Closed Fist"
    elif finger_count == 1:
        return "One Finger"
    elif finger_count == 2:
        return "Two Fingers"
    elif finger_count == 3:
        return "Three Fingers"
    elif finger_count == 4:
        return "Four Fingers"
    elif finger_count == 5:
        return "Five Fingers"
    else:
        return "Unknown Pose"

def detect_finger_count(hand_landmarks):
    # Detect the number of fingers indicated based on the hand landmarks
    # Modify this function based on the finger positions you want to detect

    finger_positions = [
        hand_landmarks[4],  # Thumb
        hand_landmarks[8],  # Index finger
        hand_landmarks[12],  # Middle finger
        hand_landmarks[16], # Ring finger
        hand_landmarks[20]  # Pinky finger
    ]

    up_fingers = sum(position[2] < position[1] for position in finger_positions)

    return up_fingers

def recognize_hand_action(hand_pose):
    # Recognize hand actions based on the detected hand poses
    # Modify this function based on the hand actions and their associated conditions

    hand_actions = {
        "Grab": ["Closed Fist"],
        "Wave": ["Open Hand"],
        "Point": ["One Finger"],
        "Thumbs-Up": ["One Finger", "Closed Fist"],
        "Peace Sign": ["Two Fingers"],
        "OK Gesture": ["Three Fingers"],
        "Fist Bump": ["Closed Fist", "Closed Fist"],
        "Thumb Down": ["Thumb", "Closed Fist"],
        "Custom Action": ["Specific Hand Gesture"]
    }

    for action, pose_conditions in hand_actions.items():
        if hand_pose in pose_conditions:
            return action

    return "Unknown Action"

# Establish connection to Access database
conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\owez\Documents\Database2.accdb;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handlms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handlms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if id == 0:
                    cv2.circle(img, (cx, cy), 15, (224, 47, 47), cv2.FILLED)
                if id == 1:
                    cv2.circle(img, (cx, cy), 15, (224, 47, 47), cv2.FILLED)
                if id == 2:
                    cv2.circle(img, (cx, cy), 15, (224, 47, 47), cv2.FILLED)
                if id == 3:
                    cv2.circle(img, (cx, cy), 15, (224, 47, 47), cv2.FILLED)
                if id == 4:
                    cv2.circle(img, (cx, cy), 15, (224, 47, 47), cv2.FILLED)
                if id == 5:
                    cv2.circle(img, (cx, cy), 15, (224, 47, 47), cv2.FILLED)
            mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)

            # Detect hand poses
            hand_pose = detect_hand_poses(lmList)
            # Calculate hand metrics
            hand_size, finger_lengths = calculate_hand_metrics(lmList)
            print("Hand Size:", hand_size)
            print("Finger Lengths:", finger_lengths)
            print("Hand Pose:", hand_pose)

            # Detect finger count
            finger_count = detect_finger_count(lmList)
            print("Finger Count:", finger_count)

            # Recognize hand action
            hand_action = recognize_hand_action(hand_pose)
            print("Hand Action:", hand_action)

            # Insert hand metrics, hand pose, and finger count into the HandMetrics table
            cursor.execute('INSERT INTO HandMetrics (HandSize, FingerLengths, HandPose) VALUES (?, ?, ?)',
                           hand_size, ','.join(map(str, finger_lengths)), hand_pose)
            conn.commit()

            # Insert hand action and finger count into the HandActions table
            cursor.execute('INSERT INTO HandActions (HandAction, FingerCount) VALUES (?, ?)',
                           hand_action, finger_count)
            conn.commit()

    cTime = time.time()
    fbs = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fbs)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)

# Close the database connection
cursor.close()
conn.close()
