from datetime import datetime

import pandas as pd

from Agent.db_connector import fetch_from_database


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
             The input should be a string representing the drone name.''')
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
            print()
            print(drone_name)
            print(50 * '*')
            return f'No UAV record'

        record = data.iloc[0].to_dict()
        info_lines = [f'{key}: {value}' for key, value in record.items()]
        info_str = '\n'.join(info_lines)

        msg = info_str
        return msg
