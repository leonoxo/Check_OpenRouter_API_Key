import os
import json
import time
import random
import logging
import requests
from typing import List, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 設定 ---
# 金鑰檔案的名稱
API_KEYS_FILE = "api_keys.txt"
# 輸出檔案的目錄 ('.' 代表目前目錄)
OUTPUT_DIR = "."
# 驗證不同金鑰之間的延遲設定 (秒)
DELAY = 5.0
JITTER = 2.0
# 內部請求之間的延遲 (秒)，以符合 20 RPM 的限制
INTRA_REQUEST_DELAY = 3.1

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(),
    logging.FileHandler(os.path.join(OUTPUT_DIR, 'validation_log.log'), mode='w')
])
logger = logging.getLogger(__name__)

class OpenRouterValidator:
    """用於驗證 OpenRouter API 金鑰的類別"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    AUTH_ENDPOINT = f"{BASE_URL}/auth/key"
    MODELS_ENDPOINT = f"{BASE_URL}/models"
    CHAT_ENDPOINT = f"{BASE_URL}/chat/completions"
    
    def __init__(self, max_retries: int = 3):
        """初始化驗證器"""
        self.session = self._create_session(max_retries)
        self.free_models: List[str] = []

    def _create_session(self, max_retries: int) -> requests.Session:
        """創建具有重試機制的 HTTP 會話"""
        session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session
        
    def load_api_keys(self) -> List[str]:
        """從檔案讀取 API 金鑰"""
        keys = []
        try:
            logger.info(f"正在從 {API_KEYS_FILE} 讀取金鑰...")
            with open(API_KEYS_FILE, 'r') as f:
                for line in f:
                    key = line.strip()
                    if key and not key.startswith('#'):
                        keys.append(key)
            logger.info(f"成功讀取 {len(keys)} 個金鑰。")
        except FileNotFoundError:
            logger.error(f"找不到金鑰檔案 {API_KEYS_FILE}。請確保檔案與腳本在同一個目錄中。")
        except Exception as e:
            logger.error(f"讀取金鑰檔案時發生錯誤: {e}")
        return keys
    
    def get_free_models(self) -> List[str]:
        """從 OpenRouter API 獲取免費模型列表"""
        if self.free_models:
            return self.free_models
        try:
            logger.info("正在從 OpenRouter 獲取模型列表...")
            response = self.session.get(self.MODELS_ENDPOINT, timeout=15)
            response.raise_for_status()
            models_data = response.json()
            if 'data' in models_data:
                self.free_models = [model['id'] for model in models_data['data']
                                  if isinstance(model, dict) and 'id' in model and ':free' in model['id']]
                logger.info(f"找到 {len(self.free_models)} 個免費模型: {self.free_models}")
            else:
                logger.warning("無法從 API 回應中解析模型數據。")
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取模型列表失敗: {e}")
        except json.JSONDecodeError:
            logger.error("解析模型列表回應 JSON 失敗。")
        except Exception as e:
            logger.error(f"獲取模型列表時發生未預期錯誤: {e}")
        if not self.free_models:
            logger.warning("未能獲取到任何免費模型列表，將無法進行聊天驗證。")
        return self.free_models
    
    def validate_api_key(self, api_key: str) -> bool:
        """驗證單個 API 金鑰"""
        masked_key = f"{api_key[:15]}..."
        headers = {'Authorization': f'Bearer {api_key}'}
        try:
            response = self.session.get(self.AUTH_ENDPOINT, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"金鑰 {masked_key} 基本驗證通過。")
        except requests.exceptions.RequestException as e:
            logger.error(f"金鑰 {masked_key} 基本驗證失敗: {e}")
            return False
        
        time.sleep(INTRA_REQUEST_DELAY)

        if not self.free_models:
            logger.warning(f"金鑰 {masked_key} 跳過聊天驗證，因為沒有可用的免費模型列表。")
            return False
            
        chat_headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        model_id = random.choice(self.free_models)
        logger.info(f"金鑰 {masked_key} 隨機選擇免費模型 '{model_id}' 進行聊天驗證...")
        payload = {"model": model_id, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 10}
        
        try:
            response = self.session.post(self.CHAT_ENDPOINT, headers=chat_headers, json=payload, timeout=20)
            if response.ok:
                logger.info(f"金鑰 {masked_key} 使用模型 '{model_id}' 聊天 API 驗證成功！")
                return True
            elif response.status_code == 402:
                logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 失敗：餘額不足 (402)。")
                return False
            elif response.status_code == 429:
                logger.warning(f"金鑰 {masked_key} 驗證成功，但已達到速率限制 (429)。")
                return True
            else:
                error_msg = f"HTTP {response.status_code} 錯誤"
                try:
                    error_details = response.json()
                    if 'error' in error_details and 'message' in error_details['error']:
                        error_msg = f"{error_msg} - {error_details['error']['message']}"
                except (json.JSONDecodeError, AttributeError):
                    pass
                logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 失敗: {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 驗證時發生錯誤: {e}")
            return False
    
    def validate_all_keys(self) -> tuple[List[str], List[str]]:
        """驗證所有 API 金鑰"""
        api_keys = self.load_api_keys()
        if not api_keys:
            return [], []
        
        self.get_free_models()
        if not self.free_models:
            logger.error("無法獲取免費模型列表，無法繼續進行聊天驗證。")
            return [], []
            
        logger.info(f"\n--- 開始驗證 {len(api_keys)} 個金鑰 ---")
        valid_keys, invalid_keys = [], []
        
        for i, key in enumerate(api_keys, 1):
            if self.validate_api_key(key):
                valid_keys.append(key)
            else:
                invalid_keys.append(key)
            logger.info(f"已驗證 {i}/{len(api_keys)} 個金鑰")
            
            if i < len(api_keys):
                actual_delay = random.uniform(DELAY - JITTER, DELAY + JITTER)
                if actual_delay > 0:
                    logger.info(f"隨機延遲 {actual_delay:.2f} 秒後繼續...")
                    time.sleep(actual_delay)
            logger.info("-" * 30)
                
        return valid_keys, invalid_keys
    
    def log_results(self, valid_keys: List[str], invalid_keys: List[str]) -> None:
        """記錄驗證結果並將金鑰寫入檔案"""
        logger.info("\n--- 驗證結果 ---")
        logger.info(f"有效的金鑰數量: {len(valid_keys)}")
        logger.info(f"無效的金鑰數量: {len(invalid_keys)}")

        valid_keys_file = os.path.join(OUTPUT_DIR, 'valid_keys.txt')
        try:
            with open(valid_keys_file, 'w') as f:
                for key in valid_keys:
                    f.write(f"{key}\n")
            if valid_keys:
                logger.info(f"有效的金鑰已儲存至 {valid_keys_file}")
        except IOError as e:
            logger.error(f"寫入有效金鑰檔案失敗: {e}")

        if invalid_keys:
            invalid_keys_file = os.path.join(OUTPUT_DIR, 'invalid_keys.txt')
            try:
                with open(invalid_keys_file, 'w') as f:
                    for key in invalid_keys:
                        f.write(f"{key}\n")
                logger.info(f"無效的金鑰已儲存至 {invalid_keys_file}")
            except IOError as e:
                logger.error(f"寫入無效金鑰檔案失敗: {e}")

            logger.info("\n--- 無效的 API 金鑰列表 ---")
            for key in invalid_keys:
                logger.info(key)
        else:
            logger.info("\n所有金鑰均驗證通過！")

def main():
    """主函數"""
    # 檢查相依性
    try:
        import requests
    except ImportError:
        logger.error("缺少 'requests' 套件。請執行 'pip install -r requirements.txt' 來安裝。")
        return

    validator = OpenRouterValidator()
    valid_keys, invalid_keys = validator.validate_all_keys()
    validator.log_results(valid_keys, invalid_keys)

if __name__ == "__main__":
    main()