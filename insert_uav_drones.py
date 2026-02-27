import json
import os
import sqlalchemy as sa


# =========================
# 数据库工具
# =========================
def get_engine():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "db.sqlite3")
    db_uri = f"sqlite:///{db_path}"
    return sa.create_engine(db_uri)


def insert_into_database(sql: str, params: dict):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(sa.text(sql), params)


# =========================
# 递归提取 aircraft_id
# =========================
def extract_aircraft_ids(obj, result_set):
    """
    在任意嵌套 JSON 结构中递归查找 aircraft_id
    """
    if isinstance(obj, dict):
        if "aircraft_id" in obj:
            result_set.add(obj["aircraft_id"])
        for v in obj.values():
            extract_aircraft_ids(v, result_set)

    elif isinstance(obj, list):
        for item in obj:
            extract_aircraft_ids(item, result_set)


# =========================
# 读取 JSON（你已有的文件）
# =========================
INPUT_JSON = r"C:\Users\Leon\Desktop\adsb_graph_mapped_trajectories.json"

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)


# =========================
# 提取 aircraft_id（不再猜结构）
# =========================
aircraft_ids = set()
extract_aircraft_ids(data, aircraft_ids)

if not aircraft_ids:
    raise ValueError("❌ JSON 中完全未发现 aircraft_id")

print(f"✅ 提取到 aircraft 数量: {len(aircraft_ids)}")


# =========================
# UAV 插入 SQL
# =========================
insert_sql = """
INSERT INTO uav_drones
(name, max_speed, safe_radius, proposal_id)
VALUES
(:name, :max_speed, 10, 1)
"""


# =========================
# 插入 uav_drones
# =========================
count = 0

for aid in sorted(aircraft_ids):
    params = {
        "name": aid,
        "max_speed": 10
    }
    insert_into_database(insert_sql, params)
    count += 1

print(f"🚁 已成功插入 uav_drones 数量: {count}")
