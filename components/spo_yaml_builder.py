# -*- coding: utf-8 -*-
import yaml
import json
import random
from pathlib import Path
from loguru import logger
from typing import List, Dict

class SPOYamlBuilder:
    """从融合的JSON和MD文章构建SPO所需的YAML文件"""
    
    def __init__(self, 
                 merged_json_dir: str = "merged_articles",
                 md_articles_dir: str = "articles_md",
                 output_dir: str = "auto_generated"):
        """
        初始化YAML构建器
        :param merged_json_dir: 融合后的JSON文件目录
        :param md_articles_dir: MD文章目录
        :param output_dir: 输出YAML目录
        """
        self.base_dir = Path(__file__).parent.parent / "dataset"
        self.merged_json_dir = self.base_dir / merged_json_dir
        self.md_articles_dir = self.base_dir / md_articles_dir
        self.output_dir = self.base_dir.parent / "settings" / output_dir
        
        # 创建目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载资源
        self.merged_jsons = self._load_merged_jsons()
        self.md_articles = self._load_md_articles()
        
        if not self.merged_jsons:
            logger.warning(f"未找到融合的JSON文件：{self.merged_json_dir}")
        if not self.md_articles:
            logger.warning(f"未找到MD文章：{self.md_articles_dir}")
    
    def _load_merged_jsons(self) -> List[Dict]:
        """加载所有融合的JSON文件"""
        if not self.merged_json_dir.exists():
            return []
            
        json_files = [p for p in self.merged_json_dir.iterdir() if p.suffix == ".json"]
        results = []
        for file in json_files:
            with open(file, "r", encoding="utf-8") as f:
                try:
                    results.append(json.load(f))
                except Exception as e:
                    logger.warning(f"加载JSON文件失败 {file}：{str(e)}")
        return results
    
    def _load_md_articles(self) -> List[str]:
        """加载所有MD文章内容"""
        if not self.md_articles_dir.exists():
            return []
            
        md_files = [p for p in self.md_articles_dir.iterdir() if p.suffix == ".md"]
        results = []
        for file in md_files:
            with open(file, "r", encoding="utf-8") as f:
                try:
                    results.append(f.read())
                except Exception as e:
                    logger.warning(f"加载MD文件失败 {file}：{str(e)}")
        return results
    
    def build_yaml(self, 
                  num_qa_pairs: int = 3, 
                  output_name: str = None) -> Path:
        """
        构建SPO所需的YAML文件
        :param num_qa_pairs: 生成的QA对数量
        :param output_name: 输出文件名
        :return: 输出路径
        """
        if not self.merged_jsons or not self.md_articles:
            raise ValueError("缺少必要的资源文件（融合JSON或MD文章）")
        
        # 随机选择一个融合的prompt
        merged_data = random.choice(self.merged_jsons)
        prompt = merged_data.get("prompt", "")
        
        # 生成QA对
        qa_pairs = []
        selected_articles = random.sample(
            self.md_articles, 
            min(num_qa_pairs, len(self.md_articles))
        )
        
        for article in selected_articles:
            # 随机选择一个风格作为question
            style_candidate = random.choice(self.merged_jsons)
            question = style_candidate.get("style", {})
            qa_pairs.append({
                "question": question,
                "answer": article
            })
        
        # 构建YAML内容
        yaml_content = {
            "prompt": prompt,
            "requirements": """
            1. 事实提取：100%覆盖目标文本的核心实体、事件、数据，无遗漏或错误；
            2. 文风匹配：生成内容的语气、句式、叙述逻辑与原文完全一致，无违和感；
            3. 输出约束：仅输出结果，不添加额外分析或解释。
            """,
            "count": None,
            "qa": qa_pairs
        }
        
        # 保存YAML
        if not output_name:
            output_name = f"auto_spo_{random.randint(1, 9999)}"
        output_path = self.output_dir / f"{output_name}.yaml"
        
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(
                yaml_content, 
                f, 
                allow_unicode=True, 
                sort_keys=False, 
                default_flow_style=False, 
                indent=2
            )
        
        logger.info(f"自动生成的SPO YAML已保存到：{output_path}")
        return output_path

# 使用示例
if __name__ == "__main__":
    builder = SPOYamlBuilder()
    builder.build_yaml(num_qa_pairs=3)