# 快速启动

## 方式一：Docker（推荐）  
```bash
docker build -t alertmanager-feishu-webhook .
docker run -d -p 9527:9527 \
  -e FEISHU_WEBHOOK="你的飞书机器人地址" \
  -e FEISHU_SECRET="飞书机器人签名" \
  --name alertmanager-feishu-webhook \
  alertmanager-feishu-webhook
```
## 方式二：直接通过本地python启动
### 先升级python至3.7以上过程不多赘述
### 安装升级好python后安装依赖包
```bash
#安装依赖
pip install --no-cache-dir flask requests gunicorn tenacity
#运行脚本
python alertmanager_feishu_webhook.py
```

## 然后修改alertmanager发送地址
```bash
receivers:
  #此处省略其他配置
  - name: 'feishu'
    webhook_configs:
    - url: 'http://ip:9527/webhook'
      send_resolved: true
```
