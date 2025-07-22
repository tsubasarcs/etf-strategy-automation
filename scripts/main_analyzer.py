# main_analyzer.py
"""
ETF策略主分析程式 - 簡化版（v2.0）

主要改動：
1. 移除除息API依賴 - 使用新的配置系統
2. 簡化分析流程 - 專注核心功能
3. 保持所有投資策略邏輯
4. 提高系統穩定性

版本：v2.0 - Simplified & Stable
更新日期：2025-07-22
"""

import sys
import os
from datetime import datetime, date
from typing import Dict, Any, List

# 確保路徑正確
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入模組
from core import FirebaseClient, ETFDataCollector, ETFDataParser
from strategy import OpportunityFinder
from config import ETF_LIST
from config.etf_config import get_dividend_schedule

class SimplifiedETFAnalyzer:
    """簡化版ETF策略分析器"""
    
    def __init__(self):
        print("🚀 初始化簡化版ETF策略分析系統...")
        
        # 初始化核心組件
        self.firebase_client = FirebaseClient()
        self.data_collector = ETFDataCollector()
        self.data_parser = ETFDataParser()
        self.opportunity_finder = OpportunityFinder()
        
        print("✅ 系統初始化完成")
    
    def run_daily_analysis(self) -> Dict[str, Any]:
        """執行每日分析流程（簡化版）"""
        try:
            print(f"\n🔄 開始執行每日分析流程 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 1. 載入除息配置（使用新系統）
            print(f"\n📅 第1步：載入除息配置...")
            dividend_config = self._load_dividend_configuration()
            
            # 2. 數據收集和更新
            print(f"\n📊 第2步：收集ETF數據...")
            update_status = self._update_etf_data()
            
            # 3. 載入數據進行分析
            print(f"\n📈 第3步：載入分析數據...")
            etf_data_dict = self._load_analysis_data()
            
            # 4. 尋找投資機會
            print(f"\n🎯 第4步：分析投資機會...")
            opportunities = self.opportunity_finder.find_enhanced_opportunities(etf_data_dict)
            
            # 5. 獲取最新價格
            print(f"\n💰 第5步：更新價格資訊...")
            latest_prices = self._get_latest_prices()
            
            # 6. 生成分析報告
            print(f"\n📋 第6步：生成分析報告...")
            analysis_report = self._generate_analysis_report(
                opportunities, latest_prices, update_status, dividend_config
            )
            
            # 7. 保存結果
            print(f"\n💾 第7步：保存分析結果...")
            self._save_analysis_results(analysis_report)
            
            # 8. 顯示摘要
            print(f"\n📊 第8步：顯示分析摘要...")
            self._print_analysis_summary(analysis_report)
            
            print(f"\n🎉 每日分析流程執行完成！")
            return analysis_report
            
        except Exception as e:
            print(f"\n💥 分析流程執行失敗: {e}")
            import traceback
            traceback.print_exc()
            
            # 返回錯誤報告
            return self._generate_error_report(str(e))
    
    def _load_dividend_configuration(self) -> Dict[str, Any]:
        """載入除息配置（使用新的配置系統）"""
        try:
            # 使用新的配置系統
            dividend_schedule = get_dividend_schedule()
            
            print(f"✅ 除息配置載入成功")
            print(f"📊 配置包含 {len(dividend_schedule)} 個ETF")
            
            total_dates = sum(len(dates) for dates in dividend_schedule.values())
            print(f"📅 總計 {total_dates} 個未來除息日期")
            
            # 顯示近期除息日期
            today = date.today()
            for etf_code, dates in dividend_schedule.items():
                if dates:
                    next_date = dates[0]
                    try:
                        next_date_obj = datetime.strptime(next_date, '%Y-%m-%d').date()
                        days_until = (next_date_obj - today).days
                        print(f"📅 {etf_code}: {next_date} ({days_until}天後)")
                    except:
                        print(f"📅 {etf_code}: {next_date}")
            
            return {
                'success': True,
                'schedule': dividend_schedule,
                'total_etfs': len(dividend_schedule),
                'total_dates': total_dates,
                'source': 'integrated_config_system',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 除息配置載入失敗: {e}")
            return {
                'success': False,
                'error': str(e),
                'schedule': {},
                'source': 'error',
                'last_updated': datetime.now().isoformat()
            }
    
    def _update_etf_data(self) -> Dict[str, bool]:
        """更新ETF數據（簡化版）"""
        update_status = {}
        
        print(f"📊 開始更新ETF數據...")
        
        for etf in ETF_LIST:
            print(f"  📈 更新 {etf} 數據...")
            
            try:
                # 收集歷史數據
                historical_data = self.data_collector.get_historical_data(etf)
                
                if historical_data is not None and len(historical_data) > 0:
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
                            'data_source': 'twse_api',
                            'data_points': len(historical_data)
                        }
                        self.firebase_client.save(f"latest_prices/{etf}", latest_info)
                        
                        update_status[etf] = True
                        print(f"    ✅ {etf}: 成功更新 {len(historical_data)} 筆數據")
                    else:
                        update_status[etf] = False
                        print(f"    ❌ {etf}: Firebase保存失敗")
                else:
                    update_status[etf] = False
                    print(f"    ❌ {etf}: 數據收集失敗或無數據")
                    
            except Exception as e:
                print(f"    ❌ {etf}: 更新錯誤 - {e}")
                update_status[etf] = False
        
        # 統計結果
        success_count = sum(update_status.values())
        total_count = len(ETF_LIST)
        success_rate = success_count / total_count if total_count > 0 else 0
        
        print(f"📊 數據更新完成: {success_count}/{total_count} 成功 ({success_rate:.1%})")
        
        return update_status
    
    def _load_analysis_data(self) -> Dict[str, Any]:
        """載入分析數據"""
        etf_data_dict = {}
        
        print(f"📈 開始載入分析數據...")
        
        for etf in ETF_LIST:
            print(f"  📊 載入 {etf} 分析數據...")
            
            try:
                # 從Firebase載入數據
                firebase_data = self.firebase_client.get(f"etf_data/{etf}")
                
                if firebase_data:
                    # 轉換為DataFrame格式
                    etf_df = self.data_parser.convert_from_firebase_format(firebase_data)
                    if etf_df is not None and len(etf_df) > 0:
                        etf_data_dict[etf] = etf_df
                        print(f"    ✅ {etf}: 載入成功 - {len(etf_df)} 筆數據")
                    else:
                        etf_data_dict[etf] = None
                        print(f"    ⚠️ {etf}: 數據轉換失敗")
                else:
                    etf_data_dict[etf] = None
                    print(f"    ⚠️ {etf}: Firebase無數據")
                    
            except Exception as e:
                print(f"    ❌ {etf}: 載入錯誤 - {e}")
                etf_data_dict[etf] = None
        
        # 統計結果
        successful_loads = sum(1 for data in etf_data_dict.values() if data is not None)
        print(f"📈 數據載入完成: {successful_loads}/{len(ETF_LIST)} 個ETF有可用數據")
        
        return etf_data_dict
    
    def _get_latest_prices(self) -> Dict[str, Any]:
        """獲取最新價格資訊"""
        latest_prices = {}
        
        print(f"💰 獲取最新價格資訊...")
        
        for etf in ETF_LIST:
            try:
                price_data = self.firebase_client.get(f"latest_prices/{etf}")
                if price_data:
                    latest_prices[etf] = price_data
                    price = price_data.get('latest_price', 'N/A')
                    date_str = price_data.get('latest_date', 'N/A')
                    print(f"  💰 {etf}: ${price} ({date_str})")
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
                print(f"  ❌ {etf}: 價格獲取失敗 - {e}")
        
        return latest_prices
    
    def _generate_analysis_report(self, opportunities, latest_prices, update_status, dividend_config) -> Dict[str, Any]:
        """生成分析報告"""
        
        # 分析投資機會
        buy_signals = [o for o in opportunities 
                      if o.get('final_recommendation', {}).get('action') in ['BUY', 'STRONG_BUY']]
        
        sell_signals = [o for o in opportunities 
                       if o.get('final_recommendation', {}).get('action') == 'SELL_PREPARE']
        
        high_confidence = [o for o in opportunities 
                          if o.get('enhanced_confidence') in ['high', 'very_high']]
        
        # 計算系統健康度
        data_success_rate = sum(update_status.values()) / len(update_status) if update_status else 0
        dividend_success = dividend_config.get('success', False)
        overall_health = (data_success_rate + (1 if dividend_success else 0)) / 2
        
        health_status = 'excellent' if overall_health >= 0.9 else \
                       'good' if overall_health >= 0.7 else \
                       'fair' if overall_health >= 0.5 else 'poor'
        
        # 計算數據新鮮度
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
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_date': date.today().isoformat(),
            'system_version': 'Simplified_v2.0_Stable',
            'opportunities': opportunities,
            'latest_prices': latest_prices,
            'update_status': update_status,
            'dividend_config_status': dividend_config,
            'system_health': {
                'overall_score': overall_health,
                'status': health_status,
                'data_success_rate': data_success_rate,
                'dividend_config_success': dividend_success
            },
            'summary': {
                'total_opportunities': len(opportunities),
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals),
                'high_confidence': len(high_confidence),
                'data_freshness': {
                    'freshness_rate': freshness_rate,
                    'fresh_data_count': fresh_data_count,
                    'total_data_count': len(latest_prices)
                },
                'system_features': [
                    'integrated_dividend_config',
                    'simplified_stable_architecture',
                    'enhanced_technical_analysis',
                    'comprehensive_risk_assessment',
                    'dynamic_position_sizing'
                ]
            },
            'next_actions': self._generate_next_actions(buy_signals, sell_signals)
        }
        
        return report
    
    def _generate_next_actions(self, buy_signals: List[Dict], sell_signals: List[Dict]) -> List[str]:
        """生成下一步行動建議"""
        actions = []
        
        if buy_signals:
            actions.append(f"🟢 發現 {len(buy_signals)} 個買進機會")
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
        
        try:
            # 保存每日分析報告
            daily_path = f"simplified_analysis/{report['analysis_date']}"
            success = self.firebase_client.save(daily_path, report)
            
            if success:
                print("  💾 每日報告已保存")
            else:
                print("  ⚠️ 每日報告保存失敗")
            
            # 更新最新狀態
            latest_status = {
                'last_update': report['timestamp'],
                'opportunities': report['opportunities'],
                'summary': report['summary'],
                'system_health': report['system_health'],
                'next_actions': report['next_actions'],
                'status': 'simplified_analysis_complete',
                'system_version': 'Simplified_v2.0_Stable'
            }
            
            success = self.firebase_client.save("latest_modular_status", latest_status)
            
            if success:
                print("  💾 最新狀態已更新")
            else:
                print("  ⚠️ 最新狀態更新失敗")
            
            print("  ✅ 分析結果已保存到Firebase")
            
        except Exception as e:
            print(f"  ❌ 保存分析結果失敗: {e}")
    
    def _generate_error_report(self, error_message: str) -> Dict[str, Any]:
        """生成錯誤報告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'analysis_date': date.today().isoformat(),
            'system_version': 'Simplified_v2.0_Stable',
            'status': 'error',
            'error_message': error_message,
            'opportunities': [],
            'summary': {
                'total_opportunities': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'high_confidence': 0,
                'system_status': 'failed'
            },
            'system_health': {
                'overall_score': 0,
                'status': 'critical_error'
            },
            'next_actions': ['🚨 系統錯誤，需要檢查日誌']
        }
    
    def _print_analysis_summary(self, report: Dict[str, Any]) -> None:
        """顯示分析摘要"""
        
        print(f"\n" + "="*80)
        print(f"🎯 ETF簡化版策略分析報告")
        print(f"="*80)
        print(f"📅 分析日期: {report['analysis_date']}")
        print(f"⏰ 分析時間: {datetime.fromisoformat(report['timestamp']).strftime('%H:%M:%S')}")
        print(f"🔧 系統版本: {report['system_version']}")
        print(f"✨ 系統特色: 簡化穩定架構，整合配置系統")
        
        # 系統健康度
        health = report['system_health']
        health_emoji = "🟢" if health['status'] == 'excellent' else \
                      "🟡" if health['status'] == 'good' else \
                      "🟠" if health['status'] == 'fair' else "🔴"
        print(f"\n💊 系統健康度: {health_emoji} {health['status'].upper()} ({health['overall_score']:.1%})")
        
        # 除息配置狀態
        dividend_status = report['dividend_config_status']
        if dividend_status['success']:
            print(f"📅 除息配置: ✅ 成功 ({dividend_status['total_dates']} 個日期)")
        else:
            print(f"📅 除息配置: ❌ 失敗 - {dividend_status.get('error', 'Unknown')}")
        
        # 數據更新狀況
        print(f"\n📊 數據更新狀況:")
        for etf, status in report['update_status'].items():
            emoji = "✅" if status else "❌"
            print(f"  {emoji} {etf}: {'成功' if status else '失敗'}")
        
        # 最新價格
        print(f"\n💰 最新價格:")
        for etf, data in report['latest_prices'].items():
            if data.get('latest_price'):
                price = data['latest_price']
                date_str = data['latest_date']
                print(f"  {etf}: ${price:.2f} ({date_str})")
            else:
                print(f"  {etf}: 資料載入中...")
        
        # 投資機會摘要
        opportunities = report['opportunities']
        if opportunities:
            print(f"\n🎯 投資機會總覽 ({len(opportunities)}個):")
            
            for i, opp in enumerate(opportunities, 1):
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
                
                print(f"\n  {action_emoji} #{i} {etf_code} - {action}")
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
        
        freshness = summary.get('data_freshness', {})
        if freshness:
            print(f"  數據新鮮度: {freshness['freshness_rate']:.1%}")
        
        print(f"\n" + "="*80)
        print(f"🎉 簡化版分析系統執行完成！")
        print(f"✨ 新特色：穩定配置系統，移除API依賴，專注核心分析")
        print(f"="*80)

def main():
    """主函數"""
    try:
        print(f"🎯 ETF簡化版策略分析器啟動")
        print(f"版本: v2.0 - Simplified & Stable")
        print(f"特色: 整合配置系統，移除除息API依賴")
        print(f"="*60)
        
        # 創建分析器實例
        analyzer = SimplifiedETFAnalyzer()
        
        # 執行每日分析
        result = analyzer.run_daily_analysis()
        
        # GitHub Actions 輸出摘要
        if result.get('status') != 'error':
            print(f"\n📈 GitHub Actions 執行摘要:")
            print(f"🔧 系統版本: Simplified v2.0")
            print(f"📅 除息系統: {'✅ 整合配置' if result['dividend_config_status']['success'] else '❌ 配置失敗'}")
            print(f"📊 數據更新: {sum(result['update_status'].values())}/{len(result['update_status'])} 成功")
            print(f"🎯 投資機會: {len(result['opportunities'])} 個")
            print(f"💊 系統健康: {result['system_health']['status']}")
            print(f"💾 結果保存: Firebase 簡化版分析")
            print(f"⚡ 系統狀態: 運行正常")
        else:
            print(f"\n💥 GitHub Actions 錯誤摘要:")
            print(f"❌ 錯誤訊息: {result.get('error_message', 'Unknown error')}")
            print(f"🔧 建議: 檢查系統日誌和依賴項目")
        
        return result
        
    except Exception as e:
        print(f"💥 主程式執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()