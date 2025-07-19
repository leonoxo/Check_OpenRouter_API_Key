# 1. 使用官方的輕量級 Python 映像作為基礎
FROM python:3.9-slim

# 2. 在容器中設定一個工作目錄
WORKDIR /app

# 3. 複製相依性檔案並安裝
# --no-cache-dir 選項可以減小映像體積
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 複製主要的 Python 腳本
COPY validate_keys.py .

# 5. 設定容器啟動時執行的命令
# 這允許使用者在 `docker run` 時傳遞參數給腳本
ENTRYPOINT ["python", "validate_keys.py"]

# 6. 設定預設命令
# 如果使用者沒有提供任何參數，執行 `docker run <image>` 將會顯示幫助訊息
CMD ["--help"]