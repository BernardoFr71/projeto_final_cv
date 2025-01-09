import socket
import os

def send_to_blender(command):
    host = '127.0.0.1'
    port = 5000

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        client.send(command.encode())  # Envia o comando ao Blender
        print(f"Comando enviado: {command}")
    except Exception as e:
        print(f"Erro ao enviar comando: {e}")
    finally:
        client.close()

# Exemplo de uso com base no gesto detectado
gesture = "move_object"
if gesture == "move_object":
    command = "bpy.data.objects['Cube'].location.x += 1"
    send_to_blender(command)
