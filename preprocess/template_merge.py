import os
import re
import json
import random
from datetime import datetime
from openai import AzureOpenAI

# --------------------------
# 配置（替换为你的实际信息）
# --------------------------
# Azure OpenAI 配置（必须正确填写）
AZURE_API_KEY = ""
AZURE_ENDPOINT = "https://midas-openai2.openai.azure.com/"
AZURE_DEPLOYMENT = "gpt-4.1"  # 你的 Azure 部署名称
AZURE_API_VERSION = "2024-12-01-preview"

# 文件路径配置
INPUT_TXT_PATH = "/data/home/rylanwang/content_module/test_output_ugc/comment2.txt"  # 输入的TXT文件路径
OUTPUT_DIR_PATH = "test_output_ugc/"  # 输出 JSON 文件的目录
SELECTED_LINES_COUNT = 2000  # 随机选取的行数


# --------------------------
# 步骤1：读取本地TXT文件并随机选取行
# --------------------------
def read_and_select_lines(txt_path, num_lines):
    """读取本地TXT文件内容，随机选取指定数量的行，返回列表"""
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"TXT文件不存在：{txt_path}")
    
    with open(txt_path, "r", encoding="utf-8") as f:
        # 读取所有非空行
        all_lines = [line.strip() for line in f if line.strip()]
    
    # 如果总行数少于需要选取的数量，返回所有行
    if len(all_lines) <= num_lines:
        print(f"警告：文件仅包含{len(all_lines)}行，少于指定的{num_lines}行，将使用所有行")
        return all_lines

    # 随机选取指定数量的行
    #return random.sample(all_lines, num_lines)
    return all_lines[:num_lines]  # 如果不需要随机，可以使用前N行


# --------------------------
# 步骤2：调用 Azure GPT-4.1 生成标签
# --------------------------
def call_azure_gpt(selected_lines):
    """调用 Azure GPT-4.1，生成带标签的结构化结果"""
    # 初始化 Azure OpenAI 客户端
    client = AzureOpenAI(
        api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        api_version=AZURE_API_VERSION
    )
    
    # 将选中的行转换为字符串，作为输入
    lines_content = "\n".join([f"- {line}" for line in selected_lines])
    
    # 构造 Prompt（严格要求保留所有内容）
    prompt = """
        ## 你的身份和任务
        你是一个写作模版相似度分析和合并专家，能够从多个维度分析写作模版。

        ## 任务背景
        在这个任务中，你会首先收到多个标准写作模版集合set和一个待判断写作模版T。你的任务是判断T与集合set中模版的相似度，并给出最后整理的标准写作模版集合set。  

        ## 你具备的能力
        - 能够从多个维度分析写作模版，包括语法、结构、用词等。
        - 能够判断模版之间的相似度。
        - 能够根据分析结果，合并相似的模版，形成新的标准模版。

    """

    # 调用 GPT-4.1
    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,  # 使用 Azure 部署名称
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"你的输入内容为以下评论列表：\n{lines_content}\n请返回完整的输出"}
            ],
            temperature=0  # 确保结果稳定，不省略内容
        )
        return response.choices[0].message.content
    
    except Exception as e:
        raise ValueError(f"GPT-4.1 调用失败：{str(e)}")


# --------------------------
# 步骤3：解析模型输出并保存为 JSON
# --------------------------
def parse_and_save(gpt_response, output_file_path):
    """解析 GPT 输出并保存为 JSON 文件"""
    # 提取 JSON（去除可能的多余文本）
    import re
    pattern = r'```json\s*([\s\S]*?)```'
    match = re.search(pattern, gpt_response)
    if match:
        gpt_response = match.group(1).strip()
    
    try:
        result_json = json.loads(gpt_response)

        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        # 保存到本地
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(result_json, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存至：{output_file_path}")
        return result_json
    
    except json.JSONDecodeError:
        raise ValueError("GPT 输出的 JSON 格式错误")


# --------------------------
# 主流程：处理TXT文件
# --------------------------
if __name__ == "__main__":
    try:
        # 创建输出目录（如果不存在）
        os.makedirs(OUTPUT_DIR_PATH, exist_ok=True)
        
        # 生成输出文件名（基于输入文件名）
        base_name = os.path.splitext(os.path.basename(INPUT_TXT_PATH))[0]
        output_json_path = os.path.join(OUTPUT_DIR_PATH, f"{base_name}_tags.json")
        
        try:
            print(f"处理文件：{INPUT_TXT_PATH}")
            
            selected_lines = read_and_select_lines(INPUT_TXT_PATH, SELECTED_LINES_COUNT)
            print(f"已随机选取 {len(selected_lines)} 行内容")
 
            # 2. 调用 GPT-4.1 生成标签
            print("调用 GPT-4.1 处理内容...")
            gpt_result = call_azure_gpt(selected_lines)
            
            # 3. 解析并保存结果
            print("解析结果并保存...")
            parse_and_save(gpt_result, output_json_path)
            
            print(f"文件处理完成")
            
        except Exception as e:
            print(f"处理文件时出错：{str(e)}")
            
        print("\n所有处理完成！")
    
    except Exception as e:
        print(f"整体处理失败：{str(e)}")
