# 快速启动

## 拉取项目
```bash
git clone https://github.com/woniusnai/alertmanagerTofeishu.git
cd alertmanagerTofeishu
```

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
#运行脚本（运行脚本前先确认脚本15，17行的机器人地址和签名正确，可直接修改脚本，变量内容，或者通过环境变量映射，未配置环境变量默认读取脚本内默认配置）
python alertmanager_feishu_webhook.py
```

## 测试消息：运行test.sh
```bash
# 注意默认test.sh 连接的是本地9527端口，需要根据实际的脚本启动或者映射的ip端口修改。
sh test.sh
```

## 配置alertmanager.yml发送地址
```bash
receivers:
  #此处省略其他配置
  - name: 'feishu'
    webhook_configs:
    - url: 'http://ip:9527/webhook'
      send_resolved: true
```

## 效果展示
<img width="660" height="640" alt="image" src="https://github.com/user-attachments/assets/ee7b437a-82a1-46ce-949d-52611eb1ae40" />

