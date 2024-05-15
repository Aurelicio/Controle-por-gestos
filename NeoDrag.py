import cv2
import pyautogui
import time

# Inicializa a câmera
cap = cv2.VideoCapture(0)

width = int(cap.get(3))  # Largura da imagem (índice 3)
height = int(cap.get(4))  # Altura da imagem (índice 4)

# Define uma área de detecção de gestos
detect_area = 20

# Inicialize uma variável de tempo
last_gesture_time = 0 

# Define o tempo mínimo de espera entre os gestos (em segundos)
gestures_cooldown = 1.7

arraste_ativo = False
arrast_persist = 0
last_gesture_right_click = False

# Inicializa as coordenadas do ponto inicial e final para o arraste
start_point = None
end_point = None

# Flag para indicar se o arraste está ativo
dragging = False

pyautogui.FAILSAFE = False

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Espelha o quadro horizontalmente

    current_time = time.time()
    if current_time - last_gesture_time >= gestures_cooldown:
        # Define uma região de interesse (ROI) para a detecção de gestos
        roi = frame[120:360, 160:480]

        # Converte a ROI para escala de cinza
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Suaviza a imagem para reduzir o ruído
        gray_roi = cv2.GaussianBlur(gray_roi, (15, 15), 0)

        # Detecta as bordas na imagem
        edges = cv2.Canny(gray_roi, 30, 150)

        # Encontra os contornos na ROI
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filtra os contornos com uma área mínima
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > detect_area: 
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Calcula o centro do retângulo
                cx = x + w // 2
                cy = y + h // 2

                # Se o centro estiver à esquerda, simule um clique esquerdo
                if cx < 150 and not dragging:
                    cv2.putText(frame, "Clique Esquerdo", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    pyautogui.rightClick()
                    last_gesture_right_click = False

                # Se o centro estiver à direita, simule um clique direito
                elif cx > 150 and not dragging:
                    cv2.putText(frame, "Clique Direito", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    pyautogui.click()
                    last_gesture_right_click = True
                    dragging = False 
                    arrast_persist = 0
                    arraste_ativo = 0

                # Atualiza as coordenadas do ponto inicial para arrastar
                start_point = (cx, cy)

        # Após a detecção bem-sucedida de um gesto
        last_gesture_time = current_time

    else:

        if last_gesture_right_click:
            arrast_persist = current_time - last_gesture_time
        else:
            arrast_persist = 0

        if arrast_persist > 1.0:
            arraste_ativo = True
            dragging = True

        roi = frame[120:360, 160:480]

        # Converte a ROI para escala de cinza
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Suaviza a imagem para reduzir o ruído
        gray_roi = cv2.GaussianBlur(gray_roi, (15, 15), 0)

        # Detecta as bordas na imagem
        edges = cv2.Canny(gray_roi, 30, 150)

        # Encontra os contornos na ROI
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filtra os contornos com uma área mínima
        for contour in contours:

            area = cv2.contourArea(contour)

            if area > detect_area: 
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Calcula o centro do retângulo
                cx = x + w // 2
                cy = y + h // 2

                # if cx > 150 and arraste_ativo:
                #     dragging = True

                if cx > 150 and dragging and arraste_ativo:
                    # Se o arraste está ativo, atualiza as coordenadas do ponto final
                    end_point = pyautogui.position()

                    # Simula o arraste do mouse
                    pyautogui.drag(100, 0, duration=0.2)

                    last_gesture_time = current_time 
                    
            else:
                dragging = False
                arrast_persist = 0
                arraste_ativo = False
                
             

    resolution_text = f"Resolucao da camera: {width}x{height}"

    # Imprime no frame a resolução da imagem capturada pela câmera
    cv2.putText(frame, resolution_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (165,42,42), 2)

    cv2.imshow("ROI", roi)
    cv2.imshow("Edges", edges)
    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
