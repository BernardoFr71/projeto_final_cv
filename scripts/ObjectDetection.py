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

        self.target_classes = ["bottle", "cup", "cell phone", "spoon"]
        self.classes_index = self.get_class_index()

    def get_class_index(self):
        # Iterar sobre os índices e nomes das classes no dicionário
        class_index = [idx for idx, name in self.model.names.items() if name in self.target_classes]
        return class_index

    def predict(self, img):
        if self.target_classes:
            #print(f"Modelo carregado com as seguintes classes: {self.model.names}")
            #print(f"Classes indexadas: {self.classes_index}")
            results = self.model.predict(
                img, classes=self.classes_index, conf=self.conf_threshold, verbose=False)

        else:
            results = self.model.predict(img, conf=self.conf_threshold, verbose=False)

        return results

    def predict_and_detect(self, img, classes=[]):
        results = self.predict(img)

        # Lista apenas com os nomes das classes detectadas
        class_names = []

        for result in results:
            for box in result.boxes:
                class_idx = int(box.cls[0])
                class_name = result.names[class_idx]
                class_names.append(class_name)

        return class_names

# Exemplo de uso
if __name__ == "__main__":
    model_path = "C:/Users/tanastacio/Desktop/Universidade/3ano/Computação Visual/PF/projeto_final_cv/models/yolo11s.pt"
    detector = ObjectDetection(model_path=model_path)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduz a resolução para melhorar o desempenho
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error capturing video.")
            break

        detected_objects = detector.predict_and_detect(frame)

        print(detected_objects)  # Exibe os objetos detectados

        if cv2.waitKey(1) & 0xFF == 27:  # Pressione Esc para sair
            break

    cap.release()
    cv2.destroyAllWindows()

