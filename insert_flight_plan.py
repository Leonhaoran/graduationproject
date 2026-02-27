import datetime
import json
import os
import sqlalchemy as sa


# =========================
# 数据库工具
# =========================
def get_engine():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "db.sqlite3")
    return sa.create_engine(f"sqlite:///{db_path}")


# =========================
# 从数据库加载映射
# =========================
def load_drone_name_to_id():
    engine = get_engine()
    mapping = {}
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT id, name FROM uav_drones"))
        for row in result:
            mapping[row.name] = row.id
    return mapping


def load_node_name_to_gps():
    engine = get_engine()
    mapping = {}
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT name, gps FROM air_road_nodes"))
        for row in result:
            mapping[row.name] = row.gps
    return mapping


def load_airport_gps_to_id():
    engine = get_engine()
    mapping = {}
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT id, gps FROM air_road_airports"))
        for row in result:
            mapping[row.gps] = row.id
    return mapping


# =========================
# 读取轨迹 JSON
# =========================
INPUT_JSON = r"C:\Users\Leon\Desktop\adsb_graph_mapped_trajectories.json"

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    trajectories = json.load(f)

if not isinstance(trajectories, list):
    raise ValueError("❌ 轨迹 JSON 不是 list 结构")


# =========================
# 加载数据库映射
# =========================
drone_name_to_id = load_drone_name_to_id()
node_name_to_gps = load_node_name_to_gps()
airport_gps_to_id = load_airport_gps_to_id()

print(f"已加载 drones: {len(drone_name_to_id)}")
print(f"已加载 nodes: {len(node_name_to_gps)}")
print(f"已加载 airports: {len(airport_gps_to_id)}")


# =========================
# Flight plan 插入 SQL
# =========================
insert_sql = """
INSERT INTO flight_plan_flightrequirements
(
    name,
    start_time,
    end_time,
    drone_id,
    start_airport_id,
    proposal_id,
    end_airport_id
)
VALUES
(
    :name,
    :start_time,
    :end_time,
    :drone_id,
    :start_airport_id,
    1,
    :end_airport_id
)
"""


# =========================
# 插入 flight plans
# =========================
engine = get_engine()
count = 0

with engine.begin() as conn:
    for item in trajectories:
        aircraft_id = item.get("aircraft_id")
        node_traj = item.get("node_trajectory")

        if not aircraft_id or not node_traj or len(node_traj) < 2:
            print("⚠️ 轨迹不完整，已跳过")
            continue

        # ---------- drone_id ----------
        if aircraft_id not in drone_name_to_id:
            print(f"⚠️ 找不到 drone: {aircraft_id}")
            continue

        drone_id = drone_name_to_id[aircraft_id]

        # ---------- 起点 / 终点 node ----------
        start_node_name = node_traj[0]
        end_node_name = node_traj[-1]

        if start_node_name not in node_name_to_gps or end_node_name not in node_name_to_gps:
            print(f"⚠️ 找不到 node: {start_node_name} 或 {end_node_name}")
            continue

        start_gps = node_name_to_gps[start_node_name]
        end_gps = node_name_to_gps[end_node_name]

        if start_gps not in airport_gps_to_id or end_gps not in airport_gps_to_id:
            print(f"⚠️ 找不到 airport(gps): {start_gps} 或 {end_gps}")
            continue

        params = {
            "name": aircraft_id,
            "start_time": '13:05:16.668661',
            "end_time": '13:05:16.668661',
            "drone_id": drone_id,
            "start_airport_id": airport_gps_to_id[start_gps],
            "end_airport_id": airport_gps_to_id[end_gps]
        }

        conn.execute(sa.text(insert_sql), params)
        count += 1


print(f"✈️ 已成功插入 flight plan 数量: {count}")
