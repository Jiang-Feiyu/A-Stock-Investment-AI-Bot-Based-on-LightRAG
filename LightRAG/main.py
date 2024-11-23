import requests
import json
import os
from datetime import datetime
import time
import logging
import sys
import select
from collections import defaultdict

fina_dir = '../fina'
data_file = '../fina/data.jsonl'
company_list = 'company.json'
knowledge_file = '../fina/dynamic_knowledge.txt'

def ensure_directory():
    """确保目录存在"""
    if not os.path.exists(fina_dir):
        os.makedirs(fina_dir)

def load_company_list():
    """加载公司列表"""
    try:
        with open(company_list, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load company list: {e}")
        return {}

def query_stock(ticker):
    """查询股票信息"""
    try:
        response = requests.put(f"http://localhost:8000/stock/put/{ticker}")
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to query stock {ticker}: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error querying stock {ticker}: {e}")
        return None

def save_to_jsonl(data_list):
    """保存数据列表到JSONL文件"""
    try:
        # 以写入模式打开文件（覆写之前的内容）
        with open(data_file, 'w') as f:
            for data in data_list:
                json_str = json.dumps(data)
                f.write(json_str + '\n')
    except Exception as e:
        logging.error(f"Failed to save data: {e}")

def query_all_stocks():
    """查询所有股票信息并生成知识文本"""
    all_data = []
    all_knowledge = []
    companies = load_company_list()
    
    print("==================companies==================")
    print(companies)
    
    for category, tickers in companies.items():
        logging.info(f"Processing category: {category}")
        for ticker in tickers:
            logging.info(f"Querying stock: {ticker}")
            
            stock_data = query_stock(ticker)
            
            if stock_data:
                stock_data['category'] = category
                stock_data['query_time'] = datetime.now().isoformat()
                all_data.append(stock_data)
                
                print("==================stock_data==================")
                print(stock_data)
                
                # 处理指标并生成文本
                knowledge_text = process_metrics(stock_data)
                all_knowledge.append(knowledge_text)
                
                time.sleep(1)
            else:
                logging.warning(f"Failed to get data for {ticker}")
    
    combined_knowledge = '\n\n'.join(all_knowledge)
    return all_data, combined_knowledge

def process_metrics(data):
    """处理指标数据并生成文本描述"""
    knowledge_text = []
    
    # 基本信息
    basic_info = [
        f"## Data about the {data.get('stock_ticker', 'N/A')}",
        f"### Basic information about the company",
        f"stock ticker is: {data.get('stock_ticker', 'N/A')}",
        f"industry category is: {data.get('industry', 'N/A')}",
        f"company business summary is: {data.get('longBusinessSummary', 'N/A')}"
    ]
    
    # 风险指标
    risk_metrics = {
        f"beta is: {data.get('beta','N/A')}",
        f"debtToEquity is: {data.get('debtToEquity','N/A')}",
        f"priceToSalesTrailing12Months is: {data.get('priceToSalesTrailing12Months','N/A')}",
        f"shortRatio is : {data.get('shortRatio','N/A')}"
    }
    
    # 财务指标
    financial_metrics = {
        f"profitMargins is: {data.get('profitMargins','N/A')}",
        f"totalCash is: {data.get('totalCash','N/A')}",
        f"totalRevenue is: {data.get('totalRevenue','N/A')}",
        f"floatShares is: {data.get('floatShares','N/A')}"
    }
    
    # 估值指标
    valuation_metrics = {
        f"trailingPE is: {data.get('trailingPE','N/A')}",
        f"forwardPE is: {data.get('forwardPE','N/A')}",
        f"priceToBook is: {data.get('priceToBook','N/A')}",
        f"priceToSalesTrailing12Months is: {data.get('priceToSalesTrailing12Months','N/A')}"
    }
    
    # 添加基本信息
    knowledge_text.extend(basic_info)
    
    # 添加风险指标
    knowledge_text.extend(risk_metrics)
    
    # 添加财务指标
    knowledge_text.extend(financial_metrics)
    
    # 添加估值指标
    knowledge_text.extend(valuation_metrics)
    
    return '\n'.join(knowledge_text)

def save_knowledge(text):
    """保存知识文本到文件"""
    try:
        with open(knowledge_file, 'w') as f:
            f.write(text)
    except Exception as e:
        logging.error(f"Failed to save knowledge text: {e}")
        
def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    ensure_directory()

    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"Starting new query cycle at {current_time}")
            
            # 查询所有股票数据并生成知识文本
            all_stock_data, knowledge_text = query_all_stocks()
            
            # 保存数据和知识文本
            if all_stock_data:
                save_to_jsonl(all_stock_data)
                save_knowledge(knowledge_text)
                logging.info(f"Successfully updated data and knowledge for {len(all_stock_data)} stocks")
            else:
                logging.warning("No data was collected in this cycle")
            
            logging.info("Waiting 60 seconds before next cycle...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        logging.info("Program stopped by user")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    print("server start")
    main()