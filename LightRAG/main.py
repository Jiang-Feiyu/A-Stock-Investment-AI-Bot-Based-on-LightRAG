import requests
import json
import os
from datetime import datetime
import time
import logging
import sys
import select
from collections import defaultdict

# 检查文件和目录的写入权限
def check_permissions():
    fina_dir = './fina'
    data_file = './fina/data.jsonl'
    
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(fina_dir):
        try:
            os.makedirs(fina_dir)
            logging.info(f"Created directory: {fina_dir}")
        except PermissionError:
            logging.error(f"Permission denied: Cannot create directory {fina_dir}")
            return False
            
    # 检查文件写入权限
    try:
        with open(data_file, 'a') as f:
            pass
        return True
    except PermissionError:
        logging.error(f"Permission denied: Cannot write to {data_file}")
        return False
    
def setup_logger():
    """设置日志配置"""
    log_dir = './log/data_acquire'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f'data_acquire_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger()

def check_exit_command():
    """检查是否有退出命令"""
    if sys.platform == 'win32':
        import msvcrt
        if msvcrt.kbhit():
            if msvcrt.getch().decode().lower() == 'q':
                return True
    else:
        # Unix-like systems
        if select.select([sys.stdin], [], [], 0.0)[0]:
            if sys.stdin.readline().strip().lower() == 'exit':
                return True
    return False

def ensure_directory_exists(filepath):
    """确保目录存在，如果不存在则创建"""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def fetch_stock_data(ticker):
    """从FastAPI获取股票数据"""
    url = f"http://127.0.0.1:8000/stock/put/{ticker}"
    try:
        response = requests.put(url)
        response.raise_for_status()  # 会抛出异常如果状态码不是200
        data = response.json()
        logging.info(f"Successfully fetched data for {ticker}")
        return data
    except requests.RequestException as e:
        logger.error(f"获取{ticker}数据时出错: {e}")
        return None

def manage_stock_data(filepath, new_data, max_records=5):
    """管理股票数据，保持每个公司最多max_records条记录"""
    ensure_directory_exists(filepath)
    
    # 读取现有数据
    existing_data = defaultdict(list)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        ticker = record.get('symbol', '')
                        if ticker:
                            existing_data[ticker].append(record)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON line in file: {line}")
                        continue
        except IOError as e:
            logger.error(f"Error reading file {filepath}: {e}")
            return

    # 验证新数据格式
    ticker = new_data.get('symbol', '')
    if not ticker:
        logger.error(f"Invalid data format, missing symbol: {new_data}")
        return

    # 添加新数据并保持记录数限制
    existing_data[ticker].append(new_data)
    existing_data[ticker] = existing_data[ticker][-max_records:]

    # 写入数据到临时文件
    temp_filepath = filepath + '.tmp'
    try:
        with open(temp_filepath, 'w', encoding='utf-8') as f:
            records_written = 0
            for company_records in existing_data.values():
                for record in company_records:
                    json_line = json.dumps(record, ensure_ascii=False)
                    f.write(json_line + '\n')
                    records_written += 1
            # 确保数据写入磁盘
            f.flush()
            os.fsync(f.fileno())

        # 原子性地替换文件
        os.replace(temp_filepath, filepath)
        
        # 验证写入
        with open(filepath, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
            if line_count != records_written:
                raise ValueError(f"Written records verification failed: expected {records_written}, got {line_count}")
            
        logger.info(f"Successfully wrote and verified {records_written} records to {filepath}")
        
    except Exception as e:
        logger.error(f"Failed to write to file {filepath}: {e}")
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except OSError:
                pass

def load_companies(filepath='./fina/company.json'):
    """加载公司列表"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            companies = json.load(f)
            if not companies:
                logger.error("Company list is empty")
                return {}
            logger.info(f"Successfully loaded {len(companies)} companies")
            return companies
    except FileNotFoundError:
        logger.error(f"错误：未找到文件 {filepath}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"错误：无法解析JSON文件 {filepath}")
        return {}

def main():
    global logger
    logger = setup_logger()
    
    # 加载公司列表
    stock_tickers = load_companies()
    if not stock_tickers:
        logger.error("未能成功加载公司列表，程序退出")
        return

    filepath = './fina/data.jsonl'
    
    logger.info("程序启动 - 输入'exit'或按'q'键退出程序")
    
    try:
        while True:
            # 获取并保存每个行业的股票数据
            for industry, tickers in stock_tickers.items():
                logger.info(f"\n开始获取{industry}行业的数据...")
                for ticker in tickers:
                    if check_exit_command():
                        logger.info("收到退出指令，程序结束")
                        return

                    logger.info(f"正在获取 {ticker} 的数据...")
                    data = fetch_stock_data(ticker)
                    if data:
                        data['industry'] = industry  # 添加行业信息
                        data['timestamp'] = datetime.now().isoformat()
                        manage_stock_data(filepath, data)
                        logger.info(f"{ticker} 数据已保存")
                        time.sleep(1)  # 添加延迟以避免请求过于频繁
                    else:
                        logger.warning(f"{ticker} 数据获取失败")

            logger.info("本轮数据获取完成，等待下一轮...")
            
            # 等待60秒，期间检查是否有退出命令
            for _ in range(60):
                if check_exit_command():
                    logger.info("收到退出指令，程序结束")
                    return
                time.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("程序被手动中断")
    except Exception as e:
        logger.error(f"程序发生错误: {e}")
        logger.exception("详细错误信息：")

if __name__ == "__main__":
    print("server start")
    main()