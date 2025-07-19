# OpenRouter API 金鑰驗證器

這是一個 Python 腳本，用於批量驗證 OpenRouter API 金鑰的有效性。它會檢查每個金鑰是否能成功授權，並嘗試使用一個免費模型進行聊天 API 呼叫，以確保金鑰不僅有效且可用。

## 主要功能

- **批量驗證**：從指定的文字檔案讀取多個 API 金鑰進行驗證。
- **兩階段驗證**：
  1.  透過 `/auth/key` 端點進行基本授權驗證。
  2.  隨機選取一個免費模型，嘗試呼叫聊天 API 進行進階可用性驗證。
- **速率限制處理**：
  - 嚴格遵守單一金鑰 20 RPM 的限制（在兩次請求間固定延遲 3.1 秒）。
  - 在驗證不同金鑰之間加入可配置的隨機延遲，模擬人類行為以避免觸發整體速率限制。
  - 將 `HTTP 429` (Too Many Requests) 錯誤視為金鑰有效，因為這本身證明了金鑰的有效性。
- **結果分類**：自動將驗證後的金鑰分類並儲存到 `valid_keys.txt` 和 `invalid_keys.txt`。
- **詳細日誌**：將詳細的驗證過程記錄到 `validation_log.log` 檔案中，方便追蹤與除錯。
- **靈活配置**：支援透過命令列參數自訂金鑰檔案、輸出目錄和延遲時間。

## 安裝指南

1.  **複製倉庫**
    ```bash
    git clone https://github.com/leonoxo/Check_OpenRouter_API_Key.git
    cd Check_OpenRouter_API_Key
    ```

2.  **建立並啟用虛擬環境 (建議)**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安裝相依套件**
    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

1.  **準備 API 金鑰檔案**
    - 在專案根目錄下建立一個名為 `api_keys.txt` 的檔案（或使用 `--keys-file` 參數指定其他路徑）。
    - 每行放置一個 API 金鑰。
    - 以 `#` 開頭的行將被視為註解，會被忽略。

2.  **執行驗證腳本**
    - **使用預設設定執行：**
      ```bash
      python validate_keys.py
      ```
    - **使用自訂參數執行：**
      ```bash
      python validate_keys.py --keys-file "my_keys.txt" --delay 7 --jitter 3 --output-dir "results/"
      ```

### 命令列參數說明

- `--keys-file`：指定包含 API 金鑰的檔案路徑。預設為 `api_keys.txt`。
- `--output-dir`：指定儲存結果檔案（`valid_keys.txt`, `invalid_keys.txt`）的目錄。預設為目前目錄。
- `--delay`：設定在驗證不同金鑰之間的**基礎延遲時間**（秒）。預設為 `5.0`。
- `--jitter`：設定延遲時間的**隨機變化範圍**（秒）。實際延遲會在 `delay ± jitter` 之間。預設為 `2.0`。

## 輸出說明

- `valid_keys.txt`：包含所有驗證通過的金鑰（包括因速率限制返回 429 的金鑰）。
- `invalid_keys.txt`：包含所有驗證失敗的金鑰。
- `validation_log.log`：包含詳細的執行過程日誌。

## 注意事項

- 請確保您的 API 金鑰檔案 (`api_keys.txt`) 已被加入到 `.gitignore` 中，以避免意外上傳到公開倉庫。本專案已預設配置好 `.gitignore`。
- 根據 OpenRouter 的速率限制（特別是 `50 RPD`），建議不要過於頻繁地執行此腳本。預設的延遲設定是為了在安全範圍內操作。
---

## 使用 Docker 執行

為了簡化環境設定，您也可以使用 Docker 來執行此腳本。

1.  **建置 Docker 映像**
    在專案根目錄下，執行以下命令來建置 Docker 映像：
    ```bash
    docker build -t check-openrouter-keys .
    ```

2.  **準備資料目錄並執行容器**
    Docker 容器與您的主機檔案系統是隔離的。您需要透過「磁碟區掛載」的方式，將包含金鑰的檔案提供給容器，並讓容器將結果寫回到您的主機。

    - **建立一個用於交換資料的目錄**（例如 `data`），並將您的金鑰檔案放入其中。
      ```bash
      mkdir data
      # 假設您的金鑰在 api_keys.txt
      cp api_keys.txt data/
      ```

    - **執行 Docker 容器**：
      以下命令會啟動一個容器，並將您主機的 `data` 目錄掛載到容器內的 `/app/data` 目錄。
      ```bash
      docker run --rm -v "$(pwd)/data:/app/data" check-openrouter-keys --keys-file /app/data/api_keys.txt --output-dir /app/data
      ```
      - `--rm`：容器停止後自動刪除，保持系統乾淨。
      - `-v "$(pwd)/data:/app/data"`：將您目前路徑下的 `data` 資料夾，掛載到容器內的 `/app` 工作目錄下的 `data` 資料夾。
      - `--keys-file` 和 `--output-dir` 的路徑必須是**容器內的路徑**，也就是 `/app/data/...`。

    執行完畢後，您會在本地的 `data` 資料夾中找到 `valid_keys.txt`、`invalid_keys.txt` 和 `validation_log.log` 等結果檔案。