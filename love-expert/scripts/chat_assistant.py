#!/usr/bin/env python3
"""
恋爱达人 Expert - 聊天助理引擎 v2.0
======================================
功能：
1. 聊天记录分析诊断（提取IOI/IOD/WC/GC信号）
2. 真人感自动回复生成（按关系阶段+消息类型匹配）
3. 真人感Checkpoint验证
4. 男女双视角支持
5. 节奏控制建议
"""

import random
import re
from typing import List, Dict, Optional, Tuple

# ================================================================
# 真人感修饰引擎
# ================================================================

PREFIXES_MALE = ["嗯…让我想想啊", "诶，这个嘛", "哈哈", "哎哟", "话说", "emmm", 
                  "怎么说呢", "让我捋捋", "嗯哼", "诶对了", "我跟你说", "好家伙"]
PREFIXES_FEMALE = ["唔…", "哈哈哈", "诶诶", "哎呀", "话说", "emmm", 
                    "怎么说呢", "让我想想", "嗯哼", "对了对了", "我跟你讲"]

SUFFIXES = ["你觉得呢", "是吧", "是不是", "哈哈", "哎你懂的", "emmm",
            "🌚", "😏", "😂", "🤔", "🤨", "😌", "😅", "🥺", "～", "……",
            "（认真脸）", "（狗头）", "（小声）", "（bushi）"]

FILLERS = ["就是吧", "说实话", "其实吧", "认真的说", "不是我说", "反正吧", "讲真"]

COLLOQUIAL_MAP = {
    "您好": "你好", "关于": "说到", "此外": "还有就是", "因此": "所以",
    "然而": "不过", "例如": "比如", "通过": "靠", "是否": "是不是",
    "解决方案": "办法",
}


def add_human_touch(text: str, intensity: float = 0.6, gender: str = "male") -> str:
    """给文本加真人感。intensity:0-1。"""
    prefixes = PREFIXES_FEMALE if gender == "female" else PREFIXES_MALE

    # 1. 口语化替换
    for old, new in COLLOQUIAL_MAP.items():
        text = text.replace(old, new)

    # 2. 随机加语气前缀
    if random.random() < intensity * 0.35:
        text = f"{random.choice(prefixes)}，{text}"

    # 3. 随机加填充词
    if random.random() < intensity * 0.25:
        sentences = text.split("。")
        if len(sentences) >= 2:
            idx = random.randint(1, len(sentences) - 1)
            sentences[idx] = f"{random.choice(FILLERS)}，{sentences[idx]}"
            text = "。".join(sentences)

    # 4. 随机加后缀/表情
    if random.random() < intensity * 0.55:
        text = f"{text}{random.choice(SUFFIXES)}"

    return text


def human_touch_check(text: str) -> Dict[str, bool]:
    """真人感6维检查"""
    checks = {
        "有口语化": any(kw in text for kw in ["哈", "诶", "嗯", "话说", "就是", "emmm"]),
        "有表情/emoji": bool(re.search(r'[😂😏🤔😌😅🥺🌚😜🤪]', text)),
        "有话题钩子": "…" in text or "……" in text or bool(re.search(r'(有空|改天|下次|回头)', text)),
        "有自嘲/幽默": any(kw in text for kw in ["哈哈", "😂", "狗头", "bushi", "小声"]),
        "接地气": len(text) < 80 and not bool(re.search(r'(您|关于|此外|因此)', text)),
        "有个人风格": len(set(text)) / max(len(text), 1) > 0.6,  # 字符多样性
    }
    checks["通过"] = sum(checks.values()) >= 4
    return checks


# ================================================================
# 聊天记录分析器
# ================================================================

IOI_PATTERNS = [
    (r"你(呢|觉得|怎么看|认为)", "主动询问你的看法"),
    (r"(哈哈|哈哈哈|笑死|好逗)", "积极情绪回应"),
    (r"(晚安|早安|早点睡|记得)", "关心性表达"),
    (r"(好呀|可以呀|来呀|行)", "积极接受"),
    (r"(你呢|你的)", "反问关注你"),
    (r"[?？]\s*$", "主动提问"),
]

IOD_PATTERNS = [
    (r"^(嗯|哦|好的|知道|行|嗯嗯)$", "敷衍单字回复"),
    (r"(洗澡|睡了|忙|开会|有事)", "回避性借口"),
    (r"^\.+$", "无语/不想回"),
    (r"(呵呵|哦哦|好吧)", "消极应付"),
]

WC_PATTERNS = [  # 错误操作
    (r"(在吗|在不在|hello|你好)", "低价值开场"),
    (r"你(哪里人|多大|做什么|有男朋友)", "查户口式提问"),
    (r"(喜欢我|做我女朋友|在一起)", "过早表白"),
    (r"(教你|你应该|你要知道)", "好为人师/讲道理"),
    (r"(新车|新房|月薪|工资)", "刻意炫耀"),
]

GC_PATTERNS = [  # 正确操作
    (r"(看起来|感觉|猜|觉得)(你|你是个)", "冷读技巧"),
    (r"(有点|不过|虽然|但是)", "推拉技巧使用"),
    (r"(抱抱|心疼|懂你|辛苦了)", "情绪价值提供"),
    (r"(改天|下次|有空|一起)", "模糊邀约"),
    (r"(爱妃|朕|同学|师傅|本)", "角色扮演"),
]


def analyze_chat_history(messages: List[Dict[str, str]]) -> Dict:
    """分析聊天记录"""
    analysis = {
        "signals": {"IOI": [], "IOD": [], "WC": [], "GC": []},
        "scores": {"好感度": 5, "兴趣度": 5, "舒适度": 5},
        "relation_stage": "破冰期",
        "key_findings": [],
        "advice": [],
    }

    for msg in messages:
        content = msg.get("content", "")
        sender = msg.get("sender", "对方")

        # 检查IOI
        for pattern, label in IOI_PATTERNS:
            if re.search(pattern, content):
                analysis["signals"]["IOI"].append(f"{sender}:{label}")
                analysis["scores"]["好感度"] = min(10, analysis["scores"]["好感度"] + 1)

        # 检查IOD
        for pattern, label in IOD_PATTERNS:
            if re.search(pattern, content):
                analysis["signals"]["IOD"].append(f"{sender}:{label}")
                analysis["scores"]["好感度"] = max(1, analysis["scores"]["好感度"] - 1.5)

        # 检查错误操作
        for pattern, label in WC_PATTERNS:
            if re.search(pattern, content):
                analysis["signals"]["WC"].append(f"{sender}:{label}")
                analysis["scores"]["好感度"] = max(1, analysis["scores"]["好感度"] - 2)

        # 检查正确操作
        for pattern, label in GC_PATTERNS:
            if re.search(pattern, content):
                analysis["signals"]["GC"].append(f"{sender}:{label}")
                analysis["scores"]["好感度"] = min(10, analysis["scores"]["好感度"] + 2)

    # 判断关系阶段
    io_count = len(analysis["signals"]["IOI"])
    gc_count = len(analysis["signals"]["GC"])
    
    if analysis["scores"]["好感度"] >= 8:
        analysis["relation_stage"] = "暧昧期"
    elif analysis["scores"]["好感度"] >= 6:
        if gc_count >= 2:
            analysis["relation_stage"] = "舒适期"
        else:
            analysis["relation_stage"] = "舒适期（技巧不足，容易下跌）"
    elif analysis["scores"]["好感度"] >= 4:
        analysis["relation_stage"] = "破冰期"
    else:
        analysis["relation_stage"] = "危险期（需要冷冻重建吸引）"

    # 生成发现和建议
    if analysis["signals"]["WC"]:
        analysis["key_findings"].append(f"存在错误操作：{', '.join(set(analysis['signals']['WC']))}")
        analysis["advice"].append("立即停止上述错误操作模式")

    if len(analysis["signals"]["IOI"]) > len(analysis["signals"]["IOD"]) * 2:
        analysis["advice"].append("对方兴趣良好，可以尝试适度拉升关系")
    elif len(analysis["signals"]["IOD"]) > len(analysis["signals"]["IOI"]):
        analysis["advice"].append("对方兴趣偏低，建议冷冻+展示高价值，减少主动联系频率")

    if not analysis["signals"]["GC"]:
        analysis["advice"].append("你的回复中缺乏技巧性操作（冷读/推拉/共情），建议补充")

    return analysis


def format_diagnosis_report(analysis: Dict) -> str:
    """格式化诊断报告"""
    signals = analysis["signals"]
    scores = analysis["scores"]

    report = "📊 **诊断报告**\n"
    report += "━━━━━━━━━━━━━━━━━\n"
    
    # 好感度评分
    stars = "★" * int(scores["好感度"] // 2) + "☆" * (5 - int(scores["好感度"] // 2))
    report += f"好感度评分：{stars}（{scores['好感度']:.0f}/10）\n"
    
    # 关系阶段
    stage_emoji = {"破冰期": "🟢", "舒适期": "🟡", "暧昧期": "🟠", "危险期": "🔴"}
    emoji = "⚠️"
    for k, v in stage_emoji.items():
        if k in analysis["relation_stage"]:
            emoji = v
            break
    report += f"关系阶段：{emoji} {analysis['relation_stage']}\n"

    # 信号汇总
    report += f"\n**信号检测**\n"
    report += f"✅ 兴趣指标(IOI)：{len(signals['IOI'])}个\n"
    report += f"⚠️ 无兴趣指标(IOD)：{len(signals['IOD'])}个\n"
    if signals["WC"]:
        report += f"❌ 错误操作(WC)：{len(signals['WC'])}个\n"
    if signals["GC"]:
        report += f"👍 正确操作(GC)：{len(signals['GC'])}个\n"

    # 关键发现
    if analysis["key_findings"]:
        report += f"\n**关键发现**\n"
        for f in analysis["key_findings"][:3]:
            report += f"- {f}\n"

    # 建议
    if analysis["advice"]:
        report += f"\n**建议**\n"
        for i, a in enumerate(analysis["advice"][:3], 1):
            report += f"{i}. {a}\n"

    report += "━━━━━━━━━━━━━━━━━"
    return report


# ================================================================
# 回复生成器 v2（按关系阶段×消息类型匹配）
# ================================================================

REPLY_TEMPLATES = {
    "破冰期": {
        "分享情绪": [
            "啊这……也太那个了吧！我上次也遇到过类似的，当时我整个人都不好了😅 你后来咋整的？",
            "抱抱你🥺 虽然刚认识说这个可能有点突然，但我觉得你是个挺有意思的人",
            "哈哈你这经历让我想起一句话——人生嘛，就是用来体验的😂 对了你是做什么方向的？",
        ],
        "提问": [
            "我是做{job}的，就是那种天天被甲方虐但看到成品又觉得值了的工作😅 你呢？看你朋友圈不像干我这行的",
            "让我想想……我最近在忙{thing}。话说你问这个是想约我吗😏（开玩笑的）",
            "刚在{place}呢。你呢？看你上次发的那个{detail}，感觉你生活挺有意思的",
        ],
        "冷淡": ["哈哈好的，那你先忙，改天聊～", "嗯嗯，注意休息🌙", "好的收到🫡"],
        "主动": [
            "这么突然的吗？不过我喜欢😏 你挑个时间，我看看档期",
            "哈哈哈你这么热情我有点招架不住——不过还挺开心的🥰",
        ],
    },
    "舒适期": {
        "分享情绪": [
            "心疼了🥺 来来来朕的肩膀借你靠一会儿——不过不能哭太久哈，限量版衬衫蹭脏了可赔不起😏",
            "啊这……你们老板也太离谱了！要我我就直接……算了我不教坏你了😂 走，带你去吃好吃的消消气",
            "摸摸头😢 说真的，你这种人就是太负责了才会被欺负。下次再这样你就跟我说，我去给你撑场子（虽然可能没啥用🤪）",
        ],
        "提问": [
            "{answer}。感觉主角跟你有点像——表面淡定其实内心戏很多哈哈。你平时看啥类型的？",
            "我最近在{activity}。话说你问这个……该不会是想约我吧？我不贵的，请顿饭就行😏",
        ],
        "冷淡": [
            "看来今天有点不在状态啊，那我先不打扰你了～",
            "好嘞，那你先忙，我刷会儿剧去",
            "收到🫡 你忙完要是想聊天就找我～",
        ],
        "主动": [
            "可以呀！不过我得提前说一下——见面不许盯着我看超过3秒，我会害羞的😂",
            "我看看档期……嗯，为了你勉强挤一挤吧😏 不过去哪儿得听我的，我带你去个宝藏地方",
        ],
    },
    "暧昧期": {
        "分享情绪": [
            "呀，谁欺负我家宝贝了？名字报上来，我这就去……给他点个赞😏 开玩笑的，过来抱抱🥰",
            "心疼死我了😢 你在哪？我过去陪你……虽然可能远水救不了近火，但精神支持还是很到位的！",
        ],
        "提问": [
            "这么关心我？该不会喜欢上我了吧😏 好吧被你看穿了，我刚才在{place}，想我没？",
            "你想知道？那你先回答我一个问题——今天有没有想我？😌",
        ],
        "主动": [
            "来呀！正好我也想你了🥰 不过你要做好准备，我可能会忍不住一直看着你",
            "你终于说出来了😏 我还以为你要憋到什么时候呢。时间地点你定，我随时有空～",
        ],
    },
    "亲密期": {
        "分享情绪": [
            "抱抱宝宝😢 辛苦了，回家给你做好吃的。想吃什么？",
            "心疼了……快来我怀里充电🔋 今天给你按按头，保证比spa还舒服",
        ],
        "主动": [
            "想你了🥰 今天特别想抱抱你，比昨天多想一点，比前天多想两点，比刚认识多想一万点",
            "我老婆/老公最好啦🥰 虽然刚分开没多久但已经开始想了……完蛋了完蛋了",
        ],
    },
}


def generate_reply_v2(
    user_message: str,
    msg_type: str,
    stage: str = "破冰期",
    gender: str = "male",
    context: Optional[Dict] = None
) -> Tuple[str, Dict]:
    """生成回复 + Checkpoint结果"""
    if context is None:
        context = {}

    stage_templates = REPLY_TEMPLATES.get(stage, REPLY_TEMPLATES["破冰期"])
    type_templates = stage_templates.get(msg_type, stage_templates.get("分享情绪", ["哈哈你说的对😄"]))

    reply = random.choice(type_templates)

    # 填充变量
    reply = reply.replace("{job}", context.get("job", "打工人"))
    reply = reply.replace("{thing}", context.get("thing", "搬砖"))
    reply = reply.replace("{place}", context.get("place", "家里蹲"))
    reply = reply.replace("{detail}", context.get("detail", "日常"))
    reply = reply.replace("{activity}", context.get("activity", "躺平"))
    reply = reply.replace("{answer}", context.get("answer", "刚看完一个电影"))

    # 真人感修饰
    intensity_map = {"破冰期": 0.4, "舒适期": 0.6, "暧昧期": 0.75, "亲密期": 0.85}
    intensity = intensity_map.get(stage, 0.5)
    reply = add_human_touch(reply, intensity, gender)

    # Checkpoint
    checks = human_touch_check(reply)

    return reply, checks


def get_rhythm_advice(their_response_time: str = "5-10分钟") -> str:
    """根据对方回复节奏给出建议"""
    advice_map = {
        "秒回": "对方兴趣很高！你可以适当加快节奏，但不要同样秒回，间隔15-30秒，长度略短于对方。",
        "5-10分钟": "正常节奏。你间隔3-5分钟回，长度匹配。保持这个节奏。",
        "30分钟+": "对方兴趣一般或正在忙。间隔30-60分钟再回，简短回应。不要追问。",
        "很久/不回了": "建议冷冻。今天不再发消息，隔1-2天后发条有趣的朋友圈刷存在感。",
    }
    return advice_map.get(their_response_time, "镜像对方节奏，她多久回你就多久回。")


def suggest_stage_upgrade(stage: str, context: Dict) -> str:
    """根据当前阶段给出推进建议"""
    suggestions = {
        "破冰期": "尝试让对方主动开启话题。可以发一条有趣的朋友圈，等她评论后顺势私聊。",
        "舒适期": "可以尝试推拉和模糊邀约了。注意：先确认对方有IOI信号再行动。",
        "暧昧期": "确认关系窗口期！尝试服从测试（如'记得明天跟我说早安'），通过后推进关系。",
        "亲密期": "关系已稳定，重点转向长期经营：制造共同回忆、规划未来。",
    }
    return suggestions.get(stage, "继续建设吸引力。")


# ================================================================
# CLI交互
# ================================================================

def main():
    print("=== 恋爱达人 Expert 聊天引擎 v2.0 ===")
    print("模式：1=聊天记录分析 2=回复生成 3=节奏建议")
    print("输入 'quit' 退出\n")

    while True:
        cmd = input("选择模式 (1/2/3): ").strip()
        if cmd == "quit":
            break

        if cmd == "1":
            print("\n输入聊天记录（每人一行，格式：我/对方:内容，空行结束）：")
            msgs = []
            while True:
                line = input()
                if not line:
                    break
                parts = line.split(":", 1)
                if len(parts) == 2:
                    msgs.append({"sender": parts[0].strip(), "content": parts[1].strip()})

            if msgs:
                result = analyze_chat_history(msgs)
                print("\n" + format_diagnosis_report(result))

        elif cmd == "2":
            stage = input("关系阶段 (破冰期/舒适期/暧昧期/亲密期): ").strip() or "破冰期"
            msg_type = input("对方消息类型 (分享情绪/提问/冷淡/主动): ").strip() or "分享情绪"
            gender = input("你的性别 (male/female): ").strip() or "male"

            reply, checks = generate_reply_v2("", msg_type, stage, gender)
            print(f"\n💬 推荐回复：{reply}")
            print(f"📋 Checkpoint：{'✅ 通过' if checks['通过'] else '❌ 不通过，需重写'}")
            for k, v in checks.items():
                if k != "通过":
                    print(f"  {'✅' if v else '❌'} {k}")

        elif cmd == "3":
            rt = input("对方回复节奏 (秒回/5-10分钟/30分钟+/很久): ").strip()
            print(f"\n💡 {get_rhythm_advice(rt)}")


if __name__ == "__main__":
    main()