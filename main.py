import time
import socket
import json
import threading
import os
import cv2
import mediapipe as mp


json_data = {}


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Função para detectar gestos
def detect_gestures(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    gestures = {}

    if results.multi_hand_landmarks:
        for hand_landmarks, hand_type in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            hand_label = hand_type.classification[0].label  # 'Left' ou 'Right'
            fingers_up = count_fingers(hand_landmarks)
            gestures[hand_label] = fingers_up

    return gestures

# Função para contar os dedos levantados
def count_fingers(hand_landmarks):
    fingers = []

    # Verificação do polegar
    if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:  # Para mão direita
        fingers.append(1)
    else:
        fingers.append(0)

    # Verificação dos outros dedos (comparando as posições dos dedos)
    for tip_id, base_id in zip([8, 12, 16, 20], [6, 10, 14, 18]):
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[base_id].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

def main_menu():
    cap = cv2.VideoCapture(0)
    option = 0
    luz = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gestures = detect_gestures(frame)

        # Exibe o menu
        cv2.putText(frame, "1: Ligar Luz", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Identificar o gesto
        for hand, fingers in gestures.items():
            cv2.putText(frame, f"{hand} hand: {fingers} fingers", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            if fingers == 1 and not luz:
                json_data["command"] = "bpy.data.materials[\"Material.007\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = (0.136535, 0.800149, 0.0275523, 1)"  # Altera a cor da esfera
                luz = True
            elif fingers == 2 and luz:
                luz = False
                json_data["command"] ="bpy.data.materials[\"Material.007\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = (0.769648, 0.800157, 0.739828, 1)"  # Altera a cor da esfera

        # Mostra o frame
        cv2.imshow("Camera", frame)

        # Verifica se a tecla 'q' foi pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def start_server():
    host = "127.0.0.1"
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor ouvindo em {host}:{port}...")

    def handle_client(conn, addr):
        print(f"Conexão estabelecida com {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"Conexão encerrada por {addr}")
                    break
                message = json.loads(data.decode("utf-8"))

                if message["action"] == "get":
                    conn.sendall(json.dumps(json_data).encode("utf-8"))
            except Exception as e:
                print(f"Erro com o cliente {addr}: {e}")
                break
        try:
            conn.close()
        except OSError:
            print(f"Erro ao tentar fechar a conexão com {addr}")

    def accept_connections():
        while True:
            try:
                conn, addr = server_socket.accept()
                threading.Thread(
                    target=handle_client, args=(conn, addr), daemon=True
                ).start()
            except OSError:
                print("Erro ao aceitar novas conexões.")
                break

    threading.Thread(target=accept_connections, daemon=True).start()
    main_menu()
    print("Servidor está rodando. Pressione 'Q' para parar.")


if __name__ == "__main__":
    start_server()
