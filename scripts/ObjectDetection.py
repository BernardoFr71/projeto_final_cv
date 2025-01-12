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

        load_overlay_images
        overlay_image


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

        return img, results, detected_objects

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
