#!/usr/bin/env python3
"""
ETF配置系統完整測試腳本

此腳本會測試：
1. 基礎配置檔案載入
2. 動態配置檔案創建和載入
3. 配置管理器功能
4. 配置合併邏輯
5. 更新機制

使用方式：
    python test_config_system.py

執行位置：scripts/ 目錄
"""

import os
import sys
import json
from datetime import datetime, date

def setup_test_environment():
    """設置測試環境"""
    print("🔧 設置測試環境...")
    
    # 確保在正確的目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"   當前目錄: {current_dir}")
    
    # 檢查目錄結構
    expected_dirs = ['config', 'core']
    for dir_name in expected_dirs:
        dir_path = os.path.join(current_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"   創建目錄: {dir_path}")
        else:
            print(f"   ✅ 目錄存在: {dir_path}")
    
    return current_dir

def test_base_config():
    """測試基礎配置"""
    print("\n📋 測試基礎配置...")
    
    try:
        # 嘗試導入基礎配置
        sys.path.insert(0, 'config')
        import base_dividend
        
        # 檢查配置內容
        patterns = base_dividend.BASE_DIVIDEND_PATTERNS
        print(f"   ✅ 基礎配置載入成功")
        print(f"   📊 包含 {len(patterns)} 個ETF")
        
        # 驗證每個ETF配置
        for etf_code, pattern in patterns.items():
            required_keys = ['name', 'frequency', 'estimated_months', 'typical_days']
            missing_keys = [key for key in required_keys if key not in pattern]
            
            if missing_keys:
                print(f"   ❌ {etf_code}: 缺少欄位 {missing_keys}")
                return False
            else:
                print(f"   ✅ {etf_code}: 配置完整")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 基礎配置導入失敗: {e}")
        print("   💡 請確保 base_dividend.py 存在於 config/ 目錄")
        return False
    except Exception as e:
        print(f"   ❌ 基礎配置測試失敗: {e}")
        return False

def test_dynamic_config():
    """測試動態配置"""
    print("\n🔄 測試動態配置...")
    
    dynamic_config_path = os.path.join('config', 'dynamic_dividend.json')
    
    try:
        if os.path.exists(dynamic_config_path):
            with open(dynamic_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"   ✅ 動態配置載入成功")
            print(f"   📅 配置版本: {config.get('config_version', 'Unknown')}")
            print(f"   ⏰ 最後更新: {config.get('last_updated', 'Unknown')}")
            
            # 檢查必要欄位
            required_sections = ['overrides', 'predictions', 'manual_updates_log']
            for section in required_sections:
                if section in config:
                    print(f"   ✅ 包含 {section} 區段")
                else:
                    print(f"   ⚠️ 缺少 {section} 區段")
            
            return True
        else:
            print(f"   ⚠️ 動態配置檔案不存在: {dynamic_config_path}")
            print("   💡 將由配置管理器自動創建")
            return True
            
    except json.JSONDecodeError as e:
        print(f"   ❌ 動態配置JSON格式錯誤: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 動態配置測試失敗: {e}")
        return False

def test_config_manager():
    """測試配置管理器"""
    print("\n🎛️ 測試配置管理器...")
    
    try:
        # 添加core目錄到路徑
        sys.path.insert(0, 'core')
        from config_manager import DividendConfigManager
        
        # 創建管理器實例
        manager = DividendConfigManager()
        print(f"   ✅ 配置管理器創建成功")
        
        # 測試獲取當前配置
        schedule = manager.get_current_schedule()
        
        if schedule:
            print(f"   ✅ 配置載入成功")
            print(f"   📊 ETF數量: {len(schedule)}")
            
            total_dates = sum(len(dates) for dates in schedule.values())
            print(f"   📅 總日期數: {total_dates}")
            
            # 顯示每個ETF的日期
            for etf_code, dates in schedule.items():
                print(f"   📈 {etf_code}: {len(dates)} 個日期")
                if dates:
                    print(f"       下次除息: {dates[0]}")
        else:
            print(f"   ❌ 配置載入失敗")
            return False
        
        # 測試配置狀態
        status = manager.get_config_status()
        print(f"   📊 配置狀態: {status['total_etfs']} 個ETF, {status['total_future_dates']} 個日期")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 配置管理器導入失敗: {e}")
        print("   💡 請確保 config_manager.py 存在於 core/ 目錄")
        return False
    except Exception as e:
        print(f"   ❌ 配置管理器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_update_mechanism():
    """測試更新機制"""
    print("\n🔄 測試更新機制...")
    
    try:
        sys.path.insert(0, 'core')
        from config_manager import DividendConfigManager
        
        manager = DividendConfigManager()
        
        # 測試更新功能
        test_dates = ["2025-10-16", "2026-01-16"]
        success = manager.update_confirmed_dates("0056", test_dates, "test_update")
        
        if success:
            print(f"   ✅ 配置更新成功")
            
            # 驗證更新結果
            updated_schedule = manager.get_current_schedule()
            updated_dates = updated_schedule.get("0056", [])
            
            print(f"   📅 0056 更新後日期: {updated_dates}")
            
            # 檢查是否包含測試日期
            if any(date in updated_dates for date in test_dates):
                print(f"   ✅ 更新日期已生效")
                return True
            else:
                print(f"   ❌ 更新日期未生效")
                return False
        else:
            print(f"   ❌ 配置更新失敗")
            return False
            
    except Exception as e:
        print(f"   ❌ 更新機制測試失敗: {e}")
        return False

def test_integration():
    """測試整合功能"""
    print("\n🔗 測試系統整合...")
    
    try:
        # 測試etf_config.py的新API
        sys.path.insert(0, 'config')
        import etf_config
        
        # 測試新的API函數
        schedule = etf_config.get_dividend_schedule()
        
        if schedule:
            print(f"   ✅ 整合API測試成功")
            print(f"   📊 通過etf_config獲取: {len(schedule)} 個ETF")
            
            # 測試ETF資訊獲取
            for etf_code in etf_config.get_supported_etfs():
                info = etf_config.get_etf_info(etf_code)
                if info:
                    print(f"   📈 {etf_code}: {info['name']} (優先級: {info['priority']})")
                else:
                    print(f"   ❌ {etf_code}: 無法獲取ETF資訊")
                    return False
            
            return True
        else:
            print(f"   ❌ 整合API測試失敗")
            return False
            
    except Exception as e:
        print(f"   ❌ 系統整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """執行完整測試"""
    print("🧪 ETF配置系統完整測試")
    print("="*60)
    
    # 設置測試環境
    current_dir = setup_test_environment()
    
    # 執行各項測試
    test_results = {
        'base_config': test_base_config(),
        'dynamic_config': test_dynamic_config(),
        'config_manager': test_config_manager(),
        'update_mechanism': test_update_mechanism(),
        'integration': test_integration()
    }
    
    # 統計結果
    passed = sum(test_results.values())
    total = len(test_results)
    
    print("\n" + "="*60)
    print("📊 測試結果摘要")
    print("="*60)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s}: {status}")
    
    print("-"*60)
    print(f"總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！配置系統運行正常")
        
        # 顯示系統狀態
        try:
            sys.path.insert(0, 'config')
            import etf_config
            print("\n📊 系統狀態:")
            etf_config.get_config_status()
        except:
            pass
            
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查配置")
        
        # 提供修復建議
        print("\n🔧 修復建議:")
        if not test_results['base_config']:
            print("   • 請確保 base_dividend.py 檔案存在且格式正確")
        if not test_results['config_manager']:
            print("   • 請確保 config_manager.py 檔案存在且可導入")
        if not test_results['integration']:
            print("   • 請檢查 etf_config.py 的新API整合")
        
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        exit_code = 0 if success else 1
        
        print(f"\n🏁 測試完成，退出碼: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 測試過程發生嚴重錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)