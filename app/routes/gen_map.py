import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.prompts import PromptTemplate
import json
import asyncio
from fastapi import WebSocket

load_dotenv()

async def generate_journey_map(websocket: WebSocket):
    try:
        await websocket.accept()
        
        # 定义输出解析器
        output_parser = SimpleJsonOutputParser()
        
        # 创建提示模板
        template = """请生成一个汽车用户体验地图模型的单个阶段数据，直接返回JSON格式，不要包含任何其他说明文字。

        阶段：{stage_name}

        场景描述：
        - 角色：{role}
        - 目标：{goal}
        - 环境：{environment}
        - 情况：{situation}
        - 要求：{requirements}

        请按照以下格式生成数据：
        {{
        "stage_name": "{stage_name}",
        "user_behavior": "用户行为描述",
        "touchpoints": ["接触点1", "接触点2"],
        "emotion": "用户情绪",
        "needs": ["需求1", "需求2"],
        "opportunities": ["机会点1", "机会点2"],
        "suggestions": ["改进建议1", "改进建议2"]
        }}

        注意事项：
        1. user_behavior需详细描述该阶段的具体行为
        2. touchpoints列出该阶段涉及的所有接触点（如手机APP、车内设施等）
        3. emotion描述用户情绪状态（如"开心"、"焦虑"、"平静"等）
        4. needs列出用户在该阶段的核心需求
        5. opportunities描述可能的改进机会
        6. suggestions提供具体的改进建议

        请确保数据真实合理，符合用户实际使用场景。请严格按照以上格式生成数据，不要添加任何额外的说明文字。
        """
        
        # 使用PromptTemplate创建模板
        prompt = PromptTemplate(
            template=template,
            input_variables=["stage_name", "role", "environment","goal", "situation", "requirements"]
        )

        # 初始化LLM
        llm = OpenAI(
            model="Qwen/Qwen2.5-32B-Instruct",
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.8
        )

        # 定义场景参数
        scenario_params = {
            "role": "年轻妈妈",
            "goal": "日常驾车通勤",
            "environment": "城市道路、学校、公司",
            "situation": "工作日早晚高峰",
            "requirements": "紧密联系用车行为、注意妈妈需要到幼儿园接送孩子"
        }
        # 定义阶段列表
        stages = [
            "上车前准备",
            "开车前准备",
            "上车",
            "行车途中",
            "到达幼儿园",
            "驾车上班",
            "下班",
            "接孩子回家",
            "到家后"
        ]

        json_data = []
        for stage in stages:
            try:
                # 合并场景参数和阶段名称
                prompt_params = {**scenario_params, "stage_name": stage}
                formatted_prompt = prompt.format(**prompt_params)
                result = llm.invoke(formatted_prompt)

                parsed_result = output_parser.parse(result)
                if isinstance(parsed_result, dict):
                    json_data.append(parsed_result)
                    # 发送当前阶段的数据到客户端
                    await websocket.send_json({
                        "type": "stage_complete",
                        "data": parsed_result,
                        "current_stage": stage,
                        "total_stages": len(stages)
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"跳过格式不正确的数据: {stage}"
                    })
                    
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"处理{stage}数据时出错: {str(e)}"
                })
                
            await asyncio.sleep(0.5)

        # 发送所有数据生成完成的消息
        await websocket.send_json({
            "type": "all_stages_complete",
            "data": json_data
        })
        
    except Exception as e:
        # 处理WebSocket连接异常
        if websocket.client_state.CONNECTED:
            await websocket.send_json({
                "type": "error",
                "message": f"发生错误: {str(e)}"
            })
    finally:
        # 关闭WebSocket连接
        await websocket.close()
