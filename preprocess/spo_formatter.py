# -*- coding: utf-8 -*-
import yaml
from pathlib import Path
from typing import Dict
from loguru import logger
import json

class SPOYamlFormatter:
    """将文章分析结果封装为SPO标准YAML模板"""
    @staticmethod
    def format(analysis_result: Dict, output_name: str = "extracted_article") -> str:
        """
        生成SPO YAML内容
        :param analysis_result: 文章分析结果（来自ArticleStyleExtractor.analyze_article）
        :param output_name: 输出YAML文件名（无需后缀）
        :return: YAML字符串
        """
        style = analysis_result['style_features']

        output_path = Path(__file__).parent.parent / "settings" / f"{output_name}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(style, f, ensure_ascii=False, indent=2)

        if "prompt" in style:
            style = {k: v for k, v in style.items() if k != "prompt"}
        initial_prompt = analysis_result['style_features'].get("prompt", "")

        # 2. 生成requirements（SPO优化目标）
        requirements = f"""
        1. 事实提取：100%覆盖目标文本的核心实体、事件、数据，无遗漏或错误；
        2. 文风匹配：生成内容的语气、句式、叙述逻辑与原文完全一致，无违和感；
        3. 输出约束：仅输出结果（提取的事实或生成的文本），不添加额外分析或解释。
        """
        # 3. 组织SPO YAML结构
        #style = json.dumps(style, ensure_ascii=False, indent=2)
        #breakpoint()
        spo_yaml = {
            "prompt": initial_prompt,
            "requirements": requirements,
            "count": None,  # 可根据文章长度调整，如 len(analysis_result["article_text"]) // 2
            "qa": [
                {
                    "question": style,
                    "answer": ""
                }
            ]
            
        }
        return yaml.dump(spo_yaml, allow_unicode=True, sort_keys=False, default_flow_style=False, indent=2)

    @staticmethod
    def save_to_settings(yaml_content: str, output_name: str = "extracted_article") -> Path:
        """
        保存YAML到SPO的settings目录
        :param yaml_content: SPO YAML字符串
        :param output_name: 输出文件名（无需后缀）
        :return: 保存路径
        """
        output_path = Path(__file__).parent.parent / "settings" / f"{output_name}.yaml"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        logger.info(f"SPO模板已保存到：{output_path}")
        return output_path