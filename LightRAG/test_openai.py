import json
import os

# 确保目录存在
os.makedirs('./fina', exist_ok=True)

companies = {
    "科技公司": [
        'AAPL',  # 苹果
        'MSFT',  # 微软
        'GOOGL', # Alphabet A
        'GOOG',  # Alphabet C
        'META',  # Meta
        'NVDA',  # 英伟达
        'TSLA',  # 特斯拉
        'TSM',   # 台积电
        'AVGO',  # 博通
        'ORCL',  # 甲骨文
        'CSCO',  # 思科
        'CRM',   # Salesforce
        'ADBE',  # Adobe
        'AMD',   # AMD
        'INTC'   # 英特尔
    ],
    "电商与互联网": [
        'AMZN',  # 亚马逊
        'BABA',  # 阿里巴巴
        'JD',    # 京东
        'PDD',   # 拼多多
        'SHOP',  # Shopify
        'MELI',  # MercadoLibre
        'CPNG'   # Coupang
    ],
    "金融服务": [
        'JPM',   # 摩根大通
        'BAC',   # 美国银行
        'WFC',   # 富国银行
        'MS',    # 摩根士丹利
        'GS',    # 高盛
        'V',     # Visa
        'MA',    # Mastercard
        'AXP',   # 美国运通
        'BLK',   # 贝莱德
        'SCHW'   # 嘉信理财
    ],
    "医疗健康": [
        'JNJ',   # 强生
        'UNH',   # 联合健康
        'PFE',   # 辉瑞制药
        'ABBV',  # 艾伯维
        'MRK',   # 默沙东
        'LLY',   # 礼来制药
        'TMO',   # 赛默飞世尔科技
        'ABT',   # 雅培制药
        'DHR',   # 丹纳赫
        'BMY'    # 百时美施贵宝
    ],
    "消费品": [
        'PG',    # 宝洁
        'KO',    # 可口可乐
        'PEP',   # 百事可乐
        'COST',  # Costco
        'WMT',   # 沃尔玛
        'MCD',   # 麦当劳
        'NKE',   # 耐克
        'SBUX',  # 星巴克
        'DIS',   # 迪士尼
        'HD'     # 家得宝
    ],
    "工业制造": [
        'CAT',   # 卡特彼勒
        'BA',    # 波音
        'HON',   # 霍尼韦尔
        'GE',    # 通用电气
        'MMM',   # 3M
        'UPS',   # UPS
        'RTX',   # 雷神技术
        'LMT',   # 洛克希德·马丁
        'DE',    # 迪尔
        'GM'     # 通用汽车
    ]
}

# 将数据写入JSON文件
with open('./fina/company.json', 'w', encoding='utf-8') as f:
    json.dump(companies, f, ensure_ascii=False, indent=4)