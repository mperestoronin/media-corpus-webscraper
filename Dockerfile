FROM apache/airflow:2.10.3-python3.10

# Установка системных зависимостей для Playwright
USER root
RUN apt-get update && apt-get install -y \
    wget \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libgbm-dev \
    libasound2 \
    libpangocairo-1.0-0 \
    libx11-xcb1 \
    libxfixes3 \
    libxkbcommon0 \
    xvfb \
    && apt-get clean

# Установка Python-зависимостей
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

# Установка Playwright и загрузка браузеров
RUN pip install playwright
RUN playwright install
RUN python -m nltk.downloader punkt_tab

USER airflow
