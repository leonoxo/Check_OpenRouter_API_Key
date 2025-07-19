# OpenRouter API 金鑰驗證器

這是一個用於批量驗證 OpenRouter API 金鑰有效性的 Docker image。

您可以透過此工具，輕鬆地檢查您的 API 金鑰是否能成功授權，並確保其可用於實際的聊天 API 呼叫。

**GitHub 倉庫：** [leonoxo/Check_OpenRouter_API_Key](https://github.com/leonoxo/Check_OpenRouter_API_Key)

---

## 如何使用

### 1. 拉取 Docker Image
從 Docker Hub 拉取最新的 image：
```bash
docker pull leonoxo/check-openrouter-keys:latest
```

### 2. 準備您的資料
您需要在您的電腦上建立一個資料夾，用於存放輸入的 API 金鑰檔案和接收輸出的結果。

```bash
# 1. 建立一個資料夾 (例如 data)
mkdir data

# 2. 在 data 資料夾中，建立一個名為 api_keys.txt 的檔案
#    並將您要驗證的 API 金鑰每行一個貼入此檔案
#    (您也可以從現有的檔案複製)
#
#    範例: cp /path/to/your/api_keys.txt data/
```

### 3. 執行驗證
使用 `docker run` 命令來啟動驗證程序。以下命令會將您剛剛建立的 `data` 資料夾掛載到容器中，並執行腳本。

```bash
docker run --rm -v "$(pwd)/data:/app/data" leonoxo/check-openrouter-keys --keys-file /app/data/api_keys.txt --output-dir /app/data
```

- `--rm`：容器停止後自動刪除，保持系統乾淨。
- `-v "$(pwd)/data:/app/data"`：這是最關鍵的部分，它將您目前路徑下的 `data` 資料夾，掛載到容器內的 `/app/data` 資料夾。
- `--keys-file` 和 `--output-dir` 的路徑必須是**容器內的路徑**。

執行完畢後，您會在本地的 `data` 資料夾中找到 `valid_keys.txt`、`invalid_keys.txt` 和 `validation_log.log` 等結果檔案。

---

## 進階使用：自訂參數

您可以傳遞額外的參數來調整腳本的行為：

```bash
docker run --rm -v "$(pwd)/data:/app/data" leonoxo/check-openrouter-keys \
  --keys-file /app/data/api_keys.txt \
  --output-dir /app/data \
  --delay 7 \
  --jitter 3
```

### 可用參數

- `--keys-file`：指定容器內包含 API 金鑰的檔案路徑。
- `--output-dir`：指定容器內儲存結果檔案的目錄。
- `--delay`：設定在驗證不同金鑰之間的**基礎延遲時間**（秒）。預設為 `5.0`。
- `--jitter`：設定延遲時間的**隨機變化範圍**（秒）。實際延遲會在 `delay ± jitter` 之間。預設為 `2.0`。

---

## 主要功能摘要

- **批量驗證**：從指定的文字檔案讀取多個 API 金鑰進行驗證。
- **兩階段驗證**：進行基本授權驗證和進階可用性驗證。
- **智慧速率限制處理**：
  - 遵守單一金鑰 20 RPM 的限制。
  - 在金鑰之間加入隨機延遲，模擬人類行為。
  - 將 `HTTP 429` (Too Many Requests) 錯誤視為金鑰有效。
- **結果分類**：自動將結果儲存到 `valid_keys.txt` 和 `invalid_keys.txt`。
- **詳細日誌**：將過程記錄到 `validation_log.log` 檔案中。