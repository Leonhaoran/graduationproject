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
# 读取 graph
# =========================
GRAPH_JSON = r"C:\Users\Leon\Desktop\adsb_graph_with_node_type.json"

with open(GRAPH_JSON, "r", encoding="utf-8") as f:
    graph = json.load(f)

nodes = graph["nodes"]


# =========================
# Node 插入 SQL
# =========================
insert_sql = """
INSERT INTO air_road_nodes
(
    name,
    gps,
    radius,
    layer_id,
    proposal_id,
    permission_id
)
VALUES
(
    :name,
    :gps,
    1,
    1,
    1,
    1
)
"""


# =========================
# 插入 node
# =========================
count = 0

for node_id, node in nodes.items():
    lat = node["lat"]
    lon = node["lon"]

    x, y = latlon_to_view_int(lat, lon)

    params = {
        "name": node_id,        # ⭐ 原始 node 名称（N_0 / N_1 / …）
        "gps": f"({x},{y})"     # ⭐ 展示坐标
    }

    insert_into_database(insert_sql, params)
    count += 1


print(f"✅ 已插入 air_road_nodes 数量: {count}")
