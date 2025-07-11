import requests
import pandas as pd
import json
from datetime import datetime, date, timedelta
import time
import os

class FirebaseETFAnalyzer:
    def __init__(self):
        self.etfs = ['0056', '00878', '00919']
        self.base_url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        
        # Firebase設定 - 從環境變數或直接設定
        self.firebase_url = os.getenv('FIREBASE_URL', 'https://your-project-default-rtdb.asia-southeast1.firebasedatabase.app')
        
        # 配息行事曆
        self.dividend_calendar = {
            "0056": ["2025-07-15", "2025-10-15", "2026-01-15", "2026-04-15"],
            "00878": ["2025-08-16", "2025-11-21", "2026-02-20", "2026-05-19"], 
            "00919": ["2025-09-16", "2025-12-16", "2026-03-17", "2026-06-17"]
        }
        
        print(f"🔥 Firebase URL: {self.firebase_url}")
    
    def save_to_firebase(self, path, data):
        """保存資料到Firebase"""
        url = f"{self.firebase_url}/{path}.json"
        
        try:
            response = requests.put(url, json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Firebase儲存成功: {path}")
                return True
            else:
                print(f"❌ Firebase儲存失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Firebase連線錯誤: {e}")
            return False
    
    def get_from_firebase(self, path):
        """從Firebase讀取資料"""
        url = f"{self.firebase_url}/{path}.json"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Firebase讀取失敗: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Firebase讀取錯誤: {e}")
            return None
    
    def convert_tw_date(self, date_str):
        """轉換台灣民國年為西元年"""
        try:
            parts = date_str.split('/')
            tw_year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            return f"{tw_year + 1911}-{month:02d}-{day:02d}"
        except:
            return None
    
    def get_etf_data(self, etf_code, year_month):
        """取得ETF月份資料"""
        url = f"{self.base_url}?response=json&date={year_month}01&stockNo={etf_code}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            data = response.json()
            if data.get('stat') != 'OK' or not data.get('data'):
                return None
                
            df = pd.DataFrame(data['data'], columns=data['fields'])
            df['西元日期'] = df['日期'].apply(self.convert_tw_date)
            df['西元日期'] = pd.to_datetime(df['西元日期'])
            
            # 數值轉換
            numeric_cols = ['成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].str.replace(',', '').astype(float)
            
            return df
            
        except Exception as e:
            print(f"取得 {etf_code} 資料失敗: {e}")
            return None
    
    def update_etf_data_to_firebase(self, etf_code):
        """更新ETF資料到Firebase"""
        print(f"📊 更新 {etf_code} 資料到Firebase...")
        
        # 取得最近3個月的資料
        all_data = []
        current_date = datetime.now()
        
        for i in range(3):
            year_month = (current_date - timedelta(days=30*i)).strftime('%Y%m')
            monthly_data = self.get_etf_data(etf_code, year_month)
            
            if monthly_data is not None:
                all_data.append(monthly_data)
            
            time.sleep(1)  # 避免請求過快
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df = combined_df.drop_duplicates().sort_values('西元日期').reset_index(drop=True)
            
            # 轉換為Firebase適合的格式
            firebase_data = {}
            for _, row in combined_df.iterrows():
                date_key = row['西元日期'].strftime('%Y-%m-%d')
                firebase_data[date_key] = {
                    'date': date_key,
                    'open': float(row['開盤價']),
                    'high': float(row['最高價']),
                    'low': float(row['最低價']),
                    'close': float(row['收盤價']),
                    'volume': int(row['成交股數']),
                    'amount': int(row['成交金額']),
                    'updated_at': datetime.now().isoformat()
                }
            
            # 保存到Firebase
            path = f"etf_data/{etf_code}"
            success = self.save_to_firebase(path, firebase_data)
            
            if success:
                print(f"✅ {etf_code} 資料已保存到Firebase: {len(firebase_data)} 筆記錄")
                
                # 更新最新價格資訊
                latest_data = combined_df.iloc[-1]
                latest_info = {
                    'latest_price': float(latest_data['收盤價']),
                    'latest_date': latest_data['西元日期'].strftime('%Y-%m-%d'),
                    'price_change': 0,  # 可以後續計算
                    'last_updated': datetime.now().isoformat()
                }
                
                self.save_to_firebase(f"latest_prices/{etf_code}", latest_info)
                return True
            else:
                print(f"❌ {etf_code} Firebase儲存失敗")
                return False
        else:
            print(f"❌ {etf_code} 無法取得資料")
            return False
    
    def analyze_dividend_opportunities(self):
        """分析配息機會"""
        today = date.today()
        opportunities = []
        
        for etf in self.etfs:
            dividend_dates = self.dividend_calendar.get(etf, [])
            
            for div_date_str in dividend_dates:
                try:
                    div_date = datetime.strptime(div_date_str, '%Y-%m-%d').date()
                    days_after_dividend = (today - div_date).days
                    
                    # 檢查買進機會（除息後1-7天）
                    if 1 <= days_after_dividend <= 7:
                        opportunities.append({
                            'etf': etf,
                            'action': 'BUY',
                            'dividend_date': div_date_str,
                            'days_after': days_after_dividend,
                            'priority': self.get_etf_priority(etf),
                            'reason': f'除息後第{days_after_dividend}天，建議買進',
                            'confidence': 'high' if days_after_dividend <= 3 else 'medium'
                        })
                    
                    # 檢查即將配息（提前3天通知）
                    days_to_dividend = (div_date - today).days
                    if 0 <= days_to_dividend <= 3:
                        opportunities.append({
                            'etf': etf,
                            'action': 'PREPARE',
                            'dividend_date': div_date_str,
                            'days_to_dividend': days_to_dividend,
                            'priority': self.get_etf_priority(etf),
                            'reason': f'{days_to_dividend}天後除息，準備清倉',
                            'confidence': 'high'
                        })
                        
                except ValueError:
                    continue
        
        return sorted(opportunities, key=lambda x: x['priority'])
    
    def get_etf_priority(self, etf):
        """ETF優先級（基於策略分析結果）"""
        priority_map = {
            '0056': 1,   # 最高優先級：平均報酬9.43%
            '00919': 2,  # 中優先級：平均報酬6.26%
            '00878': 3   # 低優先級：平均報酬5.56%
        }
        return priority_map.get(etf, 999)
    
    def get_latest_prices(self):
        """從Firebase取得最新價格"""
        latest_prices = {}
        
        for etf in self.etfs:
            price_data = self.get_from_firebase(f"latest_prices/{etf}")
            if price_data:
                latest_prices[etf] = price_data
            else:
                latest_prices[etf] = {
                    'latest_price': None,
                    'latest_date': None,
                    'error': 'No data available'
                }
        
        return latest_prices
    
    def generate_analysis_report(self, opportunities, latest_prices, update_status):
        """生成分析報告並保存到Firebase"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_date': date.today().isoformat(),
            'opportunities': opportunities,
            'latest_prices': latest_prices,
            'update_status': update_status,
            'summary': {
                'total_opportunities': len(opportunities),
                'buy_signals': len([o for o in opportunities if o['action'] == 'BUY']),
                'prepare_signals': len([o for o in opportunities if o['action'] == 'PREPARE']),
                'high_confidence': len([o for o in opportunities if o.get('confidence') == 'high'])
            }
        }
        
        # 保存每日分析報告
        daily_path = f"daily_analysis/{report['analysis_date']}"
        self.save_to_firebase(daily_path, report)
        
        # 更新最新狀態（供外部快速查詢）
        latest_status = {
            'last_update': report['timestamp'],
            'opportunities': opportunities,
            'summary': report['summary'],
            'status': 'active' if opportunities else 'monitoring'
        }
        
        self.save_to_firebase("latest_status", latest_status)
        
        return report
    
    def print_analysis_summary(self, report):
        """印出分析摘要"""
        print("\n" + "="*60)
        print("🎯 ETF除息策略分析報告")
        print("="*60)
        print(f"📅 分析日期: {report['analysis_date']}")
        print(f"⏰ 分析時間: {datetime.fromisoformat(report['timestamp']).strftime('%H:%M:%S')}")
        print(f"🔥 資料儲存: Firebase")
        
        # 資料更新狀況
        print(f"\n📊 資料更新狀況:")
        for etf, status in report['update_status'].items():
            emoji = "✅" if status else "❌"
            print(f"  {emoji} {etf}: {'成功' if status else '失敗'}")
        
        # 最新價格
        print(f"\n💰 最新價格:")
        for etf, data in report['latest_prices'].items():
            if data.get('latest_price'):
                print(f"  {etf}: ${data['latest_price']:.2f} ({data['latest_date']})")
            else:
                print(f"  {etf}: 資料更新中...")
        
        # 交易機會
        opportunities = report['opportunities']
        if opportunities:
            print(f"\n🎯 交易機會 ({len(opportunities)}個):")
            for opp in opportunities:
                emoji = "🟢" if opp['action'] == 'BUY' else "🟡"
                confidence_icon = "⭐" if opp.get('confidence') == 'high' else ""
                print(f"  {emoji} {opp['etf']}: {opp['action']} {confidence_icon}")
                print(f"     {opp['reason']}")
        else:
            print(f"\n😴 目前沒有交易機會")
        
        # Firebase連結
        firebase_domain = self.firebase_url.replace('https://', '').replace('.firebasedatabase.app/', '')
        print(f"\n🔗 Firebase控制台:")
        print(f"   https://console.firebase.google.com/project/{firebase_domain.split('-')[0]}/database")
        
        print("="*60)

def main():
    analyzer = FirebaseETFAnalyzer()
    
    print("🚀 開始ETF Firebase分析...")
    
    # 1. 更新所有ETF資料到Firebase
    print("\n📊 更新ETF資料到Firebase...")
    update_status = {}
    for etf in analyzer.etfs:
        update_status[etf] = analyzer.update_etf_data_to_firebase(etf)
    
    # 2. 分析交易機會
    print("\n🔍 分析交易機會...")
    opportunities = analyzer.analyze_dividend_opportunities()
    
    # 3. 取得最新價格
    print("\n💰 取得最新價格...")
    latest_prices = analyzer.get_latest_prices()
    
    # 4. 生成報告並保存到Firebase
    print("\n📋 生成分析報告...")
    report = analyzer.generate_analysis_report(opportunities, latest_prices, update_status)
    
    # 5. 顯示結果
    analyzer.print_analysis_summary(report)
    
    # 6. 輸出給GitHub Actions
    print(f"\n📈 GitHub Actions 摘要:")
    print(f"Firebase連線: ✅")
    print(f"資料更新: {sum(update_status.values())}/{len(update_status)} 成功")
    print(f"交易機會: {len(opportunities)} 個")
    print(f"報告儲存: Firebase")
    
    return report

if __name__ == "__main__":
    main()
