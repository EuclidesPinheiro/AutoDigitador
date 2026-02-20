import customtkinter as ctk
from tkinter import messagebox
import keyboard
import time
import threading

# --- Configuração do tema ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DELAY = 5       # segundos de espera antes de digitar
INTERVALO = 0.03  # intervalo entre caracteres em segundos

cancelar_evento = threading.Event()


def iniciar_digitacao():
    texto = text_box.get("1.0", "end").rstrip()

    if not texto:
        messagebox.showwarning("Aviso", "Informe algum texto antes de iniciar.")
        return

    cancelar_evento.clear()
    botao_iniciar.configure(state="disabled")
    botao_cancelar.configure(state="normal")
    progress_bar.set(0)
    atualizar_status("aguardando")

    def digitar():
        try:
            # --- Fase 1: contagem regressiva ---
            for i in range(DELAY, 0, -1):
                if cancelar_evento.is_set():
                    atualizar_status("cancelado")
                    return
                status_label.configure(text=f"Iniciando em {i} segundo{'s' if i > 1 else ''}...")
                progress_bar.set((DELAY - i) / DELAY)
                time.sleep(1)

            if cancelar_evento.is_set():
                atualizar_status("cancelado")
                return

            # --- Fase 2: digitação caractere por caractere ---
            progress_bar.set(0)
            status_label.configure(text="Digitando...")

            total = len(texto)
            for idx, char in enumerate(texto):
                if cancelar_evento.is_set():
                    atualizar_status("cancelado")
                    return

                if char == '\n':
                    keyboard.send('enter')
                    time.sleep(0.05)        # aguarda o auto-indent da aplicação destino
                    keyboard.send('home')   # vai ao início da linha
                    keyboard.send('shift+end')  # seleciona o auto-indent
                    keyboard.send('delete')     # apaga
                elif char == '\t':
                    keyboard.send('tab')
                else:
                    keyboard.write(char)

                time.sleep(INTERVALO)
                progress_bar.set((idx + 1) / total)

            progress_bar.set(1.0)
            atualizar_status("concluido")

        except Exception as e:
            status_label.configure(text=f"Erro: {str(e)}")
            atualizar_status("erro")

        finally:
            botao_iniciar.configure(state="normal")
            botao_cancelar.configure(state="disabled")

    threading.Thread(target=digitar, daemon=True).start()


def cancelar_digitacao():
    cancelar_evento.set()
    status_label.configure(text="Cancelando...")


def atualizar_status(estado):
    cores = {
        "aguardando": ("#A0A0A0", "Aguardando..."),
        "concluido":  ("#4CAF50", "Concluído ✔"),
        "cancelado":  ("#FF9800", "Cancelado."),
        "erro":       ("#F44336", "Erro."),
    }
    cor, texto = cores.get(estado, ("#A0A0A0", "Aguardando..."))
    status_label.configure(text=texto, text_color=cor)
    status_dot.configure(text_color=cor, text="●")


def selecionar_tudo(event):
    text_box.tag_add("sel", "1.0", "end")
    return "break"


def alternar_tema():
    modo_atual = ctk.get_appearance_mode()
    novo_modo = "light" if modo_atual == "Dark" else "dark"
    ctk.set_appearance_mode(novo_modo)
    tema_btn.configure(text="☀ Tema Claro" if novo_modo == "dark" else "☾ Tema Escuro")


# --- Interface ---
root = ctk.CTk()
root.title("Digitador Automático")
root.geometry("640x500")
root.resizable(False, False)

# Cabeçalho
header_frame = ctk.CTkFrame(root, fg_color="transparent")
header_frame.pack(fill="x", padx=20, pady=(20, 0))

titulo = ctk.CTkLabel(
    header_frame,
    text="Digitador Automático",
    font=ctk.CTkFont(size=22, weight="bold")
)
titulo.pack(side="left")

tema_btn = ctk.CTkButton(
    header_frame,
    text="☀ Tema Claro",
    width=120,
    height=28,
    font=ctk.CTkFont(size=12),
    fg_color="transparent",
    border_width=1,
    command=alternar_tema
)
tema_btn.pack(side="right")

# Label da caixa de texto
ctk.CTkLabel(
    root,
    text="Texto a ser digitado:",
    font=ctk.CTkFont(size=13),
    anchor="w"
).pack(fill="x", padx=20, pady=(15, 4))

# Caixa de texto
text_box = ctk.CTkTextbox(
    root,
    height=200,
    font=ctk.CTkFont(size=13),
    corner_radius=10,
    border_width=1,
)
text_box.pack(fill="both", expand=True, padx=20)
text_box.bind("<Control-a>", selecionar_tudo)
text_box.bind("<Control-A>", selecionar_tudo)

# Botões
frame_botoes = ctk.CTkFrame(root, fg_color="transparent")
frame_botoes.pack(pady=15)

botao_iniciar = ctk.CTkButton(
    frame_botoes,
    text="▶  Iniciar digitação",
    width=180,
    height=40,
    font=ctk.CTkFont(size=14, weight="bold"),
    corner_radius=10,
    command=iniciar_digitacao
)
botao_iniciar.pack(side="left", padx=8)

botao_cancelar = ctk.CTkButton(
    frame_botoes,
    text="✕  Cancelar",
    width=130,
    height=40,
    font=ctk.CTkFont(size=14),
    corner_radius=10,
    fg_color="#B22222",
    hover_color="#8B0000",
    state="disabled",
    command=cancelar_digitacao
)
botao_cancelar.pack(side="left", padx=8)

# Barra de progresso
progress_bar = ctk.CTkProgressBar(root, width=600, height=10, corner_radius=5)
progress_bar.pack(padx=20, pady=(0, 8))
progress_bar.set(0)

# Rodapé de status
status_frame = ctk.CTkFrame(root, fg_color="transparent")
status_frame.pack()

status_dot = ctk.CTkLabel(
    status_frame,
    text="●",
    font=ctk.CTkFont(size=14),
    text_color="#A0A0A0"
)
status_dot.pack(side="left", padx=(0, 5))

status_label = ctk.CTkLabel(
    status_frame,
    text="Aguardando...",
    font=ctk.CTkFont(size=13),
    text_color="#A0A0A0"
)
status_label.pack(side="left")

root.mainloop()
