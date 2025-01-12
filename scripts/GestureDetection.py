import cv2
import mediapipe as mp


class GestureDetection:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

    def detect_gestures(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        gestures = {}

        if results.multi_hand_landmarks:
            for hand_landmarks, hand_type in zip(results.multi_hand_landmarks, results.multi_handedness):
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                hand_label = hand_type.classification[0].label  # 'Left' ou 'Right'
                fingers_up = self.count_fingers(hand_landmarks)
                gestures[hand_label] = {"fingers_up": fingers_up, "hand_landmarks": hand_landmarks}

        return gestures

    def count_fingers(self, hand_landmarks):
        fingers = []

        palm_facing_camera = hand_landmarks.landmark[0].z < hand_landmarks.landmark[9].z

        # Verificação do polegar
        if palm_facing_camera:
            if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                fingers.append(1)
            else:
                fingers.append(0)

        # Verificação dos outros dedos
        for tip_id, base_id in zip([8, 12, 16, 20], [6, 10, 14, 18]):
            if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[base_id].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return sum(fingers)

    def detect_thumb_index_touch(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]  # Posição do polegar
        index_tip = hand_landmarks.landmark[8]  # Posição do dedo indicador

        distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
        return distance < 0.05
