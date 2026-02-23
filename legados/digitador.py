import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading

DELAY = 5  # segundos

def iniciar_digitacao():
    texto = text_box.get("1.0", tk.END).rstrip()

    if not texto:
        messagebox.showwarning("Aviso", "Informe algum texto antes de iniciar.")
        return

    def digitar():
        for i in range(DELAY, 0, -1):
            status_label.config(text=f"Iniciando em {i} segundos...")
            time.sleep(1)

        status_label.config(text="Digitando...")
        pyautogui.write(texto, interval=0.02)
        status_label.config(text="Concluído ✔")

    threading.Thread(target=digitar, daemon=True).start()


# --- Função para Ctrl + A ---
def selecionar_tudo(event):
    text_box.tag_add("sel", "1.0", "end")
    return "break"  # impede comportamento padrão estranho


# --- Interface ---
root = tk.Tk()
root.title("Digitador Automático")
root.geometry("600x400")

label = tk.Label(root, text="Texto a ser digitado:")
label.pack(anchor="w", padx=10, pady=5)

text_box = tk.Text(root, height=12)
text_box.pack(fill="both", expand=True, padx=10)

# Bind do Ctrl + A
text_box.bind("<Control-a>", selecionar_tudo)
text_box.bind("<Control-A>", selecionar_tudo)

botao = tk.Button(root, text="Iniciar digitação", command=iniciar_digitacao)
botao.pack(pady=10)

status_label = tk.Label(root, text="Aguardando...")
status_label.pack()

root.mainloop()
