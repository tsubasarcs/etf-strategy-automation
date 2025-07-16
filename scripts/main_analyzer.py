# main_analyzer.py
"""ETF策略主分析程式 - 完整更新版（包含除息API）"""

import sys
import os
from datetime import datetime, date
from typing import Dict, Any, List

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入模組
from core import FirebaseClient, ETFDataCollector, ETFDataParser
from core.dividend_collector import DividendDateCollector
from strategy import OpportunityFinder
from config import ETF_LIST

class ETFStrategyAnalyzer:
    """ETF策略分析主控制器 - 完整更新版"""
    
    def __init__(self):
        print("🚀 初始化ETF策略分析系統...")
        
        # 初始化各個組件
        self.firebase_client = FirebaseClient()
        self.data_collector = ETFDataCollector()
        self.data_parser = ETFDataParser()
        self.opportunity_finder = OpportunityFinder()
        self.dividend_collector = DividendDateCollector()
        
        print("✅ 系統初始化完成")
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """執行完整分析流程"""
        try:
            print("\n🔄 開始執行完整分析流程...")
            
            # 1. 更新除息日程表
            print("\n📅 第1步：更新除息日程表...")
            dividend_update_status = self._update_dividend_schedule()
            
            # 2. 數據收集和更新
            print("\n📊 第2步：收集和更新ETF數據...")
            update_status = self._update_all_etf_data()
            
            # 3. 載入數據進行分析
            print("\n📈 第3步：載入數據進行分析...")
            etf_data_dict = self._load_etf_data_for_analysis()
            
            # 4. 尋找投資機會
            print("\n🎯 第4步：尋找增強版投資機會...")
            opportunities = self.opportunity_finder.find_enhanced_opportunities(etf_data_dict)
            
            # 5. 獲取最新價格
            print("\n💰 第5步：獲取最新價格資訊...")
            latest_prices = self._get_latest_prices()
            
            # 6. 生成綜合報告
            print("\n📋 第6步：生成綜合分析報告...")
            comprehensive_report = self._generate_comprehensive_report(
                opportunities, latest_prices, update_status, dividend_update_status
            )
            
            # 7. 保存分析結果
            print("\n💾 第7步：保存分析結果...")
            self._save_analysis_results(comprehensive_report)
            
            # 8. 顯示分析摘要
            print("\n📊 第8步：顯示分析摘要...")
            self._print_analysis_summary(comprehensive_report)
            
            print("\n🎉 完整分析流程執行完成！")
            return comprehensive_report
            
        except Exception as e:
            print(f"\n💥 分析流程執行失敗: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _update_dividend_schedule(self) -> Dict[str, Any]:
        """更新除息日程表"""
        try:
            print("📅 從API更新除息日程表...")
            
            # 獲取最新的除息日程
            schedule = self.dividend_collector.get_etf_dividend_schedule(
                ETF_LIST, months_ahead=18  # 查詢未來18個月
            )
            
            # 更新配置文件
            config_path = os.path.join(os.path.dirname(__file__), "config", "etf_config.py")
            self.dividend_collector.update_config_file(schedule, config_path)
            
            # 保存到Firebase
            dividend_data = {
                'schedule': schedule,
                'last_updated': datetime.now().isoformat(),
                'source': 'twse_tpex_api',
                'update_method': 'automatic'
            }
            
            self.firebase_client.save('dividend_schedule/latest', dividend_data)
            
            print("✅ 除息日程表更新完成")
            
            return {
                'success': True,
                'etf_count': len(schedule),
                'total_dates': sum(len(dates) for dates in schedule.values()),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 除息日程表更新失敗: {e}")
            return {
                'success': False,
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
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
                            'last_updated': datetime.now().isoformat(),
                            'data_source': 'twse_api'
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
            try:
                price_data = self.firebase_client.get(f"latest_prices/{etf}")
                if price_data:
                    latest_prices[etf] = price_data
                    print(f"  💰 {etf}: ${price_data.get('latest_price', 'N/A')}")
                else:
                    latest_prices[etf] = {
                        'latest_price': None,
                        'latest_date': None,
                        'error': 'No data available'
                    }
                    print(f"  ⚠️ {etf}: 無價格數據")
                    
            except Exception as e:
                latest_prices[etf] = {
                    'latest_price': None,
                    'latest_date': None,
                    'error': str(e)
                }
                print(f"  ❌ {etf}: 價格獲取失敗")
        
        return latest_prices
    
    def _generate_comprehensive_report(self, 
                                     opportunities, 
                                     latest_prices, 
                                     update_status,
                                     dividend_update_status) -> Dict[str, Any]:
        """生成綜合分析報告"""
        
        # 分析投資機會
        buy_signals = [o for o in opportunities 
                      if o.get('final_recommendation', {}).get('action') in ['BUY', 'STRONG_BUY']]
        
        sell_signals = [o for o in opportunities 
                       if o.get('final_recommendation', {}).get('action') == 'SELL_PREPARE']
        
        high_confidence = [o for o in opportunities 
                          if o.get('enhanced_confidence') in ['high', 'very_high']]
        
        # 計算系統健康度
        system_health = self._calculate_system_health(update_status, dividend_update_status)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_date': date.today().isoformat(),
            'system_version': 'Enhanced_v2.0_with_API',
            'opportunities': opportunities,
            'latest_prices': latest_prices,
            'update_status': update_status,
            'dividend_update_status': dividend_update_status,
            'system_health': system_health,
            'summary': {
                'total_opportunities': len(opportunities),
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals),
                'high_confidence': len(high_confidence),
                'data_freshness': self._calculate_data_freshness(latest_prices),
                'analysis_features': [
                    'automatic_dividend_updates',
                    'api_data_collection',
                    'enhanced_technical_analysis',
                    'comprehensive_risk_assessment',
                    'dynamic_position_sizing'
                ]
            },
            'next_actions': self._generate_next_actions(buy_signals, sell_signals)
        }
        
        return report
    
    def _calculate_system_health(self, update_status: Dict[str, bool], 
                                dividend_status: Dict[str, Any]) -> Dict[str, Any]:
        """計算系統健康度"""
        
        # 數據更新健康度
        data_success_rate = sum(update_status.values()) / len(update_status) if update_status else 0
        
        # 除息更新健康度
        dividend_success = dividend_status.get('success', False)
        
        # 綜合健康度
        overall_health = (data_success_rate + (1 if dividend_success else 0)) / 2
        
        health_status = 'excellent' if overall_health >= 0.9 else \
                       'good' if overall_health >= 0.7 else \
                       'fair' if overall_health >= 0.5 else 'poor'
        
        return {
            'overall_score': overall_health,
            'status': health_status,
            'data_success_rate': data_success_rate,
            'dividend_update_success': dividend_success,
            'recommendations': self._get_health_recommendations(overall_health)
        }
    
    def _get_health_recommendations(self, health_score: float) -> List[str]:
        """獲取系統健康建議"""
        if health_score >= 0.9:
            return ["系統運行良好", "建議維持現有設置"]
        elif health_score >= 0.7:
            return ["系統基本正常", "建議檢查失敗的數據源"]
        elif health_score >= 0.5:
            return ["系統需要關注", "建議檢查網絡連接和API狀態"]
        else:
            return ["系統存在問題", "建議立即檢查所有數據源", "考慮使用備用數據源"]
    
    def _calculate_data_freshness(self, latest_prices: Dict[str, Any]) -> Dict[str, Any]:
        """計算數據新鮮度"""
        today = date.today()
        fresh_data_count = 0
        
        for etf, price_data in latest_prices.items():
            if price_data.get('latest_date'):
                try:
                    data_date = datetime.strptime(price_data['latest_date'], '%Y-%m-%d').date()
                    if (today - data_date).days <= 1:  # 1天內的數據視為新鮮
                        fresh_data_count += 1
                except:
                    pass
        
        freshness_rate = fresh_data_count / len(latest_prices) if latest_prices else 0
        
        return {
            'freshness_rate': freshness_rate,
            'fresh_data_count': fresh_data_count,
            'total_data_count': len(latest_prices),
            'status': 'fresh' if freshness_rate >= 0.8 else 'stale'
        }
    
    def _generate_next_actions(self, buy_signals: List[Dict], sell_signals: List[Dict]) -> List[str]:
        """生成下一步行動建議"""
        actions = []
        
        if buy_signals:
            actions.append(f"🟢 考慮買進 {len(buy_signals)} 個投資機會")
            for signal in buy_signals[:3]:  # 顯示前3個
                etf = signal.get('etf', '')
                confidence = signal.get('enhanced_confidence', 'medium')
                actions.append(f"  • {etf} (信心度: {confidence})")
        
        if sell_signals:
            actions.append(f"🟠 準備賣出 {len(sell_signals)} 個持倉")
            for signal in sell_signals:
                etf = signal.get('etf', '')
                actions.append(f"  • {etf} 即將除息")
        
        if not buy_signals and not sell_signals:
            actions.append("😴 目前沒有明確的投資機會")
            actions.append("🔍 建議繼續監控市場動態")
        
        return actions
    
    def _save_analysis_results(self, report: Dict[str, Any]) -> None:
        """保存分析結果"""
        
        # 保存每日分析報告
        daily_path = f"enhanced_analysis/{report['analysis_date']}"
        self.firebase_client.save(daily_path, report)
        
        # 更新最新狀態
        latest_status = {
            'last_update': report['timestamp'],
            'opportunities': report['opportunities'],
            'summary': report['summary'],
            'system_health': report['system_health'],
            'next_actions': report['next_actions'],
            'status': 'enhanced_analysis_complete',
            'system_version': 'Enhanced_v2.0_with_API'
        }
        
        self.firebase_client.save("latest_modular_status", latest_status)
        
        print("  💾 分析結果已保存到Firebase")
    
    def _print_analysis_summary(self, report: Dict[str, Any]) -> None:
        """顯示分析摘要"""
        
        print("\n" + "="*80)
        print("🎯 ETF增強版策略分析報告")
        print("="*80)
        print(f"📅 分析日期: {report['analysis_date']}")
        print(f"⏰ 分析時間: {datetime.fromisoformat(report['timestamp']).strftime('%H:%M:%S')}")
        print(f"🔧 系統版本: {report['system_version']}")
        print(f"🚀 新功能: 自動除息API更新")
        
        # 系統健康度
        health = report['system_health']
        health_emoji = "🟢" if health['status'] == 'excellent' else \
                      "🟡" if health['status'] == 'good' else \
                      "🟠" if health['status'] == 'fair' else "🔴"
        print(f"\n💊 系統健康度: {health_emoji} {health['status'].upper()} ({health['overall_score']:.1%})")
        
        # 除息更新狀態
        dividend_status = report['dividend_update_status']
        if dividend_status['success']:
            print(f"📅 除息更新: ✅ 成功 ({dividend_status['total_dates']} 個日期)")
        else:
            print(f"📅 除息更新: ❌ 失敗 - {dividend_status.get('error', 'Unknown')}")
        
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
                final_rec = opp.get('final_recommendation', {})
                action = final_rec.get('action', opp.get('action', ''))
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
                
                print(f"\n  {action_emoji} {etf_code} - {action}")
                print(f"     信心度: {confidence} | 技術: {tech_score:.0f}/100")
                print(f"     風險: {risk_level} | 建議配置: {allocation:.1f}%")
                
                # 具體建議
                reasoning = final_rec.get('reasoning', opp.get('reason', ''))
                if reasoning:
                    print(f"     建議: {reasoning}")
        else:
            print(f"\n😴 目前沒有投資機會")
        
        # 下一步行動
        print(f"\n🎯 下一步行動:")
        for action in report['next_actions']:
            print(f"  {action}")
        
        # 系統統計
        summary = report['summary']
        print(f"\n📈 系統統計:")
        print(f"  總機會數: {summary['total_opportunities']}")
        print(f"  買進信號: {summary['buy_signals']}")
        print(f"  賣出信號: {summary['sell_signals']}")
        print(f"  高信心機會: {summary['high_confidence']}")
        print(f"  數據新鮮度: {summary['data_freshness']['freshness_rate']:.1%}")
        
        print("\n" + "="*80)
        print("🎉 增強版分析系統執行完成！")
        print("🚀 新功能：自動除息API、增強風險評估、動態配置建議")
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
        print(f"🔧 系統版本: Enhanced v2.0 with API")
        print(f"📅 除息更新: {'✅ 成功' if result['dividend_update_status']['success'] else '❌ 失敗'}")
        print(f"📊 數據更新: {sum(result['update_status'].values())}/{len(result['update_status'])} 成功")
        print(f"🎯 投資機會: {len(result['opportunities'])} 個")
        print(f"💊 系統健康: {result['system_health']['status']}")
        print(f"💾 結果保存: Firebase 增強版分析")
        print(f"⚡ 系統狀態: 運行正常")
        
        return result
        
    except Exception as e:
        print(f"💥 主程式執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
