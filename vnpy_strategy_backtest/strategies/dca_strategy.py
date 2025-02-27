from vnpy.trader.utility import BarGenerator
from vnpy.trader.object import TickData, BarData
from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    Direction
)

from datetime import datetime, time

class DCAStrategy(CtaTemplate):
    """
    定期定額策略
    """
    author = "vnpy"

    # 策略參數
    fixed_amount = 10000        # 每次投入金額
    invest_interval = 20        # 投資間隔（交易日）
    
    # 策略變量
    day_count = 0              # 交易日計數器
    traded_today = False       # 今日是否已交易
    current_pos = 0            # 當前持倉

    parameters = ["fixed_amount", "invest_interval"]
    variables = ["day_count", "traded_today", "current_pos"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """初始化"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        print(f"create DCAStrategy, setting: {setting}")
        # 創建K線生成器
        self.bg = BarGenerator(self.on_bar)
        self.invest_interval = setting["invest_interval"]
        self.fixed_amount = setting["fixed_amount"]


        
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(10)  # 加載10天的歷史數據
    
    def on_start(self):
        """策略啟動"""
        self.write_log("策略啟動")
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")

    def on_bar(self, bar: BarData):
        """K線更新"""

        # 更新交易日計數
        
        self.day_count += 1

        # 檢查是否達到投資間隔
        if self.day_count >= self.invest_interval:
            # 計算可買入的股數
            price = bar.close_price
            shares = int(self.fixed_amount / price)
            
            if shares > 0:
                # 發出買入委託
                self.buy(price, shares)
                self.write_log(f"定期定額買入信號：{shares}股，價格：{price}")
                
            # 重置計數器和標記
            self.day_count = 0


    def on_order(self, order: OrderData):
        """委託更新"""
        pass

    def on_trade(self, trade: TradeData):
        """成交更新"""
        # 更新持倉
        if trade.direction == Direction.LONG:
            self.current_pos += trade.volume
        else:
            self.current_pos -= trade.volume
            
        self.write_log(f"成交：{trade.direction} {trade.volume}股，當前持倉：{self.current_pos}")

    def on_stop_order(self, stop_order: StopOrder):
        """停止單更新"""
        pass