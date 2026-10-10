"""
生成 PCB 钻孔工序模拟数据
字段覆盖：MES 批次信息、设备传感器、检测结果
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# -----------------------------
# 1. 基础设置
# -----------------------------
N = 2000  # 生产记录数
start_date = datetime(2025, 1, 1)

equipment_ids = ["DR-01", "DR-02", "DR-03", "DR-04", "DR-05"]
shifts = ["早班", "中班", "夜班"]
defect_types = ["无", "孔偏", "孔粗", "毛刺", "断钻"]

# -----------------------------
# 2. 生成基础字段
# -----------------------------
records = []
for i in range(N):
    batch_id = f"B{20250000 + i}"
    produce_time = start_date + timedelta(hours=i * 3)
    equipment = np.random.choice(equipment_ids)
    shift = np.random.choice(shifts)

    # 工艺参数（正常波动）
    spindle_speed = np.random.normal(80, 5)        # 主轴转速 k rpm
    feed_rate = np.random.normal(1.5, 0.2)         # 进给速度 m/min
    temperature = np.random.normal(25, 2)          # 温度 ℃
    pressure = np.random.normal(0.6, 0.05)         # 压力 MPa
    drill_life = np.random.randint(100, 1000)      # 钻头寿命 孔数

    # 模拟异常：设备偏移 + 温度漂移
    if equipment == "DR-03":
        spindle_speed += np.random.normal(5, 2)    # DR-03 转速偏高
    if equipment == "DR-05":
        temperature += np.random.normal(4, 1)      # DR-05 温度偏高
    if i > 1500:
        temperature += np.random.normal(2, 1)      # 后期温度漂移

    # -----------------------------
    # 3. 生成良率（受参数影响）
    # -----------------------------
    base_yield = 98.0
    yield_rate = (
        base_yield
        - 0.15 * abs(spindle_speed - 80)
        - 2.0 * abs(feed_rate - 1.5)
        - 0.2 * abs(temperature - 25)
        - 0.5 * abs(pressure - 0.6)
        - 0.001 * drill_life
        + np.random.normal(0, 0.5)
    )
    yield_rate = np.clip(yield_rate, 70, 100)

    # 是否不良
    is_defect = 1 if yield_rate < 95 else 0

    # 缺陷类型
    if is_defect:
        defect_type = np.random.choice(defect_types[1:], p=[0.4, 0.25, 0.2, 0.15])
    else:
        defect_type = "无"

    records.append({
        "batch_id": batch_id,
        "produce_time": produce_time,
        "equipment_id": equipment,
        "shift": shift,
        "spindle_speed": round(spindle_speed, 2),
        "feed_rate": round(feed_rate, 3),
        "temperature": round(temperature, 2),
        "pressure": round(pressure, 3),
        "drill_life": drill_life,
        "yield_rate": round(yield_rate, 2),
        "is_defect": is_defect,
        "defect_type": defect_type,
    })

df = pd.DataFrame(records)

# -----------------------------
# 4. 故意制造脏数据（模拟真实制造数据）
# -----------------------------
# 缺失值
missing_idx = np.random.choice(df.index, size=30, replace=False)
df.loc[missing_idx, "temperature"] = np.nan

missing_idx2 = np.random.choice(df.index, size=20, replace=False)
df.loc[missing_idx2, "pressure"] = np.nan

# 重复值
duplicate_rows = df.sample(10, random_state=1)
df = pd.concat([df, duplicate_rows], ignore_index=True)

# 异常值
outlier_idx = np.random.choice(df.index, size=5, replace=False)
df.loc[outlier_idx, "spindle_speed"] = 999

# -----------------------------
# 5. 保存
# -----------------------------
df.to_csv("data/raw/pcb_drill_raw.csv", index=False, encoding="utf-8-sig")

print("数据生成完成！")
print(f"总记录数：{len(df)}")
print(f"字段：{list(df.columns)}")
print(df.head())