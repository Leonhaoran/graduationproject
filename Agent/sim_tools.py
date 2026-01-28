import subprocess
import time
import webbrowser


def prompts(name, description):
    def decorator(func):
        func.name = name
        func.description = description
        return func

    return decorator


class RunRflysimUT:
    def __init__(self) -> None:
        pass

    @prompts(name='(sim_tools)Run Simulator',
             description='''This tool is used to run simulator.
             In this tool, you do not need any parameter.
             ''')
    def inference(self, input: str) -> str:
        subprocess.Popen(
            r"C:\Users\Leon\Desktop\RflyUT-Sim Python开发环境配置\PythonCode\RflyUT-main\Redis-x64-3.0.504\redis-server.exe")
        subprocess.Popen(
            [
                r"C:/Users/Leon/anaconda3/envs/RflysimUT_Django/python.exe",
                "manage.py",
                "runserver",
            ],
            cwd=r"C:/Users/Leon/Desktop/RflyUT-Sim Python开发环境配置/PythonCode/RflyUT-main/RflysimUT_Django"
        )

        subprocess.Popen(
            [r"C:\Users\Leon\Desktop\RflyUT-Sim Python开发环境配置\UE压缩包\WindowsNoEditor\Blocks.exe"]
        )

        time.sleep(1.5)

        webbrowser.open("http://127.0.0.1:8000/map_sim")

        return "SIMULATOR_AND_WEB_STARTED"
