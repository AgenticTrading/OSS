from typing import List, Optional, Sequence, Callable
from datetime import datetime
import yfinance as yf
import pandas as pd
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.datafeed import BaseDatafeed

class YFinanceDataImporter(BaseDatafeed):
    """
    YFinance數據導入器 - 實現BaseDatafeed接口
    """
    def __init__(self):
        super().__init__()

    def query_bar_history(
        self, 
        req: HistoryRequest, 
        output: Callable = print
    ) -> Sequence[BarData]:
        """實現BaseDatafeed的查詢接口"""
        # 檢查是否從數據庫讀取
        
        # 從YFinance下載數據
        df = self.download_data(
            symbol=req.symbol,
            start=req.start,
            end=req.end,
            interval=self.convert_interval_to_yf(req.interval)
        )
        
        if df is None:
            return []

        # 轉換為BarData
        bars = self.convert_to_bar_data(
            symbol=req.symbol,
            exchange=req.exchange,
            interval=req.interval,
            df=df
        )

        return bars

    def convert_interval_to_yf(self, interval: Interval) -> str:
        """將vnpy的時間週期轉換為yfinance格式"""
        interval_map = {
            Interval.MINUTE: "1m",
            Interval.HOUR: "1h",
            Interval.DAILY: "1d",
            Interval.WEEKLY: "1wk",
        }
        return interval_map.get(interval, "1d")

    def download_data(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """從YFinance下載數據"""
        try:
            # 處理股票代碼格式
            if "." in symbol:
                symbol = symbol.split(".")[0]
            
            # 下載數據
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start,
                end=end,
                interval=interval
            )

            if df.empty:
                print(f"無法獲取{symbol}的數據")
                return None

            return df
        except Exception as e:
            print(f"下載數據時發生錯誤: {str(e)}")
            return None

    def convert_to_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        df: pd.DataFrame
    ) -> List[BarData]:
        """將DataFrame轉換為BarData列表"""
        bars = []
        for index, row in df.iterrows():
            # 處理可能的NaN值
            volume = float(row.get("Volume", 0))
            if pd.isna(volume):
                volume = 0
                
            bar = BarData(
                symbol=symbol,
                exchange=exchange,
                datetime=index.to_pydatetime(),
                interval=interval,
                volume=volume,
                open_price=float(row["Open"]),
                high_price=float(row["High"]),
                low_price=float(row["Low"]),
                close_price=float(row["Close"]),
                turnover=float(volume * row["Close"]),
                open_interest=0.0,
                gateway_name="YFINANCE"
            )
            bars.append(bar)
        return bars