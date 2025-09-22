EVALUATE_PROMPT = """
根据原始思维链和需求，评估两个回答 A 和 B，判断哪一个更好地满足了需求。如果提供了参考答案，请严格遵循参考答案的格式和内容。

# 需求
{requirement}

# A
{answers}

# B
{new_answers}

# 标准答案
{ground_truth}

请给出你的分析，并用 XML 标签包裹你的回答和选择。

<analyse>分析内容</analyse>
<choose>A/B（你认为更好的答案）</choose>
"""
