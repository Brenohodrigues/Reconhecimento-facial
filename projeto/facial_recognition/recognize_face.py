"""
facial_recognition/recognize_face.py

Responsável pelo reconhecimento facial em tempo real:
  1. Carrega todos os embeddings faciais cadastrados no banco de dados.
  2. Abre a webcam e processa o vídeo continuamente.
  3. Para cada rosto detectado no frame, compara com os embeddings
     conhecidos.
  4. Se houver correspondência, exibe o nome do usuário na tela.
  5. Se não houver correspondência, exibe "Não cadastrado".

Tecla ESC encerra o reconhecimento.
"""

import cv2
import face_recognition
import numpy as np

from database.connection import get_session
from database.models import User

# Quanto MENOR, mais rigorosa é a comparação (0.6 é o padrão recomendado
# pela biblioteca face_recognition).
LIMIAR_TOLERANCIA = 0.6


def carregar_rostos_conhecidos():
    """
    Busca todos os usuários no banco e retorna duas listas paralelas:
    os embeddings faciais e os nomes correspondentes.
    """
    session = get_session()
    try:
        usuarios = session.query(User).all()
        embeddings = [np.array(u.get_face_encoding()) for u in usuarios]
        nomes = [u.full_name for u in usuarios]
        return embeddings, nomes
    finally:
        session.close()


def iniciar_reconhecimento_em_tempo_real():
    """
    Abre a webcam e roda o loop de reconhecimento facial contínuo.
    Deve ser chamada a partir da interface gráfica (main.py).
    """
    embeddings_conhecidos, nomes_conhecidos = carregar_rostos_conhecidos()

    if not embeddings_conhecidos:
        raise RuntimeError(
            "Nenhum usuário cadastrado ainda. Cadastre pelo menos um "
            "usuário antes de iniciar o reconhecimento."
        )

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        raise RuntimeError(
            "Não foi possível acessar a webcam. Verifique se ela está "
            "conectada e se nenhum outro programa está utilizando-a."
        )

    janela = "Reconhecimento Facial - ESC para sair"

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                raise RuntimeError("Falha ao capturar imagem da webcam.")

            frame_pequeno = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_pequeno = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

            localizacoes = face_recognition.face_locations(rgb_pequeno)
            codificacoes = face_recognition.face_encodings(rgb_pequeno, localizacoes)

            for (top, right, bottom, left), encoding_atual in zip(
                localizacoes, codificacoes
            ):
                top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

                distancias = face_recognition.face_distance(
                    embeddings_conhecidos, encoding_atual
                )
                indice_mais_proximo = int(np.argmin(distancias)) if len(distancias) else None

                if (
                    indice_mais_proximo is not None
                    and distancias[indice_mais_proximo] <= LIMIAR_TOLERANCIA
                ):
                    nome = nomes_conhecidos[indice_mais_proximo]
                    cor = (0, 255, 0)  # verde = reconhecido
                else:
                    nome = "Nao cadastrado"
                    cor = (0, 0, 255)  # vermelho = desconhecido

                cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)
                cv2.rectangle(
                    frame, (left, bottom - 25), (right, bottom), cor, cv2.FILLED
                )
                cv2.putText(
                    frame, nome, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1,
                )

            cv2.imshow(janela, frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                break

    finally:
        video_capture.release()
        cv2.destroyAllWindows()
