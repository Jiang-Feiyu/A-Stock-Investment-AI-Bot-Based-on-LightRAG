#!/usr/bin/env python
# coding: utf-8

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
    return ticker_data

app = FastAPI()
@app.post("/stock/")
async def create_item(s: Stock):
    return s

@app.put("/stock/put/{stock_ticker}")
def create_item(stock_ticker: str):
    stock_detail=call_finance_api(stock_ticker)
    # with open('stockdata.txt', 'w') as file:
    #  file.write(json.dumps(stock_detail)) 
    stock_list[stock_ticker]= stock_detail
    return {"stock_ticker": stock_ticker, **stock_detail}