import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class ObjectDetection:
    def __init__(self, model_path=None, score_threshold=0.5):
        """
        Inicializa a classe de detecção de objetos usando EfficientDet-Lite0.

        :param model_path: Caminho para o modelo pré-treinado (opcional).
        :param score_threshold: Limiar de confiança para considerar uma detecção válida.
        """
        self.score_threshold = score_threshold

        base_options = python.BaseOptions(model_asset_path='models/efficientdet_lite0.tflite')
        options = vision.ObjectDetectorOptions(base_options=base_options,
                                               score_threshold=0.5)
        detector = vision.ObjectDetector.create_from_options(options)

    def detect(self, frame):
        """
        Executa a detecção de objetos em um frame.

        :param frame: Imagem do OpenCV (BGR).
        :return: Lista de objetos detectados com coordenadas e pontuações.
        """
        # Converte o frame para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Converte para formato compatível com MediaPipe
        image = self.mp_vision.Image(image_format=self.mp_vision.ImageFormat.SRGB, data=rgb_frame)

        # Realiza a detecção
        detection_result = self.detector.detect(image)

        # Extrai os resultados
        detected_objects = []
        for detection in detection_result.detections:
            bbox = detection.bounding_box
            detected_objects.append({
                "class_name": detection.categories[0].category_name,
                "score": detection.categories[0].score,
                "bbox": (bbox.origin_x, bbox.origin_y, bbox.width, bbox.height)
            })

        return detected_objects

    def draw_detections(self, frame, detected_objects):
        """
        Desenha as detecções na imagem.

        :param frame: Imagem do OpenCV (BGR).
        :param detected_objects: Lista de objetos detectados.
        :return: Imagem com as detecções desenhadas.
        """
        for obj in detected_objects:
            x, y, w, h = obj["bbox"]
            class_name = obj["class_name"]
            score = obj["score"]

            # Desenha o retângulo da bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Escreve o nome da classe e a pontuação
            label = f"{class_name}: {score:.2f}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

    def start_camera(self):
        """
        Inicia a câmera para detecção em tempo real.
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Erro ao abrir a câmera.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detected_objects = self.detect(frame)
            annotated_frame = self.draw_detections(frame, detected_objects)

            # Exibe o resultado
            cv2.imshow("Detecção de Objetos", annotated_frame)

            if cv2.waitKey(1) & 0xFF == 27:  # Pressione Esc para sair
                break

        cap.release()
        cv2.destroyAllWindows()