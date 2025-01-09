import cv2
import mediapipe as mp

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def detect_gestures(frame):
    # Processa a imagem com MediaPipe
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
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gestures = detect_gestures(frame)

        # Exibe o menu
        cv2.putText(frame, "1: Ligar Luz", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "2: Aumentar Temperatura", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "3: Baixar Persiana", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Identificar o gesto
        for hand, fingers in gestures.items():
            cv2.putText(frame, f"{hand} hand: {fingers} fingers", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            if fingers == 1:
                option = 1  # Ligar Luz
            elif fingers == 2:
                option = 2  # Aumentar Temperatura
            elif fingers == 3:
                option = 3  # Baixar Persiana

        # Mostra o frame
        cv2.imshow("Camera", frame)
        
        # Verifica se a tecla 'q' foi pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return option  # Retorna a opção selecionada

if __name__ == "__main__":
    main_menu()
