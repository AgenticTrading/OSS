from vnpy_portfoliostrategy import BacktestingEngine
from strategies.rs_rank_strategy import RSRankingStopLossPortfolioStrategy
from datetime import datetime
from data_tools.yf_data_importer import YFinanceDataImporter
from vnpy.trader.constant import Interval
from vnpy.trader.engine import MainEngine, EventEngine
from vnpy_datamanager import ManagerEngine
from vnpy.trader.constant import Exchange
import argparse

def set_yf_datafeed() -> None:
    from vnpy.trader import datafeed
    datafeed.datafeed = YFinanceDataImporter()

def load_data(ticker: str, start_date: str, end_date: str, interval: Interval) -> None:
    data_manager = ManagerEngine(main_engine=MainEngine(), event_engine=EventEngine())
    data_manager.download_bar_data(
        symbol=ticker,
        exchange=Exchange.NYSE,
        interval=interval,
        start=start_date,
        # end=end_date, ManagerEngine 不支持 end 參數
        output=print
    )

def parse_arguments():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description="VNPy回測程序")
    
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
        "--capital",
        type=float,
        default=1_000_000,
        help="初始資金 (默認: 1,000,000)"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # 解析命令行參數
    args = parse_arguments()

    set_yf_datafeed()

    # 定義標的
    SYMBOLS = [
        # S&P 500 RS指標必須要的標的
        '^GSPC',
        # 科技股
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC", "CRM",
        "HIMS"
    ]

    # 載入所有標的的歷史數據
    for symbol in SYMBOLS:
        try:
            load_data(symbol, args.start, args.end, Interval.DAILY)
            print(f"成功載入 {symbol} 的歷史數據")
        except Exception as e:
            print(f"載入 {symbol} 時發生錯誤: {str(e)}")

    # 創建 Portfolio Engine
    engine = BacktestingEngine()


    engine.set_parameters(
        vt_symbols=[f"{symbol}.NYSE" for symbol in SYMBOLS],  # 添加所有標的
        interval=Interval.DAILY,
        start=datetime.strptime(args.start, "%Y-%m-%d"),
        end=datetime.strptime(args.end, "%Y-%m-%d"),
        rates={f"{symbol}.NYSE": 0.0001 for symbol in SYMBOLS},  # 設置每個標的的手續費
        slippages={f"{symbol}.NYSE": 0.01 for symbol in SYMBOLS},  # 設置每個標的的滑點
        sizes={f"{symbol}.NYSE": 1 for symbol in SYMBOLS},  # 設置每個標的的交易單位
        priceticks={f"{symbol}.NYSE": 0.01 for symbol in SYMBOLS},  # 設置每個標的的價格精度
        capital=args.capital
    )

    setting = {
        "rs_period": 5,
        "select_count": 5,
        "ma_period": 10,
        "fixed_size": 10
    }

    engine.load_data()
    engine.add_strategy(RSRankingStopLossPortfolioStrategy, setting)

    # 啟動回測
    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()



