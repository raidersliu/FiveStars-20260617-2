
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
    width = 800 + (ten_count * 500) 
    height = 1000
    
    # 背景色 (深藍夜空)
    bg_color = "#131424"
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # 🎨 修改點 1：改成讀取你準備好的可愛字體檔案 (請確保檔名一致)
    font_file = "CuteFont.ttf"
    try:
        # 為了可愛字體更清晰，將字體大小稍微調大一點點
        font = ImageFont.truetype(font_file, 20)
        font_center = ImageFont.truetype(font_file, 55)
        font_data = ImageFont.truetype(font_file, 24)
    except:
        font = ImageFont.load_default()
        font_center = ImageFont.load_default()
        font_data = ImageFont.load_default()

    # 繪製左上角分析資訊 (改用質感亮金色，無陰影)
    zz = 0
    for k, v in result.items():
        draw.text((50, 50 + zz), f"{k}: {v}", fill='#D4AF37', font=font_data, anchor="lm")
        zz += 35

    # 準備數字計數資料 (索引 0=1, 9=10)
    numbers_with_counts = [(str(i), int(digit_count[str(i)])) for i in range(1, 11)]

    current_t = typen

    # 繪製星星階段
    for trans in range(ten_count + 1):
        if trans > 0:
            current_t = get_next_type(current_t)
            
        center = (400 + (trans * 500), height // 2)
        
        # 計算五角星頂點
        radius_outer = 200
        radius_inner = 80
        # 🎨 修改點 2：大幅縮小偏移量，讓數字靠近星星中心 (原本是 65，改為 35)
        label_offset = 35 
        layer_spacing = 15

        points = []
        for i in range(5):
            outer_angle = math.radians(90 + i * 72)
            inner_angle = math.radians(90 + i * 72 + 36)
            points.append((center[0] + radius_outer * math.cos(outer_angle),
                           center[1] - radius_outer * math.sin(outer_angle)))
            points.append((center[0] + radius_inner * math.cos(inner_angle),
                           center[1] - radius_inner * math.sin(inner_angle)))

        # 程式碼繪製 3D 星星底層陰影
        shadow_offset = 15
        shadow_points = [(x + shadow_offset, y + shadow_offset) for x, y in points]
        draw.polygon(shadow_points, fill='#080910')

        # 程式碼繪製 3D 光影切面星星 (10 個三角形)
        color_light = "#FFD700"  # 亮金色 (受光面)
        color_dark = "#B8860B"   # 暗金色 (背光面)
        
        for i in range(5):
            outer_idx = 2 * i
            inner_prev_idx = (2 * i - 1) % 10
            inner_next_idx = (2 * i + 1) % 10
            
            outer_pt = points[outer_idx]
            inner_prev_pt = points[inner_prev_idx]
            inner_next_pt = points[inner_next_idx]
            
            # 繪製受光面
            draw.polygon([center, inner_prev_pt, outer_pt], fill=color_light)
            # 繪製背光面
            draw.polygon([center, outer_pt, inner_next_pt], fill=color_dark)
            
        # 畫外圍輪廓線，讓切面的邊緣更銳利
        draw.line(points + [points[0]], fill="#FFF8DC", width=2)

        # 標記數字 (使用平面單色)
        for idx, (px, py) in enumerate(points):
            number, count = numbers_with_counts[idx]
            static_text = ",".join([number] * count) if count > 0 else " "
            
            shift_idx = (idx - 1 + current_t) % 10
            number1, count1 = numbers_with_counts[shift_idx]
            dy_text = f"({','.join([number1] * count1)})" if count1 > 0 else " "

            angle = math.atan2(py - center[1], px - center[0])
            base_x = px + label_offset * math.cos(angle) 
            base_y = py + label_offset * math.sin(angle)
            
            # 動態數字: 無陰影的珊瑚紅
            if dy_text.strip():
                draw.text((base_x, base_y - layer_spacing), dy_text, fill="#FF6B6B", font=font, anchor="mm")
            
            # 靜態數字: 無陰影的淺金色
            if static_text.strip():
                draw.text((base_x, base_y + layer_spacing), static_text, fill="#F9E596", font=font, anchor="mm")

        # 中心底座與文字
        circle_radius = 45
        circle_box = [center[0] - circle_radius, center[1] - circle_radius, 
                      center[0] + circle_radius, center[1] + circle_radius]
        draw.ellipse(circle_box, fill="#1A1C29", outline="#D4AF37", width=2)
        
        # 顯示中心 T 類型 (無陰影的經典金色)
        draw.text(center, f"T {current_t}", fill="#D4AF37", font=font_center, anchor="mm")

    # 輸出圖檔
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return img_buffer

# ==========================================
# Streamlit 網頁 UI
# ==========================================
st.set_page_config(page_title="身體自覺五星術分析", layout="wide")

st.title("🌟 身體自覺五星術分析系統")

col1, col2 = st.columns([1, 3])

with col1:
    birthday = st.text_input("輸入生日 (YYYYMMDD)", value="20250519", max_chars=8)
    run_btn = st.button("開始分析與繪圖", type="primary", use_container_width=True)

if run_btn:
    if len(birthday) == 8 and birthday.isdigit():
        try:
            valid_date = datetime.strptime(birthday, "%Y%m%d")
            
            with st.spinner('繪製專屬星圖中...'):
                res, start_t, num_trans = calculate_star_type(birthday)
                counts = analyze_date_code(birthday)
                counts = modify_code(birthday, counts)
                
                with col1:
                    st.subheader("📋 數據報告")
                    for key, val in res.items():
                        st.write(f"**{key}**: {val}")
                
                with col2:
                    st.subheader("🎨 星型變化圖軌跡")
                    final_img = draw_star_with_repeated_numbers(res, start_t, counts, num_trans)
                    
                    st.image(final_img, use_container_width=True)
                    
                    st.download_button(
                        label="📥 下載完整分析圖",
                        data=final_img,
                        file_name=f"5star_{birthday}.png",
                        mime="image/png",
                        use_container_width=True
                    )
        except ValueError:
            st.error("❌ 日期無效：請輸入真實存在的日期（例如：不能輸入 13 月或 32 日）")
    else:
        st.error("❌ 格式錯誤：請輸入 8 位數字的生日，例如 19851020")
