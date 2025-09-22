# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Union
import re
import markdown
from docx import Document
import random
from loguru import logger

class ArticleReader:
    """文章读取与文本清洗工具"""

    def read_article(self, input_source: Union[str, Path]) -> str:
        """读取文章内容，支持文本输入或文件输入（txt/md/docx）"""
        # 处理Path类型输入（直接视为文件路径）
        if isinstance(input_source, Path):
            return self._read_from_file(input_source)
        
        # 处理字符串类型输入：先判断是否为文件路径，不是则视为文本
        if isinstance(input_source, str):
            # 尝试判断是否为有效文件路径（捕获路径过长等异常）
            try:
                file_path = Path(input_source)
                # 只有当路径存在且是文件时，才视为文件输入
                if file_path.exists() and file_path.is_file():
                    return self._read_from_file(file_path)
            except (OSError, FileNotFoundError):
                # 捕获路径过长（OSError）或文件不存在的异常，视为文本输入
                pass
            
            # 若不是有效文件路径，则直接返回文本（处理长文本输入）
            return input_source.strip()
        
        # 不支持的输入类型
        raise TypeError(f"不支持的输入类型：{type(input_source)}，仅支持字符串或Path")


    def _read_from_file(self, file_path: Path) -> str:
        """从文件读取内容（内部辅助方法）"""
        if not file_path.exists():
            raise FileNotFoundError(f"文章文件不存在：{file_path}")
        
        # 按文件格式读取
        suffix = file_path.suffix.lower()
        if suffix == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        elif suffix == ".md":
            with open(file_path, "r", encoding="utf-8") as f:
                md_text = f.read().strip()
            return markdown.markdown(md_text)  # 转换为HTML文本
        elif suffix == ".docx":
            doc = Document(file_path)
            paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs)
        else:
            raise ValueError(f"不支持的文件格式：{suffix}，仅支持txt/md/docx")

    @staticmethod
    def _clean_text(text: str) -> str:
        """清洗文本：移除多余空格、空行、特殊符号"""
        text = re.sub(r"\n+", "\n", text)  # 合并多空行
        text = re.sub(r"\s+", " ", text)   # 合并多空格
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s.,;!?()（），。；！？：：“”‘’]", "", text)  # 保留常见符号
        return text.strip()