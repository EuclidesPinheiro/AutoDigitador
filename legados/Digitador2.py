import customtkinter as ctk
from tkinter import messagebox
import pyautogui
import time
import threading

# Configuração global do visual moderno
ctk.set_appearance_mode("System")  # Segue o tema do SO (Dark/Light)
ctk.set_default_color_theme("blue") # Tema de cores dos botões

class DigitadorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Digitador Automático PRO")
        self.geometry("650x550")
        self.minsize(500, 450)
        
        # Variáveis de controle
        self.is_typing = False
        
        self.setup_ui()

    def setup_ui(self):
        # --- Painel Superior (Configurações) ---
        config_frame = ctk.CTkFrame(self)
        config_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Delay
        ctk.CTkLabel(config_frame, text="Atraso inicial (seg):").pack(side="left", padx=(10, 5), pady=10)
        self.delay_var = ctk.IntVar(value=5)
        self.delay_menu = ctk.CTkOptionMenu(config_frame, variable=ctk.StringVar(value="5"), 
                                            values=["3", "5", "10"], width=70,
                                            command=lambda v: self.delay_var.set(int(v)))
        self.delay_menu.pack(side="left", padx=5)

        # Velocidade
        ctk.CTkLabel(config_frame, text="Velocidade:").pack(side="left", padx=(20, 5), pady=10)
        self.speed_var = ctk.DoubleVar(value=0.02)
        self.speed_menu = ctk.CTkOptionMenu(config_frame, variable=ctk.StringVar(value="Rápida (0.02s)"),
                                            values=["Muito Rápida (0.00s)", "Rápida (0.02s)", "Lenta (0.05s)", "Segura VM (0.1s)"],
                                            command=self.atualizar_velocidade)
        self.speed_menu.pack(side="left", padx=5)

        # Sempre no topo
        self.top_var = ctk.BooleanVar(value=False)
        self.top_checkbox = ctk.CTkCheckBox(config_frame, text="Sempre no Topo", variable=self.top_var, 
                                            command=self.toggle_topmost)
        self.top_checkbox.pack(side="right", padx=10)

        # --- Área de Texto ---
        self.text_box = ctk.CTkTextbox(self, height=200, font=("Consolas", 14))
        self.text_box.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Binds de atalho
        self.text_box.bind("<Control-a>", self.selecionar_tudo)
        self.text_box.bind("<Control-A>", self.selecionar_tudo)

        # --- Painel Inferior (Ações e Status) ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.btn_limpar = ctk.CTkButton(action_frame, text="Limpar", fg_color="transparent", 
                                        border_width=1, text_color=("gray10", "#DCE4EE"), 
                                        command=self.limpar_texto)
        self.btn_limpar.pack(side="left")

        self.btn_iniciar = ctk.CTkButton(action_frame, text="▶ Iniciar Digitação", 
                                         font=("Arial bold", 14), command=self.iniciar_digitacao)
        self.btn_iniciar.pack(side="right")

        self.status_label = ctk.CTkLabel(self, text="Pronto para uso.", text_color="gray")
        self.status_label.pack(pady=(0, 10))

    # --- Funções Lógicas ---
    def toggle_topmost(self):
        self.attributes("-topmost", self.top_var.get())

    def atualizar_velocidade(self, escolha):
        mapa_velocidade = {
            "Muito Rápida (0.00s)": 0.00,
            "Rápida (0.02s)": 0.02,
            "Lenta (0.05s)": 0.05,
            "Segura VM (0.1s)": 0.1
        }
        self.speed_var.set(mapa_velocidade[escolha])

    def limpar_texto(self):
        self.text_box.delete("1.0", "end")
        self.status_label.configure(text="Texto limpo.", text_color="gray")

    def selecionar_tudo(self, event):
        self.text_box.tag_add("sel", "1.0", "end")
        return "break"

    def iniciar_digitacao(self):
        texto = self.text_box.get("1.0", "end").rstrip()

        if not texto:
            messagebox.showwarning("Aviso", "Informe algum texto antes de iniciar.")
            return
        
        if self.is_typing:
            return

        self.is_typing = True
        self.btn_iniciar.configure(state="disabled")
        self.text_box.configure(state="disabled")

        # Inicia a thread para não travar a interface
        threading.Thread(target=self._processo_digitar, args=(texto,), daemon=True).start()

    def _processo_digitar(self, texto):
        delay = self.delay_var.get()
        velocidade = self.speed_var.get()

        # Contagem regressiva
        for i in range(delay, 0, -1):
            self.status_label.configure(text=f"⏳ Mude para a VM! Iniciando em {i}...", text_color="orange")
            time.sleep(1)

        self.status_label.configure(text="⌨ Digitando...", text_color="#2FA572")
        
        try:
            pyautogui.write(texto, interval=velocidade)
            self.status_label.configure(text="✔ Concluído com sucesso!", text_color="#2FA572")
        except Exception as e:
            self.status_label.configure(text=f"❌ Erro: {e}", text_color="red")
        finally:
            # Restaura a interface
            self.is_typing = False
            self.btn_iniciar.configure(state="normal")
            self.text_box.configure(state="normal")


if __name__ == "__main__":
    app = DigitadorApp()
    app.mainloop()

