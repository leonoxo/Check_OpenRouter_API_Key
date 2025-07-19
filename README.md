# OpenRouter API 金鑰驗證器

這是一個 Python 腳本，用於批量驗證 OpenRouter API 金鑰的有效性。它會檢查每個金鑰是否能成功授權，並嘗試使用一個免費模型進行聊天 API 呼叫，以確保金鑰不僅有效且可用。

## 主要功能

- **零設定執行**：無需任何命令列參數或額外資料夾，開箱即用。
- **批量驗證**：直接從與腳本相同目錄下的 `api_keys.txt` 檔案讀取金鑰。
- **兩階段驗證**：
  1.  基本授權驗證。
  2.  進階聊天可用性驗證。
- **智慧速率限制處理**：
  - 內建固定的請求延遲，以遵守單一金鑰 20 RPM 的限制。
  - 在驗證不同金鑰之間加入隨機延遲，模擬人類行為。
  - 將 `HTTP 429` (Too Many Requests) 錯誤視為金鑰有效。
- **結果自動分類**：自動將結果儲存到目前目錄下的 `valid_keys.txt` 和 `invalid_keys.txt`。
- **詳細日誌**：將詳細的驗證過程記錄到 `validation_log.log` 檔案中。

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

1.  **準備 API 金鑰檔案**
    在專案根目錄下（與 `validate_keys.py` 相同目錄），建立一個名為 `api_keys.txt` 的檔案，並將您要驗證的 API 金鑰每行一個貼入此檔案。

2.  **執行驗證腳本**
    ```bash
    python validate_keys.py
    ```
    執行完畢後，結果檔案將會出現在同一個目錄中。

---

## 使用方法 (Docker 執行)

1.  **建置 Docker 映像**
    ```bash
    docker build -t check-openrouter-keys .
    ```

2.  **準備工作目錄並執行容器**
    將您的 `api_keys.txt` 檔案放在一個工作目錄中，然後執行以下命令。它會將您目前的工作目錄掛載到容器中。
    ```bash
    # 確保你的 api_keys.txt 在目前目錄下
    docker run --rm -v "$(pwd):/app" check-openrouter-keys
    ```
    執行完畢後，結果檔案將會出現在您執行命令的目錄中。