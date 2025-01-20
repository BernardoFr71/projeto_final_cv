import cv2
import mediapipe as mp
import json
import socket
import threading
import time
<<<<<<< HEAD

from ObjectDetection import ObjectDetection
=======
>>>>>>> 61575d5636416aa8b0f67fe0d698b0987556bf96

# Configurações globais
json_data = {}

# Configuração do MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

<<<<<<< HEAD
=======
#Instancia do detetor de objetos
#detector = ObjectDetection(model_path="caminho/para/o/modelo.pt")

>>>>>>> 61575d5636416aa8b0f67fe0d698b0987556bf96
# Variável para controle do tempo do toque
last_touch_time = 0

#Lista para mostrar objeto a ser controlado
object_control_mapping = {
    "remote": "TV",
    "cup": "Lâmpada",
    "cell phone": "Cortinas",
    "book": "Ar condicionado"
}


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
            gestures[hand_label] = {"fingers_up": fingers_up, "hand_landmarks": hand_landmarks}

    return gestures

# Função para contar os dedos levantados
def count_fingers(hand_landmarks):
    fingers = []

    # Determinar a orientação da palma:
    palm_facing_camera = hand_landmarks.landmark[0].z < hand_landmarks.landmark[9].z

    # Verificação do polegar
    if palm_facing_camera:
        if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:  # Para mão direita
            fingers.append(1)
        else:
            fingers.append(0)
    else:
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:  # Para mão direita
            fingers.append(1)
        else:
            fingers.append(0)

    # Verificação dos outros dedos
    for tip_id, base_id in zip([8, 12, 16, 20], [6, 10, 14, 18]):
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[base_id].y:  # Dedo levantado
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

# Função para detectar o toque entre o polegar e o indicador
def detect_thumb_index_touch(hand_landmarks):
    global last_touch_time  # Declarando a variável global aqui
    thumb_tip = hand_landmarks.landmark[4]  # Posição do polegar
    index_tip = hand_landmarks.landmark[8]  # Posição do dedo indicador

    # Calcular a distância entre o polegar e o indicador
    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5

    # Se a distância entre os dois for muito pequena, consideramos que eles estão tocando
    if distance < 0.05:  # Ajuste esse valor para sua necessidade
        return True
    return False

detector = ObjectDetection()

# Função principal do menu
def main_menu():
    global last_touch_time  # Declarando a variável global aqui
    cap = cv2.VideoCapture(0)
    luz = False
    volume = 5
    cortinas_abertas = False
    temperatura = 22  # Temperatura inicial
    touch_count = 0  # Contador de toques

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Espelha a imagem horizontalmente
        gestures = detect_gestures(frame)
        detected_objects = detector.predict_and_detect(frame)
        print(detected_objects)

        # Exibe o menu no frame
        cv2.rectangle(frame, (10, 10), (400, 200), (0, 0, 0), -1)  # Fundo preto para o menu
        cv2.putText(frame, "Controle de Dispositivos", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "1: Ligar/Desligar Luz", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "2: Ajustar Volume (+/-)", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "3: Abrir/Fechar Cortinas", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "4: Ajustar Temperatura", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Exibe status atual
        cv2.putText(frame, f"TV: {'ON' if luz else 'OFF'}", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Volume: {volume}", (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Cortinas: {'Abertas' if cortinas_abertas else 'Fechadas'}", (10, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Temperatura: {temperatura} C", (10, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Identificar o gesto
        for hand, hand_info in gestures.items():
            fingers = hand_info["fingers_up"]
            hand_landmarks = hand_info["hand_landmarks"]

            #Configuração TV - LIGAR E DESLIGAR
            if "remote" in detected_objects:
                current_time = time.time()
                if detect_thumb_index_touch(hand_landmarks) and (current_time - last_touch_time > 1.0):
                    last_touch_time = current_time
                    if touch_count % 2 == 0:
                        json_data["command"] = (
                            "bpy.data.materials[\"led\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = "
                            "(0.800071, 0.00497789, 0.0100464, 1); "  # led tv ligada
                            "bpy.data.materials[\"screen\"].node_tree.nodes[\"Mix Shader\"].inputs[0].default_value = 0.856396"  # TV ligada
                        )
                        luz = True
                    else:
                        json_data["command"] = (
                            "bpy.data.materials[\"led\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = "
                            "(0.771298, 0.800079, 0.778437, 1); "  # led tv desligada
                            "bpy.data.materials[\"screen\"].node_tree.nodes[\"Mix Shader\"].inputs[0].default_value = 0.14211"  # TV desligada
                        )
                        luz = False
                    touch_count += 1

            # Exibe número de dedos levantados
            cv2.putText(frame, f"{hand} HAND: {fingers} dedo/s", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # 1 dedo levantado: Controla a luz
            if "cup" in detected_objects:
                if fingers == 1 and not luz:
                    json_data["command"] = "bpy.data.materials[\"Material.007\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = (0.136535, 0.800149, 0.0275523, 1)"
                    luz = True
                elif fingers == 2 and luz:
                    luz = False
                    json_data["command"] = "bpy.data.materials[\"Material.007\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = (0.769648, 0.800157, 0.739828, 1)"

            # 2 dedos levantados: Ajusta o volume
            elif fingers == 2:
                volume = min(volume + 1, 10)  # Aumenta o volume
            elif fingers == 3:
                volume = max(volume - 1, 0)  # Diminui o volume

            # 3 dedos levantados: Controla cortinas
            elif fingers == 3:
                cortinas_abertas = not cortinas_abertas

            # 4 dedos levantados: Ajusta a temperatura
            elif fingers == 4:
                temperatura += 1

            # 5 dedos com a mão esquerda e inicia a animacao no blender (cortina)
            if "cell phone" in detected_objects:
                if hand=="Left" and fingers == 5:
                    json_data["command"] = "bpy.ops.screen.animation_play()"
                else:
                    json_data['command'] = ""

            # Configuração para o funcionamento de ligar e desligar a luz
            if "bottle" in detected_objects:
                if detect_thumb_index_touch(hand_landmarks) and (current_time - last_touch_time > 1.0):
                    last_touch_time = current_time
                    touch_count += 1
                    if hand=="Right" and touch_count % 3 == 0:  # Alterna entre Luz, Volume, Cortinas
                        luz = True
                        json_data["command"] = "bpy.data.materials[\"Material.007\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = (0.136535, 0.800149, 0.0275523, 1)"
                    elif hand=="Right" and touch_count % 3 == 1:  # Alterna volume
                        luz = False
                        cortinas_abertas = False
                        volume = 10
                        json_data["command"] = "bpy.data.materials[\"Material.007\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = (0.769648, 0.800157, 0.739828, 1)"
                    else:  # Alterna cortinas
                        luz = False

        # Mostra o frame
        cv2.imshow("Camera", frame)

        # Verifica se a tecla 'q' foi pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Função do servidor --
def start_server():
    host = "127.0.0.1"
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor em escuta em {host}:{port}...")

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
    print("Servidor está prontíssimo. Pressiona 'Q' para parar.")

