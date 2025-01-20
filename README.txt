Descrição
Este projeto utiliza as bibliotecas OpenCV e MediaPipe para capturar gestos das mãos e permitir o controlo de dispositivos como luz, volume, cortinas e temperatura. O sistema também interage com o Blender para controlar a animação das cortinas através de gestos.

Além disso, é configurado um servidor TCP que permite a clientes consultar o estado atual dos dispositivos em tempo real.

Requisitos
Python 3.x
OpenCV
MediaPipe
JSON
Socket
Blender

Para instalar as dependências necessárias, basta executar o seguinte comando:
pip install opencv-python mediapipe

Como executar
1. Iniciar o servidor
O código configura um servidor TCP a escutar na porta 5000 e no endereço 127.0.0.1. O servidor aceita conexões de clientes, que podem consultar o estado atual dos dispositivos. Para iniciar o servidor, basta executar o script Python.

2. Gestos suportados
A interação com o sistema é realizada através de gestos manuais. Os gestos reconhecidos são os seguintes:

1 dedo levantado: Ligar ou desligar a luz.
2 dedos levantados: Aumentar ou diminuir o volume.
3 dedos levantados: Abrir ou fechar as cortinas.
4 dedos levantados: Ajustar a temperatura.
5 dedos levantados (mão esquerda): Iniciar a animação das cortinas no Blender.
Além disso, o sistema detecta o toque entre o polegar e o indicador, permitindo alternar entre diferentes modos de controlo (luz, volume e cortinas).

3. Controlo dos dispositivos
Com base nos gestos, é possível controlar os seguintes dispositivos:

Luz: Com 1 dedo levantado, é possível ligar ou desligar a luz.
Volume: O volume pode ser ajustado com 2 ou 3 dedos.
Cortinas: As cortinas podem ser abertas ou fechadas com  dedos.
Temperatura: A temperatura é ajustada com 4 dedos.
Animação das cortinas no Blender: Ao levantar 5 dedos com a mão esquerda, a animação das cortinas no Blender é iniciada.
O sistema alterna também entre os modos de controlo quando detecta o toque entre o polegar e o indicador.

4. Terminar a execução
Para terminar a execução do sistema, basta pressionar a tecla Q.

Servidor de Comunicação
O código também implementa um servidor TCP, que escuta na porta 5000. Os clientes podem solicitar o estado atual dos dispositivos conectados. O servidor responde com os dados em formato JSON.

Comandos do servidor
GET: O cliente pode pedir o estado atual dos dispositivos.
Estrutura do Projeto
O código principal contém a lógica para capturar os gestos e controlar os dispositivos.
O servidor TCP implementado aguarda as conexões e responde às solicitações dos clientes.
Como testar o sistema
Execute o código Python.
Use um cliente TCP para se ligar ao servidor na porta 5000.
Envie um comando "GET" para obter o estado atual dos dispositivos controlados.
