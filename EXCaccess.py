# -*- coding: utf-8 -*-
from zaifapi import ZaifPublicApi, ZaifTradeApi
from decimal import Decimal, ROUND_DOWN
from TickChanger import Tick_int
import numpy
import time
import traceback
import re
import datetime


class EXCaccess:
    def __init__(self):
        self.investment = 10000  # 投資制限額
        # 予想利益額の閾値（閾値以上で注文）========================
        self.threshold_jpy_btc_mona = 300
        self.threshold_jpy_btc_bch = 150
        self.threshold_jpy_btc_xem = 150
        self.threshold_jpy_btc_eth = 150
        
        # 手数料 ( % )
        self.fee_BTC_JPY = 0
        self.fee_MONA_BTC = 0.1
        self.fee_MONA_JPY = 0.1
        self.fee_BCH_BTC = 0.3
        self.fee_BCH_JPY = 0.3
        self.fee_XEM_BTC = 0.1
        self.fee_XEM_JPY = 0.1
        self.fee_ETH_BTC = 0.1
        self.fee_ETH_JPY = 0.1
        
        # 注文確認の手がかりとして注文に付けるコメント
        self.order_comment = 'AutoTA'
        # API用キーの読み込み
        f = open('key_secret.txt', 'r')  # 本番用
        # f = open('test_keys.txt', 'r')  # テスト用
        txt = f.read()
        f.close()
        data = txt.split('\n')
        self.key = data[0]
        self.secret = data[1]
    
    def createErrorLog(self, locate: str):
        now = datetime.datetime.now()
        Path = 'error.log'
        with open(Path, 'a', newline='', encoding='shift-jis') as f:
            f.write('=====================================\n')
            f.write(str(now))
            f.write(locate)
            traceback.print_exc(file=f)
    
    # 公開情報に接続
    def getPublicAPI(self):
        while (1):
            try:
                self.zaif = ZaifPublicApi()
                break
            except:
                time.sleep(1)
    
    # 個人の情報に接続
    def getPrivateAPI(self):
        while (1):
            try:
                self.zaifp = ZaifTradeApi(self.key, self.secret)
                break
            except:
                time.sleep(1)
    
    # 余力額取得
    def getFunds(self):
        self.getPrivateAPI()
        while (1):
            try:
                result = self.zaifp.get_info2()['funds']
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getFunds')
                time.sleep(1)
        return result
    
    # 各通貨ペアの相場から買い気配値と売り気配値の中間値を返す
    # 公開情報の.currency_pairsで取得できるaux_unit_step（取引単価?）
    # BTC/JPY:5.0
    # MONA/BTC:0.00000001
    # MONA/JPY:0.1
    # BCH/BTC:0.0001
    # BCH/JPY:5.0
    # XEM/BTC:0.00000001
    # XEM/JPY:0.0001
    # ETH/BTC:0.0001
    # ETH/JPY:5.0
    # ====================================================
    # fund type: JPY BTC MONA ETH XEM BCH
    # ask:sell, bid:buy
    # [0]:value [1]:quantity
    def getBTC_JPY(self):
        while (1):
            try:
                Btc_Jpy = self.zaif.depth('btc_jpy')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getBTC_JPY')
                time.sleep(1)
        askBtcJpy = Btc_Jpy['asks'][0][0]
        bidBtcJpy = Btc_Jpy['bids'][0][0]
        aveBtcJpy = (askBtcJpy + bidBtcJpy) / 2.0
        T_aveBtcJpy = Tick_int(int(aveBtcJpy), 5)
        return T_aveBtcJpy
    
    def getMONA_JPY(self):
        while (1):
            try:
                Mona_Jpy = self.zaif.depth('mona_jpy')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getMONA_JPY')
                time.sleep(1)
        askMonaJpy = Mona_Jpy['asks'][0][0]
        bidMonaJpy = Mona_Jpy['bids'][0][0]
        aveMonaJpy = (askMonaJpy + bidMonaJpy) / 2.0
        T_aveMonaJpy = Decimal(aveMonaJpy).quantize(Decimal('0.0'),
                                                    rounding=ROUND_DOWN)
        return T_aveMonaJpy
    
    def getMONA_BTC(self):
        while (1):
            try:
                Mona_Btc = self.zaif.depth('mona_btc')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getMONA_BTC')
                time.sleep(1)
        askMonaBtc = Mona_Btc['asks'][0][0]
        bidMonaBtc = Mona_Btc['bids'][0][0]
        aveMonaBtc = (askMonaBtc + bidMonaBtc) / 2.0
        T_aveMonaBtc = Decimal(aveMonaBtc).quantize(Decimal('0.00000000'),
                                                    rounding=ROUND_DOWN)
        return T_aveMonaBtc
    
    def getBCH_JPY(self):
        while (1):
            try:
                Bch_Jpy = self.zaif.depth('bch_jpy')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getBCH_JPY')
                time.sleep(1)
        askBchJpy = Bch_Jpy['asks'][0][0]
        bidBchJpy = Bch_Jpy['bids'][0][0]
        aveBchJpy = (askBchJpy + bidBchJpy) / 2.0
        T_aveBchJpy = Tick_int(int(aveBchJpy), 5)
        return T_aveBchJpy
    
    def getBCH_BTC(self):
        while (1):
            try:
                Bch_Btc = self.zaif.depth('bch_btc')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getBCH_BTC')
                time.sleep(1)
        askBchBtc = Bch_Btc['asks'][0][0]
        bidBchBtc = Bch_Btc['bids'][0][0]
        aveBchBtc = (askBchBtc + bidBchBtc) / 2.0
        T_aveBchBtc = Decimal(aveBchBtc).quantize(Decimal('0.0000'),
                                                  rounding=ROUND_DOWN)
        return T_aveBchBtc
    
    def getXEM_JPY(self):
        while (1):
            try:
                Xem_Jpy = self.zaif.depth('xem_jpy')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getXEM_JPY')
                time.sleep(1)
        askXemJpy = Xem_Jpy['asks'][0][0]
        bidXemJpy = Xem_Jpy['bids'][0][0]
        aveXemJpy = (askXemJpy + bidXemJpy) / 2.0
        T_aveXemJpy = Decimal(aveXemJpy).quantize(Decimal('0.0000'),
                                                  rounding=ROUND_DOWN)
        return T_aveXemJpy
    
    def getXEM_BTC(self):
        while (1):
            try:
                Xem_Btc = self.zaif.depth('xem_btc')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getXEM_BTC')
                time.sleep(1)
        askXemBtc = Xem_Btc['asks'][0][0]
        bidXemBtc = Xem_Btc['bids'][0][0]
        aveXemBtc = (askXemBtc + bidXemBtc) / 2.0
        T_aveXemBtc = Decimal(aveXemBtc).quantize(Decimal('0.00000000'),
                                                  rounding=ROUND_DOWN)
        return T_aveXemBtc
    
    def getETH_JPY(self):
        while (1):
            try:
                Eth_Jpy = self.zaif.depth('eth_jpy')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getETH_JPY')
                time.sleep(1)
        askEthJpy = Eth_Jpy['asks'][0][0]
        bidEthJpy = Eth_Jpy['bids'][0][0]
        aveEthJpy = (askEthJpy + bidEthJpy) / 2.0
        T_aveEthJpy = Tick_int(int(aveEthJpy), 5)
        return T_aveEthJpy
    
    def getETH_BTC(self):
        while (1):
            try:
                Eth_Btc = self.zaif.depth('eth_btc')
                break
            except:
                traceback.print_exc()
                self.createErrorLog('getETH_BTC')
                time.sleep(1)
        askEthBtc = Eth_Btc['asks'][0][0]
        bidEthBtc = Eth_Btc['bids'][0][0]
        aveEthBtc = (askEthBtc + bidEthBtc) / 2.0
        T_aveEthBtc = Decimal(aveEthBtc).quantize(Decimal('0.0000'),
                                                  rounding=ROUND_DOWN)
        return T_aveEthBtc
    
    # 三角裁定で利益が出るか計算
    def Monitoring(self):
        fj = self.getFunds()['jpy']
        
        if fj > self.investment:
            fj = self.investment
        
        self.getPublicAPI()
        aveBtcJpy = self.getBTC_JPY()
        aveMonaJpy = self.getMONA_JPY()
        aveMonaBtc = self.getMONA_BTC()
        aveBchJpy = self.getBCH_JPY()
        aveBchBtc = self.getBCH_BTC()
        aveXemJpy = self.getXEM_JPY()
        aveXemBtc = self.getXEM_BTC()
        aveEthJpy = self.getETH_JPY()
        aveEthBtc = self.getETH_BTC()
        
        # 買いと売りの中間点
        aves = [aveBtcJpy,
                aveMonaBtc,
                aveMonaJpy,
                aveBchBtc,
                aveBchJpy,
                aveXemBtc,
                aveXemJpy,
                aveEthBtc,
                aveEthJpy]
        
        # ===========================================================
        # JPY->BTC, BTC->MONA, MONA->JPY
        #  BTC-ask,  MONA-ask,  MONA-bid
        
        # JPY->MONA, MONA->BTC, BTC->JPY
        #  MONA-ask,  MONA-bid,  BTC-bid
        
        # 手数料抜き============================================
        # Jpy_Btc_Mona = ((aveMonaJpy * fj) / (aveBtcJpy * aveMonaBtc))
        # Jpy_Mona_Btc = ((aveBtcJpy * aveMonaBtc * fj) / aveMonaJpy)
        # Jpy_Btc_Bch = ((aveBchJpy * fj) / (aveBtcJpy * aveBchBtc))
        # Jpy_Bch_Btc = ((aveBtcJpy * aveBchBtc * fj) / aveBchJpy)
        # Jpy_Btc_Xem = ((aveXemJpy * fj) / (aveBtcJpy * aveXemBtc))
        # Jpy_Xem_Btc = ((aveBtcJpy * aveXemBtc * fj) / aveXemJpy)
        # Jpy_Btc_Eth = ((aveEthJpy * fj) / (aveBtcJpy * aveEthBtc))
        # Jpy_Eth_Btc = ((aveBtcJpy * aveEthBtc * fj) / aveEthJpy)
        
        # 手数料あり============================================
        # ※decimal * floatができない．同じ型にキャストする必要あり
        Jpy_Btc_Mona = ((100 * float(aveMonaJpy))
                        / (float(aveMonaBtc) * (100 + self.fee_MONA_JPY))) * \
                       (100 / (float(aveBtcJpy) * (100 + self.fee_MONA_BTC))) * \
                       ((100 * fj) / (100 + self.fee_BTC_JPY))
        Jpy_Mona_Btc = ((100 * float(aveBtcJpy) * float(aveMonaBtc))
                        / (100 + self.fee_BTC_JPY)) * \
                       (100 / (float(aveMonaJpy) * (100 + self.fee_MONA_BTC))) * \
                       ((100 * fj) / (100 + self.fee_MONA_JPY))
        
        Jpy_Btc_Bch = ((100 * float(aveBchJpy))
                       / (float(aveBchBtc) * (100 + self.fee_BCH_JPY))) * \
                      (100 / (float(aveBtcJpy) * (100 + self.fee_BCH_BTC))) * \
                      ((100 * fj) / (100 + self.fee_BTC_JPY))
        Jpy_Bch_Btc = ((100 * float(aveBtcJpy) * float(aveBchBtc))
                       / (100 + self.fee_BTC_JPY)) * \
                      (100 / (float(aveBchJpy) * (100 + self.fee_BCH_BTC))) * \
                      ((100 * fj) / (100 + self.fee_BCH_JPY))
        
        Jpy_Btc_Xem = ((100 * float(aveXemJpy))
                       / (float(aveXemBtc) * (100 + self.fee_XEM_JPY))) * \
                      (100 / (float(aveBtcJpy) * (100 + self.fee_XEM_BTC))) * \
                      ((100 * fj) / (100 + self.fee_BTC_JPY))
        Jpy_Xem_Btc = ((100 * float(aveBtcJpy) * float(aveXemBtc))
                       / (100 + self.fee_BTC_JPY)) * \
                      (100 / (float(aveXemJpy) * (100 + self.fee_XEM_BTC))) * \
                      ((100 * fj) / (100 + self.fee_XEM_JPY))
        
        Jpy_Btc_Eth = ((100 * float(aveEthJpy))
                       / (float(aveEthBtc) * (100 + self.fee_ETH_JPY))) * \
                      (100 / (float(aveBtcJpy) * (100 + self.fee_ETH_BTC))) * \
                      ((100 * fj) / (100 + self.fee_BTC_JPY))
        Jpy_Eth_Btc = ((100 * float(aveBtcJpy) * float(aveEthBtc))
                       / (100 + self.fee_BTC_JPY)) * \
                      (100 / (float(aveEthJpy) * (100 + self.fee_ETH_BTC))) * \
                      ((100 * fj) / (100 + self.fee_ETH_JPY))
        
        # 各予想結果額
        estimates = [Jpy_Btc_Mona,
                     Jpy_Mona_Btc,
                     Jpy_Btc_Bch,
                     Jpy_Bch_Btc,
                     Jpy_Btc_Xem,
                     Jpy_Xem_Btc,
                     Jpy_Btc_Eth,
                     Jpy_Eth_Btc]
        
        # 最も高い予想結果額
        maxIndex = numpy.argmax(estimates)
        
        if maxIndex == 0 \
                and estimates[maxIndex] > (fj + self.threshold_jpy_btc_mona):
            judge = 'Jpy_Btc_Mona'
        elif maxIndex == 1 \
                and estimates[maxIndex] > (fj + self.threshold_jpy_btc_mona):
            judge = 'Jpy_Mona_Btc'
        elif maxIndex == 2 \
                and estimates[maxIndex] > (fj + self.threshold_jpy_btc_bch):
            judge = 'Jpy_Btc_Bch'
        elif maxIndex == 3 \
                and estimates[maxIndex] > (fj + self.threshold_jpy_btc_bch):
            judge = 'Jpy_Bch_Btc'
        elif maxIndex == 4 \
                and estimates[maxIndex] > (fj + self.threshold_jpy_btc_xem):
            judge = 'Jpy_Btc_Xem'
        elif maxIndex == 5 \
                and estimates[maxIndex] > (fj + self.threshold_jpy_btc_xem):
            judge = 'Jpy_Xem_Btc'
        elif maxIndex == 6 \
                and estimates[maxIndex] > (fj + self.threshold_jpy_btc_eth):
            judge = 'Jpy_Btc_Eth'
        elif maxIndex == 7 \
                and estimates[maxIndex] > (fj + self.threshold_jpy_btc_eth):
            judge = 'Jpy_Eth_Btc'
        else:
            judge = 'no routes'
        
        # 各予想利益額
        diffs = [int(Jpy_Btc_Mona - fj),
                 int(Jpy_Mona_Btc - fj),
                 int(Jpy_Btc_Bch - fj),
                 int(Jpy_Bch_Btc - fj),
                 int(Jpy_Btc_Xem - fj),
                 int(Jpy_Xem_Btc - fj),
                 int(Jpy_Btc_Eth - fj),
                 int(Jpy_Eth_Btc - fj)]
        
        resultList = [judge, fj, diffs[maxIndex], diffs, aves]
        return resultList
    
    # コメント'AutoTA'の注文が残っているか確認
    def checkActiveOrders(self, pair: str):
        # active_ordersの形式：
        # {'270906448': {
        # 'currency_pair': 'mona_btc',
        # 'action': 'ask',
        # 'amount': 33.0,
        # 'price': 0.00035692,
        # 'timestamp': '1510122394',
        # 'comment': ''}}
        time.sleep(0.3)
        self.getPrivateAPI()
        orderID = 0  # 注文が無ければこのまま0を返す
        price = 0
        amount = 0
        orders = []
        while 1:
            try:
                if pair == 'btc_jpy':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='btc_jpy'))
                elif pair == 'mona_btc':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='mona_btc'))
                elif pair == 'mona_jpy':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='mona_jpy'))
                elif pair == 'xem_btc':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='xem_btc'))
                elif pair == 'xem_jpy':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='xem_jpy'))
                elif pair == 'bch_btc':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='bch_btc'))
                elif pair == 'bch_jpy':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='bch_jpy'))
                elif pair == 'eth_btc':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='eth_btc'))
                elif pair == 'eth_jpy':
                    orders.append(
                        self.zaifp.active_orders(currency_pair='eth_jpy'))
                else:
                    pass
                break
            except:
                traceback.print_exc()
                time.sleep(1)
        
        # コメントが'AutoTA'のオーダーがあればID，価格，数量を返す
        for i in range(len(orders)):
            if orders[i] != []:
                for j in orders[i].keys():
                    if re.search(self.order_comment,
                                 str(orders[i][j]['comment'])):
                        orderID = int(j)
                        price = orders[i][j]['price']
                        amount = orders[i][j]['amount']
        resultList = [orderID, price, amount]
        return resultList
    
    # 注文IDと通貨ペアを指定して注文を取り消し
    def cancelOrder(self, orderID: int, pair: str):
        cancelFlag = False
        time.sleep(1)
        try:
            self.zaifp.cancel_order(order_id=orderID, currency_pair=pair)
            print('order canceled')
            cancelFlag = True
        except:
            traceback.print_exc()
            self.createErrorLog('cancelOrder')
        time.sleep(1)
        return cancelFlag
    
    # コメント'AutoTA'を付けて注文実行
    def tradePairs(self, pair, act, price, amount):
        while 1:
            try:
                self.getPrivateAPI()
                self.zaifp.trade(currency_pair=pair, action=act, price=price,
                                 amount=amount, comment=self.order_comment)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('tradePairs')
            time.sleep(1)
    
    # 各取引======================================
    # JPY->BTC->MONA
    def order_JPY_BTC(self, prevFund, T_aveBtcJpy):
        print('JPY->BTC: ', end='', flush=True)
        # 手数料分を残して取引
        tradeJPY = (100 * prevFund) / (100 + self.fee_BTC_JPY)
        pair = 'btc_jpy'  # trade pair
        act = 'bid'  # ask ( sell order ) or bid ( buy order )
        price = T_aveBtcJpy
        amount = Decimal(tradeJPY / float(price)).quantize(Decimal('0.0000'),
                                                           rounding=ROUND_DOWN)
        print(price, end=' amount: ', flush=True)
        print(amount)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_BTC_MONA(self, T_aveMonaBtc):
        print('BTC->MONA: ', end='', flush=True)
        while 1:
            try:
                myBTC = self.getFunds()['btc']
                # 手数料分を残して取引
                tradeBTC = (100 * myBTC) / (100 + self.fee_MONA_BTC)
                pair = 'mona_btc'  # trade pair
                act = 'bid'  # ask ( sell order ) or bid ( buy order )
                price = T_aveMonaBtc
                amount = Decimal(tradeBTC / float(price)).quantize(
                    Decimal('0'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('order_BTC_MONA')
            time.sleep(1)
        time.sleep(1)
        if amount >= 1:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_MONA_JPY(self, T_aveMonaJpy):
        print('MONA->JPY: ', end='', flush=True)
        while 1:
            try:
                myMONA = self.getFunds()['mona']
                # 手数料分を残して取引
                tradeMONA = (100 * myMONA) / (100 + self.fee_MONA_JPY)
                pair = 'mona_jpy'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveMonaJpy
                amount = int(tradeMONA)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('order_MONA_JPY')
            time.sleep(1)
        time.sleep(1)
        if amount >= 1:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
        return price * amount
    
    # JPY->MONA->BTC
    def order_JPY_MONA(self, prevFund, T_aveMonaJpy):
        print('JPY->MONA: ', end='', flush=True)
        while 1:
            try:
                # 手数料分を残して取引
                tradeJPY = (100 * prevFund) / (100 + self.fee_MONA_JPY)
                pair = 'mona_jpy'  # trade pair
                act = 'bid'  # ask ( sell order ) or bid ( buy order )
                price = T_aveMonaJpy
                amount = Decimal(tradeJPY / float(price)).quantize(
                    Decimal('0'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('JPY->MONA')
            time.sleep(1)
        time.sleep(1)
        if amount >= 1:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_MONA_BTC(self, T_aveMonaBtc):
        print('MONA->BTC: ', end='', flush=True)
        while 1:
            try:
                myMONA = self.getFunds()['mona']
                # 手数料分を残して取引
                tradeMONA = (100 * myMONA) / (100 + self.fee_MONA_BTC)
                pair = 'mona_btc'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveMonaBtc
                amount = int(tradeMONA)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('MONA->BTC')
            time.sleep(1)
        time.sleep(1)
        if amount >= 1:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_BTC_JPY(self, T_aveBtcJpy):
        print('BTC->JPY: ', end='', flush=True)
        while 1:
            try:
                myBTC = self.getFunds()['btc']
                # 手数料分を残して取引
                tradeBTC = (100 * myBTC) / (100 + self.fee_BTC_JPY)
                pair = 'btc_jpy'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveBtcJpy
                amount = Decimal(tradeBTC).quantize(Decimal('0.0000'),
                                                    rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('BTC->JPY')
            time.sleep(1)
        time.sleep(1)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
        return price * amount
    
    # JPY->BTC->BCH
    def order_BTC_BCH(self, T_aveBchBtc):
        print('BTC->BCH: ', end='', flush=True)
        while 1:
            try:
                myBTC = self.getFunds()['btc']
                # 手数料分を残して取引
                tradeBTC = (100 * myBTC) / (100 + self.fee_BCH_BTC)
                pair = 'bch_btc'  # trade pair
                act = 'bid'  # ask ( sell order ) or bid ( buy order )
                price = T_aveBchBtc
                amount = Decimal(tradeBTC / float(price)).quantize(
                    Decimal('0.0000'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('BTC->BCH')
            time.sleep(1)
        time.sleep(1)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_BCH_JPY(self, T_aveBchJpy):
        print('BCH->JPY: ', end='', flush=True)
        while 1:
            try:
                myBCH = self.getFunds()['BCH']
                # 手数料分を残して取引
                tradeBCH = (100 * myBCH) / (100 + self.fee_BCH_JPY)
                pair = 'bch_jpy'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveBchJpy
                amount = Decimal(tradeBCH).quantize(
                    Decimal('0.0000'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('BCH->JPY')
            time.sleep(1)
        time.sleep(1)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
        return price * amount
    
    # JPY->BCH->BTC
    def order_JPY_BCH(self, prevFund, T_aveBchJpy):
        print('JPY->BCH: ', end='', flush=True)
        # 手数料分を残して取引
        tradeJPY = (100 * prevFund) / (100 + self.fee_BCH_JPY)
        pair = 'bch_jpy'  # trade pair
        act = 'bid'  # ask ( sell order ) or bid ( buy order )
        price = T_aveBchJpy
        amount = Decimal(tradeJPY / float(price)).quantize(
            Decimal('0.0000'), rounding=ROUND_DOWN)
        print(price, end=' amount: ', flush=True)
        print(amount)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_BCH_BTC(self, T_aveBchBtc):
        print('BCH->BTC: ', end='', flush=True)
        while 1:
            try:
                myBCH = self.getFunds()['BCH']
                # 手数料分を残して取引
                tradeBCH = (100 * myBCH) / (100 + self.fee_BCH_BTC)
                pair = 'bch_btc'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveBchBtc
                amount = Decimal(tradeBCH).quantize(
                    Decimal('0.0000'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('BCH->BTC')
            time.sleep(1)
        time.sleep(1)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    # JPY->BTC->XEM
    def order_BTC_XEM(self, T_aveXemBtc):
        print('BTC->XEM: ', end='', flush=True)
        while 1:
            try:
                myBTC = self.getFunds()['btc']
                # 手数料分を残して取引
                tradeBTC = (100 * myBTC) / (100 + self.fee_XEM_BTC)
                pair = 'xem_btc'  # trade pair
                act = 'bid'  # ask ( sell order ) or bid ( buy order )
                price = T_aveXemBtc
                amount = Decimal(tradeBTC / float(price)).quantize(
                    Decimal('0'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('BTC->XEM')
            time.sleep(1)
        time.sleep(1)
        if amount >= 1:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_XEM_JPY(self, T_aveXemJpy):
        print('XEM->JPY: ', end='', flush=True)
        while 1:
            try:
                myXEM = self.getFunds()['xem']
                # 手数料分を残して取引
                tradeXEM = (100 * myXEM) / (100 + self.fee_XEM_JPY)
                pair = 'xem_jpy'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveXemJpy
                amount = Decimal(tradeXEM).quantize(
                    Decimal('0.0'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('XEM->JPY')
            time.sleep(1)
        time.sleep(1)
        if amount >= 0.1:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
        return price * amount
    
    # JPY->XEM->BTC
    def order_JPY_XEM(self, prevFund, T_aveXemJpy):
        print('JPY->XEM: ', end='', flush=True)
        # 手数料分を残して取引
        tradeJPY = (100 * prevFund) / (100 + self.fee_XEM_JPY)
        pair = 'xem_jpy'  # trade pair
        act = 'bid'  # ask ( sell order ) or bid ( buy order )
        price = T_aveXemJpy
        amount = Decimal(tradeJPY / float(price)).quantize(
            Decimal('0.0'), rounding=ROUND_DOWN)
        print(price, end=' amount: ', flush=True)
        print(amount)
        if amount >= 0.1:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_XEM_BTC(self, T_aveXemBtc):
        print('XEM->BTC: ', end='', flush=True)
        while 1:
            try:
                myXEM = self.getFunds()['xem']
                # 手数料分を残して取引
                tradeXEM = (100 * myXEM) / (100 + self.fee_XEM_BTC)
                pair = 'xem_btc'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveXemBtc
                amount = Decimal(tradeXEM).quantize(
                    Decimal('0'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('XEM->BTC')
            time.sleep(1)
        time.sleep(1)
        if amount >= 1:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    # JPY->BTC->ETH
    def order_BTC_ETH(self, T_aveEthBtc):
        print('BTC->ETH: ', end='', flush=True)
        while 1:
            try:
                myBTC = self.getFunds()['btc']
                # 手数料分を残して取引
                tradeBTC = (100 * myBTC) / (100 + self.fee_ETH_BTC)
                pair = 'eth_btc'  # trade pair
                act = 'bid'  # ask ( sell order ) or bid ( buy order )
                price = T_aveEthBtc
                amount = Decimal(tradeBTC / float(price)).quantize(
                    Decimal('0.0000'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('BTC->ETH')
            time.sleep(1)
        time.sleep(1)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_ETH_JPY(self, T_aveEthJpy):
        print('ETH->JPY: ', end='', flush=True)
        while 1:
            try:
                myETH = self.getFunds()['ETH']
                # 手数料分を残して取引
                tradeETH = (100 * myETH) / (100 + self.fee_ETH_JPY)
                pair = 'eth_jpy'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveEthJpy
                amount = Decimal(tradeETH).quantize(
                    Decimal('0.0000'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('ETH->JPY')
            time.sleep(1)
        time.sleep(1)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
        return price * amount
    
    # JPY->ETH->BTC
    def order_JPY_ETH(self, prevFund, T_aveEthJpy):
        print('JPY->ETH: ', end='', flush=True)
        # 手数料分を残して取引
        tradeJPY = (100 * prevFund) / (100 + self.fee_ETH_JPY)
        pair = 'eth_jpy'  # trade pair
        act = 'bid'  # ask ( sell order ) or bid ( buy order )
        price = T_aveEthJpy
        amount = Decimal(tradeJPY / float(price)).quantize(
            Decimal('0.0000'), rounding=ROUND_DOWN)
        print(price, end=' amount: ', flush=True)
        print(amount)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
    
    def order_ETH_BTC(self, T_aveEthBtc):
        print('ETH->BTC: ', end='', flush=True)
        while 1:
            try:
                myETH = self.getFunds()['ETH']
                # 手数料分を残して取引
                tradeETH = (100 * myETH) / (100 + self.fee_ETH_BTC)
                pair = 'eth_btc'  # trade pair
                act = 'ask'  # ask ( sell order ) or bid ( buy order )
                price = T_aveEthBtc
                amount = Decimal(tradeETH).quantize(
                    Decimal('0.0000'), rounding=ROUND_DOWN)
                print(price, end=' amount: ', flush=True)
                print(amount)
                break
            except:
                traceback.print_exc()
                self.createErrorLog('ETH->BTC')
            time.sleep(1)
        time.sleep(1)
        if amount >= 0.0001:
            self.tradePairs(pair, act, price, amount)
        else:
            print('Do not Trade. Checking active orders...')
