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
# 从数据库加载 node 映射
# node_name (N_0) -> db_id
# =========================
def load_node_name_to_id():
    engine = get_engine()
    mapping = {}

    with engine.connect() as conn:
        result = conn.execute(
            sa.text("SELECT id, name FROM air_road_nodes")
        )
        for row in result:
            mapping[row.name] = row.id

    return mapping


# =========================
# 读取 graph
# =========================
GRAPH_JSON = r"C:\Users\Leon\Desktop\adsb_graph_with_node_type.json"

with open(GRAPH_JSON, "r", encoding="utf-8") as f:
    graph = json.load(f)

nodes = graph["nodes"]
edges = graph["edges"]

# =========================
# 加载 node → DB id 映射
# =========================
node_name_to_db_id = load_node_name_to_id()
print(f"✅ 已加载数据库 node 数量: {len(node_name_to_db_id)}")

# =========================
# Edge 插入 SQL
# =========================
insert_sql = """
INSERT INTO air_road_edges
(
    name,
    nodes,
    length,
    height,
    width,
    gps,
    volume,
    junction,
    rule,
    proposal_id,
    end_node_id,
    start_node_id,
    permission_id
)
VALUES
(
    :name,
    :nodes,
    1,
    1,
    1,
    :gps,
    1,
    0,
    0,
    1,
    :end_node_id,
    :start_node_id,
    1
)
"""

# =========================
# 插入有向 edge（双向）
# =========================
count = 0

for e in edges:
    a = e["from"]  # 原始 node_id，例如 N_0
    b = e["to"]

    # 必须能在数据库中找到 node
    if a not in node_name_to_db_id or b not in node_name_to_db_id:
        print(f"⚠️ node 不在数据库中：{a} 或 {b}")
        continue

    id_a = node_name_to_db_id[a]
    id_b = node_name_to_db_id[b]

    # 经纬度
    lat_a, lon_a = nodes[a]["lat"], nodes[a]["lon"]
    lat_b, lon_b = nodes[b]["lat"], nodes[b]["lon"]

    # 整数展示坐标
    xa, ya = latlon_to_view_int(lat_a, lon_a)
    xb, yb = latlon_to_view_int(lat_b, lon_b)

    # edge 中使用的 3D node 表达（⚠️ 不来自数据库）
    node3d_a = f"({xa},{ya},-120)"
    node3d_b = f"({xb},{yb},-120)"



    # ---------- 正向 ----------
    forward = {
        "name": f"{node3d_a}to{node3d_b}",
        "nodes": f"{node3d_a};{node3d_b}",
        "gps": f"({xa},{ya})to({xb},{yb})",
        "start_node_id": id_a,
        "end_node_id": id_b
    }

    # ---------- 反向 ----------
    backward = {
        "name": f"{node3d_b}to{node3d_a}",
        "nodes": f"{node3d_b};{node3d_a}",
        "gps": f"({xb},{yb})to({xa},{ya})",
        "start_node_id": id_b,
        "end_node_id": id_a
    }

    if f"{node3d_a}to{node3d_b}" == "(-346,446,-120)to(-325,461,-120)":
        print(forward)
        print(a, b)

    if f"{node3d_b}to{node3d_a}" == "(-346,446,-120)to(-325,461,-120)":
        print(backward)
        print(a, b)

    insert_into_database(insert_sql, forward)
    insert_into_database(insert_sql, backward)
    count += 2

print(f"✅ 已插入有向 edge 数量: {count}")
