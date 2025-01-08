import cv2
import mediapipe as mp
import math

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)

# Função para detectar gestos na mão esquerda
def detect_left_hand_gestures(hand_landmarks, frame):
    h, w, _ = frame.shape
    landmarks = hand_landmarks.landmark

    # Coordenadas normalizadas para pixels
    wrist = landmarks[mp_hands.HandLandmark.WRIST]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]

    gestures = []

    # Gesto: Mão aberta
    if index_tip.y < wrist.y - 0.1:  # Índice acima do pulso
        gestures.append("Mão aberta")

    # Gesto: Espiral com o dedo
    dist_thumb_index = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
    if dist_thumb_index < 0.05:
        gestures.append("Espiral direita")
    elif dist_thumb_index > 0.2:
        gestures.append("Espiral esquerda")

    return gestures

# Função para detectar objetos na mão direita
def detect_right_hand_object(hand_landmarks, frame):
    h, w, _ = frame.shape
    landmarks = hand_landmarks.landmark

    # Coordenadas do polegar e indicador
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # Simular detecção de objetos com base na distância entre polegar e indicador
    dist_thumb_index = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
    if dist_thumb_index < 0.05:
        return "Garrafa"
    elif dist_thumb_index < 0.1:
        return "Telemóvel"
    return "Nenhum objeto"

# Função para executar ações com base no objeto e no gesto
def perform_action(object_right, gesture_left):
    if object_right == "Garrafa":
        if gesture_left == "Mão aberta":
            return "Abrir uma garrafa virtual"
        elif gesture_left == "Espiral direita":
            return "Derramar conteúdo"
        elif gesture_left == "Espiral esquerda":
            return "Fechar a garrafa"
    elif object_right == "Telemóvel":
        if gesture_left == "Mão aberta":
            return "Abrir app no telemóvel"
        elif gesture_left == "Espiral direita":
            return "Aumentar volume"
        elif gesture_left == "Espiral esquerda":
            return "Diminuir volume"
    return "Nenhuma ação"

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: Não foi possível acessar a câmera.")
        return

    print("Pressione 'q' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar o frame. Saindo...")
            break

        # Converter o frame para RGB e processar com MediaPipe Hands
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        gestures_left = []
        object_right = "Nenhum objeto"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Determinar se a mão é esquerda ou direita
                wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
                is_left = wrist_x < 0.5  # Assumindo que a mão esquerda está à esquerda na tela

                if is_left:
                    # Detectar gestos na mão esquerda
                    gestures_left = detect_left_hand_gestures(hand_landmarks, frame)
                else:
                    # Detectar objeto na mão direita
                    object_right = detect_right_hand_object(hand_landmarks, frame)

        # Executar ação com base no gesto e objeto
        if gestures_left:
            for gesture in gestures_left:
                action = perform_action(object_right, gesture)
                cv2.putText(frame, f"Ação: {action}", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Mostrar informações na tela
        cv2.putText(frame, f"Objeto: {object_right}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("Smart Home Control", frame)

        # Encerrar ao pressionar a tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("A encerrar o programa...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
