import cv2
import mediapipe as mp
import numpy as np


class HandDetection:
    def __init__(self, hand_image_path):
        self.hand_image_path = hand_image_path
        self.hand_image = cv2.imread(self.hand_image_path, cv2.IMREAD_UNCHANGED)  # Lê a imagem com o canal alfa
        if self.hand_image is None:
            raise ValueError(f"Imagem da mão não encontrada: {self.hand_image_path}")

        # Inicializa o MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # Fatores de escala separados para largura (x) e altura (y)
        self.scale_factor_x = 1.5  # Fator de escala para a largura
        self.scale_factor_y = 1  # Fator de escala para a altura

    def replace_hands_with_image(self, frame):
        # Converte a imagem para RGB (necessário para o MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Realiza a detecção das mãos
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                # Calcula as dimensões da mão com base nos pontos de referência
                wrist = landmarks.landmark[0]  # Pulso
                middle_finger_tip = landmarks.landmark[12]  # Ponta do dedo médio

                # Calcula a distância entre o pulso e a ponta do dedo médio em pixels
                hand_width = int(abs(middle_finger_tip.x - wrist.x) * frame.shape[1] * 2 * self.scale_factor_x)
                hand_height = int(abs(middle_finger_tip.y - wrist.y) * frame.shape[0] * 2 * self.scale_factor_y)

                # Determina o centro da mão
                x = int(landmarks.landmark[9].x * frame.shape[1])  # Posição central x
                y = int(landmarks.landmark[9].y * frame.shape[0])  # Posição central y

                # Chama a função para sobrepor a imagem da mão ajustada
                self.overlay_hand_image(frame, x, y, hand_width, hand_height)

        return frame

    def overlay_hand_image(self, frame, x, y, hand_width, hand_height):
        # Ajusta a posição da imagem da mão para não sair dos limites da tela
        x1 = max(0, x - hand_width // 2)
        x2 = min(frame.shape[1], x + hand_width // 2)
        y1 = max(0, y - hand_height // 2)
        y2 = min(frame.shape[0], y + hand_height // 2)

        # Verifica se as dimensões são válidas antes de redimensionar
        roi_width = x2 - x1
        roi_height = y2 - y1
        if roi_width <= 0 or roi_height <= 0:
            return  # Evita redimensionamentos inválidos

        # Redimensiona a imagem da mão para o tamanho da ROI
        hand_resized = cv2.resize(self.hand_image, (roi_width, roi_height))

        # Verifica se a imagem tem um canal alfa (transparência) e faz a sobreposição com transparência
        if hand_resized.shape[2] == 4:  # Se tiver canal alfa
            alpha_channel = hand_resized[:, :, 3] / 255.0
            for c in range(0, 3):  # Sobrepõe os canais RGB
                roi = frame[y1:y2, x1:x2, c]
                frame[y1:y2, x1:x2, c] = (roi * (1 - alpha_channel) + hand_resized[:, :, c] * alpha_channel)
        else:
            # Caso não tenha transparência, sobrepõe diretamente
            frame[y1:y2, x1:x2] = hand_resized

    def start_hand_detection(self):
        # Inicia a captura da webcam
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Substitui as mãos detectadas pela imagem da mão
            frame = self.replace_hands_with_image(frame)

            # Exibe o resultado
            cv2.imshow('Hand Detection', frame)

            if cv2.waitKey(1) & 0xFF == 27:  # Pressione 'Esc' para sair
                break

    def detect_object_in_hand(self, hand_landmarks):
        # Lógica baseada na distância entre o polegar e o indicador
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

        dist_thumb_index = self.calculate_distance(thumb_tip, index_tip)

        if dist_thumb_index < 0.05:
            return "Garrafa"
        elif dist_thumb_index < 0.1:
             return "Telemóvel"
        return "Nenhum objeto"


    cap.release()
    cv2.destroyAllWindows()
