import os
import json
import time
import random
import logging
import requests
from typing import List, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(),  # 輸出到控制台
    logging.FileHandler('validation_log.log')  # 輸出到檔案
])
logger = logging.getLogger(__name__)

class OpenRouterValidator:
    """用於驗證 OpenRouter API 金鑰的類別"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    AUTH_ENDPOINT = f"{BASE_URL}/auth/key"
    MODELS_ENDPOINT = f"{BASE_URL}/models"
    CHAT_ENDPOINT = f"{BASE_URL}/chat/completions"
    
    def __init__(self, api_keys_file: str = "api_keys.txt", max_retries: int = 3):
        """初始化驗證器"""
        self.api_keys_file = api_keys_file
        self.session = self._create_session(max_retries)
        self.free_models: List[str] = []
        
    def _create_session(self, max_retries: int) -> requests.Session:
        """創建具有重試機制的 HTTP 會話"""
        session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session
        
    def load_api_keys(self) -> List[str]:
        """從檔案讀取 API 金鑰"""
        keys = []
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, self.api_keys_file)
            logger.info(f"正在從 {file_path} 讀取金鑰...")
            
            with open(file_path, 'r') as f:
                for line in f:
                    key = line.strip()
                    if key and not key.startswith('#'):
                        keys.append(key)
            logger.info(f"成功讀取 {len(keys)} 個金鑰。")
        except FileNotFoundError:
            logger.error(f"找不到金鑰檔案 {file_path}")
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
        
        # 基本驗證
        headers = {'Authorization': f'Bearer {api_key}'}
        try:
            response = self.session.get(self.AUTH_ENDPOINT, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"金鑰 {masked_key} 基本驗證通過。")
        except requests.exceptions.RequestException as e:
            logger.error(f"金鑰 {masked_key} 基本驗證失敗: {e}")
            return False
            
        # 進階驗證 - 聊天 API 測試
        if not self.free_models:
            logger.warning(f"金鑰 {masked_key} 跳過聊天驗證，因為沒有可用的免費模型列表。")
            return False
            
        chat_headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        model_id = random.choice(self.free_models)
        logger.info(f"金鑰 {masked_key} 隨機選擇免費模型 '{model_id}' 進行聊天驗證...")
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10
        }
        
        try:
            response = self.session.post(self.CHAT_ENDPOINT, headers=chat_headers, json=payload, timeout=20)
            if response.ok:
                try:
                    data = response.json()
                    if data and 'choices' in data and data['choices']:
                        logger.info(f"金鑰 {masked_key} 使用模型 '{model_id}' 聊天 API 驗證成功！")
                        return True
                    else:
                        logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 成功請求，但回應格式不符預期。")
                        return False
                except json.JSONDecodeError:
                    logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 成功請求，但無法解析回應 JSON。")
                    return False
            elif response.status_code == 402:
                logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 失敗：餘額不足 (402)。")
                return False
            elif response.status_code == 429:
                logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 失敗：達到速率限制 (429)。")
                return False
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
        except requests.exceptions.Timeout:
            logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 驗證超時。")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 驗證時發生網路錯誤: {e}")
            return False
        except Exception as e:
            logger.error(f"金鑰 {masked_key} 使用模型 '{model_id}' 驗證時發生未預期錯誤: {e}")
            return False
    
    def validate_all_keys(self) -> tuple[List[str], List[str]]:
        """驗證所有 API 金鑰"""
        api_keys = self.load_api_keys()
        self.get_free_models()
        
        if not api_keys:
            logger.warning("未從檔案中讀取到任何 API 金鑰。請檢查檔案是否在腳本同目錄下且包含有效的金鑰。")
            return [], []
            
        if not self.free_models:
            logger.error("無法獲取免費模型列表，無法繼續進行聊天驗證。")
            return [], []
            
        logger.info("\n--- 開始驗證金鑰 ---")
        valid_keys, invalid_keys = [], []
        
        for i, key in enumerate(api_keys, 1):
            if self.validate_api_key(key):
                valid_keys.append(key)
            else:
                invalid_keys.append(key)
            logger.info(f"已驗證 {i}/{len(api_keys)} 個金鑰")
            logger.info("-" * 30)
            
            if i < len(api_keys):  # 最後一個金鑰不需要延遲
                delay = random.uniform(5, 15)
                logger.info(f"延遲 {delay:.2f} 秒後繼續...")
                time.sleep(delay)
                
        return valid_keys, invalid_keys
    
    def log_results(self, valid_keys: List[str], invalid_keys: List[str]) -> None:
        """記錄驗證結果"""
        logger.info("\n--- 驗證結果 ---")
        logger.info(f"有效的金鑰數量 (通過基本和隨機一個免費模型聊天驗證): {len(valid_keys)}")
        logger.info(f"無效的金鑰數量 (基本驗證失敗或隨機免費模型聊天驗證失敗/跳過): {len(invalid_keys)}")
        
        if invalid_keys:
            logger.info("\n--- 無效的 API 金鑰列表 ---")
            for key in invalid_keys:
                logger.info(key)
        else:
            logger.info("\n所有金鑰均驗證通過！")

def check_and_setup_environment():
    """檢查並設置運行環境，包括虛擬環境和所需套件"""
    import subprocess
    import sys
    import os.path

    logger.info("正在檢查運行環境...")

    # 檢查並安裝所需套件（直接在系統環境中）
    required_packages = ['requests']
    for pkg in required_packages:
        logger.info(f"正在檢查套件 {pkg}...")
        try:
            __import__(pkg)
            logger.info(f"套件 {pkg} 已安裝。")
        except ImportError:
            logger.info(f"套件 {pkg} 未安裝，正在安裝...")
            try:
                subprocess.run(['pip', 'install', pkg], check=True)
                logger.info(f"套件 {pkg} 安裝成功。")
            except subprocess.CalledProcessError:
                logger.error(f"安裝套件 {pkg} 失敗。")
                sys.exit(1)

def main():
    """主函數"""
    check_and_setup_environment()
    validator = OpenRouterValidator()
    valid_keys, invalid_keys = validator.validate_all_keys()
    validator.log_results(valid_keys, invalid_keys)

if __name__ == "__main__":
    main()