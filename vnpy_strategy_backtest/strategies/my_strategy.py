from vnpy.trader.utility import BarGenerator, ArrayManager
from vnpy_ctastrategy.template import CtaTemplate, StopOrder, TickData, BarData, TradeData, OrderData

class MyStrategy(CtaTemplate):
    """
    简单的演示策略
    """
    # 策略作者
    author = "Your Name"

    # 定义参数
    window = 20  # 移动平均线周期
    
    # 定义变量
    am = None  # K线序列
    ma_value = 0  # 当前MA数值

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """
        初始化策略
        """
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        # 创建K线生成器
        self.bg = BarGenerator(self.on_bar)
        # 创建技术指标计算器
        self.am = ArrayManager()

    def on_init(self):
        """
        策略初始化
        """
        self.write_log("策略初始化")
        self.load_bar(10)  # 加载10天的历史数据

    def on_start(self):
        """
        策略启动
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        策略停止
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Tick数据更新
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        K线数据更新
        """
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        # 计算技术指标
        ma_value = self.am.sma(self.window)
        # 判断是否有交易信号
        if bar.close_price > ma_value:
            # 生成买入信号
            if not self.pos:
                self.buy(bar.close_price, 1)
        elif bar.close_price < ma_value:
            # 生成卖出信号
            if self.pos:
                self.sell(bar.close_price, 1)

        # 保存指标值
        self.ma_value = ma_value