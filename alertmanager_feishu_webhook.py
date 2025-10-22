#!/usr/bin/env python3
# 这是一个 Flask 应用，用于接收 Alertmanager 的告警消息，并将其转发到飞书机器人。

import os
import logging
import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
from tenacity import retry, stop_after_attempt, wait_fixed

# 飞书机器人 Webhook URL
FEISHU_WEBHOOK = os.getenv(
    "FEISHU_WEBHOOK", "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxxxxxxxxxxx")
FEISHU_SECRET = os.getenv("FEISHU_SECRET", "xxxxxxxxxxxxxxxxxxxxxx")

if not FEISHU_WEBHOOK:
    raise RuntimeError("FEISHU_WEBHOOK 未配置")

# 日志配置
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

feishu = Flask(__name__)

def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"),
                         digestmod=hashlib.sha256).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign

def utc2cst(iso: str) -> str:
    # UTC 时间转 CST 时间，返回格式化字符串
    if not iso:
        return ""
    # 去掉末尾 'Z' 并加上 +00:00，方便 fromisoformat
    utc = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    cst = utc.astimezone(timezone(timedelta(hours=8)))
    return cst.strftime("%Y-%m-%d %H:%M:%S")

def build_msg(alerts, is_firing: bool):
    """飞书消息卡片"""
    color = "red" if is_firing else "green"
    title = " 🚨告警🚨" if is_firing else " ✅恢复✅"

    elements = []
    for a in alerts:
        labels = a.get("labels", {})
        annos = a.get("annotations", {})
        env = labels.get("environment", "unknown")
        name = labels.get("alertname", "unknown")
        level = labels.get("severity", "unknown")
        inst = labels.get("instance", "").split(":")[0]
        summary = annos.get("summary", "")
        desc = annos.get("description", "")
        start = utc2cst(a.get("startsAt", ""))
        # cluster = labels.get("cluster", "无")
        # container = labels.get("container", "无")
        # pod = labels.get("pod", "无")
        # team = labels.get("team", "")
        end = utc2cst(a.get("endsAt", "")) if not is_firing else ""

        # 根据环境艾特不同的人
        at_text = ""
        if "生产环境" in env:
            at_text = "<at id=all></at>"  # 艾特所有人
        elif "测试环境" in env:
            at_text = "<at id=all></at>"
        elif "开发环境" in env:
            at_text = "<at id=all></at>"
        else:
            at_text = "<at id=all></at>"

        # 使用 Markdown 格式
        content = (
            # f"**{title}**\n"
            f"- **告警类型**：<font color='{color}'>{name}</font>\n"
            f"- **告警级别**：<font color='{color}'>{level}</font>\n"
            f"- **系统环境**：<font color='{color}'>{env}</font>\n"
            f"- **告警主题**：<font color='{color}'>{summary}</font>\n"
            f"- **告警详情**：<font color='{color}'>{desc}</font>\n"
            f"- **故障实例**：<font color='{color}'>{inst}</font>\n"
            f"- **故障时间**：<font color='{color}'>{start}</font>\n"
            # f"- **集群**：<font color='{color}'>{cluster}</font>\n"
            # f"- **容    器**：<font color='{color}'>{container}</font>\n"
            # f"- **Pod 资源**：<font color='{color}'>{pod}</font>\n"
        )
        
        if end:
            content += f"- **恢复时间**：<font color='{color}'>{end}</font>\n" 
        content += f"{at_text}\n"

        elements.append({
            "tag": "markdown",
            "content": content
        })

    header_title = f"{env}{title}" if env != "unknown" else f"{title}"
    
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": header_title},
            "template": color
        },
        "elements": elements
    }
    return card


@retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
def send_feishu(payload):
    # 发送飞书消息，失败则重试3次，每次间隔10秒
    resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=5)
    resp.raise_for_status()
    return resp


@feishu.route("/webhook", methods=["POST"])
def webhook():
    # 接收 Alertmanager 的告警请求
    data = request.get_json(force=True)
    # logging.info("收到告警: %s", data)
    alerts = data.get("alerts", [])

    firing = [a for a in alerts if a.get("status") == "firing"]
    resolved = [a for a in alerts if a.get("status") == "resolved"]

    ts = int(time.time())
    sign = gen_sign(ts, FEISHU_SECRET)

    for group, flag in ((firing, True), (resolved, False)):
        if not group:
            continue
        card = build_msg(group, flag)
        payload = {
            "timestamp": str(ts),
            "sign": sign,
            "msg_type": "interactive",
            "card": card
        }
        try:
            resp = send_feishu(payload)
        except Exception as e:
            log.error("发送失败: %s", e)
    return jsonify({"status": "ok", "resp": resp.text}), 200


if __name__ == "__main__":
    port = os.getenv("PORT", "9527")
    print(f"启动服务（端口：{port}")
    feishu.run(host="0.0.0.0", port=port)

# 健康检查接口
@feishu.route("/health", methods=["GET"])
def health():
    return "ok", 200
