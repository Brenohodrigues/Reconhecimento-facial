"""
facial_recognition/register_face.py

Responsável por abrir a webcam, detectar um rosto ao vivo e gerar o
"embedding" facial (vetor de 128 números) que será salvo no banco de
dados durante o cadastro do usuário.

Fluxo:
  1. Abre a webcam.
  2. Mostra o vídeo ao vivo com um retângulo ao redor do rosto detectado.
  3. Coleta várias amostras do rosto (para maior robustez) quando o
     usuário pressiona a tecla ESPAÇO.
  4. Calcula a média dos embeddings coletados.
  5. Retorna o vetor final, pronto para ser salvo no banco.

Teclas durante a captura:
  ESPAÇO - capturar uma amostra do rosto atual
  ESC    - cancelar o cadastro facial
"""

import cv2
import face_recognition
import numpy as np

NUM_AMOSTRAS_NECESSARIAS = 5


def capturar_rosto_pela_webcam():
    """
    Abre a webcam e guia o usuário na captura de múltiplas amostras do
    rosto. Retorna o embedding facial médio (lista de floats) ou None
    caso o usuário cancele ou nenhum rosto seja detectado.
    """
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        raise RuntimeError(
            "Não foi possível acessar a webcam. Verifique se ela está "
            "conectada e se nenhum outro programa está utilizando-a."
        )

    amostras_coletadas = []

    janela = "Cadastro Facial - ESPACO para capturar | ESC para cancelar"

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                raise RuntimeError("Falha ao capturar imagem da webcam.")

            # Reduz o frame para acelerar a detecção, depois escala de volta.
            frame_pequeno = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_pequeno = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

            localizacoes = face_recognition.face_locations(rgb_pequeno)

            # Desenha o retângulo do rosto detectado (se houver) na tela.
            for (top, right, bottom, left) in localizacoes:
                top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            texto_status = (
                f"Amostras capturadas: {len(amostras_coletadas)}/"
                f"{NUM_AMOSTRAS_NECESSARIAS}"
            )
            cv2.putText(
                frame, texto_status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
            )

            if len(localizacoes) == 0:
                cv2.putText(
                    frame, "Nenhum rosto detectado", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
                )
            elif len(localizacoes) > 1:
                cv2.putText(
                    frame, "Apenas 1 rosto por vez, por favor", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
                )

            cv2.imshow(janela, frame)
            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 27:  # ESC
                return None

            if tecla == 32:  # ESPACO
                if len(localizacoes) == 1:
                    rgb_completo = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    codificacoes = face_recognition.face_encodings(
                        rgb_completo, [
                            tuple(
                                v for v in (
                                    localizacoes[0][0] * 4,
                                    localizacoes[0][1] * 4,
                                    localizacoes[0][2] * 4,
                                    localizacoes[0][3] * 4,
                                )
                            )
                        ]
                    )
                    if codificacoes:
                        amostras_coletadas.append(codificacoes[0])

                if len(amostras_coletadas) >= NUM_AMOSTRAS_NECESSARIAS:
                    break

    finally:
        video_capture.release()
        cv2.destroyAllWindows()

    if not amostras_coletadas:
        return None

    # Calcula a média das amostras para gerar um embedding mais estável.
    embedding_medio = np.mean(amostras_coletadas, axis=0)
    return embedding_medio.tolist()
