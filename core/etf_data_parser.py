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
