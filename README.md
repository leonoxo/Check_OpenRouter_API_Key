# OpenRouter API 金鑰驗證工具

[![Python 版本](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 簡介

這是一個用於驗證 OpenRouter API 金鑰有效性的 Python 工具。它可以從檔案中讀取多個 API 金鑰，並透過 OpenRouter 的 API 進行基本驗證和聊天功能測試，確保金鑰不僅有效，還能實際用於聊天模型。

## 功能

- **批量驗證**：從 `api_keys.txt` 檔案中讀取多個 API 金鑰並進行驗證。
- **雙重驗證**：
  - 基本驗證：檢查金鑰是否能通過 OpenRouter 的認證端點。
  - 聊天驗證：使用隨機選擇的免費模型進行簡單的聊天測試，確保金鑰能實際使用。
- **免費模型檢測**：自動從 OpenRouter API 獲取當前可用的免費模型列表，用於聊天驗證。
- **詳細日誌**：將驗證過程和結果記錄到控制台和 `validation_log.log` 檔案中，方便排查問題。
- **錯誤處理**：完善的錯誤處理機制，包括網路問題、API 限制和無效回應等情況。
- **延遲機制**：在驗證多個金鑰時，加入隨機延遲（5-15 秒），避免觸發速率限制。

## 安裝

1. 確保您已安裝 Python 3.6 或更高版本。
2. 克隆此倉庫或下載 `validate_keys.py` 檔案。
3. 安裝所需的套件（腳本會自動檢查並安裝）：
   ```
   pip install requests
   ```

## 使用方法

1. 在與 `validate_keys.py` 相同目錄下創建一個名為 `api_keys.txt` 的檔案。
2. 在 `api_keys.txt` 中，每行輸入一個 OpenRouter API 金鑰（可以包含註釋行，以 `#` 開頭）。
   範例：
   ```
   # 測試金鑰
   sk-or-v1-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
   sk-or-v1-abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
   ```
3. 執行腳本：
   ```
   python validate_keys.py
   ```
4. 查看結果：
   - 驗證過程和結果會顯示在控制台中。
   - 詳細日誌會儲存到 `validation_log.log` 檔案中。
   - 腳本會總結有效和無效金鑰的數量，並列出無效的金鑰。

## 注意事項

- 請確保 `api_keys.txt` 檔案與腳本位於同一目錄下。
- 腳本會自動檢查並安裝所需的 Python 套件（`requests`）。
- 由於 OpenRouter 的速率限制，腳本在驗證多個金鑰時會加入隨機延遲。
- 聊天驗證需要至少一個可用的免費模型，如果無法獲取免費模型列表，則無法完成完整驗證。
- 請勿將包含 API 金鑰的檔案上傳到公開倉庫，建議將 `api_keys.txt` 和 `validation_log.log` 加入 `.gitignore`。

## 貢獻

歡迎提交問題報告和功能建議。如果您希望貢獻程式碼，請遵循以下步驟：
1. Fork 此倉庫。
2. 創建您的功能分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交您的變更 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 開啟一個 Pull Request。

## 授權

本專案採用 MIT 授權 - 詳情請見 [LICENSE](LICENSE) 檔案。

## 聯絡方式

如有任何問題或建議，請在 GitHub 上開啟一個 Issue 或聯絡 [leonoxo](https://github.com/leonoxo)。