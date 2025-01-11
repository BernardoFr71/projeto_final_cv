import cv2
import mediapipe as mp
import json
import socket
import threading
import time

class GestureControl:
    def __init__(self):
        # Configurações globais
        self.json_data = {}
        self.last_touch_time = 0
        self.touch_count = 0

        # Configurações do MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

        # Variáveis do sistema
        self.luz = False
        self.volume = 5
        self.cortinas_abertas = False
        self.temperatura = 22

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
            fingers.append(int(hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x))
        else:
            fingers.append(int(hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x))

        # Verificação dos outros dedos
        for tip_id, base_id in zip([8, 12, 16, 20], [6, 10, 14, 18]):
            fingers.append(int(hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[base_id].y))

        return sum(fingers)

    def detect_thumb_index_touch(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
        return distance < 0.05

    def main_menu(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            gestures = self.detect_gestures(frame)

            # Exibe o menu
            self.display_menu(frame)

            for hand, hand_info in gestures.items():
                fingers = hand_info["fingers_up"]
                hand_landmarks = hand_info["hand_landmarks"]
                current_time = time.time()

                if self.detect_thumb_index_touch(hand_landmarks) and (current_time - self.last_touch_time > 1.0):
                    self.last_touch_time = current_time
                    self.toggle_light()

                # Realiza ações baseadas no número de dedos levantados
                self.perform_action(fingers)

                # Exibe o número de dedos levantados
                cv2.putText(frame, f"{hand} HAND: {fingers} dedo/s", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            cv2.imshow("Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def display_menu(self, frame):
        cv2.rectangle(frame, (10, 10), (400, 200), (0, 0, 0), -1)
        cv2.putText(frame, "Controle de Dispositivos", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "1: Ligar/Desligar Luz", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "2: Ajustar Volume (+/-)", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "3: Abrir/Fechar Cortinas", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "4: Ajustar Temperatura", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Luz: {'ON' if self.luz else 'OFF'}", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Volume: {self.volume}", (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Cortinas: {'Abertas' if self.cortinas_abertas else 'Fechadas'}", (10, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Temperatura: {self.temperatura} C", (10, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def toggle_light(self):
        self.touch_count += 1
        if self.touch_count % 2 == 0:
            self.json_data["command"] = "Luz Ligada"
            self.luz = True
        else:
            self.json_data["command"] = "Luz Desligada"
            self.luz = False

    def perform_action(self, fingers):
        if fingers == 1 and not self.luz:
            self.toggle_light()
        elif fingers == 2:
            self.volume = min(self.volume + 1, 10)
        elif fingers == 3:
            self.volume = max(self.volume - 1, 0)
        elif fingers == 4:
            self.cortinas_abertas = not self.cortinas_abertas
        elif fingers == 5:
            self.temperatura += 1

    def start_server(self):
        host = "127.0.0.1"
        port = 5000
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)

        def handle_client(conn, addr):
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = json.loads(data.decode("utf-8"))

                    if message["action"] == "get":
                        conn.sendall(json.dumps(self.json_data).encode("utf-8"))
                except Exception as e:
                    break

        def accept_connections():
            while True:
                conn, addr = server_socket.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

        threading.Thread(target=accept_connections, daemon=True).start()
        self.main_menu()

if __name__ == "__main__":
    controller = GestureControl()
    controller.start_server()