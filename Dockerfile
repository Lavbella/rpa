# 1. Base oficial do Playwright (já traz as libs de sistema para o browser)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 2. Diretório onde o código vai viver no container
WORKDIR /app

# --- NOVO: Instala o motor do Tesseract no Linux ---
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*
# ---------------------------------------------------

# 3. Instalar dependências de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Instalar o browser Chromium dentro da imagem
RUN playwright install chromium

# 5. Copiar o teu script principal
COPY . .

# 6. Criar a pasta onde o volume será montado
RUN mkdir -p /app/data && chmod 777 /app/data

# Expõe o porto do Streamlit
EXPOSE 8501

# Comando para iniciar o painel
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]