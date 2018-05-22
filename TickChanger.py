# -*- coding: utf-8 -*-
# 入力値を任意の刻み幅に変換
def Tick_int(num:int, tick):
    mod = num % 10  # 入力値の最小桁
    times = int(mod / tick)  # 最小桁はtick何個分か？
    result = tick * times  # 最小桁 = tick刻みでの最大値
    change = num - num % 10 + result  # 最小桁をtick刻みに変換
    return change
