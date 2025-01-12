import cv2
import os
import numpy as np
import time
from threading import Thread
from ultralytics import YOLO


class ObjectDetection:
    def __init__(
        self,
        model_path = None,
        conf_threshold = 0.5,
    ):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

        self.target_classes = ["remote", "cup", "cell phone", "wallet"]
        self.classes_index = self.get_class_index()


    def get_class_index(self):
        # Obter o mapeamento de nomes das classes para índices
        class_index = []
        for name, idx in self.model.names.items():
            if name in self.target_classes:
                class_index.append(idx)
        return class_index

    def predict(self, img):
        if self.target_classes:
            results = self.model.predict(
                img, classes=self.classes_index, conf=self.conf_threshold, verbose=False)

        else:
            results = self.model.predict(img, conf=self.conf_threshold, verbose=False)
        return results

    def predict_and_detect(self, img, classes=[]):
        results = self.predict(img)

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

        return detected_objects



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
