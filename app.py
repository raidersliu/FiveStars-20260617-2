import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math
import io
from datetime import datetime

# ==========================================
# 核心計算邏輯
# ==========================================
def split_and_sum(date_str):
    """計算生日數字總和，若為2開頭則加18"""
    digits = [int(ch) for ch in date_str if ch.isdigit()]
    total = sum(digits)
    if date_str[0] == '2':
        total += 18
    return digits, total

def reduce_to_single_digit(n):
    """將數字簡化至 1-10 之間"""
    while n > 10:
        n = sum(int(d) for d in str(n))
    return n

def get_next_type(current):
    """
    關鍵規則：當類型為 10 時，下一個轉換是 2 (跳過 1)
    循環順序為：2, 3, 4, 5, 6, 7, 8, 9, 10
    """
    if current == 10:
        return 2
    return current + 1

def get_type_chain(start_type, steps):
    """計算星型類型變化序列"""
    chain = []
    curr = start_type
    for _ in range(steps):
        curr = get_next_type(curr)
        chain.append(curr)
    return chain

def count_10_components(date_str):
    """計算生日中年份、月份、日期為 10 的倍數之次數"""
    year = int(date_str[2:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    return sum(1 for val in [year, month, day] if val % 10 == 0)

def sum_mmdd_digits(date_str):
    """計算人格數字 (MMDD)"""
    mmdd = date_str[4:8]
    digits = [int(d) for d in mmdd]
    summ = sum(digits)
    while summ > 10:
        summ = sum(int(d) for d in str(summ))
    return summ

def analyze_date_code(date_str):
    """統計生日碼中各個數字出現次數 (1-10)"""
    yy = date_str[2:4]
    mm = date_str[4:6]
    dd = date_str[6:8]
    combined_digits = yy + mm + dd
    digit_count = {str(i): 0 for i in range(1, 11)}
    for ch in combined_digits:
        if ch in digit_count:
            digit_count[ch] += 1
    # 統計 10 的數量
    digit_count["10"] = sum(1 for x in [yy, mm, dd] if int(x) % 10 == 0)
    return digit_count

def modify_code(date_str, digit_count):
    """修正 1 的計數（若有 10 出現，需扣除誤算的 1）"""
    yy = int(date_str[2:4])
    mm = int(date_str[4:6])
    dd = int(date_str[6:8])
    aaa = sum(1 for v in [yy, mm, dd] if v == 10)
    digit_count["1"] = str(int(digit_count["1"]) - aaa)
    return digit_count

def calculate_star_type(birthday_str):
    """統整所有分析數據"""
    digits, total_sum = split_and_sum(birthday_str)
    simplified = reduce_to_single_digit(total_sum)
    ten_count = count_10_components(birthday_str)
    personality = sum_mmdd_digits(birthday_str)
    result = {
        "生日": birthday_str,
        "原始加總": total_sum,
        "轉換次數": ten_count,
        "類型 Type": simplified,
        "人格 Personality": personality,
        "星型類型變化": get_type_chain(simplified, ten_count),
        "成熟年齡": total_sum,
        "轉變年齡": [total_sum + 10 * i for i in range(1, ten_count + 1)]
    }
    return result, simplified, ten_count

# ==========================================
# 繪圖邏輯 (3D 星星 + 靠內可愛文字)
# ==========================================
def draw_star_with_repeated_numbers(result, typen, digit_count, ten_count):
    # 動態寬度：根據星星數量增加畫布寬度
    width = 8
