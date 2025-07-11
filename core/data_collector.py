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
