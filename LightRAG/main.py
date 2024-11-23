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
    """查询所有股票信息"""
    all_data = []
    companies = load_company_list()
    
    for category, tickers in companies.items():
        logging.info(f"Processing category: {category}")
        for ticker in tickers:
            logging.info(f"Querying stock: {ticker}")
            
            stock_data = query_stock(ticker)
            
            if stock_data:
                stock_data['category'] = category
                stock_data['query_time'] = datetime.now().isoformat()
                all_data.append(stock_data)
                
                # 添加延时避免过于频繁的请求
                time.sleep(1)
            else:
                logging.warning(f"Failed to get data for {ticker}")
    
    return all_data

def main():
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 确保目录存在
    ensure_directory()

    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"Starting new query cycle at {current_time}")
            
            # 查询所有股票数据
            all_stock_data = query_all_stocks()
            
            # 保存所有数据（覆写文件）
            if all_stock_data:
                save_to_jsonl(all_stock_data)
                logging.info(f"Successfully updated data for {len(all_stock_data)} stocks")
            else:
                logging.warning("No data was collected in this cycle")
            
            # 等待60秒
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