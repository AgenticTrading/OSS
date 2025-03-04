from vnpy_portfoliostrategy import StrategyTemplate
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Direction
from vnpy.trader.utility import ArrayManager


class RSRankingStopLossPortfolioStrategy(StrategyTemplate):
    """
    利用 RS Ranking 挑選強勢股，並將停損點設在移動平均線下緣
    1. 計算所有標的的相對強度(RS)
    2. 選擇RS排名最高的幾個標的做多
    3. 使用移動平均線作為停損點
    """
    author = "vnpy"

    # 策略參數
    rs_period = 252          # RS 計算期數（例如一年 252 個交易日）
    select_count = 5         # 每次挑選前幾名標的進行交易
    ma_period = 10          # 計算停損用的移動平均期數
    fixed_size = 1          # 每次交易的數量

    parameters = ["rs_period", "select_count", "ma_period", "fixed_size"]
    variables = ["trading_symbols"]

    def __init__(self, portfolio_engine, strategy_name, vt_symbols, setting):
        """
        初始化策略
        """
        super().__init__(portfolio_engine, strategy_name, vt_symbols, setting)

        # 用來存放各標的的技術指標
        self.am_dict = {}
        self.rs_dict = {}
        self.trading_symbols = []  # 當前交易的標的列表

        for symbol in self.vt_symbols:
            if symbol == "^GSPC.NYSE":
                self.spx_am = ArrayManager(self.rs_period + 20)
            self.am_dict[symbol] = ArrayManager(self.rs_period + 20)

    def on_init(self):
        """
        策略初始化
        """
        self.write_log("策略初始化")
        
        # 載入足夠的歷史數據用於計算指標
        self.load_bars(self.rs_period + 20)
        
    def on_start(self):
        """
        策略啟動
        """
        self.write_log("策略啟動")

    def on_stop(self):
        """
        策略停止
        """
        self.write_log("策略停止")

    def on_bars(self, bars: dict[str, BarData]):
        """
        K線更新
        """
        # 檢查是否有SPX數據
        if "^GSPC.NYSE" not in bars:
            return
        
        # 更新SPX數據
        spx_bar = bars["^GSPC.NYSE"]
        self.spx_am.update_bar(spx_bar)
        
        # 更新各個標的的K線數據
        for symbol, bar in bars.items():
            if symbol == "^GSPC.NYSE":  # 跳過SPX本身
                continue
                
            am = self.am_dict[symbol]
            am.update_bar(bar)

        # 如果SPX或任何標的的技術指標未初始化完成，則暫不進行交易
        if not self.spx_am.inited:
            return

        # 計算相對強度RS
        spx_close_array = self.spx_am.close_array
        spx_return = spx_close_array[-1] / spx_close_array[-self.rs_period]

        # 計算每個標的的RS值
        for symbol in self.vt_symbols:
            if symbol == "^GSPC.NYSE":
                continue
                
            am = self.am_dict[symbol]
            if not am.inited:
                continue

            close_array = am.close_array
            if len(close_array) >= self.rs_period:
                stock_return = close_array[-1] / close_array[-self.rs_period]
                rs_value = stock_return / spx_return  # 相對強度 = 個股報酬率 / 大盤報酬率
                self.rs_dict[symbol] = rs_value

        # 確保所有標的都有RS值
        if len(self.rs_dict) < len(self.vt_symbols) - 1:  # -1是因為不包括SPX
            return

        # 根據RS值排序
        ranked_symbols = sorted(self.rs_dict.items(), key=lambda x: x[1], reverse=True)

        selected_symbols = [s for s, _ in ranked_symbols[:self.select_count]]
        
        # 更新交易標的列表
        self.trading_symbols = selected_symbols

        # 對每個標的進行交易處理
        for symbol, bar in bars.items():
            # 取得技術指標
            am = self.am_dict[symbol]
            ma_value = am.sma(self.ma_period)
            current_pos = self.get_pos(symbol)

            # 交易邏輯
            if symbol in selected_symbols:
                # 強勢標的，考慮做多
                if current_pos == 0:
                    self.buy(symbol, bar.close_price, self.fixed_size)
                    print(f"[{bar.datetime}] {symbol}進場做多: 價格={bar.close_price:.2f}, 數量={self.fixed_size}")
            else:
                # 非強勢標的，平掉持倉
                if current_pos > 0:
                    self.sell(symbol, bar.close_price, abs(current_pos))
                    print(f"[{bar.datetime}] {symbol}平倉: 價格={bar.close_price:.2f}, 數量={current_pos}")

            # 檢查停損條件
            if current_pos > 0:
                if bar.close_price < ma_value:
                    self.sell(symbol, bar.close_price, abs(current_pos))
                    print(f"[{bar.datetime}] {symbol}停損: MA{self.ma_period}={ma_value:.2f}, 價格={bar.close_price:.2f}")

    def on_order(self, order):
        """
        委託更新
        """
        pass

    def on_trade(self, trade):
        """
        成交更新
        """
        self.write_log(f"成交: {trade.vt_symbol}, 方向={trade.direction}, 價格={trade.price:.2f}, 數量={trade.volume}")
