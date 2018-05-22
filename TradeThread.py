from PyQt5.QtCore import QThread, pyqtSignal
import time


# thread========================================
class TradeThread(QThread):
    # シグナルで値を返す場合は，その型を指定
    stateChangeSignal = pyqtSignal(str)  # 取引状態の表示を更新
    monitoredSignal = pyqtSignal(list)  # 三角裁定計算の結果
    stoppedTradeSignal = pyqtSignal()  # 取引終了後にGUIへ発信
    fundsSignal = pyqtSignal(list)  # 取引毎に余力額の表示を更新
    profitSignal = pyqtSignal(int)  # 取引終了後，最新の損益額の表示を更新
    statisticsSignal = pyqtSignal(list)  # DB内データの統計結果を発
    
    def __init__(self):
        super().__init__()
        # 各取引の制限時間
        self.limitTime_BTC_JPY = 60 * 60 * 2
        self.limitTime_MONA_BTC = 60 * 60 * 6
        self.limitTime_MONA_JPY = 60 * 60 * 3
        self.limitTime_BCH_BTC = 60 * 60 * 6
        self.limitTime_BCH_JPY = 60 * 60 * 3
        self.limitTime_XEM_BTC = 60 * 60 * 4
        self.limitTime_XEM_JPY = 60 * 60 * 3
        self.limitTime_ETH_BTC = 60 * 60 * 4
        self.limitTime_ETH_JPY = 60 * 60 * 3
        # ループフラグ：終了時は0にする
        self.loopFlag = 1
        # 制限時間に到達した回数
        self.limited_BtcJpy = 0
        self.limited_MonaBtc = 0
        self.limited_MonaJpy = 0
        self.limited_BchBtc = 0
        self.limited_BchJpy = 0
        self.limited_XemBtc = 0
        self.limited_XemJpy = 0
        self.limited_EthBtc = 0
        self.limited_EthJpy = 0
    
    # ループフラグon/off: onである限りループ==========
    def onLoop(self):
        self.loopFlag = 1
    
    def offLoop(self):
        self.loopFlag = 0
    
    # インスタンスを共有
    def setObj(self, exc, dba):
        """
        :type exc: six_funds.EXCaccess.EXCaccess
        :type dba: six_funds.DBaccess.DBaccess
        """
        self.exc = exc
        self.dba = dba
    
    # ループ処理
    def run(self):
        while 1:
            if self.loopFlag == 1:
                self.trading()
            else:
                self.stoppedTradeSignal.emit()
                break
    
    # 取引順決定
    def trading(self):
        # [0]:取引順
        # [1]:日本円余力額
        # [2]:最も高い予想利益額
        # [3]:予想利益額のリスト
        # [4]:買いと売りの中間値のリスト
        self.stateChangeSignal.emit('Monitoring')
        monitorList = self.exc.Monitoring()
        judge = monitorList[0]
        prevJPY = monitorList[1]
        routeEstimate = monitorList[2]
        diffs = monitorList[3]
        T_aves = monitorList[4]
        
        self.monitoredSignal.emit(diffs)  # 各予想をGUIに表示させる
        if judge != 'no routes':
            print(judge, end=' est=: ')
            print(routeEstimate)
        
        # T_aves中身:
        # [0]:T_aveBtcJpy,
        # [1]:T_aveMonaBtc,
        # [2]:T_aveMonaJpy,
        # [3]:T_aveBchBtc,
        # [4]:T_aveBchJpy,
        # [5]:T_aveXemBtc,
        # [6]:T_aveXemJpy,
        # [7]:T_aveEthBtc,
        # [8]:T_aveEthJpy
        
        # 取引順に従って取引
        if judge == 'Jpy_Btc_Mona':
            self.stateChangeSignal.emit('JPY->BTC->MONA')
            self.exchange_JpyBtcMona(prevJPY, T_aves[0], routeEstimate)
        elif judge == 'Jpy_Mona_Btc':
            self.stateChangeSignal.emit('JPY->MONA->BTC')
            self.exchange_JpyMonaBtc(prevJPY, T_aves[2], routeEstimate)
        elif judge == 'Jpy_Btc_Bch':
            self.stateChangeSignal.emit('JPY->BTC->BCH')
            self.exchange_JpyBtcBch(prevJPY, T_aves[0], routeEstimate)
        elif judge == 'Jpy_Bch_Btc':
            self.stateChangeSignal.emit('JPY->BCH->BTC')
            self.exchange_JpyBchBtc(prevJPY, T_aves[4], routeEstimate)
        elif judge == 'Jpy_Btc_Xem':
            self.stateChangeSignal.emit('JPY->BTC->XEM')
            self.exchange_JpyBtcXem(prevJPY, T_aves[0], routeEstimate)
        elif judge == 'Jpy_Xem_Btc':
            self.stateChangeSignal.emit('JPY->XEM->BTC')
            self.exchange_JpyXemBtc(prevJPY, T_aves[6], routeEstimate)
        elif judge == 'Jpy_Btc_Eth':
            self.stateChangeSignal.emit('JPY->BTC->ETH')
            self.exchange_JpyBtcEth(prevJPY, T_aves[0], routeEstimate)
        elif judge == 'Jpy_Eth_Btc':
            self.stateChangeSignal.emit('JPY->ETH->BTC')
            self.exchange_JpyEthBtc(prevJPY, T_aves[8], routeEstimate)
        else:
            return
        
        self.stateChangeSignal.emit('trade finished')
        statList = self.dba.statisticsTradeResult()
        self.statisticsSignal.emit(statList)
        print('Complete. Ready >')
    
    # 現在の余力額一覧をGUIに表示させる
    def emitFunds(self):
        funds = self.exc.getFunds()
        fundsList = [funds['jpy'],
                     funds['btc'],
                     funds['mona'],
                     funds['BCH'],
                     funds['xem'],
                     funds['ETH']]
        self.fundsSignal.emit(fundsList)
        time.sleep(1)
        return fundsList
    
    def exchange_JpyBtcMona(self, prevJPY, aveBtcJpy, estJPY):
        routeName = 'JPY->BTC->MONA'
        # JPY->BTC==============================================
        self.exc.order_JPY_BTC(prevJPY, aveBtcJpy)
        time.sleep(1)
        # コメントが'AutoTA'の注文が残っている限りループ
        # その注文が無くなれば0を受け取る→ループを抜ける
        # 制限時間内にループが終わらなければ強制終了，監視からやり直し
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('btc_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BTC_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'btc_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBtcJpy = self.exc.getBTC_JPY()
                        time.sleep(1)
                        self.exc.order_BTC_JPY(aveBtcJpy)
                        self.limited_BtcJpy += 1
        min_BtcJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'JPY->BTC', min_BtcJpy, self.limited_BtcJpy)
        self.emitFunds()
        
        # BTC->MONA==============================================
        aveMonaBtc = self.exc.getMONA_BTC()
        time.sleep(1)
        self.exc.order_BTC_MONA(aveMonaBtc)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('mona_btc')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_MONA_BTC:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'mona_btc')
                    if cancelFlag:
                        seconds = 0
                        aveMonaBtc = self.exc.getMONA_BTC()
                        time.sleep(1)
                        self.exc.order_BTC_MONA(aveMonaBtc)
                        self.limited_MonaBtc += 1
        min_MonaBtc = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BTC->MONA', min_MonaBtc, self.limited_MonaBtc)
        self.limited_MonaBtc = 0
        self.emitFunds()
        
        # MONA->JPY==============================================
        aveMonaJpy = self.exc.getMONA_JPY()
        time.sleep(1)
        nextJPY = self.exc.order_MONA_JPY(aveMonaJpy)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('mona_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_MONA_JPY:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'mona_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveMonaJpy = self.exc.getMONA_JPY()
                        time.sleep(1)
                        nextJPY = self.exc.order_MONA_JPY(aveMonaJpy)
                        self.limited_MonaJpy += 1
        min_MonaJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'MONA->JPY', min_MonaJpy, self.limited_MonaJpy)
        self.limited_MonaJpy = 0
        self.emitFunds()
        
        # 差の計算======================================
        profit = int(nextJPY - prevJPY)
        self.profitSignal.emit(int(profit))
        # >>DBに追加
        self.dba.insertRoute(routeName, prevJPY, estJPY, profit)
    
    def exchange_JpyMonaBtc(self, prevJPY, aveMonaJpy, estJPY):
        routeName = 'JPY->MONA->BTC'
        # JPY->MONA==============================================
        self.exc.order_JPY_MONA(prevJPY, aveMonaJpy)
        time.sleep(1)
        # コメントが'AutoTA'の注文が残っている限りループ
        # その注文が無くなれば0を受け取る→ループを抜ける
        # 制限時間内にループが終わらなければ強制終了，監視からやり直し
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('mona_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_MONA_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'mona_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveMonaJpy = self.exc.getMONA_JPY()
                        time.sleep(1)
                        self.exc.order_MONA_JPY(aveMonaJpy)
                        self.limited_MonaJpy += 1
        min_MonaJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'JPY->MONA', min_MonaJpy, self.limited_MonaJpy)
        self.emitFunds()
        
        # MONA->BTC==============================================
        aveMonaBtc = self.exc.getMONA_BTC()
        time.sleep(1)
        self.exc.order_MONA_BTC(aveMonaBtc)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('mona_btc')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_MONA_BTC:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'mona_btc')
                    if cancelFlag:
                        seconds = 0
                        aveMonaBtc = self.exc.getMONA_BTC()
                        time.sleep(1)
                        self.exc.order_MONA_BTC(aveMonaBtc)
                        self.limited_MonaBtc += 1
        min_MonaBtc = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'MONA->BTC', min_MonaBtc, self.limited_MonaBtc)
        self.limited_MonaBtc = 0
        self.emitFunds()
        
        # BTC->JPY==============================================
        aveBtcJpy = self.exc.getBTC_JPY()
        time.sleep(1)
        nextJPY = self.exc.order_BTC_JPY(aveBtcJpy)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('btc_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BTC_JPY:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'btc_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBtcJpy = self.exc.getBTC_JPY()
                        time.sleep(1)
                        nextJPY = self.exc.order_BTC_JPY(aveBtcJpy)
                        self.limited_BtcJpy += 1
        min_BtcJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BTC->JPY', min_BtcJpy, self.limited_BtcJpy)
        self.limited_BtcJpy = 0
        self.emitFunds()
        
        # 差の計算======================================
        profit = int(nextJPY - prevJPY)
        self.profitSignal.emit(int(profit))
        # >>DBに追加
        self.dba.insertRoute(routeName, prevJPY, estJPY, profit)
    
    def exchange_JpyBtcBch(self, prevJPY, aveBtcJpy, estJPY):
        routeName = 'JPY->BTC->BCH'
        # JPY->BTC==============================================
        self.exc.order_JPY_BTC(prevJPY, aveBtcJpy)
        time.sleep(1)
        # コメントが'AutoTA'の注文が残っている限りループ
        # その注文が無くなれば0を受け取る→ループを抜ける
        # 制限時間内にループが終わらなければ強制終了，監視からやり直し
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('btc_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BTC_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'btc_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBtcJpy = self.exc.getBTC_JPY()
                        time.sleep(1)
                        self.exc.order_BTC_JPY(aveBtcJpy)
                        self.limited_BtcJpy += 1
        min_BtcJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'JPY->BTC', min_BtcJpy, self.limited_BtcJpy)
        self.emitFunds()
        
        # BTC->BCH==============================================
        aveBchBtc = self.exc.getBCH_BTC()
        time.sleep(1)
        self.exc.order_BTC_BCH(aveBchBtc)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('bch_btc')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BCH_BTC:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'bch_btc')
                    if cancelFlag:
                        seconds = 0
                        aveBchBtc = self.exc.getBCH_BTC()
                        time.sleep(1)
                        self.exc.order_BTC_BCH(aveBchBtc)
                        self.limited_BchBtc += 1
        min_BchBtc = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BTC->BCH', min_BchBtc, self.limited_BchBtc)
        self.limited_BchBtc = 0
        self.emitFunds()
        
        # BCH->JPY==============================================
        aveBchJpy = self.exc.getBCH_JPY()
        time.sleep(1)
        nextJPY = self.exc.order_BCH_JPY(aveBchJpy)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('bch_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BCH_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'bch_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBchJpy = self.exc.getBCH_JPY()
                        time.sleep(1)
                        nextJPY = self.exc.order_BCH_JPY(aveBchJpy)
                        self.limited_BchJpy += 1
        min_BchJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BCH->JPY', min_BchJpy, self.limited_BchJpy)
        self.limited_BchJpy = 0
        self.emitFunds()
        
        # 差の計算======================================
        profit = int(nextJPY - prevJPY)
        self.profitSignal.emit(int(profit))
        # >>DBに追加
        self.dba.insertRoute(routeName, prevJPY, estJPY, profit)
    
    def exchange_JpyBchBtc(self, prevJPY, aveBchJpy, estJPY):
        routeName = 'JPY->BCH->BTC'
        # JPY->BCH==============================================
        self.exc.order_JPY_BCH(prevJPY, aveBchJpy)
        time.sleep(1)
        # コメントが'AutoTA'の注文が残っている限りループ
        # その注文が無くなれば0を受け取る→ループを抜ける
        # 制限時間内にループが終わらなければ強制終了，監視からやり直し
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('bch_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BCH_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'bch_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBchJpy = self.exc.getBCH_JPY()
                        time.sleep(1)
                        self.exc.order_BCH_JPY(aveBchJpy)
                        self.limited_BchJpy += 1
        min_BchJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'JPY->BCH', min_BchJpy, self.limited_BchJpy)
        self.emitFunds()
        
        # BCH->BTC==============================================
        aveBchBtc = self.exc.getBCH_BTC()
        time.sleep(1)
        self.exc.order_BCH_BTC(aveBchBtc)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('bch_btc')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BCH_BTC:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'bch_btc')
                    if cancelFlag:
                        seconds = 0
                        aveBchBtc = self.exc.getBCH_BTC()
                        time.sleep(1)
                        self.exc.order_BCH_BTC(aveBchBtc)
                        self.limited_BchBtc += 1
        min_BchBtc = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BCH->BTC', min_BchBtc, self.limited_BchBtc)
        self.limited_BchBtc = 0
        self.emitFunds()
        
        # BTC->JPY==============================================
        aveBtcJpy = self.exc.getBTC_JPY()
        time.sleep(1)
        nextJPY = self.exc.order_BTC_JPY(aveBtcJpy)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('btc_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BTC_JPY:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'btc_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBtcJpy = self.exc.getBTC_JPY()
                        time.sleep(1)
                        nextJPY = self.exc.order_BTC_JPY(aveBtcJpy)
                        self.limited_BtcJpy += 1
        min_BtcJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BTC->JPY', min_BtcJpy, self.limited_BtcJpy)
        self.limited_BtcJpy = 0
        self.emitFunds()
        
        # 差の計算======================================
        profit = int(nextJPY - prevJPY)
        self.profitSignal.emit(int(profit))
        # >>DBに追加
        self.dba.insertRoute(routeName, prevJPY, estJPY, profit)
    
    def exchange_JpyBtcXem(self, prevJPY, aveBtcJpy, estJPY):
        routeName = 'JPY->BTC->XEM'
        # JPY->BTC==============================================
        self.exc.order_JPY_BTC(prevJPY, aveBtcJpy)
        time.sleep(1)
        # コメントが'AutoTA'の注文が残っている限りループ
        # その注文が無くなれば0を受け取る→ループを抜ける
        # 制限時間内にループが終わらなければ強制終了，監視からやり直し
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('btc_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BTC_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'btc_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBtcJpy = self.exc.getBTC_JPY()
                        time.sleep(1)
                        self.exc.order_BTC_JPY(aveBtcJpy)
                        self.limited_BtcJpy += 1
        min_BtcJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'JPY->BTC', min_BtcJpy, self.limited_BtcJpy)
        self.emitFunds()
        
        # BTC->XEM==============================================
        aveXemBtc = self.exc.getXEM_BTC()
        time.sleep(1)
        self.exc.order_BTC_XEM(aveXemBtc)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('xem_btc')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_XEM_BTC:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'xem_btc')
                    if cancelFlag:
                        seconds = 0
                        aveXemBtc = self.exc.getXEM_BTC()
                        time.sleep(1)
                        self.exc.order_BTC_XEM(aveXemBtc)
                        self.limited_XemBtc += 1
        min_XemBtc = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BTC->XEM', min_XemBtc, self.limited_XemBtc)
        self.limited_XemBtc = 0
        self.emitFunds()
        
        # XEM->JPY==============================================
        aveXemJpy = self.exc.getXEM_JPY()
        time.sleep(1)
        nextJPY = self.exc.order_XEM_JPY(aveXemJpy)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('xem_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_XEM_JPY:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'xem_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveXemJpy = self.exc.getXEM_JPY()
                        time.sleep(1)
                        nextJPY = self.exc.order_XEM_JPY(aveXemJpy)
                        self.limited_XemJpy += 1
        min_XemJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'XEM->JPY', min_XemJpy, self.limited_XemJpy)
        self.limited_XemJpy = 0
        self.emitFunds()
        
        # 差の計算======================================
        profit = int(nextJPY - prevJPY)
        self.profitSignal.emit(int(profit))
        # >>DBに追加
        self.dba.insertRoute(routeName, prevJPY, estJPY, profit)
    
    def exchange_JpyXemBtc(self, prevJPY, aveXemJpy, estJPY):
        routeName = 'JPY->XEM->BTC'
        # JPY->XEM==============================================
        self.exc.order_JPY_XEM(prevJPY, aveXemJpy)
        time.sleep(1)
        # コメントが'AutoTA'の注文が残っている限りループ
        # その注文が無くなれば0を受け取る→ループを抜ける
        # 制限時間内にループが終わらなければ強制終了，監視からやり直し
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('xem_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_XEM_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'xem_jpy')
                    if cancelFlag:
                        aveXemJpy = self.exc.getXEM_JPY()
                        time.sleep(1)
                        self.exc.order_XEM_JPY(aveXemJpy)
                        self.limited_XemJpy += 1
        min_XemJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'JPY->XEM', min_XemJpy, self.limited_XemJpy)
        self.emitFunds()
        
        # XEM->BTC==============================================
        aveXemBtc = self.exc.getXEM_BTC()
        time.sleep(1)
        self.exc.order_XEM_BTC(aveXemBtc)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('xem_btc')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_XEM_BTC:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'xem_btc')
                    if cancelFlag:
                        seconds = 0
                        aveXemBtc = self.exc.getXEM_BTC()
                        time.sleep(1)
                        self.exc.order_XEM_BTC(aveXemBtc)
                        self.limited_XemBtc += 1
        min_XemBtc = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'XEM->BTC', min_XemBtc, self.limited_XemBtc)
        self.limited_XemBtc = 0
        self.emitFunds()
        
        # BTC->JPY==============================================
        aveBtcJpy = self.exc.getBTC_JPY()
        time.sleep(1)
        nextJPY = self.exc.order_BTC_JPY(aveBtcJpy)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('btc_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BTC_JPY:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'btc_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBtcJpy = self.exc.getBTC_JPY()
                        time.sleep(1)
                        nextJPY = self.exc.order_BTC_JPY(aveBtcJpy)
                        self.limited_BtcJpy += 1
        min_BtcJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BTC->JPY', min_BtcJpy, self.limited_BtcJpy)
        self.limited_BtcJpy = 0
        self.emitFunds()
        
        # 差の計算======================================
        profit = int(nextJPY - prevJPY)
        self.profitSignal.emit(int(profit))
        # >>DBに追加
        self.dba.insertRoute(routeName, prevJPY, estJPY, profit)
    
    def exchange_JpyBtcEth(self, prevJPY, aveBtcJpy, estJPY):
        routeName = 'JPY->BTC->ETH'
        # JPY->BTC==============================================
        self.exc.order_JPY_BTC(prevJPY, aveBtcJpy)
        time.sleep(1)
        # コメントが'AutoTA'の注文が残っている限りループ
        # その注文が無くなれば0を受け取る→ループを抜ける
        # 制限時間内にループが終わらなければ強制終了，監視からやり直し
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('btc_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BTC_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'btc_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBtcJpy = self.exc.getBTC_JPY()
                        time.sleep(1)
                        self.exc.order_BTC_JPY(aveBtcJpy)
                        self.limited_BtcJpy += 1
        min_BtcJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'JPY->BTC', min_BtcJpy, self.limited_BtcJpy)
        self.emitFunds()
        
        # BTC->ETH==============================================
        aveEthBtc = self.exc.getETH_BTC()
        time.sleep(1)
        self.exc.order_BTC_ETH(aveEthBtc)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('eth_btc')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_ETH_BTC:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'eth_btc')
                    if cancelFlag:
                        seconds = 0
                        aveEthBtc = self.exc.getETH_BTC()
                        time.sleep(1)
                        self.exc.order_BTC_ETH(aveEthBtc)
                        self.limited_EthBtc += 1
        min_EthBtc = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BTC->ETH', min_EthBtc, self.limited_EthBtc)
        self.limited_EthBtc = 0
        self.emitFunds()
        
        # ETH->JPY==============================================
        aveEthJpy = self.exc.getETH_JPY()
        time.sleep(1)
        nextJPY = self.exc.order_ETH_JPY(aveEthJpy)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('eth_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_ETH_JPY:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'eth_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveEthJpy = self.exc.getETH_JPY()
                        time.sleep(1)
                        nextJPY = self.exc.order_ETH_JPY(aveEthJpy)
                        self.limited_EthJpy += 1
        min_EthJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'ETH->JPY', min_EthJpy, self.limited_EthJpy)
        self.limited_EthJpy = 0
        self.emitFunds()
        
        # 差の計算======================================
        profit = int(nextJPY - prevJPY)
        self.profitSignal.emit(int(profit))
        # >>DBに追加
        self.dba.insertRoute(routeName, prevJPY, estJPY, profit)
    
    def exchange_JpyEthBtc(self, prevJPY, aveEthJpy, estJPY):
        routeName = 'JPY->ETH->BTC'
        # JPY->ETH==============================================
        self.exc.order_JPY_ETH(prevJPY, aveEthJpy)
        time.sleep(1)
        # コメントが'AutoTA'の注文が残っている限りループ
        # その注文が無くなれば0を受け取る→ループを抜ける
        # 制限時間内にループが終わらなければ強制終了，監視からやり直し
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('eth_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_ETH_JPY:
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'eth_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveEthJpy = self.exc.getETH_JPY()
                        time.sleep(1)
                        self.exc.order_ETH_JPY(aveEthJpy)
                        self.limited_EthJpy += 1
        min_EthJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'JPY->ETH', min_EthJpy, self.limited_EthJpy)
        self.emitFunds()
        
        # ETH->BTC==============================================
        aveEthBtc = self.exc.getETH_BTC()
        time.sleep(1)
        self.exc.order_ETH_BTC(aveEthBtc)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('eth_btc')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_ETH_BTC:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'eth_btc')
                    if cancelFlag:
                        seconds = 0
                        aveEthBtc = self.exc.getETH_BTC()
                        time.sleep(1)
                        self.exc.order_ETH_BTC(aveEthBtc)
                        self.limited_EthBtc += 1
        min_EthBtc = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'ETH->BTC', min_EthBtc, self.limited_EthBtc)
        self.limited_EthBtc = 0
        self.emitFunds()
        
        # BTC->JPY==============================================
        aveBtcJpy = self.exc.getBTC_JPY()
        time.sleep(1)
        nextJPY = self.exc.order_BTC_JPY(aveBtcJpy)
        time.sleep(1)
        seconds = 0
        while 1:
            seconds += 1
            # [0]:orderID, [1]:price, [2]:amount
            check = self.exc.checkActiveOrders('btc_jpy')
            if check[0] == 0:
                break
            else:
                if seconds > self.limitTime_BTC_JPY:
                    seconds = 0
                    # オーダーキャンセル，再注文
                    cancelFlag = self.exc.cancelOrder(check[0], 'btc_jpy')
                    if cancelFlag:
                        seconds = 0
                        aveBtcJpy = self.exc.getBTC_JPY()
                        time.sleep(1)
                        nextJPY = self.exc.order_BTC_JPY(aveBtcJpy)
                        self.limited_BtcJpy += 1
        min_BtcJpy = int(seconds / 60)  # 取引にかかった時間[分]
        # >>DBに追加
        self.dba.insertTrade(
            routeName, 'BTC->JPY', min_BtcJpy, self.limited_BtcJpy)
        self.limited_BtcJpy = 0
        self.emitFunds()
        
        # 差の計算======================================
        profit = int(nextJPY - prevJPY)
        self.profitSignal.emit(int(profit))
        # >>DBに追加
        self.dba.insertRoute(routeName, prevJPY, estJPY, profit)
