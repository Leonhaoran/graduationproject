import os
import re
import yaml
from rich import print
# from langchain import OpenAI
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI

from LLMAgent.ConversationBot import ConversationBot

# from LLMAgent.dataTools import (
#     roadVolumeTrend,
#     roadVolume,
#     roadNameToID,
#     plotGeoHeatmap,
#     getCurrentTime,
#     roadVisulization,
#     odVolume,
#     odMap
# )

from Agent.data_tools import (
    GetCurrentTime,
    UAVNameToInfo
)

from Agent.sim_tools import (
    RunRflysimUT
)

import gradio as gr
import openai.api_requestor

openai.api_requestor.TIMEOUT_SECS = 30

OPENAI_CONFIG = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
if OPENAI_CONFIG['OPENAI_API_TYPE'] == 'azure':
    os.environ["OPENAI_API_TYPE"] = OPENAI_CONFIG['OPENAI_API_TYPE']
    os.environ["OPENAI_API_VERSION"] = OPENAI_CONFIG['AZURE_API_VERSION']
    os.environ["OPENAI_API_BASE"] = OPENAI_CONFIG['AZURE_API_BASE']
    os.environ["OPENAI_API_KEY"] = OPENAI_CONFIG['AZURE_API_KEY']
    llm = AzureChatOpenAI(
        deployment_name=OPENAI_CONFIG['AZURE_MODEL'],
        temperature=0,
        max_tokens=1024,
        request_timeout=60
    )
elif OPENAI_CONFIG['OPENAI_API_TYPE'] == 'openai':
    os.environ["OPENAI_API_KEY"] = OPENAI_CONFIG['OPENAI_KEY']
    llm = ChatOpenAI(
        temperature=0,
        model_name='gpt-3.5-turbo-16k-0613',  # or any other model with 8k+ context
        max_tokens=1024,
        request_timeout=60
    )
elif OPENAI_CONFIG['OPENAI_API_TYPE'] == 'deepseek':
    os.environ["OPENAI_API_KEY"] = OPENAI_CONFIG['DEEPSEEK_API_KEY']
    os.environ["OPENAI_API_BASE"] = OPENAI_CONFIG['DEEPSEEK_API_BASE']
    # 出于与 OpenAI 兼容考虑，将base_url设置为https://api.deepseek.com/v1来使用，但注意，此处v1与模型版本无关
    llm = ChatOpenAI(
        temperature=0,
        model_name=OPENAI_CONFIG['DEEPSEEK_MODEL'],
        max_tokens=1024,
        request_timeout=60
    )

if not os.path.exists('./fig/'):
    os.mkdir('./fig/')

# toolModels = [
#     roadVolumeTrend('./fig/'),
#     roadVolume(),
#     roadNameToID(),
#     plotGeoHeatmap('./fig/'),
#     GetCurrentTime(),
#     roadVisulization('./fig/'),
#     odVolume(),
#     odMap('./fig/')
# ]

toolModels = [
    GetCurrentTime(),
    UAVNameToInfo(),
    RunRflysimUT(),
]

botPrefix = """
[WHO ARE YOU]
# 1. You are a AI to assist human with traffic big-data analysis and visulization. #
# 2. You have access to the road network and traffic flow data in Xuancheng City, Anhui Province, China.
# 3. Whenever you are about to come up with a thought, recall the human message to check if you already have enough information for the final answer. If so, you shouldn't infer or fabricate any more needs or questions based on your own ideas.
# 4. You are forbidden to fabricate any tool names. If you can not find any appropriate tool for your task, try to do it using your own ability and knowledge as a chat AI.
# 5. Remember what tools you have used, DONOT use the same tool repeatedly. Try to use the least amount of tools.
# 6. DONOT fabricate any input parameters when calling tools! Check if you have the correct format of input parameters before calling tools!
# 7. When you encounter tabular content in Observation, make sure you output the tabular content in markdown format into your final answer.
# 8. Your tasks will be highly time sensitive. When generating your final answer, you need to state the time of the data you are using.
# 9. It's ok if the human message is not a traffic data related task, don't take any action and just respond to it like an ordinary conversation using your own ability and knowledge as a chat AI.
# 10. When you realize that you need to clarify what the human wants, end your actions and ask the human for more information as your final answer.
全程用英语回答，不要用汉语回答。



# 1. Thought: 思考用户的问题，决定是否需要调用工具。
# 2. Action: 工具名称（必须从可选工具列表中选择）。
# 3. Action Input: 工具的输入参数。
# 4. Observation: 工具返回的结果。
# ... （如有必要，重复上述步骤）
# 5. Final Answer: [最终结论] 当你从工具中获得足够信息后，必须且只能通过 Final Answer 给出中文回复。

# - 严禁在 Thought 阶段直接回答用户，必须通过 Final Answer 结束对话。
# - 如果工具返回明确的信息。此时你的步骤应该是：
#   Thought: ……。
#   Final Answer: ……。

"""

# 决定是否输出调试信息
bot = ConversationBot(llm, toolModels, botPrefix, verbose=True)
# bot = ConversationBot(llm, toolModels, botPrefix)


def reset(chat_history: list, thoughts: str):
    chat_history = []
    thoughts = ""
    bot.agent_memory.clear()
    bot.ch.memory = [[]]
    return chat_history, thoughts


def respond(msg: str, chat_history: list, thoughts: str):
    res, cb = bot.dialogue(msg)
    # 文件
    # regex = re.compile(r'`([^`]+)`')
    # try:
    #     filenames = regex.findall(res)
    # except AttributeError:
    #     filenames = None
    # if filenames:
    #     chat_history += [(msg, None)]
    #     for fn in filenames:
    #         chat_history += [(None, (fn,))]
    #     chat_history += [(None, res)]
    # else:
    #     chat_history += [(msg, res)]

    chat_history += [(msg, res)]

    thoughts += f"\n>>> {msg}\n"
    for actionMemory in bot.ch.memory[-2]:
        thoughts += actionMemory
        thoughts += '\n'
    thoughts += f"<<< {res}\n"
    return "", chat_history, thoughts


with gr.Blocks(
        title="Traffic Data Process Bot", theme=gr.themes.Base(text_size=gr.themes.sizes.text_md)
) as demo:
    with gr.Row(visible=True, variant="panel"):
        with gr.Column(visible=True, variant='default'):
            chatbot = gr.Chatbot(scale=2, height=650)

            with gr.Row():
                humanMsg = gr.Textbox(scale=2)
                submitBtn = gr.Button("Submit", scale=1)
            clearBtn = gr.ClearButton()
            gr.Examples(
                label='You may want to ask the following questions:',
                examples=[
                    "现在是什么时间？",
                    "drone_1对应的id是多少",
                    "drone_1的weight",
                    "跑仿真",
                    "Show me the OD map from 7am to 9am today.",
                    "Show me the current network heatmap.",
                    "Show me the traffic volume of OD pairs from 5pm to 7pm yesterday.",
                    "Show me the traffic volume data overview of yesterday in a table.",
                    "青弋江西大道在哪？",
                    "How's the traffic volume trend of road 1131 yesterday?"
                ],
                inputs=[humanMsg],
                # outputs=[humanMsg, chatbot],
                # fn=testFunc
            )
        ReActMsg = gr.Text(
            label="Thoughts and Actions of the Chatbot",
            interactive=False,
            lines=50
        )

    humanMsg.submit(
        respond,
        [humanMsg, chatbot, ReActMsg],
        [humanMsg, chatbot, ReActMsg]
    )
    submitBtn.click(
        respond,
        [humanMsg, chatbot, ReActMsg],
        [humanMsg, chatbot, ReActMsg]
    )
    clearBtn.click(reset, [chatbot, ReActMsg], [chatbot, ReActMsg])

if __name__ == "__main__":
    demo.launch()
