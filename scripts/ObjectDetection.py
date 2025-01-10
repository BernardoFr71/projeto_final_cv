import cv2
import os
import numpy as np
import time
from threading import Thread
from ultralytics import YOLO


class ObjectDetection:
    def __init__(
        self,
        model_path=None,
        conf_threshold=0.5,
        rectangle_thickness=2,
        text_thickness=1,
        image_folder="objetos",
        movement_threshold=1,
    ):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.rectangle_thickness = rectangle_thickness
        self.text_thickness = text_thickness
        self.image_folder = image_folder
        self.movement_threshold = movement_threshold  # Limiar de movimento
        self.overlay_images = self.load_overlay_images()
        self.previous_positions = {}  # Armazena posições anteriores dos objetos por classe

    def load_overlay_images(self):
        overlay_images = {}
        for filename in os.listdir(self.image_folder):
            class_name, ext = os.path.splitext(filename)
            if ext.lower() in [".png", ".jpg", ".jpeg"]:
                img_path = os.path.join(self.image_folder, filename)
                overlay_images[class_name] = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        return overlay_images

    def overlay_image(self, background, overlay, x, y, width, height):
        if overlay.shape[2] == 4:  # Imagem RGBA
            alpha = overlay[:, :, 3]
            coords = cv2.findNonZero(alpha)  # Localiza os pixels com transparência > 0
            if coords is not None:
                x_min, y_min, w, h = cv2.boundingRect(coords)  # Calcula o retângulo delimitador
                overlay_cropped = overlay[y_min:y_min+h, x_min:x_min+w]  # Recorta a região de interesse
            else:
                return  # Se não houver pixels visíveis, nada é sobreposto
        else:
            overlay_cropped = overlay  # Sem canal alfa, usa a imagem inteira

        # Redimensiona a área recortada para o tamanho do objeto detectado.
        overlay_resized = cv2.resize(overlay_cropped, (width, height))

        # Aplica a imagem sobreposta no background
        if overlay_resized.shape[2] == 4:  # Com canal alfa
            alpha = overlay_resized[:, :, 3] / 255.0  # Normaliza o canal alfa (0-1)
            for c in range(0, 3):  # Itera pelos canais RGB
                background[y:y+height, x:x+width, c] = (
                    alpha * overlay_resized[:, :, c] +  # Combina com a imagem original
                    (1 - alpha) * background[y:y+height, x:x+width, c]
                )
        else:  # Sem canal alfa
            background[y:y+height, x:x+width] = overlay_resized

    def is_moving(self, class_name, position):
        #Verifica se a posição do objeto mudou em relação ao quadro anterior.
        if class_name not in self.previous_positions:
            self.previous_positions[class_name] = position
            return False

        x1_prev, y1_prev, x2_prev, y2_prev = self.previous_positions[class_name]
        x1, y1, x2, y2 = position

        # Calcula o deslocamento da posição
        movement = np.sqrt((x1 - x1_prev)**2 + (y1 - y1_prev)**2)
        self.previous_positions[class_name] = position

        # Retorna True se o movimento for maior que o limiar
        return movement > self.movement_threshold

    def predict_and_detect(self, img, classes=[]):
        results = self.predict(img, classes)

        # Lista de objetos detectados com informações
        detected_objects = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                area = (x2 - x1) * (y2 - y1)
                class_idx = int(box.cls[0])
                class_name = result.names[class_idx]

                # Ignora objetos da classe "person"
                if class_name == "person":
                    continue

                detected_objects.append({
                    "class_name": class_name,
                    "position": (x1, y1, x2, y2),
                    "area": area,
                })

        # Filtra apenas os objetos em movimento
        moving_objects = [
            obj for obj in detected_objects
            if self.is_moving(obj["class_name"], obj["position"])
        ]

        # Determina o maior objeto em movimento
        largest_moving_object = max(
            moving_objects, key=lambda obj: obj["area"], default=None
        )

        # Marca todos os objetos (exceto "person")
        for obj in detected_objects:
            x1, y1, x2, y2 = obj["position"]
            class_name = obj["class_name"]

            cv2.rectangle(
                img, (x1, y1), (x2, y2), (255, 0, 0), self.rectangle_thickness
            )
            cv2.putText(
                img,
                f"{class_name}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_PLAIN,
                1,
                (255, 0, 0),
                self.text_thickness,
            )

        # Faz overlay no maior objeto em movimento
        if largest_moving_object:
            x1, y1, x2, y2 = largest_moving_object["position"]
            class_name = largest_moving_object["class_name"]

            if class_name in self.overlay_images:
                width, height = x2 - x1, y2 - y1
                self.overlay_image(
                    img, self.overlay_images[class_name], x1, y1, width, height
                )

        return img, results

    def predict(self, img, classes=None):
        if classes is None:
            classes = []
        if classes:
            results = self.model.predict(
                img, classes=classes, conf=self.conf_threshold, verbose=False
            )
        else:
            results = self.model.predict(img, conf=self.conf_threshold, verbose=False)
        return results

    def start_camera_detection(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduz a resolução para melhorar o desempenho
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while True:
            start_time = time.time()  # Início da contagem para FPS
            ret, frame = cap.read()
            if not ret:
                print("Error capturing video.")
                break

            result_img, _ = self.predict_and_detect(frame)

            # Calcula e exibe o FPS
            fps = int(1 / (time.time() - start_time))
            cv2.putText(
                result_img,
                f"FPS: {fps}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Object Detection", result_img)

            if cv2.waitKey(1) & 0xFF == 27:  # Pressione Esc para sair
                break

        cap.release()
        cv2.destroyAllWindows()
