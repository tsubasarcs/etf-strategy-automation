# core/firebase_client.py
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

# core/data_collector.py
"""數據收集器"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Optional, List
from .etf_data_parser import ETFDataParser

class ETFDataCollector:
    """ETF數據收集器"""
    
    def __init__(self):
        self.base_url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        self.parser = ETFDataParser()
    
    def get_monthly_data(self, etf_code: str, year_month: str) -> Optional[pd.DataFrame]:
        """獲取ETF月份資料"""
        url = f"{self.base_url}?response=json&date={year_month}01&stockNo={etf_code}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            data = response.json()
            if data.get('stat') != 'OK' or not data.get('data'):
                return None
            
            return self.parser.parse_raw_data(data)
            
        except Exception as e:
            print(f"❌ 獲取 {etf_code} 資料失敗: {e}")
            return None
    
    def get_historical_data(self, etf_code: str, months: int = 6) -> Optional[pd.DataFrame]:
        """獲取歷史資料"""
        all_data = []
        current_date = datetime.now()
        
        for i in range(months):
            year_month = (current_date - timedelta(days=30*i)).strftime('%Y%m')
            monthly_data = self.get_monthly_data(etf_code, year_month)
            
            if monthly_data is not None:
                all_data.append(monthly_data)
            
            time.sleep(1)  # 避免請求過快
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df.drop_duplicates().sort_values('date').reset_index(drop=True)
        
        return None
    
    def collect_all_etfs(self, etf_list: List[str]) -> Dict[str, Optional[pd.DataFrame]]:
        """收集所有ETF資料"""
        results = {}
        
        for etf in etf_list:
            print(f"📊 收集 {etf} 資料...")
            results[etf] = self.get_historical_data(etf)
        
        return results

# core/etf_data_parser.py
"""ETF數據解析器"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any

class ETFDataParser:
    """ETF數據解析器"""
    
    @staticmethod
    def convert_tw_date(date_str: str) -> str:
        """轉換台灣民國年為西元年"""
        try:
            parts = date_str.split('/')
            tw_year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            return f"{tw_year + 1911}-{month:02d}-{day:02d}"
        except:
            return None
    
    def parse_raw_data(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """解析原始數據"""
        df = pd.DataFrame(raw_data['data'], columns=raw_data['fields'])
        
        # 轉換日期
        df['date'] = df['日期'].apply(self.convert_tw_date)
        df['date'] = pd.to_datetime(df['date'])
        
        # 數值轉換
        numeric_cols = ['成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].str.replace(',', '').astype(float)
        
        # 重新命名欄位
        column_mapping = {
            '開盤價': 'open',
            '最高價': 'high', 
            '最低價': 'low',
            '收盤價': 'close',
            '成交股數': 'volume',
            '成交金額': 'amount'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 選擇需要的欄位
        return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
    
    def convert_to_firebase_format(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """轉換為Firebase格式"""
        firebase_data = {}
        
        for _, row in df.iterrows():
            date_key = row['date'].strftime('%Y-%m-%d')
            firebase_data[date_key] = {
                'date': date_key,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume']),
                'amount': int(row['amount']),
                'updated_at': datetime.now().isoformat()
            }
        
        return firebase_data
    
    def convert_from_firebase_format(self, firebase_data: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """從Firebase格式轉換為DataFrame"""
        if not firebase_data:
            return pd.DataFrame()
        
        data_list = []
        for date_str, day_data in firebase_data.items():
            data_list.append({
                'date': pd.to_datetime(date_str),
                'open': day_data.get('open'),
                'high': day_data.get('high'),
                'low': day_data.get('low'),
                'close': day_data.get('close'),
                'volume': day_data.get('volume', 0),
                'amount': day_data.get('amount', 0)
            })
        
        df = pd.DataFrame(data_list)
        return df.sort_values('date').reset_index(drop=True)

# core/__init__.py
"""核心模組初始化"""

from .firebase_client import FirebaseClient
from .data_collector import ETFDataCollector
from .etf_data_parser import ETFDataParser

__all__ = [
    'FirebaseClient',
    'ETFDataCollector', 
    'ETFDataParser'
]
