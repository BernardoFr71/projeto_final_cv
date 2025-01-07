import cv2
import mediapipe as mp

# Estados dos dispositivos virtuais
light_on = False
temperature = 22  # Temperatura inicial

def detect_gestures(frame, hands):
    # Converter o frame para RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Processar o frame com o MediaPipe Hands
    results = hands.process(rgb_frame)

    # Lista de gestos detectados
    gestures = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Coletar coordenadas de landmarks específicas
            wrist_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].y
            index_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y
            middle_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP].y

            # Verificar gesto: palmas acima da cabeça
            if wrist_y < 0.2:
                gestures.append("Palmas acima da cabeça")

            # Verificar gesto: swipe up/down com o dedo
            if index_tip_y < middle_tip_y:
                gestures.append("Swipe up")
            elif index_tip_y > middle_tip_y:
                gestures.append("Swipe down")

    return gestures

def handle_gestures(gestures):
    global light_on, temperature
    for gesture in gestures:
        if gesture == "Palmas acima da cabeça":
            light_on = not light_on  # Alternar estado da luz
        elif gesture == "Swipe up":
            temperature += 1  # Aumentar temperatura
        elif gesture == "Swipe down":
            temperature -= 1  # Diminuir temperatura

def main():
    # Inicializar MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

    # Captura de vídeo
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detectar gestos
        gestures = detect_gestures(frame, hands)

        # Processar gestos detectados
        handle_gestures(gestures)

        # Exibir os gestos detectados e estados dos dispositivos no frame
        for i, gesture in enumerate(gestures):
            cv2.putText(
                frame, gesture, (10, 50 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )

        # Mostrar estados dos dispositivos
        cv2.putText(
            frame, f"Luz: {'Acesa' if light_on else 'Apagada'}", (10, 150),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
        )
        cv2.putText(
            frame, f"Temperatura: {temperature}C", (10, 200),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
        )

        # Mostrar a janela de vídeo
        cv2.imshow("Smart Home Control", frame)

        # Encerrar ao pressionar a tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
