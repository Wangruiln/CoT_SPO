# -*- coding: utf-8 -*-
from typing import Dict, List,Optional
from loguru import logger
from utils.llm_client import SPO_LLM, RequestType, extract_content
from .utils import ArticleReader
import re
import json
from pathlib import Path
import random

class ArticleStyleExtractor:
    # 修改 __init__ 方法，增加输出目录配置
    def __init__(self, llm_model: str = "gpt-4.1", temperature: float = 0.2, 
                single_output_dir: str = "single_articles", 
                merged_output_dir: str = "merged_articles"):
        if not SPO_LLM._instance:
            SPO_LLM.initialize(
                optimize_kwargs={"model": llm_model, "temperature": temperature},
                evaluate_kwargs={"model": llm_model, "temperature": temperature},
                execute_kwargs={"model": llm_model, "temperature": temperature},
                mode="base_model"
            )
        self.llm = SPO_LLM.get_instance()
        self.reader = ArticleReader()
        
        # 创建输出目录
        self.single_output_dir = Path(__file__).parent.parent / "dataset" / single_output_dir
        self.merged_output_dir = Path(__file__).parent.parent / "dataset" / merged_output_dir
        self.single_output_dir.mkdir(parents=True, exist_ok=True)
        self.merged_output_dir.mkdir(parents=True, exist_ok=True)

    # 修改单篇分析方法，按原文件名保存
    async def analyze_article(self, input_source: str, extra: Optional[str] = None, local_save: bool = True) -> Dict[str, any]: 
        """
        核心入口：分析文章，输出文风特征、事实信息、QA对
        :param input_source: 纯文本或文章文件路径
        :param save_as_md: 是否将文章保存为markdown格式
        :return: 结构化分析结果
        """
        # 1. 读取并清洗文章
        logger.info(f"开始读取文章：{input_source}")
        article_text = self.reader.read_article(input_source)
        logger.info(f"文章读取完成，总长度：{len(article_text)}字")
        # 2. 提取文风特征（语气、句式、修辞、结构）
        style_features = await self._extract_style_features(article_text,extra)
        logger.info(f"文风特征提取完成")
        if local_save:
            # 生成唯一的 output_name，确保不会覆盖已有文件
            dataset_dir = Path(__file__).parent.parent / "dataset"
            # 新增：创建单篇文章的JSON输出目录（按需求1的拆分逻辑）
            single_output_dir = dataset_dir / "single_articles"
            single_output_dir.mkdir(parents=True, exist_ok=True)

            input_path = Path(input_source)
            if input_path.exists() and input_path.is_file():
                output_name = input_path.stem  # 用原文件名（无后缀）
            else:
                output_name = f"article_style_{random.randint(1, 9999)}"
            output_path = single_output_dir / f"{output_name}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(style_features, f, ensure_ascii=False, indent=2)
            logger.info(f"单篇文风分析结果已保存到：{output_path}")

        return {
            "article_text": article_text,
            "style_features": style_features,
        }

    # 新增从文件夹读取json进行融合的方法
    async def merge_from_json_folder(self, json_folder: str = None) -> Dict[str, any]:
        """从指定文件夹读取json文件进行风格融合"""
        json_folder = json_folder or str(self.single_output_dir)
        json_path = Path(json_folder)
        
        if not json_path.exists() or not json_path.is_dir():
            raise ValueError(f"文件夹不存在：{json_folder}")
        
        # 读取所有json文件
        json_files = [p for p in json_path.iterdir() if p.suffix == ".json" and p.is_file()]
        if not json_files:
            raise ValueError(f"文件夹 {json_folder} 中未找到json文件")
        
        logger.info(f"开始从 {len(json_files)} 个json文件整合风格特征")
        single_results = []
        for file in json_files:
            with open(file, "r", encoding="utf-8") as f:
                style = json.load(f)
                style_features = {
                    "style_summary": style.get("style_summary"),
                    "style_label": style.get("style_label"),
                    "style": style.get("style"),
                    "prompt": style.get("prompt")
                }
                single_results.append(style_features)
        
        # 整合特征
        integrated_features = await self._integrate_features(single_results)
        
        # 保存融合结果
        output_name = f"merged_style_{random.randint(1, 9999)}"
        output_path = self.merged_output_dir / f"{output_name}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(integrated_features, f, ensure_ascii=False, indent=2)
        logger.info(f"融合风格特征已保存到：{output_path}")
        
        return {
            "style_features": integrated_features,
            "output_path": str(output_path)
        }

    async def _integrate_features(self, single_results: List[Dict]) -> Dict[str, any]:
        """整合多篇文章的风格特征，生成更全面的prompt"""
        
        if len(single_results)==1:
            return single_results[0]

        logger.info(f"开始整合 {len(single_results)} 篇文章的风格特征")

        # 构建整合提示词
        integrate_prompt = """
        # 任务要求：整合多篇同类型文章的风格特征
        你需要基于以下输入的多篇文章的风格特征，提炼共性特征并生成通用prompt

        # 你具备的能力
        1. 聚焦所有文章的共同风格，综合各个模版的特点，整合成一个更全面的文风模版框架；
        2. 每个分析维度（语言、结构、叙事等）需总结共性规律；
        3. 生成的prompt需比单篇更全面，能指导AI模仿该类型文章的整体风格和语言特征。
        
        ## 输出格式（与单篇分析一致的JSON结构）
        ```json
        {
            "style_summary": "一句话概括这个模版的风格如何",
            "style_label": "整合后的文风标签",
            "style": {
                "language": {...},  // 整合后的语言特征
                "structure": {...},  // 整合后的结构特征
                "narrative": {...},
                "emotion": {...},
                "thinking": {...},
                "uniqueness": {...},  // 共同的个性标记
            },
            "prompt": "整合后的通用模仿prompt"
        }
        ```
        """
        response = await self.llm.responser(
            request_type=RequestType.EXECUTE,
            messages=[{"role": "system", "content": integrate_prompt},{"role":"user","content":f"根据如下文章风格模版和prompt完成整合任务。{single_results}"}],
        )
        pattern = r'```json\s*([\s\S]*?)```'
        match = re.search(pattern, response)
        if match:
            response = match.group(1).strip()
        if not response:
            raise RuntimeError("多篇特征整合失败，LLM未返回有效结果")
        integrated_features = json.loads(response)
        return integrated_features

    async def _extract_style_features(self, article_text: str, extra: Optional[str] = None) -> Dict[str, str]:
        """提取文风特征（调用LLM生成结构化结果）"""
        prompt = """
        ## 任务背景
        在这个任务中，你需要对给定的文本进行逆向提示词工程，提取出文本的主要写作元素，然后生成一个可以用于模仿这种写作风格的提示词。

        ## 你的身份和任务
        你是一位专业的文本分析师，我将给你一篇文章，你需要对其进行逆向提示词工程。你需要根据‘你具备的能力’、‘分析维度’、‘内容要求’、‘输出注意事项’和‘输出案例’输出最终内容。

        ## 你具备的能力
        1. 你能够理解和分析不同的写作风格，包括语气、词汇、句式等。
        2. 你能够从文本中提取关键的写作元素。
        3. 你能够根据提取的写作元素生成有效的提示词。
        4. 你能够对文本进行逆向工程，以理解其背后的写作技巧。
        5. 你具备良好的判断力，能够确定哪些元素对模仿特定的写作风格最为关键。

        ## 分析维度
        你将从以下维度分析文本风格特征：
        1. 语言特征（句式、用词、修辞）
        2. 结构特征（段落、过渡、层次、图文）
        3. 叙事特征（视角、距离、时序）
        4. 情感特征（浓淡、方式、基调）
        5. 思维特征（逻辑、深度、节奏）
        6. 个性标记（独特表达、意象系统）
        7. 事实信息（实体、事件、数据）

        ## 内容要求
        1. 根据分析维度提取文本的主要写作风格和事实信息。
        2. 生成能够模仿这种写作风格的提示词，每个维度越清晰的描述越好。
        3. 提示词应该能够用于任何主题的写作,因此要避免和事实信息的融合。
        4. 提示词应该是具体和明确的，可以通过规定一步一步的写作流程，用于清楚地指导AI模型的写作。
        5. 提取写作模版，模版是指文章的写作逻辑，避免加入特殊实体信息，需要通用、高度总结。
        6. 文风分析应该避免一些事实实体词的出现，更加关注于风格提取
        7. 事实信息应该尽可能具体，避免模糊和概括性的描述, 明确图文结构信息
        8. 为
        ## 输出注意事项（一条条思考）
        1. 注意prompt是通用的写作提示词，风格模版是对文章风格的总结和提炼，尽量避免事实信息的掺杂。
        2. 在生成提示词时，要确保它们具有足够的明确性和具体性。
        3. 提示词应该能够适应任何主题，而不仅仅是原文的主题。
        4. 提示词应该能够引导AI模型生成与给定文本风格类似的文章，而不是完全复制原文。
        5. 在提取写作元素和生成提示词时，要保持专业和严谨的态度。
        6. 提示词应该以如下的样式进行构造和输出：
            prompt模板：
                # 你是一个xx专家。
                你的任务是
                # 通用能力
                ## xx能力
                1.
                2.
                ## xx能力
                1.
                2.
                # 写作思维链
                # 注意事项
                # 输出格式
                (模版可以进行扩展和补充)
        7. 文风分析结果每个维度都应该详细分析
        8. style_label只能从"轻松互动、实用严谨、正式官方、幽默亲和"中选择
        9. template_label只能从"分步骤型、总览 + 细节、结构化整合、问答结合、图文结合、列表分点、表格记录"中选择
        10. 所有结果都必须输出中文简体
        
        ## 输出格式
        以下列结构化格式以代码块输出分析结果：
        ```json
        {   
            "style_summary": "一句话概括这是一篇什么类型的文章，什么风格的写作方式，分类只能从以下类别中选择一个最贴近的：充值攻略、角色介绍、游戏攻略、同人创作、版更介绍、活动介绍、内容营销",
            "style_category": "只能从以下类别中选择一个最贴近的分类：充值攻略、角色介绍、游戏攻略、同人创作、版更介绍、活动介绍、内容营销",
            "style_label": ["风格标签1", "..."],
            "style": {
                "language": {
                "sentence_pattern": ["主要句式特征", "次要句式特征"],
                "word_choice": {
                    "formality_level": "正式度 1-5",
                    "preferred_words": ["高频特征词1", "特征词2"],
                    "avoided_words": ["规避词类1", "规避词类2"]
                },
                "rhetoric": ["主要修辞手法1", "修辞手法2"]
                },
                "structure": {
                    "paragraph_length": "段落平均字数",
                    "transition_style": "过渡特征",
                    "hierarchy_pattern": "层次展开方式",
                    "use_of_graphics": "图文结合方式"
                },
                "narrative": {
                    "perspective": "叙事视角",
                    "time_sequence": "时间处理方式",
                    "narrator_attitude": "叙事态度"
                },
                "emotion": {
                    "intensity": "情感强度 1-5",
                    "expression_style": "表达方式",
                    "tone": "情感基调"
                },
                "thinking": {
                    "logic_pattern": "思维推进方式",
                    "depth": "思维深度 1-5",
                    "rhythm": "思维节奏特征"
                },
                "uniqueness": {
                    "signature_phrases": ["标志性表达1", "表达2"],
                },
            },
            "CoT": "模仿写作风格的思维链，需要和prompt中的写作思维链一致",
            "template_title": "抽象模版标题",
            "template_part":[            
                "第一部分介绍什么内容，与事实信息无关，脱离具体场景，高度结合模版标题，只需输出具体内容，不用输出第几部分",
                "...",
                "..."
            ],
            "template_label": ["模版标签1", "..."],
            "fact_info": "分点提取的文章中的所有事实信息，对于表格数据，请完整提取出来，不允许做出省略，也不需要任何解释说明,输出字符串",
            "image":" 具体的图片链接，只能输出markdown格式![title](url)， 直接提取标题和链接，输出字符串",
            "prompt": "模仿写作风格的详细提示词"
        }
        ```"""
        if extra:
            usr_prompt = f"文章内容为：{article_text}\n，这篇文章需要关注的额外信息是：{extra}"
        else:
            usr_prompt = article_text
        response = await self.llm.responser(
            request_type=RequestType.EXECUTE,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": usr_prompt}],
        )
        pattern = r'```json\s*([\s\S]*?)```'
        match = re.search(pattern, response)
        if match:
            response = match.group(1).strip()
        if not response:
            raise RuntimeError("文风特征提取失败，LLM未返回有效结果")

        style_features = json.loads(response)

        return style_features
