# -*- coding: utf-8 -*-
import sqlite3
import statistics
import csv
import os


class DBaccess:
    dbName = 'trade_history.db'  # DB名
    tableName_Routes = 'Routes'  # 取引1巡ごと
    tableName_Trades = 'Trades'  # 取引ごと
    
    def __init__(self):
        print('DB init...')
        con = sqlite3.connect(self.dbName)
        # テーブルがなければ作る
        # integer + primary keyなら自動連番もする
        con.execute("create table if not exists %s("
                    "num integer primary key,"
                    "route text not null,"
                    "prev integer not null,"
                    "estimate integer not null,"
                    "profit integer not null)" % (self.tableName_Routes))
        con.commit()  # トランザクションをコミット
        con.execute("create table if not exists %s("
                    "num integer primary key,"
                    "route text not null,"
                    "trade text not null,"
                    "minutes integer not null,"
                    "retrades integer not null)" % (self.tableName_Trades))
        con.commit()
        con.close()
    
    # デバッグ用データ登録テスト
    def insertTest(self):
        print('insert test...')
        con = sqlite3.connect(self.dbName)
        con.execute(
            "insert into %s(route,prev,estimate,profit)"
            "values('JPY->BTC->MONA',3,2,1)" %
            (self.tableName_Routes))
        con.commit()
        
        con.execute(
            "insert into %s(route,trade,minutes,retrades)"
            "values('JPY->BTC->MONA','JPY->BTC',2,1)" %
            (self.tableName_Trades))
        con.commit()
        
        con.execute(
            "insert into %s(route,trade,minutes,retrades)"
            "values('JPY->BTC->MONA','BTC->MONA',2,1)" %
            (self.tableName_Trades))
        con.commit()
        
        con.execute(
            "insert into %s(route,trade,minutes,retrades)"
            "values('JPY->BTC->MONA','MONA->JPY',2,1)" %
            (self.tableName_Trades))
        con.commit()
        con.close()
    
    # 取引1回の結果を登録
    def insertTrade(self, route: str, trade: str, minutes: int, retrades: int):
        print('insert Trade...')
        con = sqlite3.connect(self.dbName)
        con.execute(
            "insert into %s(route,trade,minutes,retrades)"
            "values(?,?,?,?)" %
            (self.tableName_Trades),
            [route, trade, minutes, retrades])
        con.commit()
        con.close()
    
    # 取引1巡の結果を登録
    def insertRoute(self, route: str, prevJPY: int, estJPY: int, profit: int):
        print('insert Route...')
        con = sqlite3.connect(self.dbName)
        con.execute(
            "insert into %s(route,prev,estimate,profit)"
            "values(?,?,?,?)" %
            (self.tableName_Routes),
            [route, prevJPY, estJPY, profit])
        con.commit()
        con.close()
    
    # DB全データをCSV出力
    def exportToCSV(self):
        print('exporting to CSV...', end=' ', flush=True)
        con = sqlite3.connect(self.dbName)
        cur = con.cursor()
        cur.execute("select * from %s" % (self.tableName_Routes))
        data = cur.fetchall()
        
        csvPath = 'dbData_Route.csv'
        if os.path.exists(csvPath):
            state = 'w'
        else:
            state = 'a'
        with open(csvPath, state, newline='', encoding='shift-jis') as f:
            writer = csv.writer(f)
            writer.writerow(['番号', '取引順', '投資額', '予想利益', '損益'])
            for row in data:
                writer.writerow(row)
        
        cur.execute("select * from %s" % (self.tableName_Trades))
        data = cur.fetchall()
        
        csvPath = 'dbData_Trade.csv'
        if os.path.exists(csvPath):
            state = 'w'
        else:
            state = 'a'
        with open(csvPath, state, newline='', encoding='shift-jis') as f:
            writer = csv.writer(f)
            writer.writerow(['番号', '取引順', '取引', '経過(分)', '再取引数'])
            for row in data:
                writer.writerow(row)
        
        con.close()
        print('Complete. Ready >')
    
    def statisticsTradeResult(self):
        print('read from database and statistics...')
        # 損益を格納，平均と標準偏差の計算に使う========================
        All_Profits = []
        JpyBtcMona_Profits = []
        JpyMonaBtc_Profits = []
        JpyBtcBch_Profits = []
        JpyBchBtc_Profits = []
        JpyBtcXem_Profits = []
        JpyXemBtc_Profits = []
        JpyBtcEth_Profits = []
        JpyEthBtc_Profits = []
        # 取引時間を格納，平均の計算に使う====================
        BTC_JPY_minutes = []
        MONA_BTC_minutes = []
        MONA_JPY_minutes = []
        BCH_BTC_minutes = []
        BCH_JPY_minutes = []
        XEM_BTC_minutes = []
        XEM_JPY_minutes = []
        ETH_BTC_minutes = []
        ETH_JPY_minutes = []
        # 再取引回数を格納，平均の計算に使う==================
        BTC_JPY_retrades = []
        MONA_BTC_retrades = []
        MONA_JPY_retrades = []
        BCH_BTC_retrades = []
        BCH_JPY_retrades = []
        XEM_BTC_retrades = []
        XEM_JPY_retrades = []
        ETH_BTC_retrades = []
        ETH_JPY_retrades = []
        
        profitsList = []  # 損益に関わる統計結果を格納
        minutesList = []  # 取引時間に関わる統計結果を格納
        retradesList = []  # 再取引回数に関わる統計結果を格納
        
        # DB接続==============================
        con = sqlite3.connect(self.dbName)
        cur = con.cursor()
        # Routesテーブル中身：
        # [0]:num
        # [1]:route
        # [2]:prev
        # [3]:estimate
        # [4]:profit
        cur.execute("select * from %s" % (self.tableName_Routes))
        data = cur.fetchall()
        for row in data:
            All_Profits.append(row[4])
            if row[1] == 'JPY->BTC->MONA':
                JpyBtcMona_Profits.append(row[4])
            elif row[1] == 'JPY->MONA->BTC':
                JpyMonaBtc_Profits.append(row[4])
            elif row[1] == 'JPY->BTC->BCH':
                JpyBtcBch_Profits.append(row[4])
            elif row[1] == 'JPY->BCH->BTC':
                JpyBchBtc_Profits.append(row[4])
            elif row[1] == 'JPY->BTC->XEM':
                JpyBtcXem_Profits.append(row[4])
            elif row[1] == 'JPY->XEM->BTC':
                JpyXemBtc_Profits.append(row[4])
            elif row[1] == 'JPY->BTC->ETH':
                JpyBtcEth_Profits.append(row[4])
            elif row[1] == 'JPY->ETH->BTC':
                JpyEthBtc_Profits.append(row[4])
            else:
                pass
        # Tradesテーブル中身：
        # [0]:num
        # [1]:route
        # [2]:trade
        # [3]:minutes
        # [4]:retrades
        cur.execute("select * from %s" % (self.tableName_Trades))
        data = cur.fetchall()
        for row in data:
            if row[2] == 'JPY->BTC' or row[2] == 'BTC->JPY':
                BTC_JPY_minutes.append(row[3])
                BTC_JPY_retrades.append(row[4])
            elif row[2] == 'BTC->MONA' or row[2] == 'MONA->BTC':
                MONA_BTC_minutes.append(row[3])
                MONA_BTC_retrades.append(row[4])
            elif row[2] == 'JPY->MONA' or row[2] == 'MONA->JPY':
                MONA_JPY_minutes.append(row[3])
                MONA_JPY_retrades.append(row[4])
            elif row[2] == 'BTC->BCH' or row[2] == 'BCH->BTC':
                BCH_BTC_minutes.append(row[3])
                BCH_BTC_retrades.append(row[4])
            elif row[2] == 'BCH->JPY' or row[3] == 'JPY->BCH':
                BCH_JPY_minutes.append(row[3])
                BCH_JPY_retrades.append(row[4])
            elif row[2] == 'BTC->XEM' or row[2] == 'XEM->BTC':
                XEM_BTC_minutes.append(row[3])
                XEM_BTC_retrades.append(row[4])
            elif row[2] == 'JPY->XEM' or row[2] == 'XEM->JPY':
                XEM_JPY_minutes.append(row[3])
                XEM_JPY_retrades.append(row[4])
            elif row[2] == 'BTC->ETH' or row[2] == 'ETH->BTC':
                ETH_BTC_minutes.append(row[3])
                ETH_BTC_retrades.append(row[4])
            elif row[2] == 'JPY->ETH' or row[2] == 'ETH->JPY':
                ETH_JPY_minutes.append(row[3])
                ETH_JPY_retrades.append(row[4])
            else:
                pass
        con.close()
        
        # 損益統計=============================================
        tmpList = [All_Profits,
                   JpyBtcMona_Profits,
                   JpyMonaBtc_Profits,
                   JpyBtcBch_Profits,
                   JpyBchBtc_Profits,
                   JpyBtcXem_Profits,
                   JpyXemBtc_Profits,
                   JpyBtcEth_Profits,
                   JpyEthBtc_Profits]
        for i in range(len(tmpList)):
            profitsList.append(self.calcStat(tmpList[i]))
        
        # 取引時間平均=============================================
        tmpList = [BTC_JPY_minutes,
                   MONA_BTC_minutes,
                   MONA_JPY_minutes,
                   BCH_BTC_minutes,
                   BCH_JPY_minutes,
                   XEM_BTC_minutes,
                   XEM_JPY_minutes,
                   ETH_BTC_minutes,
                   ETH_JPY_minutes]
        for i in range(len(tmpList)):
            if len(tmpList[i]) > 0:
                ave = int(sum(tmpList[i]) / len(tmpList[i]))
            else:
                ave = '###'
            minutesList.append(ave)
        
        # 再取引回数平均=============================================
        tmpList = [BTC_JPY_retrades,
                   MONA_BTC_retrades,
                   MONA_JPY_retrades,
                   BCH_BTC_retrades,
                   BCH_JPY_retrades,
                   XEM_BTC_retrades,
                   XEM_JPY_retrades,
                   ETH_BTC_retrades,
                   ETH_JPY_retrades]
        for i in range(len(tmpList)):
            if len(tmpList[i]) > 0:
                ave = round(sum(tmpList[i]) / len(tmpList[i]), 2)
            else:
                ave = '###'
            retradesList.append(ave)
        
        # resultList:
        # ┌             All Profits  JPY->BTC->MONA
        # ｜profitsList[ [0,1,2,3,4], [0,1,2,3,4], ...]
        # ｜
        # ｜            BTC/JPY   MONA/BTC  MONA/JPY
        # ｜minutesList[   0   ,    1    ,    2    , ...  ]
        # ｜retradesList[  0   ,    1    ,    2    , ...  ]
        # └
        resultList = [profitsList, minutesList, retradesList]
        return resultList
    
    # 損益リストから統計データを計算して結果リストを返す
    # [0]:取引回数
    # [1]:利益となった回数
    # [2]:利益となった割合
    # [3]:損益の平均
    # [4]:損益の標準偏差
    def calcStat(self, profitsList):
        Profit_N = 0
        Trade_N = len(profitsList)
        for i in range(len(profitsList)):
            if profitsList[i] > 0:
                Profit_N += 1
        if Trade_N > 0:
            Profit_Rate = int((Profit_N / Trade_N) * 100)
            Ave_Profits = int(sum(profitsList) / Trade_N)
        else:
            Profit_Rate = '###'
            Ave_Profits = '###'
        if Trade_N > 1:
            SD_Profits = round(statistics.stdev(profitsList), 1)
        else:
            SD_Profits = '###'
        resultList = [Trade_N, Profit_N, Profit_Rate, Ave_Profits, SD_Profits]
        return resultList
