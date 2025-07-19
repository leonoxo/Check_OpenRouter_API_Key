# OpenRouter API 金鑰驗證器

一個用於批量驗證 OpenRouter API 金鑰有效性的簡易、零設定 Docker image。

**GitHub 倉庫：** [leonoxo/Check_OpenRouter_API_Key](https://github.com/leonoxo/Check_OpenRouter_API_Key)

---

## 🚀 快速開始

### 步驟 1：拉取 Image
```bash
docker pull leonoxo/check-openrouter-keys:latest
```

### 步驟 2：準備您的金鑰檔案
在您的電腦上建立一個工作目錄，並在其中建立一個名為 `api_keys.txt` 的檔案。將您要驗證的 API 金鑰每行一個貼入此檔案。

### 步驟 3：執行驗證
在您的工作目錄中（`api_keys.txt` 所在的目錄），執行以下命令。

```bash
docker run --rm -v "$(pwd):/app" leonoxo/check-openrouter-keys
```

- `--rm`：容器停止後自動刪除，保持系統乾淨。
- `-v "$(pwd):/app"`：將您目前的工作目錄掛載到容器的 `/app` 目錄。

執行完畢後，驗證結果（`valid_keys.txt`, `invalid_keys.txt`, 和 `validation_log.log`）將會出現在您的工作目錄中。

---

## ✨ 主要功能

- **✅ 零設定**：無需任何命令列參數或額外資料夾，開箱即用。
- **🗂️ 批量驗證**：直接讀取您提供的 `api_keys.txt` 檔案。
- **🛡️ 智慧速率限制處理**：
  - 內建延遲以遵守單一金鑰 20 RPM 的限制。
  - 在金鑰之間加入隨機延遲，模擬人類行為。
  - 將 `HTTP 429 (Too Many Requests)` 錯誤正確地視為**有效**金鑰。
- ** sorted 自動分類**：結果會自動儲存到您掛載的工作目錄中。
- **📜 詳細日誌**：完整的執行過程會被儲存到 `validation_log.log`。