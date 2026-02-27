import json
import os
import sqlalchemy as sa


# =========================
# 经纬度 → 展示坐标映射（整数版）
# =========================
def latlon_to_view_int(lat, lon):
    LAT_MIN, LAT_MAX = 25, 55
    LON_MIN, LON_MAX = -130, -60

    X_MIN, X_MAX = -900, 400
    Y_MIN, Y_MAX = -200, 1100

    x_norm = (lon - LON_MIN) / (LON_MAX - LON_MIN)
    y_norm = (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)

    x = X_MIN + x_norm * (X_MAX - X_MIN)
    y = Y_MIN + y_norm * (Y_MAX - Y_MIN)

    return int(round(x)), int(round(y))


# =========================
# 数据库工具
# =========================
def get_engine():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "db.sqlite3")
    return sa.create_engine(f"sqlite:///{db_path}")


def insert_into_database(sql: str, params: dict):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(sa.text(sql), params)


# =========================
# 从 air_road_nodes 加载 gps → id 映射
# =========================
def load_gps_to_node_id():
    engine = get_engine()
    mapping = {}

    with engine.connect() as conn:
        result = conn.execute(
            sa.text("SELECT id, gps FROM air_road_nodes")
        )
        for row in result:
            mapping[row.gps] = row.id

    return mapping


# =========================
# 读取 graph
# =========================
GRAPH_JSON = r"C:\Users\Leon\Desktop\adsb_graph_with_node_type.json"

with open(GRAPH_JSON, "r", encoding="utf-8") as f:
    graph = json.load(f)

nodes = graph["nodes"]


# =========================
# 加载 node gps → db_id 映射
# =========================
gps_to_node_id = load_gps_to_node_id()
print(f"✅ 已加载 air_road_nodes 数量: {len(gps_to_node_id)}")


# =========================
# Airport 插入 SQL
# =========================
insert_sql = """
INSERT INTO air_road_airports
(
    name,
    gps,
    radius,
    capacity,
    proposal_id,
    entrance_node_id,
    exit_node_id,
    permission_id
)
VALUES
(
    :name,
    :gps,
    10,
    10,
    1,
    :entrance_node_id,
    :exit_node_id,
    1
)
"""


# =========================
# 插入 airport（绑定到 node）
# =========================
count = 0

for node_id, node in nodes.items():
    if node.get("type") != "airport":
        continue

    lat = node["lat"]
    lon = node["lon"]

    # 展示坐标
    x, y = latlon_to_view_int(lat, lon)
    gps = f"({x},{y})"

    # 必须能在 air_road_nodes 中找到对应点
    if gps not in gps_to_node_id:
        print(f"⚠️ 未找到匹配的 node gps={gps}，跳过 airport {node_id}")
        continue

    node_db_id = gps_to_node_id[gps]

    params = {
        "name": f"Airport_{node_id} (lat={lat:.4f}, lon={lon:.4f})",
        "gps": gps,
        "entrance_node_id": node_db_id,
        "exit_node_id": node_db_id
    }

    insert_into_database(insert_sql, params)
    count += 1


print(f"✅ 已插入 airport 节点数量: {count}")
