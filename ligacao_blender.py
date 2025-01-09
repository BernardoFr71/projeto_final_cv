import socket

def send_to_blender(command):
    host = '127.0.0.1'
    port = 5000

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send(command.encode())  # Envia o comando ao Blender
    client.close()

# Exemplo de uso com base no gesto detectado
gesture = "move_object"
if gesture == "move_object":
    send_to_blender("bpy.data.objects['Cube'].location.x += 1")
