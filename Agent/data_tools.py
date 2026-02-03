import json
from datetime import datetime

import pandas as pd

from Agent.db_connector import fetch_from_database, insert_into_database, get_table_columns


def prompts(name, description):
    def decorator(func):
        func.name = name
        func.description = description
        return func

    return decorator


class GetCurrentTime:
    def __init__(self) -> None:
        pass

    @prompts(name='(data_tools)Get Current Time',
             description='''
    Get current time
    ''')
    def inference(self, time: str) -> str:
        current_time = datetime.now()

        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_time


class UAVNameToInfo:
    def __init__(self) -> None:
        pass

    @prompts(name='(data_tools)UAV name to Info',
             description='''
             This tool is used to get the specific drone information according to drone name.
             Use this tool before others if the target drone info given by human user is the name rather than id.
             The input should be a string representing the drone name.
             Do not fabricate any field or value.
             如果查找的字段为空或者NULL，则直接返回空或者NULL
             ''')
    def inference(self, target: str) -> str:
        drone_name = target

        query = f'''
        SELECT *
        FROM uav_drones
        WHERE name = '{drone_name.strip().strip('#"')}'
        '''

        rows = fetch_from_database(query)
        data = pd.DataFrame(rows)

        if data.empty:
            return f'No UAV record'

        record = data.iloc[0].to_dict()
        info_lines = [f'{key}: {value}' for key, value in record.items()]
        info_str = '\n'.join(info_lines)

        msg = info_str
        return msg


class InsertUAV:
    def __init__(self) -> None:
        pass

    @prompts(
        name="(data_tools)insert UAV",
        description="""
            Insert a new UAV into the database.

            Input should be a JSON string.
            Required fields:
            - name
            - max_speed
            - safe_radius
            - proposal_id

            Other fields are optional.
            Do not fabricate values.
            """
    )
    def inference(self, payload: str) -> str:

        REQUIRED_FIELDS = {
            "name",
            "max_speed",
            "safe_radius",
            "proposal_id"
        }

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return "Invalid JSON input"

        # 校验必填字段
        missing = REQUIRED_FIELDS - data.keys()
        if missing:
            return f"Missing required fields: {sorted(missing)}"

        # 过滤非法字段
        table_columns = get_table_columns("uav_drones")
        valid_data = {k: v for k, v in data.items() if k in table_columns}

        if not valid_data:
            return "No valid fields to insert"

        # 动态生成 SQL
        columns = ", ".join(valid_data.keys())
        values = ", ".join(f":{k}" for k in valid_data.keys())

        sql = f"""
            INSERT INTO uav_drones ({columns})
            VALUES ({values})
            """

        insert_into_database(sql, valid_data)

        return f"UAV '{valid_data['name']}' inserted successfully"


class AllUAVDronesInfo:
    def __init__(self) -> None:
        pass

    @prompts(name='(data_tools)all UAV drones info',
             description='''
                 This tool is used to get all the drones' information from database.
                 Use this tool before others if the user wants all the drones' information and doesn't provide any specific drone id.
                 There is no input.
                 Do not fabricate any field or value.
                 If no drone exists, directly return none or NULL.
                 ''')
    def inference(self, target: str) -> str:
        query = f'''
            SELECT *
            FROM uav_drones
            '''

        rows = fetch_from_database(query)
        data = pd.DataFrame(rows)

        if data.empty:
            return f'No UAV record'

        all_records = []

        for idx, row in data.iterrows():
            info_lines = [f'{key}: {row[key]}' for key in data.columns]
            record_str = '\n'.join(info_lines)
            all_records.append(record_str)

        return ''.join(all_records)


class AllAirRoadAirportsInfo:
    def __init__(self) -> None:
        pass

    @prompts(name='(data_tools)all air road airports info',
             description='''
                 This tool is used to get all the air road airport information from database.
                 Use this tool before others if the user wants all the air road airport information and doesn't provide any specific air road airport id.
                 There is no input.
                 Do not fabricate any field or value.
                 If no air road airport exists, directly return none or NULL.
                 ''')
    def inference(self, target: str) -> str:
        query = f'''
            SELECT *
            FROM air_road_airports
            '''

        rows = fetch_from_database(query)
        data = pd.DataFrame(rows)

        if data.empty:
            return f'No Air Road Airport record'

        all_records = []

        for idx, row in data.iterrows():
            info_lines = [f'{key}: {row[key]}' for key in data.columns]
            record_str = '\n'.join(info_lines)
            all_records.append(record_str)

        return ''.join(all_records)
