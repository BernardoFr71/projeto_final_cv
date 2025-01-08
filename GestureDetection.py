import cv2
import mediapipe as mp
import math
import time


class GestureDetection:
    def __init__(self):
        # Inicializa MediaPipe Hands e Pose
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # Armazenando as posições das mãos para detectar movimento (swipe)
        self.previous_left_hand_position = None
        self.previous_right_hand_position = None
        self.swipe_threshold = 0.05  # Tamanho mínimo de movimento para detectar swipe

        # Controle de texto no canto inferior esquerdo (para swipes)
        self.display_text = ""
        self.display_until = 0  # Timestamp até quando exibir o texto

    def detect_gestures(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processa as landmarks das mãos
        hand_results = self.hands.process(rgb_frame)

        # Processa as landmarks do corpo
        pose_results = self.pose.process(rgb_frame)

        gestures = []

        # Detectar gestos das mãos
        if hand_results.multi_hand_landmarks:
            for hand_landmarks, hand_info in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                handedness = hand_info.classification[0].label  # "Left" ou "Right"
                gesture = self.check_gestures(hand_landmarks, handedness)
                if gesture:
                    gestures.extend(gesture)  # Adiciona múltiplos gestos (como "Mão aberta" e swipe)

        # Detectar gestos do corpo (braços no ar)
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            arm_gestures = self.detect_arm_gestures(pose_results.pose_landmarks)
            gestures.extend(arm_gestures)

        return frame, gestures

    def check_gestures_with_object(self, hand_landmarks, handedness, object_in_right_hand):
        gestures = []

        # Detecta se a mão está aberta ou fechada
        is_open = self.is_hand_open(hand_landmarks)
        if is_open:
            gestures.append(f"Mão {handedness} aberta")
        else:
            gestures.append(f"Mão {handedness} fechada")

        # Ações baseadas no objeto na mão direita
        if handedness.lower() == 'left':  # Apenas gestos da mão esquerda dependem do objeto na mão direita
            if object_in_right_hand == "Garrafa":
                gestures.append("Ação: Abrir garrafa")
            elif object_in_right_hand == "Telemóvel":
                gestures.append("Ação: Aumentar volume")
            else:
                gestures.append("Ação: Nenhuma ação disponível")

        return gestures


    def is_hand_open(self, hand_landmarks):
        # Calcula a média da distância entre o pulso e as pontas dos dedos
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        finger_tips = [
            hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP],
            hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP],
            hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
            hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP],
            hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP],
        ]

        distances = [self.calculate_distance(wrist, tip) for tip in finger_tips]
        avg_distance = sum(distances) / len(distances)

        # Considera a mão aberta se as distâncias forem maiores que um limiar
        return avg_distance > 0.1

    def calculate_distance(self, point1, point2):
        return math.sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2)

    def detect_arm_gestures(self, pose_landmarks):
        gestures = []
        left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

        # Detecta ambos os braços no ar
        if left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y:
            gestures.append("Dois bracos no ar")
        else:
            # Detecta braços no ar individualmente
            if left_wrist.y < left_shoulder.y:
                gestures.append("Braco esquerdo no ar")
            if right_wrist.y < right_shoulder.y:
                gestures.append("Braco direito no ar")

        return gestures

    def detect_swipe(self, hand_landmarks, handedness):
        # Detecta movimento horizontal da mão
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        hand_position = wrist.x

        if handedness == "Right":  # Mão esquerda
            if self.previous_left_hand_position and (hand_position - self.previous_left_hand_position > self.swipe_threshold):
                self.previous_left_hand_position = hand_position
                return "Swipe Left (Mao esquerda)"
            elif self.previous_left_hand_position and (self.previous_left_hand_position - hand_position > self.swipe_threshold):
                self.previous_left_hand_position = hand_position
                return "Swipe Right (Mao esquerda)"
            self.previous_left_hand_position = hand_position

        if handedness == "Left":  # Mão direita
            if self.previous_right_hand_position and (hand_position - self.previous_right_hand_position > self.swipe_threshold):
                self.previous_right_hand_position = hand_position
                return "Swipe Left (Mao direita)"
            elif self.previous_right_hand_position and (self.previous_right_hand_position - hand_position > self.swipe_threshold):
                self.previous_right_hand_position = hand_position
                return "Swipe Right (Mao direita)"
            self.previous_right_hand_position = hand_position

        return None

    def start_camera(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame, gestures = self.detect_gestures(frame)

            # Exibe gestos detectados no canto superior direito
            y_offset = 30
            for gesture in gestures:
                cv2.putText(frame, f"Gesto: {gesture}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_offset += 40

            # Exibe texto no canto inferior esquerdo por 2 segundos
            if time.time() < self.display_until:
                height, _, _ = frame.shape
                cv2.putText(frame, self.display_text, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow("Gesture Detection", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # Pressione 'Esc' para sair
                break

        cap.release()
        cv2.destroyAllWindows()
