"""ETF策略主分析程式 - 模組化版本"""

import sys
import os
from datetime import datetime, date
from typing import Dict, List, Any

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入模組
from core import FirebaseClient, ETFDataCollector, ETFDataParser
from strategy import OpportunityFinder
from config import ETF_LIST

class ETFStrategyAnalyzer:
    """ETF策略分析主控制器"""
    
    def __init__(self):
        print("🚀 初始化ETF策略分析系統...")
        
        # 初始化各個組件
        self.firebase_client = FirebaseClient()
        self.data_collector = ETFDataCollector()
        self.data_parser = ETFDataParser()
        self.opportunity_finder = OpportunityFinder()
        
        print("✅ 系統初始化完成")
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """執行完整分析流程"""
        try:
            print("\n🔄 開始執行完整分析流程...")
            
            # 1. 數據收集和更新
            print("\n📊 第1步：收集和更新ETF數據...")
            update_status = self._update_all_etf_data()
            
            # 2. 載入數據進行分析
            print("\n📈 第2步：載入數據進行分析...")
            etf_data_dict = self._load_etf_data_for_analysis()
            
            # 3. 尋找投資機會
            print("\n🎯 第3步：尋找增強版投資機會...")
            opportunities = self.opportunity_finder.find_enhanced_opportunities(etf_data_dict)
            
            # 4. 獲取最新價格
            print("\n💰 第4步：獲取最新價格資訊...")
            latest_prices = self._get_latest_prices()
            
            # 5. 生成綜合報告
            print("\n📋 第5步：生成綜合分析報告...")
            comprehensive_report = self._generate_comprehensive_report(
                opportunities, latest_prices, update_status
            )
            
            # 6. 保存分析結果
            print("\n💾 第6步：保存分析結果...")
            self._save_analysis_results(comprehensive_report)
            
            # 7. 顯示分析摘要
            print("\n📊 第7步：顯示分析摘要...")
            self._print_analysis_summary(comprehensive_report)
            
            print("\n🎉 完整分析流程執行完成！")
            return comprehensive_report
            
        except Exception as e:
            print(f"\n💥 分析流程執行失敗: {e}")
            raise
    
    def _update_all_etf_data(self) -> Dict[str, bool]:
        """更新所有ETF數據"""
        update_status = {}
        
        for etf in ETF_LIST:
            print(f"  📊 更新 {etf} 數據...")
            
            try:
                # 收集歷史數據
                historical_data = self.data_collector.get_historical_data(etf)
                
                if historical_data is not None:
                    # 轉換為Firebase格式
                    firebase_data = self.data_parser.convert_to_firebase_format(historical_data)
                    
                    # 保存到Firebase
                    success = self.firebase_client.save(f"etf_data/{etf}", firebase_data)
                    
                    if success:
                        # 更新最新價格
                        latest_row = historical_data.iloc[-1]
                        latest_info = {
                            'latest_price': float(latest_row['close']),
                            'latest_date': latest_row['date'].strftime('%Y-%m-%d'),
                            'last_updated': datetime.now().isoformat()
                        }
                        self.firebase_client.save(f"latest_prices/{etf}", latest_info)
                        
                        update_status[etf] = True
                        print(f"    ✅ {etf} 更新成功")
                    else:
                        update_status[etf] = False
                        print(f"    ❌ {etf} Firebase保存失敗")
                else:
                    update_status[etf] = False
                    print(f"    ❌ {etf} 數據收集失敗")
                    
            except Exception as e:
                print(f"    ❌ {etf} 更新錯誤: {e}")
                update_status[etf] = False
        
        success_count = sum(update_status.values())
        print(f"  📊 數據更新完成: {success_count}/{len(ETF_LIST)} 成功")
        
        return update_status
    
    def _load_etf_data_for_analysis(self) -> Dict[str, Any]:
        """載入ETF數據用於分析"""
        etf_data_dict = {}
        
        for etf in ETF_LIST:
            print(f"  📈 載入 {etf} 分析數據...")
            
            try:
                # 從Firebase載入數據
                firebase_data = self.firebase_client.get(f"etf_data/{etf}")
                
                if firebase_data:
                    # 轉換為DataFrame格式
                    etf_df = self.data_parser.convert_from_firebase_format(firebase_data)
                    etf_data_dict[etf] = etf_df
                    print(f"    ✅ {etf} 載入成功: {len(etf_df)} 筆數據")
                else:
                    print(f"    ⚠️ {etf} 無可用數據")
                    etf_data_dict[etf] = None
                    
            except Exception as e:
                print(f"    ❌ {etf} 載入錯誤: {e}")
                etf_data_dict[etf] = None
        
        return etf_data_dict
    
    def _get_latest_prices(self) -> Dict[str, Any]:
        """獲取最新價格"""
        latest_prices = {}
        
        for etf in ETF_LIST:
            price_data = self.firebase_client.get(f"latest_prices/{etf}")
            latest_prices[etf] = price_data or {
                'latest_price': None,
                'latest_date': None,
                'error': 'No data available'
            }
        
        return latest_prices
    
    def _generate_comprehensive_report(self, 
                                     opportunities, 
                                     latest_prices, 
                                     update_status) -> Dict[str, Any]:
        """生成綜合分析報告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_date': date.today().isoformat(),
            'system_version': 'Modular_v1.0',
            'opportunities': opportunities,
            'latest_prices': latest_prices,
            'update_status': update_status,
            'summary': {
                'total_opportunities': len(opportunities),
                'buy_signals': len([o for o in opportunities 
                                  if o.get('final_recommendation', {}).get('action') in ['BUY', 'STRONG_BUY']]),
                'sell_signals': len([o for o in opportunities 
                                   if o.get('final_recommendation', {}).get('action') == 'SELL_PREPARE']),
                'high_confidence': len([o for o in opportunities 
                                      if o.get('enhanced_confidence') == 'very_high']),
                'analysis_features': [
                    'modular_architecture',
                    'technical_indicators',
                    'risk_assessment',
                    'position_sizing'
                ]
            }
        }
        
        return report
    
    def _save_analysis_results(self, report: Dict[str, Any]) -> None:
        """保存分析結果"""
        
        # 保存每日分析報告
        daily_path = f"modular_analysis/{report['analysis_date']}"
        self.firebase_client.save(daily_path, report)
        
        # 更新最新狀態
        latest_status = {
            'last_update': report['timestamp'],
            'opportunities': report['opportunities'],
            'summary': report['summary'],
            'status': 'modular_analysis_complete',
            'system_version': 'Modular_v1.0'
        }
        
        self.firebase_client.save("latest_modular_status", latest_status)
        
        print("  💾 分析結果已保存到Firebase")
    
    def _print_analysis_summary(self, report: Dict[str, Any]) -> None:
        """顯示分析摘要"""
        
        print("\n" + "="*80)
        print("🎯 ETF模組化策略分析報告")
        print("="*80)
        print(f"📅 分析日期: {report['analysis_date']}")
        print(f"⏰ 分析時間: {datetime.fromisoformat(report['timestamp']).strftime('%H:%M:%S')}")
        print(f"🔧 系統版本: {report['system_version']}")
        print(f"🧩 系統特色: 模組化架構，易於維護和擴展")
        
        # 數據更新狀況
        print(f"\n📊 數據更新狀況:")
        for etf, status in report['update_status'].items():
            emoji = "✅" if status else "❌"
            print(f"  {emoji} {etf}: {'成功' if status else '失敗'}")
        
        # 最新價格
        print(f"\n💰 最新價格:")
        for etf, data in report['latest_prices'].items():
            if data.get('latest_price'):
                print(f"  {etf}: ${data['latest_price']:.2f} ({data['latest_date']})")
            else:
                print(f"  {etf}: 資料載入中...")
        
        # 投資機會摘要
        opportunities = report['opportunities']
        if opportunities:
            print(f"\n🎯 投資機會總覽 ({len(opportunities)}個):")
            
            for opp in opportunities:
                etf_code = opp.get('etf', '')
                action = opp.get('final_recommendation', {}).get('action', opp.get('action', ''))
                confidence = opp.get('enhanced_confidence', 'medium')
                
                # 技術評分
                tech_score = opp.get('technical_analysis', {}).get('score', 50)
                
                # 風險等級
                risk_level = opp.get('risk_assessment', {}).get('risk_level', 'medium')
                
                # 建議配置
                allocation = opp.get('position_sizing', {}).get('suggested_allocation_pct', 0)
                
                action_emoji = {
                    'STRONG_BUY': '🔥', 'BUY': '🟢', 'CAUTIOUS_BUY': '🟡',
                    'SELL_PREPARE': '🟠', 'HOLD': '⚪', 'MONITOR': '👀'
                }.get(action, '❓')
                
                print(f"\n  {action_emoji} {etf_code}")
                print(f"     動作: {action}")
                print(f"     信心: {confidence}")
                print(f"     技術: {tech_score:.0f}/100")
                print(f"     風險: {risk_level}")
                print(f"     配置: {allocation:.1f}%")
        else:
            print(f"\n😴 目前沒有投資機會")
        
        # 系統統計
        summary = report['summary']
        print(f"\n📈 系統統計:")
        print(f"  總機會數: {summary['total_opportunities']}")
        print(f"  買進信號: {summary['buy_signals']}")
        print(f"  賣出信號: {summary['sell_signals']}")
        print(f"  高信心機會: {summary['high_confidence']}")
        
        print("\n" + "="*80)
        print("🎉 模組化分析系統執行完成！")
        print("🧩 優勢：代碼清晰、易於維護、便於擴展")
        print("="*80)

def main():
    """主函數"""
    try:
        # 創建分析器實例
        analyzer = ETFStrategyAnalyzer()
        
        # 執行完整分析
        result = analyzer.run_complete_analysis()
        
        # GitHub Actions 輸出摘要
        print(f"\n📈 GitHub Actions 執行摘要:")
        print(f"🔧 系統架構: 模組化設計")
        print(f"📊 數據更新: {sum(result['update_status'].values())}/{len(result['update_status'])} 成功")
        print(f"🎯 投資機會: {len(result['opportunities'])} 個")
        print(f"💾 結果保存: Firebase 模組化分析")
        print(f"⚡ 系統狀態: 運行正常")
        
        return result
        
    except Exception as e:
        print(f"💥 主程式執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
