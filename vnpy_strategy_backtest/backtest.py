from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy_ctastrategy.strategies.boll_channel_strategy import BollChannelStrategy
from vnpy_ctastrategy.strategies.atr_rsi_strategy import AtrRsiStrategy
from vnpy_ctastrategy.strategies.double_ma_strategy import DoubleMaStrategy
from datetime import datetime
from strategies.my_strategy import MyStrategy
from strategies.dca_strategy import DCAStrategy
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
from vnpy.trader.object import BarData
from vnpy.trader.engine import MainEngine, EventEngine
from vnpy_datamanager import ManagerEngine
from datetime import datetime, timedelta, timezone
from vnpy.trader.datafeed import BaseDatafeed
from data_tools.yf_data_importer import YFinanceDataImporter
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.constant import Interval
import csv
import os

def set_yf_datafeed() -> None:
    from vnpy.trader import datafeed
    datafeed.datafeed = YFinanceDataImporter()


def load_strategy_class(strategy_full_name: str):
    """動態加載策略類"""
    try:
        print(f"load_strategy_class: {strategy_full_name}")
        strategy_module_name, strategy_class_name = strategy_full_name.rsplit(".", 1)
        # 假設策略文件都在 strategies 目錄下
        module_name = f"{strategy_module_name.lower()}"
        strategy_module = __import__(module_name, fromlist=[strategy_module_name])
        strategy_class = getattr(strategy_module, strategy_class_name)
        return strategy_class
    except Exception as e:
        print(f"加載策略失敗: {str(e)}")
        return None

def run_backtest(
    ticker: str,
    start_date: str,
    end_date: str,
    strategy_name: str,
    interval: str = "1d",
    capital: float = 1_000_000,
    setting: dict = None,
    output_dir: str = "results"
) -> None:
    """
    運行回測
    
    參數:
        ticker (str): 交易標的代碼
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        strategy_name (str): 策略類名稱
        interval (str): K線週期
        capital (float): 初始資金
        setting (dict): 策略參數設置
    """

    # 創建回測引擎
    engine = BacktestingEngine()
    
    # 設置回測參數
    engine.set_parameters(
        vt_symbol=f"{ticker}.SMART",     # 交易標的
        interval=interval,               # K線週期
        start=datetime.strptime(start_date, "%Y-%m-%d"),
        end=datetime.strptime(end_date, "%Y-%m-%d"),
        rate=0.0001,                    # 手續費率
        slippage=0.01,                  # 滑點
        size=1,                         # 合約大小
        pricetick=0.01,                 # 價格精度
        capital=capital                 # 初始資金
    )
    
    # 加載策略
    strategy_class = load_strategy_class(strategy_name)
    if not strategy_class:
        return
    
    # 添加策略
    engine.add_strategy(strategy_class, setting or {})
    
    # 運行回測
    engine.load_data()
    engine.run_backtesting()
    
    # 統計結果
    df = engine.calculate_result()
    engine.calculate_statistics()
    
    # 輸出結果
    print("\n回測結果:")
    engine.show_chart()
    
    # 保存結果
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存交易記錄
    trades_file = os.path.join(output_dir, f"{ticker}_{strategy_name}_trades.csv")
    trades = engine.get_all_trades()
    with open(trades_file, "w", newline="") as f:
        writer = csv.writer(f)
        for trade in trades:
            print(f'{trade.datetime} {trade.symbol} {trade.exchange} {trade.orderid} {trade.direction} {trade.offset} {trade.price} {trade.volume} {trade.tradeid} {trade.gateway_name}')
            writer.writerow([trade.datetime, trade.symbol, trade.exchange, trade.orderid, trade.direction, trade.offset, trade.price, trade.volume, trade.tradeid, trade.gateway_name])

    print(f"\n交易記錄已保存至: {trades_file}")
    
def parse_arguments():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description="VNPy回測程序")
    
    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="交易標的代碼 (例如: QQQ)"
    )
    
    parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="開始日期 (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="結束日期 (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        help="策略類名稱 (例如: DCAStrategy)"
    )
    
    parser.add_argument(
        "--interval",
        type=str,
        default="1d",
        choices=["1m", "1h", "1d"],
        help="K線週期 (默認: 1d)"
    )
    
    parser.add_argument(
        "--capital",
        type=float,
        default=1_000_000,
        help="初始資金 (默認: 1,000,000)"
    )
    
    parser.add_argument(
        "--strategy_config",
        type=str,
        default=None,
        help="策略參數 (JSON格式)"
    )
    
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="輸出目錄 (默認: results)"
    )

    return parser.parse_args()

def convert_interval(interval: str) -> Interval:
    interval_map = {
        "1m": Interval.MINUTE,
        "1h": Interval.HOUR,
        "1d": Interval.DAILY
    }
    return interval_map[interval]

def load_data(ticker: str, start_date: str, end_date: str, interval: Interval) -> None:
    data_manager = ManagerEngine(main_engine=MainEngine(), event_engine=EventEngine())
    data_manager.download_bar_data(
        symbol=ticker,
        exchange=Exchange.SMART,
        interval=interval,
        start=start_date,
        # end=end_date, ManagerEngine 不支持 end 參數
        output=print
    )



if __name__ == "__main__":
    # 解析命令行參數
    args = parse_arguments()
    
    # 解析策略參數
    strategy_setting = None
    if args.strategy_config:
        import json
        try:
            with open(args.strategy_config, "r") as f:
                strategy_setting = json.load(f)
        except json.JSONDecodeError:
            print("策略參數格式錯誤，請使用正確的JSON格式")
            exit(1)

    set_yf_datafeed()
    # 加載數據
    load_data(args.ticker, args.start, args.end, convert_interval(args.interval))

    # 運行回測
    run_backtest(
        ticker=args.ticker,
        start_date=args.start,
        end_date=args.end,
        strategy_name=args.strategy,
        interval=convert_interval(args.interval),
        capital=args.capital,
        setting=strategy_setting,
        output_dir=args.output_dir
    )

