#!/bin/bash

# ETF分析系統快速啟動腳本

echo "🚀 啟動ETF分析系統..."

# 檢查虛擬環境
if [ ! -d "etf-env" ]; then
    echo "❌ 虛擬環境不存在，請先執行 ./setup.sh"
    exit 1
fi

# 激活虛擬環境
echo "🔄 激活虛擬環境..."
source etf-env/bin/activate

# 執行分析
echo "📊 開始執行分析..."
cd scripts
python main_analyzer.py

echo "🎉 分析完成！"
