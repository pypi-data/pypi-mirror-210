class FutureSnapshot(object):
    """
    期货快照定义参考 pb/Quotation.proto #Future
        string code = 1;                                    //合约代码
        string exchange = 2;                                //交易所代码
        string tradeDay = 3;                                //交易日
        string updateTime = 4;                              //行情更新时间
        int32  updateMilliSecond = 5;                       //行情更新毫秒
        double lastPrice = 6;                               //成交价格
        int32  volume = 7;                                  //成交量
        double openPrice = 8;                               //开盘价格
        double highestPrice = 9 ;                           //交易日最高价格
        double lowestPrice = 10;                           //交易日最低价格
        double closePrice = 11;                             //收盘价，盘中无效
        double suttlementPrice = 12;                        //交易日结算价格，盘中无效
        double limitUpPrice = 13;                           //交易日合约涨停价格
        double limitDownPrice = 14;                         //交易日合约跌停价格
        double turnover = 15;                               //成交额
        int64  openInterest = 16;                           //持仓量
        double preClosePrice = 17;                          //昨收盘价格
        double preSettlementPrice = 18;                     //昨结算价格
        int64  preOpenInterest = 19;                        //昨持仓量
        string actionDay = 20;                              //业务日期
        double askPrice1 = 21;                              //卖一价
        double askPrice2 = 22;                              //卖二价
        double askPrice3 = 23;                              //卖三价
        double askPrice4 = 24;                              //卖四价
        double askPrice5 = 25;                              //卖五价
        int32  askVolume1 = 26;                             //卖一量
        int32  askVolume2 = 27;                             //卖二量
        int32  askVolume3 = 28;                             //卖三量
        int32  askVolume4 = 29;                             //卖四量
        int32  askVolume5 = 30;                             //卖五量
        double bidPrice1 = 31;                              //买一价
        double bidPrice2 = 32;                              //买二价
        double bidPrice3 = 33;                              //买三价
        double bidPrice4 = 34;                              //买四价
        double bidPrice5 = 35;                              //买五价
        int32  bidVolume1 = 36;                             //买一量
        int32  bidVolume2 = 37;                             //买二量
        int32  bidVolume3 = 38;                             //买三量
        int32  bidVolume4 = 39;                             //买四量
        int32  bidVolume5 = 40;                             //买五量
    """


class StockSnapshot(object):
    """
    股票快照定义参考 pb/Quotation.proto #Stock
        价格相关字段为真实价格×10000
        string szWindCode = 1;      //Wind代码
        string szCode = 2;      //原始代码
        int32 nActionDay = 3;      //业务发生日
        int32 nTradingDay = 4;  //交易日
        int32 nTime = 5;   //交易时间
        int32 nStatus = 6;
        int64 nPreClose = 7;  //前收盘价
        int64 nOpen = 8;  //开盘价
        int64 nHigh = 9;  //最高价
        int64 nLow = 10;  //最低价
        int64 nMatch = 11; 当前价
        int64 nAskPrice_0 = 12;   //卖10档
        int64 nAskPrice_1 = 13;
        int64 nAskPrice_2 = 14;
        int64 nAskPrice_3 = 15;
        int64 nAskPrice_4 = 16;
        int64 nAskPrice_5 = 17;
        int64 nAskPrice_6 = 18;
        int64 nAskPrice_7 = 19;
        int64 nAskPrice_8 = 20;
        int64 nAskPrice_9 = 21;
        int64 nAskVol_0 = 22;
        int64 nAskVol_1 = 23;
        int64 nAskVol_2 = 24;
        int64 nAskVol_3 = 25;
        int64 nAskVol_4 = 26;
        int64 nAskVol_5 = 27;
        int64 nAskVol_6 = 28;
        int64 nAskVol_7 = 29;
        int64 nAskVol_8 = 30;
        int64 nAskVol_9 = 31;
        int64 nBidPrice_0 = 32;  //买十档
        int64 nBidPrice_1 = 33;
        int64 nBidPrice_2 = 34;
        int64 nBidPrice_3 = 35;
        int64 nBidPrice_4 = 36;
        int64 nBidPrice_5 = 37;
        int64 nBidPrice_6 = 38;
        int64 nBidPrice_7 = 39;
        int64 nBidPrice_8 = 40;
        int64 nBidPrice_9 = 41;
        int64 nBidVol_0 = 42;
        int64 nBidVol_1 = 43;
        int64 nBidVol_2 = 44;
        int64 nBidVol_3 = 45;
        int64 nBidVol_4 = 46;
        int64 nBidVol_5 = 47;
        int64 nBidVol_6 = 48;
        int64 nBidVol_7 = 49;
        int64 nBidVol_8 = 50;
        int64 nBidVol_9 = 51;
        int32 nNumTrades = 52;
        int64 iVolume = 53;   //成交量：股
        int64 iTurnover = 54; //成交额
        int64 nTotalBidVol = 55;
        int64 nTotalAskVol = 56;
        int64 nHighLimited = 61; //涨停价
        int64 nLowLimited = 62;  //跌停价
        int32 nLocalTime = 67;
    """


class BarData(dict):
    """
        Bar定义
    """

    @property
    def code(self):
        """
        证券代码
        :return:
        """
        return self["code"]

    @property
    def symbol(self):
        """
        证券标识
        :return:
        """
        return self["symbol"]

    @property
    def time(self):
        """
        时间
        :return:
        """
        return self["time"]

    @property
    def close(self):
        """
        收盘价
        :return:
        """
        return self["close"]

    @property
    def open(self):
        """
        开盘价
        :return:
        """
        return self["open"]

    @property
    def high(self):
        """
        最高价
        :return:
        """
        return self["high"]

    @property
    def low(self):
        """
        最低价
        :return:
        """
        return self["low"]

    @property
    def pre_close(self):
        """
        前收价
        :return:
        """
        return self["pre_close"]

    @property
    def amount(self):
        """
        成交额
        :return:
        """
        return self["amount"]

    @property
    def vol(self):
        """
        成交量
        :return:
        """
        return self["vol"]

    @property
    def change(self):
        """
        涨跌
        :return:
        """
        return self["change"]

    @property
    def change_pct(self):
        """
        涨跌幅
        :return:
        """
        return self["change_pct"]

    @property
    def vol(self):
        """
        成交量
        :return:
        """
        return self["vol"]

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __str__(self):
        return super(BarData, self).__str__()

    def __repr__(self):
        return super(BarData, self).__repr__()


class RunContext(object):

    def __init__(self, config):
        self._config = config


class Order(object):

    def __init__(self,
                 code=None,
                 order_original_id=None,
                 order_side=0,
                 order_type=1,
                 quantity=0,
                 price=0,
                 position_type=0,
                 sid=None,
                 tid=None,
                 account_no=None,
                 status="未知",
                 frozen=0.0,
                 order_exchange_id=None,
                 fill_quantity=0,
                 placed_time=None,
                 fill_amount=0,
                 trade_date=None,
                 message="",
                 exchange=None,
                 clear_amount=0.0,
                 create_time=None):
        self.code = code
        self.order_original_id = order_original_id
        self.order_side = order_side
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.frozen = frozen
        self.position_type = position_type
        self.sid = sid
        self.tid = tid
        self.account_no = account_no
        self.status = status
        self.order_exchange_id = order_exchange_id
        self.fill_quantity = fill_quantity
        self.placed_time = placed_time
        self.fill_amount = fill_amount
        self.trade_date = trade_date
        self.message = message
        self.exchange = exchange
        self.clear_amount = clear_amount
        self.create_time = create_time
        # 买入冻结
        self._frozen_price = 0
        self._frozen_quantity = 0
        # 卖出冻结
        self._frozen_share = 0

    def __repr__(self):
        return f"id:{self.order_original_id},code:{self.code},quantity:{self.quantity},order_side:{self.order_side}"