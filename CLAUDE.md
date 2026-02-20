# CLAUDE.md — AutoDigitador

## Visão geral do projeto

Aplicação desktop Windows para digitação automática de texto em qualquer campo ou sistema que bloqueie Ctrl+V mas aceite entrada via teclado. Escrita em Python com interface gráfica moderna.

## Estrutura do projeto

```
DIGITADOR/
└── digitador.py   # arquivo único com toda a lógica e interface
```

## Stack e bibliotecas

| Biblioteca | Versão mínima | Uso |
|---|---|---|
| `customtkinter` | 5.x | Interface gráfica moderna (tema claro/escuro, widgets arredondados) |
| `keyboard` | 0.13.x | Simulação de teclado via Win32 SendInput — suporta Unicode completo |
| `threading` | stdlib | Thread separada para digitação, evita travar a UI |
| `tkinter` | stdlib | Base do customtkinter; `messagebox` usado para alertas |

## Arquitetura

O programa é um arquivo único sem classes. Segue o padrão:

1. **Configuração global** — constantes `DELAY` e `INTERVALO`, evento de cancelamento `cancelar_evento`
2. **Funções de lógica** — `iniciar_digitacao()`, `cancelar_digitacao()`, `atualizar_status()`
3. **Funções auxiliares da UI** — `selecionar_tudo()`, `alternar_tema()`
4. **Construção da interface** — widgets definidos no escopo global, `root.mainloop()` no fim

### Fluxo da digitação

```
iniciar_digitacao()
  ├── Desabilita CTkTextbox (state="disabled")
  └── Thread: digitar()
        ├── Fase 1: contagem regressiva (0 → 100% da progress bar)
        └── Fase 2: loop caractere por caractere
              ├── '\n' → send('enter') + limpa auto-indent (home + shift+end + delete)
              ├── '\t' → send('tab')
              └── outros → keyboard.write(char)
        └── finally: reabilita CTkTextbox (state="normal")
```

### Controle de cancelamento

Usa `threading.Event` (`cancelar_evento`). A thread verifica `cancelar_evento.is_set()` a cada iteração do loop de digitação e no início de cada segundo do countdown.

### Comportamento da janela durante digitação

O `CTkTextbox` é desabilitado (`state="disabled"`) enquanto a digitação está em andamento. Isso impede que o campo de texto capture eventos de teclado acidentalmente caso o usuário abra a janela do programa para acompanhar o progresso. A janela se comporta normalmente (ícone visível, pode ser aberta/minimizada); se ganhar foco do teclado, a digitação no destino é pausada até o usuário retornar o foco à aplicação destino.

## Decisões técnicas importantes

- **`keyboard` em vez de `pyautogui.write()`** — pyautogui não suporta Unicode no Windows; keyboard usa `KEYEVENTF_UNICODE` via SendInput
- **`keyboard` em vez de `pyperclip + Ctrl+V`** — a abordagem de clipboard apresentou instabilidade (apenas 1 caractere colado em alguns contextos)
- **Limpeza de auto-indent após `\n`** — aplicações destino com auto-indent (IDEs, editores) inserem espaços/tabs após Enter; a sequência `home → shift+end → delete` remove isso antes de continuar a digitação
- **Thread daemon** — garante que o processo encerra junto com a janela principal mesmo se a digitação estiver em andamento
- **`WS_EX_NOACTIVATE` foi descartado** — tentativa anterior de impedir roubo de foco via ctypes causou sumiço do ícone da janela na barra de tarefas; solução adotada foi apenas desabilitar o CTkTextbox durante a digitação

## Convenções do código

- Português para nomes de variáveis, funções, comentários e mensagens ao usuário
- Sem classes — estrutura procedural simples dado o escopo da ferramenta
- Constantes no topo do arquivo em `UPPER_CASE`
- Atualizações de UI feitas diretamente da thread secundária (funciona no Windows com tkinter, mas não é thread-safe oficialmente)

## Como executar

```bash
python digitador.py
# ou sem console:
pythonw digitador.py
```

## Dependências — instalação

```bash
pip install customtkinter keyboard
```

## O que evitar ao modificar

- Não substituir `keyboard` por `pyautogui.write()` — não suporta acentos
- Não remover a limpeza de auto-indent após `\n` — causa indentação acumulada
- Não chamar `root.destroy()` ou `root.quit()` de dentro da thread de digitação
- Não usar `time.sleep()` na thread principal — trava a UI
- Não aplicar `WS_EX_NOACTIVATE` via ctypes — causa sumiço do ícone na barra de tarefas do Windows

## Repositório

- GitHub: https://github.com/EuclidesPinheiro/AutoDigitador.git
- Branch principal: `main`
