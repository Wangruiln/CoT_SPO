import requests
import json
from typing import Dict, List

# 服务地址（确保FastAPI服务已启动在该地址）
BASE_URL = "http://localhost:8004"

def test_optimize_prompt():
    # 构造测试请求数据
    payload = {
        "prompt": """
            # 你是一位游戏产品评测与攻略写作专家。
            你的任务是：
            - 针对任意新品、功能或活动，撰写一篇结构化、图文结合的评测与实用攻略。
            # 通用能力
            ## 结构化信息梳理能力
            1. 能够将复杂产品或活动分解为核心功能、视觉元素、升级系统等区块。
            2. 能够用分段、小标题、列表和FAQ清晰呈现信息。
            ## 图文结合表达能力
            1. 每个核心内容配以图片或动图，强化视觉冲击力。
            2. 文字与图片紧密结合，突出产品特色与实用价值。
            ## 实用攻略写作能力
            1. 针对获取流程、优惠活动、操作步骤进行分点讲解。
            2. 结尾强化号召力，鼓励读者行动或参与。
            # 写作思维链
            1. 明确主题，设定为新品评测或攻略类内容。
            2. 采用分区块结构，先总述后细分。
            3. 每个核心功能或流程配以图文说明。
            4. 使用列表和FAQ补充细节，提升实用性。
            5. 结尾强化号召力，鼓励读者行动。
            6. 保持语言简明、信息密集、逻辑清晰。
            # 注意事项
            - 语言风格务实、信息密集，避免文学化修饰和主观泛泛词。
            - 结构分明，段落紧凑，逻辑清晰。
            - 图文结合，图片需与文字内容紧密相关。
            - 结尾需有明确号召或实用建议。
            - 可适用于任何主题的新品评测或实用攻略写作。
            # 输出格式
            - 采用分区块结构：产品/功能介绍、核心视觉元素、升级系统、实战效果、获取攻略、FAQ、结语/号召。
            - 每个区块配以相关图片链接。
            - 列表和FAQ用于补充细节，提升实用性。
            - 结尾强化行动号召或实用建议。""",
        "article_text": "# Dravion X-Suit套装实战演示｜附最优惠的充值攻略\n\n        摘要：2025年9月30日，PUBG Mobile将正式推出Dravion X-Suit.作为首款配备双人滑翔翼的X-Suit，它不仅拥有惊艳全场的外观，更配备了首款可升级的AWM狙击枪外观，以及独特的切换枪械动画、专属表情和音效。\n\n        ![Dravion X-Suit套装及专属持枪姿势展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/davion_x-suit.png)\n\n        本文将为你揭示如何以最优惠价格获取足够UC，成功抽取这款梦寐以求的顶级套装。\n\n        ## ▍ Dravion X-Suit「天蛟之怒」：实战效果全解析\n\n        ### 核心视觉元素：\n\n        - 熔岩龙翼：双翼随动作伸展，边缘散发火光与余烬，宛如一场蓄势待发的风暴\n        - 灵焰圣球：环绕身旁的赤红光球与金色浮掌，象征神圣守护与力量凝聚\n        - 鎏金龙甲：黑色铠甲内部仿佛流淌着炽热岩浆，表面镶嵌会随呼吸微动的金纹\n        - 龙角头盔与金爪护手：头盔龙角高耸如冠，让每个待机动作都充满威慑感\n\n        ![Valor’s Requiem AWM（7级）外观展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/awm.png)\n\n        ### 7级进化系统：\n\n        Dravion X-Suit支持1-7级全阶段升级，每个阶段都会解锁新的外观与功能特效：\n\n        - 特殊外观变化\n        - 豪华入场动画（Spectacular Arrival）\n        - 胜利广播（Victory Broadcast）\n        - 终极光环与变身动画（Radiant Form）\n\n        实战效果：\n\n        ![Dravion X-Suit实战效果动态演示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/show-case.gif)\n\n        ### 专属可升级AWM：Valor’s Requiem AWM\n\n        伴随套装同步上线的，还有极具辨识度的Valor’s Requiem - AWM狙击枪外观\n\n        - 升级后可解锁：\n        - 击中标记金色龙纹印记\n        - 击杀触发火焰爆裂特效\n        - 专属龙雕战利品箱\n        - 自订燃痕击杀播报\n\n        ## ▍ Midasbuy超值攻略：如何以最优惠的价格获得典藏 Dravion X-Suit套装\n\n        Midasbuy平台推出多重优惠活动，你可以以最大优惠获取足够UC，轻松拿下这款典藏套装。\n\n        ### 充值实用攻略：\n\n        购买前：\n\n        - 绑定账号即成为VIP：付费前绑定账号即成为Midasbuy VIP, 额外获得3%-7%UC。顺手完成首充，赛季权益不遗漏。\n\n        ![Midasbuy账号绑定成为VIP及首充权益说明](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/midasbuy_topup.png)\n\n        - 充值积分兑换满赠券：利用以往充值赠送积分兑换满赠券，兑换价值高达300uc的满赠券及限定奖励，长期享受福利\n\n        积分兑换活动入口\n\n        购买后：\n\n        1. 充满累充档位：一次性达到目标档位，建议满额冲至12000 UC，所有档位奖励自动叠加到账（包含额外880uc直赠、改装零件碎片礼包、神话印记、重磅uc礼箱最高单次可开出12000uc）\n\n        累充活动入口\n\n        2. 分享额外获得随机uc：邀请好友助力额外获得随机uc,单次最高可达3000uc。每日仅限参加一次。\n\n        裂变活动入口\n\n        ### FAQ｜热门疑问速查\n\n        - 累充与裂变奖励可同时获得吗？\n\n        可以，各类奖励独立累计，活动福利可叠加享受。\n\n        - 满赠券的获取途径与作用？\n\n        满赠券可通过裂变、积分兑换获得，用于在支付过程中获得额外uc，需要绑定使用。\n\n        - 裂变活动发起及参与次数有限制吗？\n\n        有，每日发起及参与均有上限，合理分配资源可天天获券。\n\n        - 充值流程是否安全？\n\n        Midasbuy为官方平台，支持多种支付方式，安全可靠。\n\n        ## ▍ 结语\n\n        Dravion X-Suit是PUBG Mobile史上最令人期待的套装之一，其震撼的视觉特效和独特的双人滑翔翼功能，让它成为了每个玩家梦寐以求的收藏品。\n\n        ![Dravion X-Suit套装整体效果展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/actual-combat-effect.gif)\n\n        现在就行动吧！ 前往Midasbuy平台，开始你的充值计划，确保在9月30日活动开始后，第一时间拥有这条炎生巨龙，让你在战场上成为最耀眼的存在！\n\n        ｜小贴士：关注Midasbuy官方社交媒体和官网，获取最新活动资讯和限时优惠码，享受额外折扣！",
        "style": "{\"language\": {\"sentence_pattern\": [\"短句与中长句交替，信息点密集\", \"大量并列结构与列表，强调条理性\"], \"word_choice\": {\"formality_level\": \"3\", \"preferred_words\": [\"核心视觉元素\", \"实战效果\", \"专属\", \"升级\", \"攻略\", \"优惠\", \"活动\", \"奖励\", \"入口\", \"结语\", \"小贴士\"], \"avoided_words\": [\"文学化修饰\", \"过度主观感受\", \"模糊泛泛词\"]}, \"rhetoric\": [\"比喻（如‘蓄势待发的风暴’）\", \"拟人（如‘铠甲流淌着岩浆’）\", \"排比与并列\", \"直接号召\"]}, \"structure\": {\"paragraph_length\": \"平均80-120字，段落紧凑\", \"transition_style\": \"通过小标题、列表和FAQ自然过渡，逻辑清晰\", \"hierarchy_pattern\": \"总分结构，先总述后分解细节，分区块展开\", \"use_of_graphics\": \"每个核心内容配有图片或动图，视觉与文字紧密结合\"}, \"narrative\": {\"perspective\": \"第三人称+直接面向读者（你）\", \"time_sequence\": \"先介绍新品与功能，再分步骤讲解获取流程，最后总结与号召\", \"narrator_attitude\": \"权威、专业、鼓励行动\"}, \"emotion\": {\"intensity\": \"4\", \"expression_style\": \"直接表达，强调期待与实用价值，偶有热情号召\", \"tone\": \"积极、热烈、务实\"}, \"thinking\": {\"logic_pattern\": \"分步骤、分区块推进，先讲产品后讲获取方法，FAQ补充细节\", \"depth\": \"4\", \"rhythm\": \"快节奏，信息密集，重点突出\"}, \"uniqueness\": {\"signature_phrases\": [\"实战效果全解析\", \"充值实用攻略\", \"FAQ｜热门疑问速查\", \"结语\", \"小贴士\"], \"imagery_system\": [\"龙翼、熔岩、圣球、金甲等强烈视觉意象\", \"动图与静态展示交替\"]}}",
        "fact_info": "- 2025年9月30日PUBG Mobile推出Dravion X-Suit。\
                    - Dravion X-Suit为首款双人滑翔翼X-Suit，拥有可升级AWM狙击枪外观、切换枪械动画、专属表情和音效。\
                    - 视觉元素包括熔岩龙翼、灵焰圣球、鎏金龙甲、龙角头盔与金爪护手。\
                    - Dravion X-Suit支持1-7级升级，解锁特殊外观、豪华入场动画、胜利广播、终极光环与变身动画。\
                    - Valor’s Requiem AWM可升级，解锁金色龙纹击中标记、火焰爆裂击杀特效、龙雕战利品箱、自订燃痕击杀播报。\
                    - Midasbuy平台提供充值优惠活动，包括VIP绑定额外3%-7%UC、积分兑换满赠券（最高300uc）、累充奖励（建议满额至12000UC，额外880UC、改装零件碎片礼包、神话印记、重磅UC礼箱最高单次可开出12000UC）、裂变活动（邀请好友最高可得3000UC，每日限一次）。\
                    - FAQ说明累充与裂变奖励可叠加，满赠券获取途径为裂变和积分兑换，裂变活动每日有次数限制，充值流程安全可靠。\
                    - 建议关注Midasbuy官方社交媒体和官网获取最新活动资讯与限时优惠码。",
        "image": "![Dravion X-Suit套装及专属持枪姿势展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/davion_x-suit.png)\
                ![Valor’s Requiem AWM（7级）外观展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/awm.png)\
                ![Dravion X-Suit实战效果动态演示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/show-case.gif)\
                ![Midasbuy账号绑定成为VIP及首充权益说明](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/midasbuy_topup.png)\
                ![Dravion X-Suit套装整体效果展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/actual-combat-effect.gif)"
    }

    try:
        # 发送POST请求
        response = requests.post(
            url=f"{BASE_URL}/optimize",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )

        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            print("优化成功！")
            print(f"最佳提示词:\n{result['best_prompt']}")
            return result
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("连接失败，请确保FastAPI服务已启动并在指定端口运行")
    except Exception as e:
        print(f"测试过程出错: {str(e)}")

if __name__ == "__main__":
    test_optimize_prompt()