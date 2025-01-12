# main.py ou mediapipe_gesture_recognition.py
import socket

def send_to_blender(command):
    host = '127.0.0.1'  # Endereço local onde o Blender está ouvindo
    port = 5000  # A mesma porta do servidor do Blender

    # Criação do socket para comunicação com o Blender
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Enviar o comando para o Blender
    client.sendall(command.encode())
    client.close()

def handle_gestures(fingers):
    if fingers == 1:
        # Envia comando para mudar a cor da esfera
        send_to_blender("bpy.data.materials['Material.007'].node_tree.nodes['Emission'].inputs[0].default_value = (0.779711, 0.800126, 0.800126, 1)")  # Exemplo de comando

# Monitoramento de gestos (simplificado)
def detect_gestures(frame):
    # ... lógica de MediaPipe para detectar gestos e contar dedos
    fingers = 1  # Apenas como exemplo, você pode obter isso do MediaPipe.
    handle_gestures(fingers)



    
