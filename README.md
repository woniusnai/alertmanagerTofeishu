# 快速启动

## 方式一：Docker（推荐）  
```bash
docker build -t alertmanager-feishu-webhook .
docker run -d -p 9527:9527 \
  -e FEISHU_WEBHOOK_URL=&lt;你的飞书机器人地址&gt; \
  --name alertmanager-feishu-webhook \
  alertmanager-feishu-webhook


