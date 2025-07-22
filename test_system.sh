#!/bin/bash

# ETF系統測試腳本

echo "🧪 ETF系統測試..."

# 激活虛擬環境
source etf-env/bin/activate

# 執行測試
cd scripts
echo "1. 依賴檢查測試..."
python check_dependencies.py

echo ""
echo "2. 配置系統測試..."
python test_config_system.py

echo "🎉 系統測試完成！"
