import sqlalchemy as sa
import yaml
import os


# def fetch_from_database(query):
#     # 读取配置文件
#     with open("dbconfig.yaml", "r", encoding="UTF-8") as f:
#         config = yaml.safe_load(f)
#
#     # 连接到PostgreSQL数据库
#     db_uri = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['db_name']}"
#     engine = sa.create_engine(db_uri)
#     conn = engine.connect()
#
#     # 执行查询
#     query_obj = sa.text(query)
#     result = conn.execute(query_obj)
#     conn.close()
#     return result

def fetch_from_database(query):
    db_path = os.path.join(os.getcwd(), 'db.sqlite3')
    db_uri = f'sqlite:///{db_path}'
    engine = sa.create_engine(db_uri)

    with engine.connect() as conn:
        query_obj = sa.text(query)
        result = conn.execute(query_obj)
        conn.close()
        return result


def insert_into_database(sql: str, params: dict):
    db_path = os.path.join(os.getcwd(), 'db.sqlite3')
    db_uri = f'sqlite:///{db_path}'
    engine = sa.create_engine(db_uri)

    with engine.begin() as conn:
        conn.execute(sa.text(sql), params)


def get_table_columns(table: str) -> set[str]:
    rows = fetch_from_database(f"PRAGMA table_info({table});")
    return {r[1] for r in rows}