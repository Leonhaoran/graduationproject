from datetime import datetime


def prompts(name, description):
    def decorator(func):
        func.name = name
        func.description = description
        return func

    return decorator


class GetCurrentTime:
    def __init__(self) -> None:
        pass

    @prompts(name='Get Current Time',
             description='''
    Get current time
    ''')
    def inference(self, time: str) -> str:
        current_time = datetime.now()

        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_time
