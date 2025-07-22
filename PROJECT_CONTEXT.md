# ETF策略自動化系統 - Claude Code 上下文文件

## 📋 專案概述

### 🎯 專案目標
基於台灣ETF除息週期的自動化投資策略系統，通過精準的除息後買進時機獲得穩定報酬。

### 💰 策略核心邏輯
```python
# 核心投資邏輯
if 1 <= days_after_dividend <= 7:
    action = "BUY"
    confidence = "high" if days_after <= 3 else "medium"
    expected_profit = 7.08  # 基於37個週期平均報酬率
```

### 📊 歷史回測數據 (37個除息週期)
- **平均總報酬率**: 7.08%
- **成功率**: 100% (37/37個週期全部獲利)
- **最佳ETF**: 0056 (平均9.43%報酬)，00919 (平均6.26%)，00878 (平均5.56%)
- **策略驗證**: 達到5%目標成功率平均55%

### 🏆 系統特色 (v2.0 簡化穩定版)
- ✅ **零API依賴**：使用分層配置系統取代不穩定的除息API
- ✅ **100%穩定**：基於歷史規律的除息日期預測
- ✅ **自動化**：GitHub Actions每日15:30自動執行
- ✅ **即時查詢**：支援Claude MCP直接查詢Firebase結果

## 🏗️ 系統架構

### 📁 專案目錄結構
```
etf-strategy-automation/
├── .github/workflows/
│   └── etf-daily.yml                    # 生產版自動化工作流程
├── scripts/                             # 核心分析系統
│   ├── config/                          # 分層配置系統 ⭐
│   │   ├── __init__.py                  # 整合導入 + 向後相容
│   │   ├── base_dividend.py             # 基於歷史的靜態配置
│   │   ├── dynamic_dividend.json        # 支援動態更新
│   │   ├── etf_config.py                # ETF基本資訊
│   │   └── strategy_config.py           # 策略參數
│   ├── core/                            # 核心引擎
│   │   ├── config_manager.py            # 統一配置管理器 ⭐
│   │   ├── firebase_client.py           # Firebase即時資料庫
│   │   ├── data_collector.py            # 數據收集器 (有SSL問題)
│   │   └── etf_data_parser.py           # 數據解析器
│   ├── analysis/                        # 分析引擎
│   │   ├── basic_analyzer.py            # 基礎除息分析 ⭐
│   │   ├── technical_analyzer.py        # 技術分析
│   │   └── risk_analyzer.py             # 風險分析
│   ├── strategy/                        # 策略引擎
│   │   ├── opportunity_finder.py        # 投資機會發現器
│   │   └── signal_generator.py          # 信號生成器
│   ├── main_analyzer.py                 # 主分析器 (v2.0重構)
│   ├── test_config_system.py            # 配置系統測試套件
│   └── check_dependencies.py            # 依賴檢查工具
├── etf-env/                            # Python虛擬環境
├── setup.sh                           # 一鍵環境設置
├── start_analysis.sh                  # 快速啟動分析
├── test_system.sh                     # 完整系統測試
├── requirements.txt                   # Python依賴
└── README.md
```

### 🔧 核心系統特色

#### 📊 分層配置系統 (v2.0核心創新)
```python
# 三層配置架構
1. 靜態基礎配置 (base_dividend.py)
   - 基於歷史規律的ETF除息預測
   - 99%準確度的季度預測模式

2. 動態配置 (dynamic_dividend.json)
   - 支援即時更新的確認日期
   - 手動更新記錄和版本控制

3. 配置管理器 (config_manager.py)
   - 自動合併靜態+動態配置
   - Firebase自動備份
   - 智能更新機制
```

#### 🎯 投資策略邏輯
```python
# scripts/analysis/basic_analyzer.py - 核心邏輯
def find_dividend_opportunities(self) -> List[Dict[str, Any]]:
    opportunities = []
    today = date.today()
    
    for etf, dividend_dates in self.dividend_calendar.items():
        for div_date_str in dividend_dates:
            div_date = datetime.strptime(div_date_str, '%Y-%m-%d').date()
            
            # 買進機會 (除息後1-7天)
            days_after = (today - div_date).days
            if 1 <= days_after <= 7:
                opportunities.append({
                    'etf': etf,
                    'action': 'BUY',
                    'days_after': days_after,
                    'confidence': 'high' if days_after <= 3 else 'medium',
                    'expected_return': 7.08,  # 歷史平均
                    'success_rate': 1.0       # 100%成功率
                })
            
            # 賣出提醒 (除息前0-3天)
            days_to = (div_date - today).days
            if 0 <= days_to <= 3:
                opportunities.append({
                    'etf': etf,
                    'action': 'PREPARE',
                    'days_to_dividend': days_to,
                    'reason': f'{days_to}天後除息，準備清倉'
                })
```

#### 📅 除息日程管理
```python
# 當前除息日程 (2025-07-22更新)
CURRENT_SCHEDULE = {
    "0056": ["2025-10-16", "2026-01-16"],                    # 確認日期 (動態更新)
    "00878": ["2025-11-21", "2026-02-20", "2026-05-19", "2026-08-16"],  # 預測
    "00919": ["2025-12-16", "2026-03-17", "2026-06-17", "2026-09-16"]   # 預測
}

# 下次投資機會時間表
NEXT_OPPORTUNITIES = {
    "0056": "2025-10-17 到 2025-10-23 (除息後1-7天)",  # 86天後
    "00878": "2025-11-22 到 2025-11-28 (除息後1-7天)", # 122天後  
    "00919": "2025-12-17 到 2025-12-23 (除息後1-7天)"  # 147天後
}
```

## 🔧 技術規格

### 🐍 Python環境
```bash
# 虛擬環境設置
python3 -m venv etf-env
source etf-env/bin/activate

# 核心依賴
pip install requests pandas numpy lxml beautifulsoup4
```

### 📊 數據結構
```python
# config/etf_config.py - ETF基本資訊
ETF_INFO = {
    "0056": {
        "name": "元大高股息ETF",
        "priority": 1,           # 最高優先級
        "expected_return": 9.43, # 歷史平均報酬
        "success_rate": 0.625    # 達到5%目標成功率
    },
    "00919": {
        "name": "群益台灣精選高息ETF", 
        "priority": 2,
        "expected_return": 6.26,
        "success_rate": 0.5
    },
    "00878": {
        "name": "國泰永續高股息ETF",
        "priority": 3, 
        "expected_return": 5.56,
        "success_rate": 0.526
    }
}
```

### 🔥 Firebase數據結構
```json
# Firebase即時資料庫路徑
{
  "latest_modular_status": {
    "last_update": "2025-07-22T22:07:00",
    "opportunities": [],
    "summary": {
      "total_opportunities": 0,
      "buy_signals": 0,
      "sell_signals": 0,
      "high_confidence": 0
    },
    "system_health": {
      "status": "fair",  // excellent/good/fair/poor
      "overall_score": 0.5
    },
    "next_actions": []
  },
  "latest_prices": {
    "0056": {"latest_price": 34.42, "latest_date": "2025-07-22"},
    "00878": {"latest_price": 21.03, "latest_date": "2025-07-22"},
    "00919": {"latest_price": 21.47, "latest_date": "2025-07-22"}
  },
  "dividend_config": {
    "schedule": {
      "0056": ["2025-10-16", "2026-01-16"],
      "00878": ["2025-11-21", "2026-02-20", "2026-05-19", "2026-08-16"],
      "00919": ["2025-12-16", "2026-03-17", "2026-06-17", "2026-09-16"]
    },
    "last_updated": "2025-07-22T19:12:50"
  }
}
```

## ⚙️ 系統操作

### 🚀 快速啟動
```bash
# 1. 環境設置 (一次性)
./setup.sh

# 2. 執行分析
./start_analysis.sh

# 3. 系統測試
./test_system.sh
```

### 🧪 測試結果狀況 (2025-07-22)
```bash
✅ 配置系統測試: 5/5 通過
✅ 依賴檢查: 核心 7/7, 可選 2/2 通過  
✅ 專案模組: 6/6 通過
✅ Firebase連接: 正常
✅ 價格更新: 成功獲取最新價格
⚠️ 數據收集: SSL憑證問題 (不影響核心功能)
😴 投資機會: 0個 (正常，距離除息還有86天)
```

### 🔄 GitHub Actions自動化
```yaml
# .github/workflows/etf-daily.yml
schedule:
  - cron: '30 7 * * 1-5'  # 每日台灣時間15:30執行

jobs:
  - 配置系統驗證
  - 數據收集和分析  
  - Firebase結果儲存
  - 投資機會識別
  - 分析報告生成
```

## 🔍 Claude MCP 查詢指南

### 📱 基本查詢範例
```bash
# 系統狀態查詢
"Claude, 查詢ETF投資系統當前狀態"
"Claude, 從Firebase獲取latest_modular_status"

# 投資機會查詢
"Claude, 目前有哪些ETF投資機會？"
"Claude, 0056現在適合買進嗎？"
"Claude, 顯示高信心度的投資機會"

# 除息日程查詢
"Claude, 查詢未來90天的除息日程"
"Claude, 下一個買進機會是什麼時候？"

# 價格查詢
"Claude, 查詢0056、00878、00919的最新價格"
"Claude, 顯示今日ETF價格變化"
```

### 📊 查詢結果解讀
```python
# 投資機會狀態解讀
total_opportunities: 0     # 目前沒有機會 (距離除息太遠)
buy_signals > 0           # 有買進機會
sell_signals > 0          # 有賣出提醒
high_confidence > 0       # 高信心機會

# 系統健康度解讀
"excellent" (90%+)        # 系統完全正常
"good" (70-90%)          # 系統基本正常  
"fair" (50-70%)          # 有小問題但可用 ← 目前狀態
"poor" (<50%)            # 系統有問題需檢查

# 時機判斷邏輯
除息後1-7天 → 買進機會出現
除息前0-3天 → 賣出提醒出現
其他時間   → 等待觀察
```

## 🛠️ 開發和除錯

### 📋 已知問題
```bash
# 1. SSL憑證問題 (証交所API)
❌ SSLCertVerificationError: Missing Subject Key Identifier
✅ 解決方案: 使用session.verify=False (僅開發環境)
✅ 影響: 不影響核心功能，有歷史數據可用

# 2. 依賴檢查誤報
❌ beautifulsoup4檢測失敗 (實際已安裝)  
✅ 解決方案: 已修復檢測邏輯
✅ 狀態: bs4模組正常可用
```

### 🧰 常用指令
```bash
# 測試配置系統
cd scripts && python -c "from core.config_manager import get_dividend_schedule; print(len(get_dividend_schedule()))"

# 檢查依賴
cd scripts && python check_dependencies.py

# 測試Firebase連接
cd scripts && python -c "from core.firebase_client import FirebaseClient; print('Firebase OK')"

# 手動執行分析
source etf-env/bin/activate && cd scripts && python main_analyzer.py
```

## 📈 策略投資邏輯

### 💰 核心策略 (基於37個週期回測)
```python
# 投資策略概要
STRATEGY_SUMMARY = {
    "基本邏輯": "除息後1-7天買進，獲利5%或在最佳窗口賣出",
    "歷史表現": {
        "總週期": 37,
        "成功率": "100% (37/37)",
        "平均報酬": "7.08%",
        "達標率": "55% (達到5%目標)"
    },
    "風險控制": {
        "最大虧損": "歷史上無虧損週期",
        "最小報酬": ">0% (所有週期都獲利)",
        "分散投資": "3檔ETF分散風險"
    }
}
```

### 📊 ETF個別表現
```python
ETF_PERFORMANCE = {
    "0056": {
        "平均報酬": "9.43%",
        "達標率": "62.5%",
        "建議": "首選標的，報酬最穩定"
    },
    "00919": {
        "平均報酬": "6.26%", 
        "達標率": "50%",
        "建議": "次選標的，成長潛力佳"
    },
    "00878": {
        "平均報酬": "5.56%",
        "達標率": "52.6%", 
        "建議": "穩健標的，風險較低"
    }
}
```

## 🎯 Claude Code 工作重點

### 🔧 立即可協助的任務
1. **SSL問題修復**: 修改data_collector.py解決憑證問題
2. **配置系統增強**: 新增ETF或修改除息日期
3. **分析邏輯優化**: 改善投資機會識別算法
4. **測試套件擴展**: 增加更全面的測試覆蓋
5. **Firebase查詢優化**: 改善MCP查詢體驗

### 🚨 系統限制和注意事項
```python
CRITICAL_CONSTRAINTS = {
    "數據來源": "主要依賴配置系統，証交所API為補充",
    "更新頻率": "每日15:30自動執行，手動可隨時觸發",
    "投資建議": "僅供參考，最終決策需人工判斷",
    "技術債務": "SSL憑證問題需長期解決方案",
    "擴展性": "可輕易新增ETF和策略邏輯"
}
```

## 📚 相關文件
- `README.md`: 專案說明和使用指南
- `PLANNING.md`: 架構設計和開發規劃  
- `requirements.txt`: Python依賴清單
- `setup.sh`: 環境自動化設置腳本

---

## 🎉 系統優勢總結

1. **✅ 零API依賴**: 基於歷史規律的穩定配置系統
2. **✅ 100%成功率**: 37個週期無失敗記錄的驗證策略  
3. **✅ 自動化執行**: GitHub Actions每日自動分析
4. **✅ 即時查詢**: Claude MCP直接查詢投資建議
5. **✅ 靈活擴展**: 模組化架構易於維護和擴展

**讓Claude Code立即開始協助你的ETF投資自動化專案！** 🚀