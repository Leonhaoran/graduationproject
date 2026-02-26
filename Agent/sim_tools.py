import subprocess
import sys
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
             description='''
             This tool is used to run simulator.
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


class DisplayModeledTrajectory:
    def __init__(self) -> None:
        pass

    @prompts(name='(sim_tools)DisplayModeledTrajectory',
             description='''
             This tool provides a lightweight visualization of the locations of airports, nodes, and air routes.
             This tool is developed by matplotlib.pyplot rather than RflysimUT.
             It displays modeled airports, nodes, and air routes instead of raw trajectories.
             If the user does not specify whether to display raw or modeled trajectory, show the modeled trajectory by default.
             In this tool, you do not need any parameter.
             ''')
    def inference(self, target: str) -> str:
        # 外部脚本的绝对路径
        script_path = r"C:\Users\Leon\Desktop\pythonProject1\ads-b\show_airports_and_waypoints_and_edges.py"

        try:

            subprocess.Popen(
                [sys.executable, script_path],
            )
            return "DISPLAY_PROCESS_LAUNCHED"

        except Exception as e:
            return f"FAILED_TO_START_DISPLAY: {str(e)}"

class DisplayRawTrajectory:
    def __init__(self) -> None:
        pass

    @prompts(name='(sim_tools)DisplayRawTrajectory',
             description='''
             This tool provides a lightweight visualization of the locations of airports, nodes, and air routes.
             This tool is developed by matplotlib.pyplot rather than RflysimUT.
             It displays raw trajectories instead of modeled airports, nodes, and air routes.
             If the user does not specify whether to display raw or modeled trajectory, show the modeled trajectory by default.
             In this tool, you do not need any parameter.
             ''')
    def inference(self, target: str) -> str:
        # 外部脚本的绝对路径
        script_path = r"C:\Users\Leon\Desktop\pythonProject1\ads-b\show_path.py"

        try:
            subprocess.Popen(
                [sys.executable, script_path],
                # 如果你的脚本里有相对路径，可以加上 cwd 指定工作目录
                # cwd=r"C:\Users\Leon\Desktop\pythonProject1\ads-b"
            )
            return "DISPLAY_PROCESS_LAUNCHED"

        except Exception as e:
            return f"FAILED_TO_START_DISPLAY: {str(e)}"

