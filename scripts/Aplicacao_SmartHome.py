import cv2
import json
import socket
import threading

from ObjectDetection import ObjectDetection
from GestureDetection import GestureDetection
from DeviceController import DeviceController

#variaveis globais
json_data = {}
luz = False
volume = 5
cortinas_abertas = False
temperatura = 22  # Temperatura inicial

object_control_mapping = {
    "remote": "TV",
    "cup": "Lâmpada",
    "cell phone": "Cortinas",
    "book": "Ar condicionado"
}


class Aplicacao_SmartHome:
    def __init__(self):
        self.detector = ObjectDetection(model_path="../models/yolo11s.pt")
        self.gesture_detector = GestureDetection()
        self.device_controller = DeviceController()
        self.self.y_offset = 30
        self.detected_classes = []
        
    def ui_menu(self, frame):
        # Exibe o menu no frame
        cv2.rectangle(frame, (10, 10), (400, 200), (0, 0, 0), -1)  # Fundo preto para o menu
        cv2.putText(frame, "Controle de Dispositivos", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "1: Ligar/Desligar Luz", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "2: Ajustar Volume (+/-)", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "3: Abrir/Fechar Cortinas", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "4: Ajustar Temperatura", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame
        
    def status_atuais(self, frame):
        # Exibe status atual
        cv2.putText(frame, f"Luz: {'ON' if luz else 'OFF'}", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2)
        cv2.putText(frame, f"Volume: {volume}", (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Cortinas: {'Abertas' if cortinas_abertas else 'Fechadas'}", (10, 280),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Temperatura: {temperatura} C", (10, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2)
        
        return frame
    
    def objetos_detetados(self, frame):
        # Exibe objetos detectados
        self.y_offset += 40
        cv2.putText(frame, "Objetos detectados:", (frame.shape[1] - 300, self.y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2)
        for detected in detected_classes:
            self.y_offset += 30
            cv2.putText(frame, detected.capitalize(), (frame.shape[1] - 300, self.y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)
            
        return frame
    
    def correspondencia(self, frame):
        # Exibe correspondência no canto superior direito
        cv2.putText(frame, "Objeto - Controlo ativado:", (frame.shape[1] - 300, self.y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 2)
        for obj, control in object_control_mapping.items():
            self.y_offset += 30
            cv2.putText(frame, f"{obj.capitalize()} - {control}", (frame.shape[1] - 300, self.y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    def start_camera(self):
        global last_touch_time
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)  # Espelha a imagem horizontalmente
            gestures = GestureDetection(frame)

            # Detecta objetos no frame
            detected_objects = ObjectDetection.predict_and_detect(frame)
            self.detected_classes = [obj["class_name"] for obj in detected_objects]

            frame = self.ui_menu(frame)

            frame = self.status_atuais(frame)

            self.correspondencia(frame)

            self.objetos_detetados(frame)

            # Lógica para ativar controles com base nos objetos detectados
            if "remote" in self.detected_classes:
                # Controle da TV
                pass  # Adicione a lógica específica
            if "cup" in self.detected_classes:
                # Controle da Lâmpada
                pass  # Adicione a lógica específica
            if "cell phone" in self.detected_classes:
                # Controle das Cortinas
                pass  # Adicione a lógica específica
            if "book" in self.detected_classes:
                # Controle do Ar Condicionado
                pass  # Adicione a lógica específica

            # Mostra o frame
            cv2.imshow("Camera", frame)

            # Verifica se a tecla 'q' foi pressionada
            if cv2.waitKey(1) & 0xFF == ord('q'):
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
                        conn.sendall(json.dumps(json_data).encode("utf-8"))
                except Exception as e:
                    print(f"Erro com o cliente {addr}: {e}")
                    break
            try:
                conn.close()
            except OSError:
                print(f"Erro ao tentar fechar a conexão com {addr}")

        def accept_connections():
            while True:
                try:
                    conn, addr = server_socket.accept()
                    threading.Thread(
                        target=handle_client, args=(conn, addr), daemon=True
                    ).start()
                except OSError:
                    print("Erro ao aceitar novas conexões.")
                    break

        threading.Thread(target=accept_connections, daemon=True).start()
        app.start_camera()
        print("Servidor está prontíssimo. Pressiona 'Q' para parar.")


if __name__ == "__main__":
    app = Aplicacao_SmartHome()
    app.start_server()
