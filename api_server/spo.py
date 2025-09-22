from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
from pathlib import Path
import sys
import os
import shutil
from loguru import logger

# 路径配置：添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# 导入项目内部模块
from components.optimizer import PromptOptimizer
from utils.llm_client import SPO_LLM, RequestType
from utils import load

# 全局请求上下文（替代yaml文件）
request_context = {
    "prompt": "",
    "requirements": "",
    "qa": [],
    "count": None
}

# -------------------------- 工具函数 --------------------------
def delete_temp_folder(folder_path: str) -> bool:
    """删除临时文件夹（支持非空文件夹）"""
    if not os.path.exists(folder_path):
        logger.warning(f"临时文件夹不存在：{folder_path}")
        return True 
    
    try:
        shutil.rmtree(folder_path)
        logger.info(f"临时文件夹已成功删除：{folder_path}")
        return True
    except Exception as e:
        logger.error(f"删除临时文件夹失败：{folder_path}，错误信息：{str(e)}")
        return False

def override_load_meta_data():
    """重写load模块函数，从内存上下文读取数据（替代yaml）"""
    return (
        request_context["prompt"],
        request_context["requirements"],
        request_context["qa"],
        request_context["count"]
    )

# 替换原load模块的加载逻辑
load.load_meta_data = override_load_meta_data

# -------------------------- 请求/响应模型 --------------------------
class OptimizationRequest(BaseModel):
    prompt: str          # 客户端提供的初始提示词（必填）
    article_text: str    # 参考文章（作为QA的answer，必填）
    style: str  # 文章风格要求（可选，允许空字典）
    fact_info: str       # 文章需包含的事实信息（必填）
    image: str           # 图片相关信息（可选，允许空字符串）

class OptimizationResponse(BaseModel):
    ret_code: int        # 0=成功，1=系统错误，2=参数不完整
    best_prompt: str     # 优化后的最佳提示词（参数不完整时返回空）
    msg: str             # 结果描述


# -------------------------- 核心业务逻辑 --------------------------
app = FastAPI(title="SPO Prompt Optimization Service")
TEMP_DIR = "workspace/api"  # 临时文件夹路径


def validate_request_params(request: OptimizationRequest) -> tuple[bool, str]:
    """
    校验客户端传入参数的完整性（业务层面必填项校验）
    :param request: 客户端请求对象
    :return: (校验结果, 错误信息) → 校验通过返回(True, "")，失败返回(False, 错误详情)
    """
    required_fields = [
        ("prompt", "初始提示词", request.prompt),
        ("article_text", "参考文章", request.article_text),
        ("fact_info", "需包含的事实信息", request.fact_info)
    ]

    # 2. 逐个校验必填字段
    for field_name, field_cn, field_value in required_fields:
        # 检查是否为空字符串或仅包含空格
        if not isinstance(field_value, str) or len(field_value.strip()) == 0:
            error_msg = f"必填字段缺失或无效：{field_cn}（{field_name}）不能为空，且需包含有效内容"
            return False, error_msg

    # 4. 所有校验通过
    return True, ""


def build_qa_pair(request: OptimizationRequest) -> List[dict]:
    """构建QA对（question=风格+事实+图片，answer=参考文章）"""
    question_parts = []
    # 基础问题前缀
    question = "请根据以下要求撰写文章："
    # 拼接风格要求（可选，有内容才添加）
    if len(request.style) > 0:
        question_parts.append(f"风格要求: {request.style}")
    # 拼接事实信息（必填，已校验过非空）
    question_parts.append(f"必须包含的事实: {request.fact_info.strip()}")
    # 拼接图片信息（可选，有内容才添加）
    if len(request.image.strip()) > 0:
        question_parts.append(f"图片库信息: {request.image.strip()}")
    
    # 组合完整question
    if question_parts:
        question += "; ".join(question_parts)
    # 返回QA对列表（单个QA，符合SPO优化器格式要求）
    return [{"question": question, "answer": request.article_text.strip()}]


@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_prompt(request: OptimizationRequest):
    # -------------------------- 新增：第一步先做参数完整性校验 --------------------------
    is_valid, validate_msg = validate_request_params(request)
    if not is_valid:
        logger.warning(f"参数不完整：{validate_msg}")
        # 参数不完整时，直接返回空的best_prompt和明确错误
        return OptimizationResponse(
            ret_code=1,  
            best_prompt="",  # 参数无效，无优化结果
            msg=f"优化失败：{validate_msg}"
        )

    # 参数校验通过，进入正常优化流程
    try:
        # 1. 构建优化上下文（基于校验后的有效参数）
        global request_context
        request_context = {
            "prompt": request.prompt.strip(),  # 去除首尾空格，避免无效字符
            "requirements": "1. 结合事实：100%覆盖输入的事实信息的核心实体、事件、数据，无遗漏或错误；2.文风匹配：生成内容的语气、句式、叙述逻辑与文风模版一致，无违和感；3、只能使用图片库中有的图片信息; 4. 输出约束：仅输出结果，不添加额外分析或解释。",
            "qa": build_qa_pair(request),
            "count": None
        }

        # 2. 初始化LLM（使用gpt-4.1，参数可根据需求调整）
        SPO_LLM.initialize(
            optimize_kwargs={"model": "gpt-4.1", "temperature": 0.7},  # 优化提示词：适度随机性
            evaluate_kwargs={"model": "gpt-4.1", "temperature": 0.3}, # 评估结果：低随机性，更客观
            execute_kwargs={"model": "gpt-4.1", "temperature": 0},    # 执行生成：零随机性，稳定输出
            mode="base_model"
        )

        # 3. 创建优化器实例（指定临时目录）
        optimizer = PromptOptimizer(
            optimized_path=TEMP_DIR,
            initial_round=1,
            max_rounds=3,  # 3轮迭代：平衡优化效果与耗时
            template="",   # 不使用yaml模板，依赖内存上下文
            name="api_request"
        )

        # 4. 异步执行提示词优化（避免阻塞FastAPI事件循环）
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, optimizer.optimize)

        # 5. 获取优化后的最佳提示词
        best_round = optimizer.data_utils.get_best_round()
        best_prompt = best_round.get("prompt", "").strip()  # 去除首尾空格，保证整洁

        # 6. 清理临时文件
        delete_temp_folder(TEMP_DIR)

        # 7. 返回成功结果
        return OptimizationResponse(
            ret_code=0,
            best_prompt=best_prompt,
            msg="提示词优化成功，临时文件已清理"
        )

    # -------------------------- 异常处理 --------------------------
    except Exception as e:
        # 系统错误时：清理临时文件 + 返回错误信息
        error_detail = str(e)
        logger.error(f"优化流程系统错误：{error_detail}")
        delete_temp_folder(TEMP_DIR)
        
        return OptimizationResponse(
            ret_code=1,  # ret_code=1：系统级错误（如LLM调用失败、文件操作异常）
            best_prompt="",  # 系统错误无有效结果
            msg=f"优化失败：系统内部错误 - {error_detail}"
        )


# -------------------------- 服务启动 --------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")