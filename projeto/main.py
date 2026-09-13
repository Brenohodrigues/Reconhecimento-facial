"""
main.py

Ponto de entrada da aplicação. Contém a interface gráfica (Tkinter) que
permite:
  - Cadastrar um novo usuário (nome, e-mail, senha + cadastro facial).
  - Iniciar o reconhecimento facial em tempo real.

Este arquivo NÃO contém regra de negócio nem acesso direto ao banco —
ele apenas coleta os dados da tela e delega o trabalho para os módulos
de services/, authentication/ e facial_recognition/.
"""

import threading
import tkinter as tk
from tkinter import messagebox

from database.connection import init_db
from services.user_service import (
    cadastrar_usuario,
    EmailInvalidoError,
    EmailJaCadastradoError,
    DadosInvalidosError,
    contar_usuarios,
)
from facial_recognition.register_face import capturar_rosto_pela_webcam
from facial_recognition.recognize_face import iniciar_reconhecimento_em_tempo_real


class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Cadastro e Reconhecimento Facial")
        self.geometry("420x420")
        self.resizable(False, False)

        self.face_encoding_capturado = None  # guarda o embedding facial temporário

        self._montar_interface()
        self._atualizar_contador_usuarios()

    # ------------------------------------------------------------------
    # Montagem da interface
    # ------------------------------------------------------------------
    def _montar_interface(self):
        padding = {"padx": 10, "pady": 6}

        tk.Label(self, text="Cadastro de Usuário", font=("Arial", 14, "bold")).pack(pady=(15, 5))

        frame_form = tk.Frame(self)
        frame_form.pack(**padding)

        tk.Label(frame_form, text="Nome completo:").grid(row=0, column=0, sticky="w")
        self.entry_nome = tk.Entry(frame_form, width=35)
        self.entry_nome.grid(row=0, column=1, pady=4)

        tk.Label(frame_form, text="E-mail:").grid(row=1, column=0, sticky="w")
        self.entry_email = tk.Entry(frame_form, width=35)
        self.entry_email.grid(row=1, column=1, pady=4)

        tk.Label(frame_form, text="Senha:").grid(row=2, column=0, sticky="w")
        self.entry_senha = tk.Entry(frame_form, width=35, show="*")
        self.entry_senha.grid(row=2, column=1, pady=4)

        self.label_status_facial = tk.Label(
            self, text="Rosto ainda não capturado", fg="red"
        )
        self.label_status_facial.pack(pady=(10, 0))

        tk.Button(
            self, text="1) Iniciar Cadastro Facial (webcam)",
            width=35, command=self._on_capturar_rosto,
        ).pack(pady=6)

        tk.Button(
            self, text="2) Finalizar Cadastro do Usuário",
            width=35, command=self._on_cadastrar_usuario,
        ).pack(pady=6)

        tk.Frame(self, height=2, bd=1, relief="sunken").pack(fill="x", padx=10, pady=12)

        tk.Label(self, text="Reconhecimento Facial", font=("Arial", 14, "bold")).pack()

        tk.Button(
            self, text="Iniciar Reconhecimento em Tempo Real",
            width=35, command=self._on_iniciar_reconhecimento,
        ).pack(pady=10)

        self.label_contador = tk.Label(self, text="", fg="gray")
        self.label_contador.pack(pady=(5, 0))

    def _atualizar_contador_usuarios(self):
        total = contar_usuarios()
        self.label_contador.config(text=f"Usuários cadastrados: {total}")

    # ------------------------------------------------------------------
    # Ações dos botões
    # ------------------------------------------------------------------
    def _on_capturar_rosto(self):
        """
        Abre a webcam (em uma thread separada para não travar a
        interface gráfica) e realiza a captura do rosto.
        """
        messagebox.showinfo(
            "Cadastro Facial",
            "Uma janela da webcam será aberta.\n\n"
            "Posicione seu rosto e pressione ESPAÇO 5 vezes para capturar "
            "amostras (olhe levemente para lados diferentes a cada "
            "captura). Pressione ESC para cancelar.",
        )

        def tarefa():
            try:
                encoding = capturar_rosto_pela_webcam()
                self.after(0, lambda: self._finalizar_captura(encoding))
            except Exception as erro:
                self.after(0, lambda: messagebox.showerror("Erro na webcam", str(erro)))

        threading.Thread(target=tarefa, daemon=True).start()

    def _finalizar_captura(self, encoding):
        if encoding is None:
            self.label_status_facial.config(text="Cadastro facial cancelado", fg="red")
            self.face_encoding_capturado = None
        else:
            self.face_encoding_capturado = encoding
            self.label_status_facial.config(text="Rosto capturado com sucesso!", fg="green")

    def _on_cadastrar_usuario(self):
        nome = self.entry_nome.get()
        email = self.entry_email.get()
        senha = self.entry_senha.get()

        try:
            cadastrar_usuario(nome, email, senha, self.face_encoding_capturado)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            self._limpar_formulario()
            self._atualizar_contador_usuarios()
        except (EmailInvalidoError, EmailJaCadastradoError, DadosInvalidosError) as erro:
            messagebox.showerror("Erro no cadastro", str(erro))
        except ValueError as erro:
            # Erro vindo do hash_password (ex.: senha curta)
            messagebox.showerror("Erro no cadastro", str(erro))
        except Exception as erro:
            messagebox.showerror("Erro inesperado", f"Ocorreu um erro: {erro}")

    def _limpar_formulario(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_senha.delete(0, tk.END)
        self.face_encoding_capturado = None
        self.label_status_facial.config(text="Rosto ainda não capturado", fg="red")

    def _on_iniciar_reconhecimento(self):
        def tarefa():
            try:
                iniciar_reconhecimento_em_tempo_real()
            except Exception as erro:
                self.after(0, lambda: messagebox.showerror("Erro no reconhecimento", str(erro)))

        threading.Thread(target=tarefa, daemon=True).start()


def main():
    init_db()  # cria as tabelas do banco, caso ainda não existam
    app = Aplicacao()
    app.mainloop()


if __name__ == "__main__":
    main()
