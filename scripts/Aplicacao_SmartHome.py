import cv2
import json
import socket
import threading

from ObjectDetection import ObjectDetection
from GestureDetection import GestureDetection
from DeviceController import DeviceController


class Aplicacao_SmartHome:
    def __init__(self):
        self.detector = ObjectDetection(model_path="caminho/para/o/modelo.pt")
        self.gesture_detector = GestureDetection()
        self.device_controller = DeviceController()

    def start_camera(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            # Detecção de gestos
            gestures = self.gesture_detector.detect_gestures(frame)

            # Controle de dispositivos
            self.device_controller.control_devices(gestures)

            # Mostra o frame
            cv2.imshow("Camera", frame)

            # Verifica se a tecla 'q' foi pressionada
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    def start_server(self):
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
                        conn.sendall(json.dumps(self.device_controller.json_data).encode("utf-8"))
                except Exception as e:
                    print(f"Erro com o cliente {addr}: {e}")
                    break

        threading.Thread(target=self.start_camera, daemon=True).start()
        threading.Thread(target=lambda: server_socket.accept(), daemon=True).start()


if __name__ == "__main__":
    app = Aplicacao_SmartHome()
    app.start_server()
