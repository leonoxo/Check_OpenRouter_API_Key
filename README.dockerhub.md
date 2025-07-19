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
您需要在您的電腦上建立一個資料夾，並在其中放入您的 API 金鑰檔案。

```bash
# 1. 建立一個資料夾 (名稱必須是 data)
mkdir data

# 2. 在 data 資料夾中，建立一個名為 api_keys.txt 的檔案
#    並將您要驗證的 API 金鑰每行一個貼入此檔案。
```

### 3. 執行驗證
使用 `docker run` 命令來啟動驗證程序。以下命令會將您本地的 `data` 目錄掛載到容器中並執行腳本。

**這是一個零設定命令，無需任何額外參數。**

```bash
docker run --rm -v "$(pwd)/data:/app/data" leonoxo/check-openrouter-keys
```

- `--rm`：容器停止後自動刪除，保持系統乾淨。
- `-v "$(pwd)/data:/app/data"`：將您目前路徑下的 `data` 資料夾，掛載到容器內的 `/app/data` 資料夾。

執行完畢後，您會在本地的 `data` 資料夾中找到 `valid_keys.txt`、`invalid_keys.txt` 和 `validation_log.log` 等結果檔案。

---

## 功能摘要

- **零設定執行**：無需任何命令列參數，開箱即用。
- **批量驗證**：從 `data/api_keys.txt` 檔案讀取多個 API 金鑰進行驗證。
- **兩階段驗證**：進行基本授權驗證和進階可用性驗證。
- **智慧速率限制處理**：
  - 內建固定的請求延遲，以遵守單一金鑰 20 RPM 的限制。
  - 在驗證不同金鑰之間加入隨機延遲，模擬人類行為。
  - 將 `HTTP 429` (Too Many Requests) 錯誤視為金鑰有效。
- **結果自動分類**：自動將結果儲存到 `data` 資料夾下的 `valid_keys.txt` 和 `invalid_keys.txt`。
- **詳細日誌**：將過程記錄到 `data/validation_log.log` 檔案中。