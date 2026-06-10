# Breaking the RPA Black Box: Real-Time Tracking, Live Metrics, and Persistent Robots

---

## 🌍 Language / Idioma
* [Português (#-português)](#-português)
* [English (#-english)](#-english)

---

## 🇵🇹 Português

Esta solução quebra a "caixa negra" tradicional das automações (RPA), transformando robôs isolados em processos persistentes, totalmente monitorizados em tempo real através de métricas vivas e dashboards interativos.

### Estrutura do Projeto & Stack
O projeto é desenvolvido em Python e contentorizado com Docker para garantir a persistência e isolamento do robô:
* **Streamlit (`app.py`)**: Interface web interativa com atualização automática (`streamlit-autorefresh`) para exibir métricas, tabelas (`pandas`/`openpyxl`) e o estado do robô em direto.
* **Automação & RPA (`main.py`)**: O núcleo do robô, utilizando **Playwright** para automação web de alta performance.
* **Inteligência Visual / OCR**: Integração com **Pytesseract** e **Pillow (PIL)** para processamento de imagens e reconhecimento ótico de caracteres (OCR).
* **Autenticação (`gerar_auth.py`)**: Script utilitário para gravação de fluxos de login (Atualmente em *Standby*).
* **Persistência (`data/`)**: Pasta local mapeada para armazenar logs, relatórios Excel ou o histórico do robô.

### Arquitetura de Autenticação e Decisões de Engenharia
* **O papel do `gerar_auth.py`**: Este script foi originalmente concebido para gravar todos os passos necessários para efetuar um login e navegar até um local específico do site-alvo, armazenando o estado da sessão.
* **Estratégia Atual (Standby)**: Por opção técnica, a utilização deste fluxo automatizado de sessões gravadas foi colocada em *standby*. Muitos sites modernos limitam fortemente o reaproveitamento de sessões devido a tokens dinâmicos, expiração rápida de cookies e mudanças estruturais dinâmicas nas páginas.
* **Abordagem no `main.py`**: Para garantir a resiliência e estabilidade do robô, optou-se por construir, diretamente no `main.py`, um caminho de atuação dedicado e adaptável para cada caso específico com o qual o robô tenha de interagir. Isto permite uma tomada de decisão inteligente em tempo real durante a execução.

### Pré-requisitos
* [Docker](https://docker.com) e [Docker Compose](https://docker.com) instalados (Recomendado para execução).
* Python 3.10+ instalado (Caso pretenda correr localmente sem Docker).

---

## 🔧 Como Executar o Projeto

### 1. Clonar o Repositório
Abra o seu terminal e descarregue o projeto do seu GitHub:
```bash
git clone https://github.com/Lavbella/rpa.git
cd rpa
```

### 2. Garantir os Requirements (Execução Local / Desenvolvimento)
Se optar por correr ou testar o projeto localmente na sua máquina (fora do Docker), siga estes passos:

1. **Criar e ativar o ambiente virtual (venv):**
   ```bash
   python -m venv venv

   # Ativar no Windows (Prompt de Comando):
   venv\Scripts\activate
   # Ativar no Windows (PowerShell):
   .\venv\Scripts\activate
   # Ativar no Linux/macOS:
   source venv/bin/activate
   ```

2. **Instalar os pacotes Python:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Garantir os binários do Playwright:**
   ```bash
   playwright install chromium
   ```

4. **Nota sobre o Pytesseract (OCR):**
   O `pytesseract` necessita do motor do Tesseract instalado no seu sistema operativo.
   * *Ubuntu/Linux:* `sudo apt install tesseract-ocr`
   * *Windows:* Descarregue o instalador oficial do Tesseract e adicione-o ao PATH do sistema.

---

### 🐳 Execução Automatizada com Docker (Recomendado)
Ao utilizar o Docker, não precisa de se preocupar com os passos do ambiente virtual ou instalações locais, pois o contentor já traz o Tesseract e os browsers configurados de fábrica.

1. **Subir os Contentores:**
   ```bash
   docker compose up -d --build
   ```

2. **Aceder ao Dashboard:**
   Abra o navegador em: [http://localhost:8501](http://localhost:8501)

---

## 🇬🇧 English

This solution breaks the traditional "black box" of robotic process automations (RPA) by turning isolated bots into persistent processes, fully tracked in real-time through live metrics and interactive dashboards.

### Project Structure & Stack
The project is built with Python and containerized using Docker to ensure bot persistence and environment isolation:
* **Streamlit (`app.py`)**: Interactive web dashboard utilizing `streamlit-autorefresh` to expose real-time tracking metrics, dataframes (`pandas`/`openpyxl`), and bot status.
* **Automation & RPA (`main.py`)**: The core robot logic powered by **Playwright** for high-performance browser automation.
* **Visual Intelligence / OCR**: Integrated with **Pytesseract** and **Pillow (PIL)** for image processing and Optical Character Recognition (OCR).
* **Authentication (`gerar_auth.py`)**: Utility script to record login flows (Currently on *Standby*).
* **Persistence (`data/`)**: Local directory mapped to store persistent logs, Excel reports, or robot history.

### Authentication Architecture & Engineering Decisions
* **The role of `gerar_auth.py`**: This script was originally designed to record all the necessary steps to perform a login and navigate to a specific location on the target website, storing the session state.
* **Current Strategy (Standby)**: By technical choice, the use of this automated pre-recorded session flow has been placed on *standby*. Many modern websites heavily restrict session reuse due to dynamic tokens, strict cookie expiration, and dynamic structural changes within pages.
* **Approach in `main.py`**: To guarantee the robot's resilience and stability, we opted to build a dedicated and adaptable execution path directly inside `main.py` for each specific case the robot needs to interact with. This allows for intelligent, real-time decision-making during execution.

### Prerequisites
* [Docker](https://docker.com) and [Docker Compose](https://docker.com) installed (Recommended).
* Python 3.10+ installed (If running locally without Docker).

---

## How to Run the Project

### 1. Clone the Repository
Open your terminal and download the project from your GitHub:
```bash
git clone https://github.com/Lavbella/rpa.git
cd rpa
```

### 2. Install Requirements (Local Execution / Development)
If you choose to run or test the project locally on your machine (outside of Docker), follow these steps:

1. **Create and activate the virtual environment (venv):**
   ```bash
   python -m venv venv

   # Activate on Windows (Command Prompt):
   venv\Scripts\activate
   # Activate on Windows (PowerShell):
   .\venv\Scripts\activate
   # Activate on Linux/macOS:
   source venv/bin/activate
   ```

2. **Install Python packages:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install Playwright Browser Binaries:**
   ```bash
   playwright install chromium
   ```

4. **Note regarding Pytesseract (OCR):**
   `pytesseract` requires the Tesseract OCR engine to be installed on your host system.
   * *Ubuntu/Linux:* `sudo apt install tesseract-ocr`
   * *Windows:* Download the Tesseract installer and add it to your system PATH.

---

### 🐳 Automated Execution with Docker (Recommended)
By using Docker, you can skip the virtual environment setup and local installations. The container comes pre-configured with the Tesseract engine and browser dependencies out of the box.

1. **Spin Up the Containers:**
   ```bash
   docker compose up -d --build
   ```

2. **Open the Dashboard:**
   Navigate to: [http://localhost:8501](http://localhost:8501)

---

## Logs & Monitoring / Monitorização
To track the Playwright browser automation and live data extraction in the terminal:
```bash
docker compose logs -f
```
---
<sub>Project developed by [Lavbella](https://github.com).</sub>
## Stop the Automation / Parar a Automação
```bash
docker compose down
```
