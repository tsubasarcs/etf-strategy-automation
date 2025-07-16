"""Firebase客戶端封裝"""

import requests
import json
import os
from typing import Dict, Any, Optional

class FirebaseClient:
    """Firebase操作客戶端"""
    
    def __init__(self, firebase_url: Optional[str] = None):
        self.firebase_url = firebase_url or os.getenv(
            'FIREBASE_URL', 
            'https://your-project-default-rtdb.asia-southeast1.firebasedatabase.app'
        )
    
    def save(self, path: str, data: Dict[str, Any]) -> bool:
        """保存資料到Firebase"""
        url = f"{self.firebase_url}/{path}.json"
        
        try:
            response = requests.put(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Firebase保存失敗 {path}: {e}")
            return False
    
    def get(self, path: str) -> Optional[Dict[str, Any]]:
        """從Firebase讀取資料"""
        url = f"{self.firebase_url}/{path}.json"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Firebase讀取失敗 {path}: {e}")
            return None
    
    def update(self, path: str, data: Dict[str, Any]) -> bool:
        """更新Firebase資料"""
        url = f"{self.firebase_url}/{path}.json"
        
        try:
            response = requests.patch(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Firebase更新失敗 {path}: {e}")
            return False
