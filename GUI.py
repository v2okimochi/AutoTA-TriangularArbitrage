# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, \
    QVBoxLayout, QHBoxLayout
from EXCaccess import EXCaccess
from DBaccess import DBaccess
from TradeThread import TradeThread


class GUI(QWidget):
    tradeThread = TradeThread()
    exc = EXCaccess()
    dba = DBaccess()
    yes_trading = 'Trading'
    no_trading = 'No Trading'
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AutoTA 2.1')
        # 取引状態の表示を更新
        self.tradeThread.stateChangeSignal.connect(self.stateChanger)
        # 予想利益額を取得したら表示更新
        self.tradeThread.monitoredSignal.connect(self.displayCalcs)
        # 取引終了ボタンを押した後，取引が終了してから取引開始ボタンを解放
        self.tradeThread.stoppedTradeSignal.connect(self.releaseStartButton)
        # 取引ごとに余力額の表示を更新
        self.tradeThread.fundsSignal.connect(self.displayFunds)
        # 取引1巡後に最新の損益額の表示を更新
        self.tradeThread.profitSignal.connect(self.displayProfit)
        # 取引1巡後に統計結果を受け取る
        self.tradeThread.statisticsSignal.connect(self.displayStatistics)
        # ======================================================
        self.funds = self.exc.getFunds()
        self.jpyFund = str(self.funds['jpy'])
        self.btcFund = str(self.funds['btc'])
        self.monaFund = str(self.funds['mona'])
        self.bchFund = str(self.funds['BCH'])
        self.xemFund = str(self.funds['xem'])
        self.ethFund = str(self.funds['ETH'])
        self.initUI()
        self.show()
    
    # GUIデザイン
    def initUI(self):
        # GUIレイアウト1====================================
        currentFundsLabel = QLabel('現在の余力額')
        jpyLabel = QLabel('JPY: ')
        self.jpyNow = QLabel(self.jpyFund)
        btcLabel = QLabel('BTC: ')
        self.btcNow = QLabel(self.btcFund)
        monaLabel = QLabel('MONA: ')
        self.monaNow = QLabel(self.monaFund)
        bchLabel = QLabel('BCH: ')
        self.bchNow = QLabel(self.bchFund)
        xemLabel = QLabel('XEM: ')
        self.xemNow = QLabel(self.xemFund)
        ethLabel = QLabel('ETH: ')
        self.ethNow = QLabel(self.ethFund)
        
        cutterLabel = QLabel('---------------')
        latestProfitLabel = QLabel('最新の損益：')
        self.latestProfit_Now = QLabel('###')
        
        tradeStateLabel = QLabel('状態：')
        self.tradeState = QLabel(self.no_trading)
        
        # ボタン====================================
        self.start_auto = QPushButton("取引開始")
        self.stop_auto = QPushButton("停止")
        exportCSV = QPushButton("データをCSVに出力")
        quit_app = QPushButton("AutoTAを終了")
        self.stop_auto.setEnabled(False)  # disable button
        
        # ボタンのスロット===========================
        self.start_auto.clicked.connect(self.startButton)
        self.stop_auto.clicked.connect(self.stopButton)
        exportCSV.clicked.connect(self.exportData)
        quit_app.clicked.connect(quit)
        
        # レイアウト作成
        # 日本円余力
        jpyLayout = QHBoxLayout()
        jpyLayout.addWidget(jpyLabel)
        jpyLayout.addWidget(self.jpyNow)
        jpyLayout.addStretch()
        # BTC余力
        btcLayout = QHBoxLayout()
        btcLayout.addWidget(btcLabel)
        btcLayout.addWidget(self.btcNow)
        btcLayout.addStretch()
        # MONA余力
        monaLayout = QHBoxLayout()
        monaLayout.addWidget(monaLabel)
        monaLayout.addWidget(self.monaNow)
        monaLayout.addStretch()
        # BCH余力
        bchLayout = QHBoxLayout()
        bchLayout.addWidget(bchLabel)
        bchLayout.addWidget(self.bchNow)
        bchLayout.addStretch()
        # XEM余力
        xemLayout = QHBoxLayout()
        xemLayout.addWidget(xemLabel)
        xemLayout.addWidget(self.xemNow)
        xemLayout.addStretch()
        # ETH余力
        ethLayout = QHBoxLayout()
        ethLayout.addWidget(ethLabel)
        ethLayout.addWidget(self.ethNow)
        ethLayout.addStretch()
        # 最も新しい損益
        latestProfitLayout = QHBoxLayout()
        latestProfitLayout.addWidget(latestProfitLabel)
        latestProfitLayout.addWidget(self.latestProfit_Now)
        # 取引状態
        tradeStateLayout = QHBoxLayout()
        tradeStateLayout.addWidget(tradeStateLabel)
        tradeStateLayout.addWidget(self.tradeState)
        # ボタン
        buttonsLayout = QVBoxLayout()
        buttonsLayout.addWidget(self.start_auto)
        buttonsLayout.addWidget(self.stop_auto)
        buttonsLayout.addWidget(exportCSV)
        buttonsLayout.addWidget(QLabel())
        buttonsLayout.addWidget(quit_app)
        
        # GUIレイアウト1
        GUI_Layout1 = QVBoxLayout()
        GUI_Layout1.addWidget(currentFundsLabel)
        GUI_Layout1.addLayout(jpyLayout)
        GUI_Layout1.addLayout(btcLayout)
        GUI_Layout1.addLayout(monaLayout)
        GUI_Layout1.addLayout(bchLayout)
        GUI_Layout1.addLayout(xemLayout)
        GUI_Layout1.addLayout(ethLayout)
        GUI_Layout1.addWidget(cutterLabel)
        GUI_Layout1.addLayout(latestProfitLayout)
        GUI_Layout1.addLayout(tradeStateLayout)
        GUI_Layout1.addLayout(buttonsLayout)
        
        # GUIレイアウト2====================================
        estimatesLabel = QLabel('===== 予想損益額 =====')
        estLabel_JpyBtcMona = QLabel('| JPY->BTC->MONA: ')
        self.est_JpyBtcMona = QLabel('###')
        estLabel_JpyMonaBtc = QLabel('| JPY->MONA->BTC: ')
        self.est_JpyMonaBtc = QLabel('###')
        estLabel_JpyBtcBch = QLabel('| JPY->BTC->BCH: ')
        self.est_JpyBtcBch = QLabel('###')
        estLabel_JpyBchBtc = QLabel('| JPY->BCH->BTC: ')
        self.est_JpyBchBtc = QLabel('###')
        estLabel_JpyBtcXem = QLabel('| JPY->BTC->XEM: ')
        self.est_JpyBtcXem = QLabel('###')
        estLabel_JpyXemBtc = QLabel('| JPY->XEM->BTC: ')
        self.est_JpyXemBtc = QLabel('###')
        estLabel_JpyBtcEth = QLabel('| JPY->BTC->ETH: ')
        self.est_JpyBtcEth = QLabel('###')
        estLabel_JpyEthBtc = QLabel('| JPY->ETH->BTC: ')
        self.est_JpyEthBtc = QLabel('###')
        
        statisticsLabel = QLabel('===== 三角裁定の統計 =====')
        All_Trade_N_Label = QLabel('| 取引巡数：')
        self.All_Trade_N_Now = QLabel('###')
        All_Profit_N_Label = QLabel('| 利益の回数：')
        self.All_Profit_N_Now = QLabel('###')
        All_Profit_Rate_Label = QLabel('| 利益となる割合：')
        self.All_Profit_Rate_Now = QLabel('###')
        All_Ave_Profits_Label = QLabel('| 損益の平均：')
        self.All_Ave_Profits_Now = QLabel('###')
        All_SD_Profits_Label = QLabel('| 損益の標準偏差：')
        self.All_SD_Profits_Now = QLabel('###')
        
        # レイアウト作成
        # 予想損益額
        # JPY->BTC->MONA
        estLayoutJpyBtcMona = QHBoxLayout()
        estLayoutJpyBtcMona.addWidget(estLabel_JpyBtcMona)
        estLayoutJpyBtcMona.addWidget(self.est_JpyBtcMona)
        # JPY->MONA->BTC
        estLayoutJpyMonaBtc = QHBoxLayout()
        estLayoutJpyMonaBtc.addWidget(estLabel_JpyMonaBtc)
        estLayoutJpyMonaBtc.addWidget(self.est_JpyMonaBtc)
        # JPY->BTC->BCH
        estLayoutJpyBtcBch = QHBoxLayout()
        estLayoutJpyBtcBch.addWidget(estLabel_JpyBtcBch)
        estLayoutJpyBtcBch.addWidget(self.est_JpyBtcBch)
        # JPY->BCH->BTC
        estLayoutJpyBchBtc = QHBoxLayout()
        estLayoutJpyBchBtc.addWidget(estLabel_JpyBchBtc)
        estLayoutJpyBchBtc.addWidget(self.est_JpyBchBtc)
        # JPY->BTC->XEM
        estLayoutJpyBtcXem = QHBoxLayout()
        estLayoutJpyBtcXem.addWidget(estLabel_JpyBtcXem)
        estLayoutJpyBtcXem.addWidget(self.est_JpyBtcXem)
        # JPY->XEM->BTC
        estLayoutJpyXemBtc = QHBoxLayout()
        estLayoutJpyXemBtc.addWidget(estLabel_JpyXemBtc)
        estLayoutJpyXemBtc.addWidget(self.est_JpyXemBtc)
        # JPY->BTC->ETH
        estLayoutJpyBtcEth = QHBoxLayout()
        estLayoutJpyBtcEth.addWidget(estLabel_JpyBtcEth)
        estLayoutJpyBtcEth.addWidget(self.est_JpyBtcEth)
        # JPY->ETH->BTC
        estLayoutJpyEthBtc = QHBoxLayout()
        estLayoutJpyEthBtc.addWidget(estLabel_JpyEthBtc)
        estLayoutJpyEthBtc.addWidget(self.est_JpyEthBtc)
        
        # 取引の統計
        # 取引巡数
        All_Trade_N_Layout = QHBoxLayout()
        All_Trade_N_Layout.addWidget(All_Trade_N_Label)
        All_Trade_N_Layout.addWidget(self.All_Trade_N_Now)
        # 利益の回数
        All_Profit_N_Layout = QHBoxLayout()
        All_Profit_N_Layout.addWidget(All_Profit_N_Label)
        All_Profit_N_Layout.addWidget(self.All_Profit_N_Now)
        # 利益の割合
        All_Profit_Rate_Layout = QHBoxLayout()
        All_Profit_Rate_Layout.addWidget(All_Profit_Rate_Label)
        All_Profit_Rate_Layout.addWidget(self.All_Profit_Rate_Now)
        # 損益の平均
        All_Ave_Profits_Layout = QHBoxLayout()
        All_Ave_Profits_Layout.addWidget(All_Ave_Profits_Label)
        All_Ave_Profits_Layout.addWidget(self.All_Ave_Profits_Now)
        # 損益の標準偏差
        All_SD_Profits_Layout = QHBoxLayout()
        All_SD_Profits_Layout.addWidget(All_SD_Profits_Label)
        All_SD_Profits_Layout.addWidget(self.All_SD_Profits_Now)
        
        # GUIレイアウト2
        GUI_Layout2 = QVBoxLayout()
        GUI_Layout2.addWidget(estimatesLabel)
        GUI_Layout2.addLayout(estLayoutJpyBtcMona)
        GUI_Layout2.addLayout(estLayoutJpyMonaBtc)
        GUI_Layout2.addLayout(estLayoutJpyBtcBch)
        GUI_Layout2.addLayout(estLayoutJpyBchBtc)
        GUI_Layout2.addLayout(estLayoutJpyBtcXem)
        GUI_Layout2.addLayout(estLayoutJpyXemBtc)
        GUI_Layout2.addLayout(estLayoutJpyBtcEth)
        GUI_Layout2.addLayout(estLayoutJpyEthBtc)
        GUI_Layout2.addWidget(statisticsLabel)
        GUI_Layout2.addLayout(All_Trade_N_Layout)
        GUI_Layout2.addLayout(All_Profit_N_Layout)
        GUI_Layout2.addLayout(All_Profit_Rate_Layout)
        GUI_Layout2.addLayout(All_Ave_Profits_Layout)
        GUI_Layout2.addLayout(All_SD_Profits_Layout)
        
        # GUIレイアウト3===========================================
        # 上部===========================
        Profit_in_Trade_Label = QLabel('| 取引毎の損益')
        Ave_Profits_in_Trade_Label = QLabel('【平均】')
        SD_Profits_in_Trade_Label = QLabel('【標準偏差】')
        Trade_N_in_Trade_Label = QLabel('【取引数】')
        Profit_N_in_Trade_Label = QLabel('【利益数】')
        Profit_Rate_in_Trade_Label = QLabel('【利益の割合】')
        
        JPY_BTC_MONA_Label = QLabel('| JPY->BTC->MONA: ')
        JPY_MONA_BTC_Label = QLabel('| JPY->MONA->BTC: ')
        JPY_BTC_BCH_Label = QLabel('| JPY->BTC->BCH: ')
        JPY_BCH_BTC_Label = QLabel('| JPY->BCH->BTC: ')
        JPY_BTC_XEM_Label = QLabel('| JPY->BTC->XEM: ')
        JPY_XEM_BTC_Label = QLabel('| JPY->XEM->BTC: ')
        JPY_BTC_ETH_Label = QLabel('| JPY->BTC->ETH: ')
        JPY_ETH_BTC_Label = QLabel('| JPY->ETH->BTC: ')
        # 損益の平均
        self.Ave_JPY_BTC_MONA_Now = QLabel('###')
        self.Ave_JPY_MONA_BTC_Now = QLabel('###')
        self.Ave_JPY_BTC_BCH_Now = QLabel('###')
        self.Ave_JPY_BCH_BTC_Now = QLabel('###')
        self.Ave_JPY_BTC_XEM_Now = QLabel('###')
        self.Ave_JPY_XEM_BTC_Now = QLabel('###')
        self.Ave_JPY_BTC_ETH_Now = QLabel('###')
        self.Ave_JPY_ETH_BTC_Now = QLabel('###')
        # 損益の標準偏差
        self.SD_JPY_BTC_MONA_Now = QLabel('###')
        self.SD_JPY_MONA_BTC_Now = QLabel('###')
        self.SD_JPY_BTC_BCH_Now = QLabel('###')
        self.SD_JPY_BCH_BTC_Now = QLabel('###')
        self.SD_JPY_BTC_XEM_Now = QLabel('###')
        self.SD_JPY_XEM_BTC_Now = QLabel('###')
        self.SD_JPY_BTC_ETH_Now = QLabel('###')
        self.SD_JPY_ETH_BTC_Now = QLabel('###')
        # 取引数
        self.Trade_N_JPY_BTC_MONA_Now = QLabel('###')
        self.Trade_N_JPY_MONA_BTC_Now = QLabel('###')
        self.Trade_N_JPY_BTC_BCH_Now = QLabel('###')
        self.Trade_N_JPY_BCH_BTC_Now = QLabel('###')
        self.Trade_N_JPY_BTC_XEM_Now = QLabel('###')
        self.Trade_N_JPY_XEM_BTC_Now = QLabel('###')
        self.Trade_N_JPY_BTC_ETH_Now = QLabel('###')
        self.Trade_N_JPY_ETH_BTC_Now = QLabel('###')
        # 利益数
        self.Profit_N_JPY_BTC_MONA_Now = QLabel('###')
        self.Profit_N_JPY_MONA_BTC_Now = QLabel('###')
        self.Profit_N_JPY_BTC_BCH_Now = QLabel('###')
        self.Profit_N_JPY_BCH_BTC_Now = QLabel('###')
        self.Profit_N_JPY_BTC_XEM_Now = QLabel('###')
        self.Profit_N_JPY_XEM_BTC_Now = QLabel('###')
        self.Profit_N_JPY_BTC_ETH_Now = QLabel('###')
        self.Profit_N_JPY_ETH_BTC_Now = QLabel('###')
        # 利益の割合
        self.Profit_Rate_JPY_BTC_MONA_Now = QLabel('###')
        self.Profit_Rate_JPY_MONA_BTC_Now = QLabel('###')
        self.Profit_Rate_JPY_BTC_BCH_Now = QLabel('###')
        self.Profit_Rate_JPY_BCH_BTC_Now = QLabel('###')
        self.Profit_Rate_JPY_BTC_XEM_Now = QLabel('###')
        self.Profit_Rate_JPY_XEM_BTC_Now = QLabel('###')
        self.Profit_Rate_JPY_BTC_ETH_Now = QLabel('###')
        self.Profit_Rate_JPY_ETH_BTC_Now = QLabel('###')
        
        # レイアウト作成
        Labels_in_Trade_LayoutUP = QVBoxLayout()
        Labels_in_Trade_LayoutUP.addWidget(Profit_in_Trade_Label)
        Labels_in_Trade_LayoutUP.addWidget(JPY_BTC_MONA_Label)
        Labels_in_Trade_LayoutUP.addWidget(JPY_MONA_BTC_Label)
        Labels_in_Trade_LayoutUP.addWidget(JPY_BTC_BCH_Label)
        Labels_in_Trade_LayoutUP.addWidget(JPY_BCH_BTC_Label)
        Labels_in_Trade_LayoutUP.addWidget(JPY_BTC_XEM_Label)
        Labels_in_Trade_LayoutUP.addWidget(JPY_XEM_BTC_Label)
        Labels_in_Trade_LayoutUP.addWidget(JPY_BTC_ETH_Label)
        Labels_in_Trade_LayoutUP.addWidget(JPY_ETH_BTC_Label)
        
        Aves_in_Trade_Layout = QVBoxLayout()
        Aves_in_Trade_Layout.addWidget(Ave_Profits_in_Trade_Label)
        Aves_in_Trade_Layout.addWidget(self.Ave_JPY_BTC_MONA_Now)
        Aves_in_Trade_Layout.addWidget(self.Ave_JPY_MONA_BTC_Now)
        Aves_in_Trade_Layout.addWidget(self.Ave_JPY_BTC_BCH_Now)
        Aves_in_Trade_Layout.addWidget(self.Ave_JPY_BCH_BTC_Now)
        Aves_in_Trade_Layout.addWidget(self.Ave_JPY_BTC_XEM_Now)
        Aves_in_Trade_Layout.addWidget(self.Ave_JPY_XEM_BTC_Now)
        Aves_in_Trade_Layout.addWidget(self.Ave_JPY_BTC_ETH_Now)
        Aves_in_Trade_Layout.addWidget(self.Ave_JPY_ETH_BTC_Now)
        
        SD_in_Trade_Layout = QVBoxLayout()
        SD_in_Trade_Layout.addWidget(SD_Profits_in_Trade_Label)
        SD_in_Trade_Layout.addWidget(self.SD_JPY_BTC_MONA_Now)
        SD_in_Trade_Layout.addWidget(self.SD_JPY_MONA_BTC_Now)
        SD_in_Trade_Layout.addWidget(self.SD_JPY_BTC_BCH_Now)
        SD_in_Trade_Layout.addWidget(self.SD_JPY_BCH_BTC_Now)
        SD_in_Trade_Layout.addWidget(self.SD_JPY_BTC_XEM_Now)
        SD_in_Trade_Layout.addWidget(self.SD_JPY_XEM_BTC_Now)
        SD_in_Trade_Layout.addWidget(self.SD_JPY_BTC_ETH_Now)
        SD_in_Trade_Layout.addWidget(self.SD_JPY_ETH_BTC_Now)
        
        Trade_N_in_Trade_Layout = QVBoxLayout()
        Trade_N_in_Trade_Layout.addWidget(Trade_N_in_Trade_Label)
        Trade_N_in_Trade_Layout.addWidget(self.Trade_N_JPY_BTC_MONA_Now)
        Trade_N_in_Trade_Layout.addWidget(self.Trade_N_JPY_MONA_BTC_Now)
        Trade_N_in_Trade_Layout.addWidget(self.Trade_N_JPY_BTC_BCH_Now)
        Trade_N_in_Trade_Layout.addWidget(self.Trade_N_JPY_BCH_BTC_Now)
        Trade_N_in_Trade_Layout.addWidget(self.Trade_N_JPY_BTC_XEM_Now)
        Trade_N_in_Trade_Layout.addWidget(self.Trade_N_JPY_XEM_BTC_Now)
        Trade_N_in_Trade_Layout.addWidget(self.Trade_N_JPY_BTC_ETH_Now)
        Trade_N_in_Trade_Layout.addWidget(self.Trade_N_JPY_ETH_BTC_Now)
        
        Profit_N_in_Trade_Layout = QVBoxLayout()
        Profit_N_in_Trade_Layout.addWidget(Profit_N_in_Trade_Label)
        Profit_N_in_Trade_Layout.addWidget(self.Profit_N_JPY_BTC_MONA_Now)
        Profit_N_in_Trade_Layout.addWidget(self.Profit_N_JPY_MONA_BTC_Now)
        Profit_N_in_Trade_Layout.addWidget(self.Profit_N_JPY_BTC_BCH_Now)
        Profit_N_in_Trade_Layout.addWidget(self.Profit_N_JPY_BCH_BTC_Now)
        Profit_N_in_Trade_Layout.addWidget(self.Profit_N_JPY_BTC_XEM_Now)
        Profit_N_in_Trade_Layout.addWidget(self.Profit_N_JPY_XEM_BTC_Now)
        Profit_N_in_Trade_Layout.addWidget(self.Profit_N_JPY_BTC_ETH_Now)
        Profit_N_in_Trade_Layout.addWidget(self.Profit_N_JPY_ETH_BTC_Now)
        
        Profit_Rate_in_Trade_Layout = QVBoxLayout()
        Profit_Rate_in_Trade_Layout.addWidget(Profit_Rate_in_Trade_Label)
        Profit_Rate_in_Trade_Layout.addWidget(self.Profit_Rate_JPY_BTC_MONA_Now)
        Profit_Rate_in_Trade_Layout.addWidget(self.Profit_Rate_JPY_MONA_BTC_Now)
        Profit_Rate_in_Trade_Layout.addWidget(self.Profit_Rate_JPY_BTC_BCH_Now)
        Profit_Rate_in_Trade_Layout.addWidget(self.Profit_Rate_JPY_BCH_BTC_Now)
        Profit_Rate_in_Trade_Layout.addWidget(self.Profit_Rate_JPY_BTC_XEM_Now)
        Profit_Rate_in_Trade_Layout.addWidget(self.Profit_Rate_JPY_XEM_BTC_Now)
        Profit_Rate_in_Trade_Layout.addWidget(self.Profit_Rate_JPY_BTC_ETH_Now)
        Profit_Rate_in_Trade_Layout.addWidget(self.Profit_Rate_JPY_ETH_BTC_Now)
        
        GUI_Layout3up = QHBoxLayout()
        GUI_Layout3up.addLayout(Labels_in_Trade_LayoutUP)
        GUI_Layout3up.addLayout(Aves_in_Trade_Layout)
        GUI_Layout3up.addLayout(SD_in_Trade_Layout)
        GUI_Layout3up.addLayout(Trade_N_in_Trade_Layout)
        GUI_Layout3up.addLayout(Profit_N_in_Trade_Layout)
        GUI_Layout3up.addLayout(Profit_Rate_in_Trade_Layout)
        
        # 下部===========================
        Pairs_in_Trade_Label = QLabel('| 取引ペア')
        Ave_Minutes_in_Trade_Label = QLabel('【平均[分]】')
        Ave_ReTrades_in_Trade_Label = QLabel('【再取引数】')
        
        BtcJpy_Label = QLabel('| BTC/JPY: ')
        MonaBtc_Label = QLabel('| MONA/BTC: ')
        MonaJpy_Label = QLabel('| MONA/JPY: ')
        BchBtc_Label = QLabel('| BCH/BTC: ')
        BchJpy_Label = QLabel('| BCH/JPY: ')
        XemBtc_Label = QLabel('| XEM/BTC: ')
        XemJpy_Label = QLabel('| XEM/JPY: ')
        EthBtc_Label = QLabel('| ETH/BTC: ')
        EthJpy_Label = QLabel('| ETH/JPY: ')
        
        self.Ave_Minutes_BtcJpy = QLabel('###')
        self.Ave_Minutes_MonaBtc = QLabel('###')
        self.Ave_Minutes_MonaJpy = QLabel('###')
        self.Ave_Minutes_BchBtc = QLabel('###')
        self.Ave_Minutes_BchJpy = QLabel('###')
        self.Ave_Minutes_XemBtc = QLabel('###')
        self.Ave_Minutes_XemJpy = QLabel('###')
        self.Ave_Minutes_EthBtc = QLabel('###')
        self.Ave_Minutes_EthJpy = QLabel('###')
        
        self.Ave_ReTrades_BtcJpy = QLabel('###')
        self.Ave_ReTrades_MonaBtc = QLabel('###')
        self.Ave_ReTrades_MonaJpy = QLabel('###')
        self.Ave_ReTrades_BchBtc = QLabel('###')
        self.Ave_ReTrades_BchJpy = QLabel('###')
        self.Ave_ReTrades_XemBtc = QLabel('###')
        self.Ave_ReTrades_XemJpy = QLabel('###')
        self.Ave_ReTrades_EthBtc = QLabel('###')
        self.Ave_ReTrades_EthJpy = QLabel('###')
        
        Pairs_in_Trade_Layout = QVBoxLayout()
        Pairs_in_Trade_Layout.addWidget(Pairs_in_Trade_Label)
        Pairs_in_Trade_Layout.addWidget(BtcJpy_Label)
        Pairs_in_Trade_Layout.addWidget(MonaBtc_Label)
        Pairs_in_Trade_Layout.addWidget(MonaJpy_Label)
        Pairs_in_Trade_Layout.addWidget(BchBtc_Label)
        Pairs_in_Trade_Layout.addWidget(BchJpy_Label)
        Pairs_in_Trade_Layout.addWidget(XemBtc_Label)
        Pairs_in_Trade_Layout.addWidget(XemJpy_Label)
        Pairs_in_Trade_Layout.addWidget(EthBtc_Label)
        Pairs_in_Trade_Layout.addWidget(EthJpy_Label)
        
        Ave_Minutes_in_Trade_Layout = QVBoxLayout()
        Ave_Minutes_in_Trade_Layout.addWidget(Ave_Minutes_in_Trade_Label)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_BtcJpy)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_MonaBtc)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_MonaJpy)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_BchBtc)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_BchJpy)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_XemBtc)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_XemJpy)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_EthBtc)
        Ave_Minutes_in_Trade_Layout.addWidget(self.Ave_Minutes_EthJpy)
        
        Ave_ReTrades_in_Trade_Layout = QVBoxLayout()
        Ave_ReTrades_in_Trade_Layout.addWidget(Ave_ReTrades_in_Trade_Label)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_BtcJpy)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_MonaBtc)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_MonaJpy)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_BchBtc)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_BchJpy)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_XemBtc)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_XemJpy)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_EthBtc)
        Ave_ReTrades_in_Trade_Layout.addWidget(self.Ave_ReTrades_EthJpy)
        
        GUI_Layout3down = QHBoxLayout()
        GUI_Layout3down.addLayout(Pairs_in_Trade_Layout)
        GUI_Layout3down.addLayout(Ave_Minutes_in_Trade_Layout)
        GUI_Layout3down.addLayout(Ave_ReTrades_in_Trade_Layout)
        GUI_Layout3down.addStretch()
        
        # レイアウト結合
        GUI_Layout3 = QVBoxLayout()
        GUI_Layout3.addLayout(GUI_Layout3up)
        GUI_Layout3.addLayout(GUI_Layout3down)
        
        # GUI作成
        GUI_MainLayout = QHBoxLayout()
        GUI_MainLayout.addLayout(GUI_Layout1)
        GUI_MainLayout.addLayout(GUI_Layout2)
        GUI_MainLayout.addLayout(GUI_Layout3)
        GUI_MainLayout.addStretch()
        self.setLayout(GUI_MainLayout)  # ウィンドウにレイアウトを適用
        
        # アプリ起動時にも統計データ表示
        resultList = self.dba.statisticsTradeResult()
        self.displayStatistics(resultList)
        print('stand by >')
    
    # 取引開始
    def startButton(self):
        self.tradeThread.onLoop()
        self.start_auto.setEnabled(False)
        self.stop_auto.setEnabled(True)
        self.tradeState.setText(self.yes_trading)
        
        self.tradeThread.setObj(self.exc, self.dba)
        self.tradeThread.start()
    
    # 取引終了後に呼ばれ，取引開始ボタンをクリック可能にする
    def releaseStartButton(self):
        self.start_auto.setEnabled(True)
        self.tradeState.setText(self.no_trading)
    
    # ループフラグを0にし，取引終了まで待つ
    def stopButton(self):
        self.stop_auto.setEnabled(False)
        self.tradeThread.offLoop()
    
    # 取引状態の表示を更新
    def stateChanger(self, state):
        self.tradeState.setText(state)
    
    # 予想利益額の表示を更新
    def displayCalcs(self, data):
        self.est_JpyBtcMona.setText(str(data[0]))
        self.est_JpyMonaBtc.setText(str(data[1]))
        self.est_JpyBtcBch.setText(str(data[2]))
        self.est_JpyBchBtc.setText(str(data[3]))
        self.est_JpyBtcXem.setText(str(data[4]))
        self.est_JpyXemBtc.setText(str(data[5]))
        self.est_JpyBtcEth.setText(str(data[6]))
        self.est_JpyEthBtc.setText(str(data[7]))
    
    # 統計結果の表示を更新
    def displayStatistics(self, data):
        profitsList = data[0]
        minutesList = data[1]
        retradesList = data[2]
        
        # profitsList:===================================
        # [0]:取引回数
        # [1]:利益となった回数
        # [2]:利益となった割合
        # [3]:損益の平均
        # [4]:損益の標準偏差
        #   ┌    ―――――――――――――――――――――――> j
        #   ｜        0           1        2           3              4
        # | ｜全体[ 取引数 ], [ 益数 ], [ 益率 ], [ 損益平均 ], [ 損益標偏 ]
        # | ｜JPY->BTC->MONA [  ], [  ], [  ], [  ], [  ]
        # V ｜JPY->MONA->BTC [  ], [  ], [  ], [  ], [  ]
        # i ｜JPY->BTC->BCH  [  ], [  ], [  ], [  ], [  ]
        #   ｜JPY->BCH->BTC  [  ], [  ], [  ], [  ], [  ]
        #   ｜JPY->BTC->XEM  [  ], [  ], [  ], [  ], [  ]
        #   ｜JPY->XEM->BTC  [  ], [  ], [  ], [  ], [  ]
        #   ｜JPY->BTC->ETH  [  ], [  ], [  ], [  ], [  ]
        #   ｜JPY->ETH->BTC  [  ], [  ], [  ], [  ], [  ]
        #   └
        self.All_Trade_N_Now.setText(str(profitsList[0][0]))
        self.All_Profit_N_Now.setText(str(profitsList[0][1]))
        self.All_Profit_Rate_Now.setText(str(profitsList[0][2]) + '%')
        self.All_Ave_Profits_Now.setText(str(profitsList[0][3]))
        self.All_SD_Profits_Now.setText(str(profitsList[0][4]))
        
        self.Trade_N_JPY_BTC_MONA_Now.setText(str(profitsList[1][0]))
        self.Profit_N_JPY_BTC_MONA_Now.setText(str(profitsList[1][1]))
        self.Profit_Rate_JPY_BTC_MONA_Now.setText(str(profitsList[1][2]) + '%')
        self.Ave_JPY_BTC_MONA_Now.setText(str(profitsList[1][3]))
        self.SD_JPY_BTC_MONA_Now.setText(str(profitsList[1][4]))
        
        self.Trade_N_JPY_MONA_BTC_Now.setText(str(profitsList[2][0]))
        self.Profit_N_JPY_MONA_BTC_Now.setText(str(profitsList[2][1]))
        self.Profit_Rate_JPY_MONA_BTC_Now.setText(str(profitsList[2][2]) + '%')
        self.Ave_JPY_MONA_BTC_Now.setText(str(profitsList[2][3]))
        self.SD_JPY_MONA_BTC_Now.setText(str(profitsList[2][4]))
        
        self.Trade_N_JPY_BTC_BCH_Now.setText(str(profitsList[3][0]))
        self.Profit_N_JPY_BTC_BCH_Now.setText(str(profitsList[3][1]))
        self.Profit_Rate_JPY_BTC_BCH_Now.setText(str(profitsList[3][2]) + '%')
        self.Ave_JPY_BTC_BCH_Now.setText(str(profitsList[3][3]))
        self.SD_JPY_BTC_BCH_Now.setText(str(profitsList[3][4]))
        
        self.Trade_N_JPY_BCH_BTC_Now.setText(str(profitsList[4][0]))
        self.Profit_N_JPY_BCH_BTC_Now.setText(str(profitsList[4][1]))
        self.Profit_Rate_JPY_BCH_BTC_Now.setText(str(profitsList[4][2]) + '%')
        self.Ave_JPY_BCH_BTC_Now.setText(str(profitsList[4][3]))
        self.SD_JPY_BCH_BTC_Now.setText(str(profitsList[4][4]))
        
        self.Trade_N_JPY_BTC_XEM_Now.setText(str(profitsList[5][0]))
        self.Profit_N_JPY_BTC_XEM_Now.setText(str(profitsList[5][1]))
        self.Profit_Rate_JPY_BTC_XEM_Now.setText(str(profitsList[5][2]) + '%')
        self.Ave_JPY_BTC_XEM_Now.setText(str(profitsList[5][3]))
        self.SD_JPY_BTC_XEM_Now.setText(str(profitsList[5][4]))
        
        self.Trade_N_JPY_XEM_BTC_Now.setText(str(profitsList[6][0]))
        self.Profit_N_JPY_XEM_BTC_Now.setText(str(profitsList[6][1]))
        self.Profit_Rate_JPY_XEM_BTC_Now.setText(str(profitsList[6][2]) + '%')
        self.Ave_JPY_XEM_BTC_Now.setText(str(profitsList[6][3]))
        self.SD_JPY_XEM_BTC_Now.setText(str(profitsList[6][4]))
        
        self.Trade_N_JPY_BTC_ETH_Now.setText(str(profitsList[7][0]))
        self.Profit_N_JPY_BTC_ETH_Now.setText(str(profitsList[7][1]))
        self.Profit_Rate_JPY_BTC_ETH_Now.setText(str(profitsList[7][2]) + '%')
        self.Ave_JPY_BTC_ETH_Now.setText(str(profitsList[7][3]))
        self.SD_JPY_BTC_ETH_Now.setText(str(profitsList[7][4]))
        
        self.Trade_N_JPY_ETH_BTC_Now.setText(str(profitsList[8][0]))
        self.Profit_N_JPY_ETH_BTC_Now.setText(str(profitsList[8][1]))
        self.Profit_Rate_JPY_ETH_BTC_Now.setText(str(profitsList[8][2]) + '%')
        self.Ave_JPY_ETH_BTC_Now.setText(str(profitsList[8][3]))
        self.SD_JPY_ETH_BTC_Now.setText(str(profitsList[8][4]))
        
        # minutesList:===================================
        # [0]:BTC_JPY
        # [1]:MONA_BTC
        # [2]:MONA_JPY
        # [3]:BCH_BTC
        # [4]:BCH_JPY
        # [5]:XEM_BTC
        # [6]:XEM_JPY
        # [7]:ETH_BTC
        # [8]:ETH_JPY
        self.Ave_Minutes_BtcJpy.setText(str(minutesList[0]))
        self.Ave_Minutes_MonaBtc.setText(str(minutesList[1]))
        self.Ave_Minutes_MonaJpy.setText(str(minutesList[2]))
        self.Ave_Minutes_BchBtc.setText(str(minutesList[3]))
        self.Ave_Minutes_BchJpy.setText(str(minutesList[4]))
        self.Ave_Minutes_XemBtc.setText(str(minutesList[5]))
        self.Ave_Minutes_XemJpy.setText(str(minutesList[6]))
        self.Ave_Minutes_EthBtc.setText(str(minutesList[7]))
        self.Ave_Minutes_EthJpy.setText(str(minutesList[8]))
        
        # retradesList:===================================
        # [0]:BTC_JPY
        # [1]:MONA_BTC
        # [2]:MONA_JPY
        # [3]:BCH_BTC
        # [4]:BCH_JPY
        # [5]:XEM_BTC
        # [6]:XEM_JPY
        # [7]:ETH_BTC
        # [8]:ETH_JPY
        self.Ave_ReTrades_BtcJpy.setText(str(retradesList[0]))
        self.Ave_ReTrades_MonaBtc.setText(str(retradesList[1]))
        self.Ave_ReTrades_MonaJpy.setText(str(retradesList[2]))
        self.Ave_ReTrades_BchBtc.setText(str(retradesList[3]))
        self.Ave_ReTrades_BchJpy.setText(str(retradesList[4]))
        self.Ave_ReTrades_XemBtc.setText(str(retradesList[5]))
        self.Ave_ReTrades_XemJpy.setText(str(retradesList[6]))
        self.Ave_ReTrades_EthBtc.setText(str(retradesList[7]))
        self.Ave_ReTrades_EthJpy.setText(str(retradesList[8]))
    
    # 余力額の表示を更新
    def displayFunds(self, data):
        self.jpyNow.setText(str(data[0]))
        self.btcNow.setText(str(data[1]))
        self.monaNow.setText(str(data[2]))
        self.bchNow.setText(str(data[3]))
        self.xemNow.setText(str(data[4]))
        self.ethNow.setText(str(data[5]))
    
    # 最新の損益額の表示を更新
    def displayProfit(self, data):
        self.latestProfit_Now.setText(str(data))
        print('Latest JPY&profit: ', end='')
        print(data)
    
    # DBの全データをCSV出力
    def exportData(self):
        self.dba.exportToCSV()
