# AutoDigitador

Ferramenta desktop para digitação automática de texto em qualquer aplicação do Windows. Útil em sistemas que bloqueiam Ctrl+V mas aceitam entrada pelo teclado.

## Funcionalidades

- **Digitação automática** caractere por caractere em qualquer campo ou aplicação
- **Suporte completo a acentos e caracteres especiais** (`ã`, `é`, `ç`, etc.)
- **Contagem regressiva de 5 segundos** para o usuário posicionar o cursor no destino
- **Barra de progresso em tempo real** acompanhando o avanço da digitação
- **Botão Cancelar** para interromper a qualquer momento
- **Correção de auto-indent** — remove indentação automática inserida pela aplicação destino após quebras de linha
- **Alternância de tema** claro/escuro
- **Atalho Ctrl+A** para selecionar todo o texto na caixa de entrada

## Pré-requisitos

- Python 3.8 ou superior
- Windows 10/11

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/EuclidesPinheiro/AutoDigitador.git
   cd AutoDigitador
   ```

2. Instale as dependências:
   ```bash
   pip install customtkinter keyboard
   ```

## Como usar

1. Execute o programa:
   ```bash
   python digitador.py
   ```

2. Cole ou digite o texto desejado na caixa de entrada

3. Clique em **▶ Iniciar digitação**

4. Você tem **5 segundos** para clicar no campo de destino onde o texto será digitado

5. Aguarde a conclusão — a barra de progresso indica o andamento

> Para interromper a digitação a qualquer momento, clique em **✕ Cancelar**

## Dependências

| Biblioteca | Finalidade |
|---|---|
| `customtkinter` | Interface gráfica moderna |
| `keyboard` | Simulação de teclado com suporte a Unicode |

## Licença

MIT
