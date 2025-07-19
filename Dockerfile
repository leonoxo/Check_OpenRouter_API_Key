# 1. 使用官方的輕量級 Python 映像作為基礎
FROM python:3.9-slim

# 2. 在容器中設定一個工作目錄
WORKDIR /app

# 3. 複製相依性檔案並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 複製主要的 Python 腳本
COPY validate_keys.py .

# 5. 建立資料目錄，以便使用者掛載磁碟區
# 這也確保了腳本在容器內執行時，'data' 目錄是存在的
RUN mkdir data

# 6. 設定容器啟動時執行的命令
CMD ["python", "validate_keys.py"]