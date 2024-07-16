import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup as bs

class IPO_Crawler:

    def html_parsing(self, url):
        # 세션 생성
        session = requests.Session()
        
        # 재시도 로직 설정
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        
        try:
            response = session.get(url)
            response.raise_for_status()  # HTTP 에러가 발생하면 예외를 발생시킴
            response.encoding='UTF-8' # 한글 깨지는 문제 예방
            html_text = response.text
            html_text = bs(html_text, 'html.parser')
            return html_text
            # print(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    def make_ipo_calender(self, soup):
        # 데이터 저장을 위한 딕셔너리 초기화
        data = {}

        # td 태그를 모두 찾음
        tds = soup.find_all('td', class_='days')

        for td in tds:
            date_tag = td.find('strong')
            if date_tag:
                date = date_tag.text.strip()
                rows = td.find_all('tr')
                
                for row in rows:
                    img_tag = row.find('img')
                    a_tag = row.find('a')
                    
                    if img_tag and a_tag:
                        img_src = img_tag['src']
                        link = a_tag['href']
                        title = a_tag['title']
                        
                        # 날짜를 키로 사용하여 링크, 제목, 이미지 src를 저장
                        if date not in data:
                            data[date] = []
                        data[date].append({'link': link, 'title': title, 'img_src': img_src})

        return data

    
    def detail_crawling(self, table):
        # 필요한 정보 저장을 위한 변수 초기화
        ipo_sub_date = None
        ipo_refund_date = None
        ipo_public_date = None
        confirmed_ipo_price = None
        company = []
        
        for row in table[0].find_all('tr'):
            cells = row.find_all('td')
            if '공모청약일' in cells[0].text:
                ipo_sub_date = cells[1].text.strip()
            elif '환불일' in cells[0].text:
                ipo_refund_date = cells[1].text.strip()
            elif '상장일' in cells[0].text:
                ipo_public_date = cells[1].text.strip()
        
        for row in table[1].find_all('tr'):
            cells = row.find_all('td')
            if '(확정)공모가격' in cells[0].text:
                confirmed_ipo_price = cells[1].text.strip()
        
        for row in table[3].find_all('tr'):
            cells = row.find_all('td')
            if '증권회사' not in cells[0].text:
                company.append(cells[0].text.strip())

        return ipo_sub_date, ipo_refund_date, ipo_public_date, confirmed_ipo_price, company

if __name__ == "__main__":
    crawler = IPO_Crawler()
    url = 'http://www.ipostock.co.kr/sub03/ipo06.asp'
    ipo_html = crawler.html_parsing(url)
    ipo_cal = crawler.make_ipo_calender(ipo_html)

    today_ipo_data = {}
    today = '3'

    if ipo_cal[today]:
        for i in range(len(ipo_cal[today])):
            link = ipo_cal[today][i]['link']
            detail_url = 'http://www.ipostock.co.kr' + link
            table = crawler.html_parsing(detail_url).find_all('table', class_='view_tb')
            ipo_sub_date, ipo_refund_date, ipo_public_date, confirmed_ipo_price, company = crawler.detail_crawling(table)
            today_ipo_data[ipo_cal[today][i]['title']] = [ipo_sub_date, ipo_refund_date, ipo_public_date, confirmed_ipo_price, company]

    print(today_ipo_data)

