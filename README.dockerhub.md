# OpenRouter API Key Validator

A simple, zero-config Docker image to bulk validate your OpenRouter API keys.

**GitHub Repository:** [leonoxo/Check_OpenRouter_API_Key](https://github.com/leonoxo/Check_OpenRouter_API_Key)

---

## 🚀 Quick Start

### Step 1: Pull the Image
```bash
docker pull leonoxo/check-openrouter-keys:latest
```

### Step 2: Prepare Your Keys
Create a directory named `data` on your machine, and inside it, create a file named `api_keys.txt`. Place one API key per line in this file.

```bash
# Create a directory
mkdir data

# Create the key file and add your keys into it
# For example:
echo "sk-or-v1-..." > data/api_keys.txt
echo "sk-or-v1-..." >> data/api_keys.txt
```

### Step 3: Run the Validator
Execute the following command from the same location where you created the `data` directory.

```bash
docker run --rm -v "$(pwd)/data:/app/data" leonoxo/check-openrouter-keys
```

That's it! The validation results (`valid_keys.txt`, `invalid_keys.txt`, and `validation_log.log`) will appear in your `data` directory.

---

## ✨ Features

- **✅ Zero Configuration**: No command-line arguments needed. Just run and go.
- **批量驗證**：從 `data/api_keys.txt` 檔案讀取多個 API 金鑰進行驗證。
- **🛡️ Smart Rate-Limit Handling**:
  - Built-in delays to respect the 20 RPM per-key limit.
  - Randomized delays between validating different keys to mimic human behavior.
  - `HTTP 429 (Too Many Requests)` errors are correctly treated as a **valid** key.
- **🗂️ Automatic Sorting**: Results are automatically saved to `valid_keys.txt` and `invalid_keys.txt` in your data volume.
- **📜 Detailed Logging**: A full execution log is saved to `validation_log.log`.

## How It Works

The container expects a volume mounted at `/app/data`. It will look for `api_keys.txt` inside this volume and write all output files back to the same volume, making them accessible on your host machine.