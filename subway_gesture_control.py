import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(1)

reset_index_x = None
reset_middle_y = None
last_action_time = 0
action_delay = 0.5

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark
            fingers_open = []

            tips = [4, 8, 12, 16, 20]
            for tip in tips:
                if tip == 4:
                    fingers_open.append(landmarks[tip].x < landmarks[tip - 1].x)
                else:
                    fingers_open.append(landmarks[tip].y < landmarks[tip - 2].y)

            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            index_x = index_tip.x
            middle_y = middle_tip.y

            cv2.putText(img, f"Index X: {index_x:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, f"Middle Y: {middle_y:.2f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            current_time = time.time()
            if fingers_open == [False, False, False, False, False]:
                reset_index_x = index_x
                reset_middle_y = middle_y
                cv2.putText(img, "Reset Captured", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                print("Reset Point Set")

            elif reset_index_x is not None and reset_middle_y is not None:
                if current_time - last_action_time > action_delay:
                    movement_detected = False

                    if all(fingers_open[1:]):  # Full palm open for slide down
                        pyautogui.press('down')
                        print("Slide Down")
                        movement_detected = True

                    elif fingers_open[1] and fingers_open[2]:  # Index + middle up for jump
                        pyautogui.press('up')
                        print("Jump")
                        movement_detected = True

                    elif fingers_open[1] and not fingers_open[2]:  # Only index for left/right
                        if index_x < reset_index_x - 0.05:
                            pyautogui.press('left')
                            print("Move Left")
                            movement_detected = True
                        elif index_x > reset_index_x + 0.05:
                            pyautogui.press('right')
                            print("Move Right")
                            movement_detected = True

                    if movement_detected:
                        last_action_time = current_time

    cv2.imshow("Subway Surfers Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()