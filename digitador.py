import customtkinter as ctk
from tkinter import messagebox
import keyboard
import time
import threading

# --- Configuração do tema ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DELAY = 5         # segundos de espera antes de digitar
INTERVALO = 0.03  # intervalo entre caracteres em segundos

cancelar_evento = threading.Event()


def formatar_tempo(segundos):
    s = int(segundos)
    m = s // 60
    s = s % 60
    return f"{m:02d}:{s:02d}"


def fmt_num(n):
    """Formata número com separador de milhar em PT-BR."""
    return f"{n:,}".replace(",", ".")


def resetar_metricas():
    for lbl in (lbl_chars_val, lbl_linhas_val, lbl_palavras_val,
                lbl_decorrido_val, lbl_restante_val, lbl_velocidade_val):
        lbl.configure(text="—")


def iniciar_digitacao():
    texto = text_box.get("1.0", "end").rstrip()

    if not texto:
        messagebox.showwarning("Aviso", "Informe algum texto antes de iniciar.")
        return

    cancelar_evento.clear()
    botao_iniciar.configure(state="disabled")
    botao_cancelar.configure(state="normal")
    text_box.configure(state="disabled")
    progress_bar.set(0)
    resetar_metricas()
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

            total          = len(texto)
            total_linhas   = texto.count('\n') + 1
            total_palavras = len(texto.split())

            linhas_digitadas  = 1
            palavras_digitadas = 0
            em_palavra        = False
            start_time        = time.time()
            ultima_atualizacao = 0.0

            intervalo = 1.0 / max(float(slider_velocidade.get()), 1)

            for idx, char in enumerate(texto):
                if cancelar_evento.is_set():
                    atualizar_status("cancelado")
                    return

                # --- Envia tecla ---
                if char == '\n':
                    linhas_digitadas += 1
                    if em_palavra:
                        palavras_digitadas += 1
                        em_palavra = False
                    keyboard.send('enter')
                    time.sleep(0.05)
                    keyboard.send('home')
                    keyboard.send('shift+end')
                    keyboard.send('delete')
                elif char in (' ', '\t'):
                    if em_palavra:
                        palavras_digitadas += 1
                        em_palavra = False
                    keyboard.send('tab') if char == '\t' else keyboard.write(char)
                else:
                    em_palavra = True
                    keyboard.write(char)

                time.sleep(intervalo)
                progress_bar.set((idx + 1) / total)

                # --- Atualiza métricas a cada 100ms ---
                agora = time.time()
                if agora - ultima_atualizacao >= 0.1:
                    elapsed   = agora - start_time
                    remaining = (total - idx - 1) * intervalo
                    speed     = (idx + 1) / elapsed * 60 if elapsed > 0.1 else 0

                    lbl_chars_val.configure(text=f"{fmt_num(idx + 1)} / {fmt_num(total)}")
                    lbl_linhas_val.configure(text=f"{linhas_digitadas} / {total_linhas}")
                    lbl_palavras_val.configure(text=f"{palavras_digitadas} / {total_palavras}")
                    lbl_decorrido_val.configure(text=formatar_tempo(elapsed))
                    lbl_restante_val.configure(text=f"~{formatar_tempo(remaining)}")
                    lbl_velocidade_val.configure(text=f"{fmt_num(int(speed))}/min")
                    ultima_atualizacao = agora

            # Conta última palavra se texto não terminar com espaço
            if em_palavra:
                palavras_digitadas += 1

            elapsed = time.time() - start_time
            lbl_chars_val.configure(text=f"{fmt_num(total)} / {fmt_num(total)}")
            lbl_linhas_val.configure(text=f"{total_linhas} / {total_linhas}")
            lbl_palavras_val.configure(text=f"{total_palavras} / {total_palavras}")
            lbl_decorrido_val.configure(text=formatar_tempo(elapsed))
            lbl_restante_val.configure(text="00:00")
            lbl_velocidade_val.configure(text=f"{fmt_num(int(total / elapsed * 60))}/min")

            progress_bar.set(1.0)
            atualizar_status("concluido")

        except Exception as e:
            status_label.configure(text=f"Erro: {str(e)}")
            atualizar_status("erro")

        finally:
            text_box.configure(state="normal")
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


def on_texto_alterado(event=None):
    """Atualiza prévia de Chars, Linhas e Palavras conforme o texto é editado."""
    texto = text_box.get("1.0", "end").rstrip()
    if texto:
        lbl_chars_val.configure(text=fmt_num(len(texto)))
        lbl_linhas_val.configure(text=str(texto.count('\n') + 1))
        lbl_palavras_val.configure(text=str(len(texto.split())))
    else:
        for lbl in (lbl_chars_val, lbl_linhas_val, lbl_palavras_val):
            lbl.configure(text="—")
    text_box._textbox.edit_modified(False)  # reseta flag para próximo evento


def limpar_texto():
    text_box.delete("1.0", "end")
    progress_bar.set(0)
    resetar_metricas()
    atualizar_status("aguardando")


def on_slider_velocidade(valor):
    chars_s = int(float(valor))
    lbl_slider_vel.configure(text=f"{chars_s} chars/s")


def alternar_tema():
    modo_atual = ctk.get_appearance_mode()
    novo_modo = "light" if modo_atual == "Dark" else "dark"
    ctk.set_appearance_mode(novo_modo)
    if novo_modo == "dark":
        tema_btn.configure(text="☀ Tema Claro", text_color="white")
    else:
        tema_btn.configure(text="☾ Tema Escuro", text_color="#1a1a1a")


# ============================================================
# --- Interface ---
# ============================================================
root = ctk.CTk()
root.title("Digitador Automático")
root.geometry("640x630")
root.resizable(False, False)

# --- Cabeçalho ---
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

# --- Caixa de texto ---
ctk.CTkLabel(
    root,
    text="Texto a ser digitado:",
    font=ctk.CTkFont(size=13),
    anchor="w"
).pack(fill="x", padx=20, pady=(15, 4))

text_box = ctk.CTkTextbox(
    root,
    height=180,
    font=ctk.CTkFont(size=13),
    corner_radius=10,
    border_width=1,
)
text_box.pack(fill="both", expand=True, padx=20)
text_box.bind("<Control-a>", selecionar_tudo)
text_box.bind("<Control-A>", selecionar_tudo)
text_box._textbox.bind("<<Modified>>", on_texto_alterado)

# --- Botões ---
frame_botoes = ctk.CTkFrame(root, fg_color="transparent")
frame_botoes.pack(pady=12)

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

botao_limpar = ctk.CTkButton(
    frame_botoes,
    text="🗑  Limpar",
    width=120,
    height=40,
    font=ctk.CTkFont(size=14),
    corner_radius=10,
    fg_color="#555555",
    hover_color="#333333",
    command=limpar_texto
)
botao_limpar.pack(side="left", padx=8)

# --- Slider de velocidade ---
frame_slider = ctk.CTkFrame(root, fg_color="transparent")
frame_slider.pack(fill="x", padx=24, pady=(0, 8))

ctk.CTkLabel(frame_slider, text="Velocidade:",
             font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))

ctk.CTkLabel(frame_slider, text="Lento",
             font=ctk.CTkFont(size=11), text_color="#888888").pack(side="left")

slider_velocidade = ctk.CTkSlider(frame_slider, from_=5, to=200,
                                   number_of_steps=195, width=340,
                                   command=on_slider_velocidade)
slider_velocidade.set(33)
slider_velocidade.pack(side="left", padx=6)

ctk.CTkLabel(frame_slider, text="Rápido",
             font=ctk.CTkFont(size=11), text_color="#888888").pack(side="left")

lbl_slider_vel = ctk.CTkLabel(frame_slider, text="33 chars/s",
                               font=ctk.CTkFont(size=12, weight="bold"), width=90)
lbl_slider_vel.pack(side="left", padx=(10, 0))

# --- Painel de métricas ---
metrics_frame = ctk.CTkFrame(root, corner_radius=10)
metrics_frame.pack(fill="x", padx=20, pady=(0, 10))

def criar_metrica(parent, col, titulo_txt):
    cell = ctk.CTkFrame(parent, fg_color="transparent")
    cell.grid(row=0, column=col, padx=16, pady=8, sticky="nsew")
    parent.columnconfigure(col, weight=1)
    ctk.CTkLabel(cell, text=titulo_txt,
                 font=ctk.CTkFont(size=11), text_color="#888888").pack()
    val = ctk.CTkLabel(cell, text="—",
                       font=ctk.CTkFont(size=13, weight="bold"))
    val.pack()
    return val

lbl_chars_val     = criar_metrica(metrics_frame, 0, "Caracteres")
lbl_linhas_val    = criar_metrica(metrics_frame, 1, "Linhas")
lbl_palavras_val  = criar_metrica(metrics_frame, 2, "Palavras")
lbl_decorrido_val = criar_metrica(metrics_frame, 3, "Decorrido")
lbl_restante_val  = criar_metrica(metrics_frame, 4, "Restante")
lbl_velocidade_val= criar_metrica(metrics_frame, 5, "Velocidade")

# --- Barra de progresso ---
progress_bar = ctk.CTkProgressBar(root, width=600, height=10, corner_radius=5)
progress_bar.pack(padx=20, pady=(0, 8))
progress_bar.set(0)

# --- Status ---
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
