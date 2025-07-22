# Load ETF Project Context

快速載入ETF策略自動化專案的當前狀態和背景資訊。

## 執行流程

1. **讀取系統背景**
   - 載入 docs/SYSTEM_CONTEXT.md (專案核心資訊)
   - 了解投資策略、系統架構、技術規格

2. **檢查當前狀態**
   - 讀取 docs/PROJECT_STATUS.md (最新系統狀態)
   - 了解當前版本、功能狀態、已知問題

3. **瀏覽最近變更**
   - 讀取 docs/RECENT_CHANGES.md (最近更新記錄)
   - 了解最新功能、bug修復、配置變更

4. **執行狀態檢查**
   - 檢查虛擬環境: source etf-env/bin/activate
   - 驗證配置系統: cd scripts && python -c "from core.config_manager import get_dividend_schedule; print(f'✅ {len(get_dividend_schedule())} ETFs configured')"
   - 測試Firebase連接: python -c "from core.firebase_client import FirebaseClient; print('✅ Firebase OK')"

5. **總結當前狀態**
   - 報告系統健康度
   - 列出可立即協助的任務
   - 提醒重要注意事項

## 輸出格式
🎯 ETF策略系統 - 當前狀態載入完成

📊 系統基本資訊:
   版本: v2.0 簡化穩定版
   策略: 除息後1-7天買進 (37週期100%成功率)
   ETF標的: 0056, 00878, 00919

💊 系統健康檢查:
   ✅ 配置系統: 3個ETF, 10個除息日期
   ✅ Firebase連接: 正常
   ⚠️ 數據收集: SSL憑證問題 (不影響核心功能)

📅 最近更新: (從RECENT_CHANGES.md)
   2025-07-22: 分層配置系統重構完成
   2025-07-22: Firebase MCP整合準備就緒
   
🎯 可立即協助的任務:
   1. SSL憑證問題修復
   2. 配置系統功能增強  
   3. 測試覆蓋率提升
   4. Firebase查詢優化

⚠️ 重要注意事項:
   - 不可修改歷史績效數據 (37週期驗證結果)
   - 維護向後相容性 (DIVIDEND_CALENDAR API)
   - 配置系統為專案核心，變更需謹慎