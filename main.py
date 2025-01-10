import cv2
from ObjectDetection import ObjectDetection

# Configuração inicial
model_path = "/models/efficientdet_lite0.tflite"  # Substituir pelo caminho real do modelo YOLO
image_folder = "objetos"  # Pasta com imagens para overlay

def object_detection():
    # Inicializar o módulo de deteção de objetos
    detector = ObjectDetection(
        model_path=model_path,
        image_folder=image_folder,
    )

    # Captura de vídeo
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar o vídeo.")
            break

        # Deteção e overlay de objetos
        result_frame, _ = detector.predict_and_detect(frame)

        # Exibir o frame processado
        cv2.imshow("Object Detection", result_frame)

        # Sair ao pressionar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    while True:
        print("Menu Principal")
        print("1. Controle de Smart Home por Gestos")
        print("2. Deteção de Objetos")
        print("3. Sair")
        
        choice = input("Escolha uma opção: ")
        
        if choice == "1":
            import SmartHomeGestures
            SmartHomeGestures.main()  # Executar o main do módulo
        elif choice == "2":
            detector = ObjectDetection(model_path="models/yolo11s.pt")
            detector.start_camera_detection()
        elif choice == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")
