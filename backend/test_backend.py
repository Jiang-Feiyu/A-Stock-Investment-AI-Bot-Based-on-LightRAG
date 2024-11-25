import unittest
import yfinance as yf
from fastapi.testclient import TestClient
from backend import app

class TestStockAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_ticker = "AAPL"
    
    def test_stock_data_format(self):
        # 测试直接调用Yahoo Finance API
        stock_data = yf.Ticker(self.test_ticker).info
        
        # 检查返回的是否为字典类型
        self.assertIsInstance(stock_data, dict)
            
        # 打印获取到的数据结构
        print("\nReceived data structure:")
        for key, value in stock_data.items():
            print(f"{key}: {type(value)} = {value}")
            
    def test_api_endpoint(self):
        # 测试API端点
        response = self.client.put(f"/stock/put/{self.test_ticker}")
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应数据
        response_data = response.json()
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data['stock_ticker'], self.test_ticker)

if __name__ == '__main__':
    unittest.main(verbosity=2)