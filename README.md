# OpenRouter API 金鑰驗證器

這是一個 Python 腳本，用於批量驗證 OpenRouter API 金鑰的有效性。它會檢查每個金鑰是否能成功授權，並嘗試使用一個免費模型進行聊天 API 呼叫，以確保金鑰不僅有效且可用。

## 主要功能

- **零設定執行**：無需任何命令列參數，開箱即用。
- **批量驗證**：從 `data/api_keys.txt` 檔案讀取多個 API 金鑰進行驗證。
- **兩階段驗證**：
  1.  基本授權驗證。
  2.  進階聊天可用性驗證。
- **智慧速率限制處理**：
  - 內建固定的請求延遲，以遵守單一金鑰 20 RPM 的限制。
  - 在驗證不同金鑰之間加入隨機延遲，模擬人類行為。
  - 將 `HTTP 429` (Too Many Requests) 錯誤視為金鑰有效。
- **結果自動分類**：自動將結果儲存到 `data` 資料夾下的 `valid_keys.txt` 和 `invalid_keys.txt`。
- **詳細日誌**：將詳細的驗證過程記錄到 `data/validation_log.log` 檔案中。

## 安裝指南

1.  **複製倉庫**
    ```bash
    git clone https://github.com/leonoxo/Check_OpenRouter_API_Key.git
    cd Check_OpenRouter_API_Key
    ```

2.  **安裝相依套件**
    ```bash
    pip install -r requirements.txt
    ```

## 使用方法 (本地執行)

1.  **建立 `data` 資料夾**
    在專案根目錄下建立一個名為 `data` 的資料夾。
    ```bash
    mkdir data
    ```

2.  **準備 API 金鑰檔案**
    在 `data` 資料夾中，建立一個名為 `api_keys.txt` 的檔案，並將您要驗證的 API 金鑰每行一個貼入此檔案。

3.  **執行驗證腳本**
    ```bash
    python validate_keys.py
    ```
    執行完畢後，結果檔案將會出現在 `data` 資料夾中。

---

## 使用方法 (Docker 執行)

1.  **建置 Docker 映像**
    ```bash
    docker build -t check-openrouter-keys .
    ```

2.  **準備資料目錄**
    在您的主機上建立一個 `data` 資料夾，並將 `api_keys.txt` 放入其中。
    ```bash
    mkdir data
    # 將您的金鑰檔案放入 data 資料夾
    cp /path/to/your/api_keys.txt data/
    ```

3.  **執行容器**
    使用以下命令啟動容器，它會將您本地的 `data` 目錄掛載到容器中並執行腳本。
    ```bash
    docker run --rm -v "$(pwd)/data:/app/data" check-openrouter-keys
    ```
    執行完畢後，結果檔案將會出現在您本地的 `data` 資料夾中。