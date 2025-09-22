from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path
import sys
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
    style_label: Optional[list[str]] = None    # 风格标签
    style: Optional[Dict[str, Any]] = None  # 多维度风格特征
    fact_info: Optional[str] = None  # 事实信息
    image: Optional[str] = None  # 图片链接
    CoT: Optional[str] = None  # 写作思维链
    prompt: Optional[str] = None  # 写作提示词


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
                "style_label": None,
                "style": None,
                "fact_info": None,
                "image": None,
                "CoT": None,
                "prompt": None
            }
        extra = input_data.extra if input_data.extra else None
        # 调用现有模块的分析方法
        result = await extractor.analyze_article(input_data.text, extra, local_save=False)
        result = result["style_features"]
        if not result:
            # 分析失败时返回错误码和信息
            return {
                "ret_code": 1,
                "msg": "文风特征提取失败",
                "style_summary": None,
                "style_label": None,
                "style": None,
                "fact_info": None,
                "image": None,
                "CoT": None,
                "prompt": None
            }
        style_summary = result.get("style_summary", "")
        style_label = result.get("style_label", "") 
        style = result.get("style", {})
        fact_info = result.get("fact_info", "")
        image = result.get("image", "")
        CoT = result.get("CoT", "")
        prompt = result.get("prompt", "")
        # 成功时返回ret_code=0和数据
        return {
            "ret_code": 0,
            "msg": "",
            "style_summary": style_summary,
            "style_label": style_label,
            "style": style,
            "fact_info": fact_info,
            "image": image,
            "CoT": CoT,
            "prompt": prompt
        }
    except Exception as e:
        # 其他错误返回500错误码和具体信息
        return {
            "ret_code": 1,
            "msg": f"处理失败: {str(e)}",
            "style_summary": None,
            "style_label": None,
            "style": None,
            "fact_info": None,
            "image": None,
            "CoT": None,
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