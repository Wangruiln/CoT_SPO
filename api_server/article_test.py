import requests
import json
from typing import Optional, Dict, Any
from requests.exceptions import RequestException, Timeout, ConnectionError


class ArticleFeatureClient:
    """文章思维链提取服务的调用客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        """
        初始化客户端
        :param base_url: 服务基础地址（默认：本地8002端口，与服务配置一致）
        """
        self.base_url = base_url.rstrip("/")  # 确保地址末尾无斜杠
        self.headers = {"Content-Type": "application/json"}  # 请求头（JSON格式）
        self.timeout = 300000  # 请求超时时间（单位：秒，可根据文本长度调整）


    def extract_style(self, article_text: str) -> Dict[str, Any]:
        """
        调用文风特征提取接口（/extract-style）
        :param article_text: 待分析的文章文本（非空）
        :return: 提取结果（含ret_code、msg、style_summary、CoT等字段）
        :raises ValueError: 输入文本为空时抛出
        :raises RequestException: 网络请求异常时抛出
        """
        # 1. 校验输入（避免空文本请求）
        if not article_text.strip():
            raise ValueError("输入文本不能为空，请提供有效的文章内容")
        
        # 2. 构造请求参数
        url = f"{self.base_url}/extract-style"
        payload = {"text": article_text.strip()}  # 去除文本前后空白
        
        try:
            # 3. 发送POST请求
            response = requests.post(
                url=url,
                headers=self.headers,
                data=json.dumps(payload),  # 转为JSON字符串（避免requests自动编码问题）
                timeout=self.timeout
            )
            response.raise_for_status()  # 捕获HTTP错误（如404、500）
            result = response.json()
            
            # 4. 解析服务返回的状态（非0表示失败）
            if result.get("ret_code") != 0:
                raise RequestException(f"服务处理失败：{result.get('msg', '未知错误')}")
            
            return result
        
        except ConnectionError:
            raise RequestException(f"特征提取失败：无法连接服务（{url}），请确认服务已启动")
        except Timeout:
            raise RequestException(f"特征提取失败：请求超时（文本过长时可适当延长timeout）")
        except RequestException as e:
            raise RequestException(f"特征提取异常：{str(e)}")


# ------------------- 示例：如何使用客户端 -------------------
if __name__ == "__main__":
    # 1. 初始化客户端（默认连接本地8002端口，若服务部署在其他机器，需修改base_url）
    client = ArticleFeatureClient(base_url="http://localhost:7002")

    try:

        # 3. 准备测试文章文本（可替换为实际需要分析的文本）
        test_article = """
        # Dravion X-Suit套装实战演示｜附最优惠的充值攻略

        摘要：2025年9月30日，PUBG Mobile将正式推出Dravion X-Suit.作为首款配备双人滑翔翼的X-Suit，它不仅拥有惊艳全场的外观，更配备了首款可升级的AWM狙击枪外观，以及独特的切换枪械动画、专属表情和音效。

        ![Dravion X-Suit套装及专属持枪姿势展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/davion_x-suit.png)

        本文将为你揭示如何以最优惠价格获取足够UC，成功抽取这款梦寐以求的顶级套装。

        ## ▍ Dravion X-Suit「天蛟之怒」：实战效果全解析

        ### 核心视觉元素：

        - 熔岩龙翼：双翼随动作伸展，边缘散发火光与余烬，宛如一场蓄势待发的风暴
        - 灵焰圣球：环绕身旁的赤红光球与金色浮掌，象征神圣守护与力量凝聚
        - 鎏金龙甲：黑色铠甲内部仿佛流淌着炽热岩浆，表面镶嵌会随呼吸微动的金纹
        - 龙角头盔与金爪护手：头盔龙角高耸如冠，让每个待机动作都充满威慑感

        ![Valor’s Requiem AWM（7级）外观展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/awm.png)

        ### 7级进化系统：

        Dravion X-Suit支持1-7级全阶段升级，每个阶段都会解锁新的外观与功能特效：

        - 特殊外观变化
        - 豪华入场动画（Spectacular Arrival）
        - 胜利广播（Victory Broadcast）
        - 终极光环与变身动画（Radiant Form）

        实战效果：

        ![Dravion X-Suit实战效果动态演示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/show-case.gif)

        ### 专属可升级AWM：Valor’s Requiem AWM

        伴随套装同步上线的，还有极具辨识度的Valor’s Requiem - AWM狙击枪外观

        - 升级后可解锁：
        - 击中标记金色龙纹印记
        - 击杀触发火焰爆裂特效
        - 专属龙雕战利品箱
        - 自订燃痕击杀播报

        ## ▍ Midasbuy超值攻略：如何以最优惠的价格获得典藏 Dravion X-Suit套装

        Midasbuy平台推出多重优惠活动，你可以以最大优惠获取足够UC，轻松拿下这款典藏套装。

        ### 充值实用攻略：

        购买前：

        - 绑定账号即成为VIP：付费前绑定账号即成为Midasbuy VIP, 额外获得3%-7%UC。顺手完成首充，赛季权益不遗漏。

        ![Midasbuy账号绑定成为VIP及首充权益说明](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/midasbuy_topup.png)

        - 充值积分兑换满赠券：利用以往充值赠送积分兑换满赠券，兑换价值高达300uc的满赠券及限定奖励，长期享受福利

        积分兑换活动入口

        购买后：

        1. 充满累充档位：一次性达到目标档位，建议满额冲至12000 UC，所有档位奖励自动叠加到账（包含额外880uc直赠、改装零件碎片礼包、神话印记、重磅uc礼箱最高单次可开出12000uc）

        累充活动入口

        2. 分享额外获得随机uc：邀请好友助力额外获得随机uc,单次最高可达3000uc。每日仅限参加一次。

        裂变活动入口

        ### FAQ｜热门疑问速查

        - 累充与裂变奖励可同时获得吗？

        可以，各类奖励独立累计，活动福利可叠加享受。

        - 满赠券的获取途径与作用？

        满赠券可通过裂变、积分兑换获得，用于在支付过程中获得额外uc，需要绑定使用。

        - 裂变活动发起及参与次数有限制吗？

        有，每日发起及参与均有上限，合理分配资源可天天获券。

        - 充值流程是否安全？

        Midasbuy为官方平台，支持多种支付方式，安全可靠。

        ## ▍ 结语

        Dravion X-Suit是PUBG Mobile史上最令人期待的套装之一，其震撼的视觉特效和独特的双人滑翔翼功能，让它成为了每个玩家梦寐以求的收藏品。

        ![Dravion X-Suit套装整体效果展示](https://midas-global-1259340503.cos.ap-singapore.myqcloud.com/cms/actual-combat-effect.gif)

        现在就行动吧！ 前往Midasbuy平台，开始你的充值计划，确保在9月30日活动开始后，第一时间拥有这条炎生巨龙，让你在战场上成为最耀眼的存在！

        ｜小贴士：关注Midasbuy官方社交媒体和官网，获取最新活动资讯和限时优惠码，享受额外折扣！
        """

        # 4. 调用特征提取接口
        print("\n" + "=" * 50)
        print("开始提取文章特征...")
        extract_result = client.extract_style(article_text=test_article)

        # 5. 打印提取结果（按需解析字段）
        print("\n文章特征提取结果：")
        print(f"状态码：{extract_result['ret_code']}")
        print(f"风格概括：{extract_result['style_summary']}")
        print(f"风格标签：{extract_result['style_label']}")
        print(f"多维度风格特征：{json.dumps(extract_result['style'], indent=2, ensure_ascii=False)}")
        print(f"事实信息：{extract_result['fact_info']}")
        print(f"图片链接：{extract_result['image'] or '无'}")
        print(f"写作思维链（CoT）：{extract_result['CoT']}")
        print(f"写作提示词：{extract_result['prompt']}")

    except (ValueError, RequestException) as e:
        # 捕获并打印所有异常
        print("\n" + "=" * 50)
        print(f"调用失败：{str(e)}")