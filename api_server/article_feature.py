from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
from pathlib import Path
import sys
import json
from opencc import OpenCC

# 初始化OpenCC转换器：繁体转简体
cc = OpenCC('t2s')

# 获取当前文件（main.py）的父目录（fastapi_service）
current_dir = Path(__file__).parent
# 获取项目根目录（your_project，即fastapi_service的同级目录）
project_root = current_dir.parent
# 将项目根目录添加到Python路径
sys.path.append(str(project_root))

from preprocess.article_analyzer import ArticleStyleExtractor

app = FastAPI(
    title="文章思维链提取服务",
    version="1.0"
)

class ArticleInput(BaseModel):
    text: str  # 待分析的文章文本
    extra: Optional[str] = None  


class StyleFeatureOutput(BaseModel):
    ret_code: int = 0  # 0代表成功
    msg: str = ""      # 错误信息
    style_summary: Optional[str] = None  # 风格概括
    style_category: Optional[str] = None  # 风格分类
    style_label: Optional[List[str]] = None    # 风格标签
    style: Optional[Dict[str, Any]] = None  # 多维度风格特征
    fact_info: Optional[str] = None  # 事实信息
    image: Optional[str] = None  # 图片链接
    CoT: Optional[str] = None  # 写作思维链
    template_title: Optional[str] = None  # 模版标题
    template_part: Optional[List[str]] = None  # 模版内容分部分描述
    template_label: Optional[List[str]] = None  # 模版标签
    prompt: Optional[str] = None  # 写作提示词


def traditional_to_simplified(data: Any) -> Any:
    """
    递归将任意类型数据中的繁体中文转换为简体中文，保持原数据类型不变
    
    Args:
        data: 任意类型的数据（字符串、字典、列表、元组等）
        
    Returns:
        转换后的同类型数据，其中的繁体中文已转为简体
    """
    # 处理字符串类型
    if isinstance(data, str):
        return cc.convert(data)
    
    # 处理字典类型
    if isinstance(data, dict):
        return {key: traditional_to_simplified(value) for key, value in data.items()}
    
    # 处理列表类型
    if isinstance(data, list):
        return [traditional_to_simplified(item) for item in data]
    
    # 处理元组类型
    if isinstance(data, tuple):
        return tuple(traditional_to_simplified(item) for item in data)
    
    # 其他类型直接返回，不做转换
    return data


# 初始化文风提取器（全局单例）
extractor = ArticleStyleExtractor()

@app.post("/extract-style", response_model=StyleFeatureOutput, description="接收文章文本，返回提取的文风特征")
async def extract_style(input_data: ArticleInput):
    try:
        if not input_data.text.strip():
            # 输入为空时返回错误码和信息
            return {
                "ret_code": 1,
                "msg": "输入文本不能为空",
                "style_summary": None,
                "style_category": None,
                "style_label": None,
                "style": None,
                "fact_info": None,
                "image": None,
                "CoT": None,
                "template_title": None,
                "template_part": None,
                "template_label": None,
                "prompt": None
            }
        
        # 先将输入文本转换为简体（如果需要）
        simplified_text = traditional_to_simplified(input_data.text)
        simplified_extra = traditional_to_simplified(input_data.extra) if input_data.extra else None
        
        # 调用现有模块的分析方法
        result = await extractor.analyze_article(simplified_text, simplified_extra, local_save=False)
        result = result["style_features"]
        
        if not result:
            # 分析失败时返回错误码和信息
            return {
                "ret_code": 1,
                "msg": "文风特征提取失败",
                "style_summary": None,
                "style_category": None,
                "style_label": None,
                "style": None,
                "fact_info": None,
                "image": None,
                "CoT": None,
                "template_title": None,
                "template_part": None,
                "template_label": None,
                "prompt": None
            }
        
        # 对结果进行繁简转换
        simplified_result = traditional_to_simplified(result)
        
        # 从转换后的结果中提取各个字段
        return {
            "ret_code": 0,
            "msg": "",
            "style_summary": simplified_result.get("style_summary", ""),
            "style_category": simplified_result.get("style_category", ""),
            "style_label": simplified_result.get("style_label", []),
            "style": simplified_result.get("style", {}),
            "fact_info": simplified_result.get("fact_info", ""),
            "image": simplified_result.get("image", ""),
            "CoT": simplified_result.get("CoT", ""),
            "template_title": simplified_result.get("template_title", ""),
            "template_part": simplified_result.get("template_part", []),
            "template_label": simplified_result.get("template_label", []),
            "prompt": simplified_result.get("prompt", "")
        }
    except Exception as e:
        # 其他错误返回错误码和具体信息
        return {
            "ret_code": 1,
            "msg": f"处理失败: {str(e)}",
            "style_summary": None,
            "style_category": None,
            "style_label": None,
            "style": None,
            "fact_info": None,
            "image": None,
            "CoT": None,
            "template_title": None,
            "template_part": None,
            "template_label": None,
            "prompt": None
        }

@app.get("/health", response_model=StyleFeatureOutput, description="服务健康检查")
async def health_check():
    return {
        "ret_code": 0,
        "msg": "success"
    }

if __name__ == "__main__":
    import uvicorn
    # 启动服务，默认监听本地8002端口
    uvicorn.run("article_feature:app", host="0.0.0.0", port=8002, reload=False)
    