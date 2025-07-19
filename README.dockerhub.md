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
在您的電腦上建立一個名為 `data` 的資料夾，並在其中建立一個名為 `api_keys.txt` 的檔案。將您要驗證的 API 金鑰每行一個貼入此檔案。

```bash
# 建立一個資料夾
mkdir data

# 建立金鑰檔案並將您的金鑰加入其中
# 範例:
echo "sk-or-v1-..." > data/api_keys.txt
echo "sk-or-v1-..." >> data/api_keys.txt
```

### 步驟 3：執行驗證器
在您建立 `data` 資料夾的相同位置，執行以下命令。

```bash
docker run --rm -v "$(pwd)/data:/app/data" leonoxo/check-openrouter-keys
```

這樣就完成了！驗證結果（`valid_keys.txt`, `invalid_keys.txt`, 和 `validation_log.log`）將會出現在您本地的 `data` 資料夾中。

---

## ✨ 主要功能

- **✅ 零設定**：無需任何命令列參數，開箱即用。
- **🗂️ 批量驗證**：從 `data/api_keys.txt` 檔案讀取多個 API 金鑰進行驗證。
- **🛡️ 智慧速率限制處理**：
  - 內建延遲以遵守單一金鑰 20 RPM 的限制。
  - 在金鑰之間加入隨機延遲，模擬人類行為。
  - 將 `HTTP 429 (Too Many Requests)` 錯誤正確地視為**有效**金鑰。
- ** sorted 自動分類**：結果會自動儲存到您掛載的資料夾中的 `valid_keys.txt` 和 `invalid_keys.txt`。
- **📜 詳細日誌**：完整的執行過程會被儲存到 `validation_log.log`。

## 運作原理

此容器預期有一個磁碟區掛載到 `/app/data`。它會在此磁碟區中尋找 `api_keys.txt`，並將所有輸出檔案寫回到同一個磁碟區，讓您可以在您的主機電腦上存取它們。