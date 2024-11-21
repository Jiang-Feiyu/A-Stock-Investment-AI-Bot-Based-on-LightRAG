#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# from typing import List, Optional
# from fastapi import FastAPI
# from fastapi.encoders import jsonable_encoder
# from pydantic import BaseModel


# app = FastAPI()
# class Item(BaseModel):
#     name: Optional[str] = None
#     description: Optional[str] = None
#     price: Optional[float] = None
#     tax: float = 10.5
#     tags: List[str] = []
        
# items = {
#     "one": {"name": "苹果", "price": 50.2}
# }
# @app.put("/items/", response_model=Item)
# def update_item(name: str, item: Item):
#     update_item_encoded = jsonable_encoder(item)
#     items[name] = update_item_encoded
#     return update_item_encoded
# @app.get("/items/{item_id}", response_model=Item)
# def read_item(item_id: str):
#     return items[item_id]


# In[ ]:

import yfinance as yf
import json
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
 
class Stock(BaseModel):
    name:str
    ticker: str 
    exchange:str
    price: float 
    
stock_list=dict() 

def call_finance_api(ticker_name):
    ticker_data = yf.Ticker(ticker_name).info

#     finance_data = f"Fetching finance data for {ticker_name}"
    return ticker_data




app = FastAPI()
@app.post("/stock/")
async def create_item(s: Stock):
    return s

@app.put("/stock/put/{stock_ticker}")
def create_item(stock_ticker: str):
    stock_detail=call_finance_api(stock_ticker)
    with open('stockdata.txt', 'w') as file:
     file.write(json.dumps(stock_detail)) 
    stock_list[stock_ticker]= stock_detail
    return {"stock_ticker": stock_ticker, **stock_detail}

@app.get("/stock/getstock/{stock_ticker}")
async def return_stock(stock_ticker:str):
    return stock_list[stock_ticker]

