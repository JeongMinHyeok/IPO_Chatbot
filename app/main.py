from fastapi import FastAPI
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
from app.ipo_crawler import IPO_Crawler
import json

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="공모주 챗봇", version="0.0.1")

scheduler = AsyncIOScheduler()

@app.post('/')
def root():
    ipo_cal = json.loads('./ipo_cal.json')
    crawler = IPO_Crawler
    today_ipo_data = {}
    today = datetime.now().strftime('%d')

    if ipo_cal[today]:
        for i in range(len(ipo_cal[today])):
            link = ipo_cal[today][i]['link']
            detail_url = 'http://www.ipostock.co.kr' + link
            table = crawler.html_parsing(detail_url).find_all('table', class_='view_tb')
            ipo_sub_date, ipo_refund_date, ipo_public_date, confirmed_ipo_price, company = crawler.detail_crawling(table)
            today_ipo_data[ipo_cal[today][i]['title']] = [ipo_sub_date, ipo_refund_date, ipo_public_date, confirmed_ipo_price, company]

    return today_ipo_data

def make_ipo_cal():
    crawler = IPO_Crawler()
    url = 'http://www.ipostock.co.kr/sub03/ipo06.asp'
    ipo_html = crawler.html_parsing(url)
    ipo_cal = crawler.make_ipo_calender(ipo_html)
    with open('ipo_cal.json', 'w') as f:
        json.dump(ipo_cal, f, indent=4)

# 일정 시간마다 collect_and_store_data 함수 실행
scheduler = BackgroundScheduler(timezone='Asia/Seoul')
scheduler.add_job(make_ipo_cal, 'cron', hour='8', minute='00', id='test')
scheduler.start()


@app.on_event("startup")  # 앱이 실행될 때 아래 함수 실행됨
def on_app_start():
    """before app starts"""
    if not scheduler.running:
        scheduler.start()


@app.on_event("shutdown")  # 앱이 종료될 때 아래 함수 실행됨
def on_app_shutdown():
    print("bye")
    """after app shutdown"""
    scheduler.shutdown()

