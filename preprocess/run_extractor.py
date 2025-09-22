# -*- coding: utf-8 -*-
import argparse
import asyncio
from pathlib import Path
from loguru import logger
from .article_analyzer import ArticleStyleExtractor
from .spo_formatter import SPOYamlFormatter


async def main():
    args = parse_args()
    input_source = args.input
    input_path = Path(input_source)
    
    # 初始化提取器
    extractor = ArticleStyleExtractor(
        llm_model=args.llm_model, 
        temperature=args.temp
    )
    
    # 判断输入类型并处理
    if input_path.is_dir() and args.mode == "single":
        # 批量处理单篇文章
        supported_ext = (".txt", ".md", ".docx")
        file_list = [p for p in input_path.iterdir() if p.suffix in supported_ext and p.is_file()]
        if not file_list:
            logger.error(f"文件夹 {input_source} 中未找到支持的文件")
            return
            
        for file in file_list:
            await extractor.analyze_article(str(file))

    elif args.mode == "merge":
        # 从json文件夹融合
        await extractor.merge_from_json_folder(args.input)
        
    else:
        # 处理单个文件或文本
        await extractor.analyze_article(input_source)

    logger.info("\n处理完成！")

# 修改参数解析
def parse_args():
    parser = argparse.ArgumentParser(description="文章文风提取模块")
    parser.add_argument("--input", required=True, help="输入：文本/文件路径/文件夹路径")
    parser.add_argument("--mode", default="single", choices=["single", "merge"], 
                      help="模式：single(处理单篇/批量单篇)，merge(融合json文件)")
    parser.add_argument("--llm-model", default="gpt-4.1", help="用于分析的LLM模型")
    parser.add_argument("--temp", type=float, default=0.3, help="LLM温度")
    return parser.parse_args()

if __name__ == "__main__":
    asyncio.run(main())