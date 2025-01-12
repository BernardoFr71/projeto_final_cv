from GestureDetection import GestureDetection
import time

class DeviceController:
    def __init__(self):
        self.luz = False
        self.volume = 5
        self.cortinas_abertas = False
        self.temperatura = 22
        self.last_touch_time = 0
        self.touch_count = 0
        self.json_data = {}
        self.object_control_mapping = {
            "remote": "TV",
            "cup": "Lâmpada",
            "cell phone": "Cortinas",
            "book": "Ar condicionado",
        }

    def control_devices(self, gestures):
        for hand, hand_info in gestures.items():
            fingers = hand_info["fingers_up"]
            hand_landmarks = hand_info["hand_landmarks"]
            current_time = time.time()

            # Detecta toque entre polegar e indicador
            if GestureDetection().detect_thumb_index_touch(hand_landmarks) and (current_time - self.last_touch_time > 1.0):
                self.last_touch_time = current_time
                self.touch_count += 1
                if self.touch_count % 2 == 0:
                    self.luz = True
                    self.json_data["command"] = (
                        "bpy.data.materials[\"led\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = (0.8, 0.005, 0.01, 1); "
                        "bpy.data.materials[\"screen\"].node_tree.nodes[\"Mix Shader\"].inputs[0].default_value = 0.85"
                    )
                else:
                    self.luz = False
                    self.json_data["command"] = (
                        "bpy.data.materials[\"led\"].node_tree.nodes[\"Emission\"].inputs[0].default_value = (0.77, 0.8, 0.77, 1); "
                        "bpy.data.materials[\"screen\"].node_tree.nodes[\"Mix Shader\"].inputs[0].default_value = 0.14"
                    )

            # Controles específicos
            if fingers == 1:
                self.luz = not self.luz
            elif fingers == 2:
                self.volume = min(self.volume + 1, 10)
            elif fingers == 3:
                self.cortinas_abertas = not self.cortinas_abertas
            elif fingers == 4:
                self.temperatura += 1
            elif fingers == 5:
                self.temperatura -= 1