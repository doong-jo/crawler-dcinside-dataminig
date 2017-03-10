#-*- coding: utf-8 -*-

#교수님이 주신 네이버 뉴스 파싱

from bs4 import BeautifulSoup

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
    
page=BeautifulSoup(urllib2.urlopen('http://news.naver.com'), "lxml", fromEncoding="ko")

print (page.head.title)
print (page.head.title.string)
for i in range(100):
    print (i, page('a')[i].string)


#인터넷에서 구한 네이버 웹툰 제목 파싱
"""
import urllib.request
from bs4 import BeautifulSoup

html = urllib.request.urlopen('http://comic.naver.com/webtoon/weekday.nhn')
soup = BeautifulSoup(html, "lxml")
titles = soup.find_all("a", "title")

for title in titles:
    print('title:{0:10s} link:{1:20s}\n'.format(title['title'], title['href']))
"""

#직접 짠 네이버 웹소설 베스트리그 제목 파싱
"""
import urllib.request
from bs4 import BeautifulSoup

#f = open("webnovel_best_list.txt", "w")

for n in range(87):
    html = urllib.request.urlopen('http://novel.naver.com/best/genre.nhn?page=%d' % n)
    soup = BeautifulSoup(html, "lxml")
    titles = soup.find("tbody")
    for m in range(10):
        novel_best_num = 10*n + m+1
        novel_best_titles = str(novel_best_num) + ' ' + titles("strong")[m].string
        try:
            print (novel_best_titles)
            #f.write(str(novel_best_titles)+"\n")
        except UnicodeEncodeError:
            print (novel_best_titles)

#f.close()
"""

#직접 짠 네이버 영화 네티즌 평점,리뷰 파싱(레버넌트)
"""
import odbc
import time
import urllib.request as ur
from bs4 import BeautifulSoup

connect=odbc.odbc('Snoopy')
db=connect.cursor()

for n in range(0,805):
    html = ur.urlopen('http://movie.naver.com/movie/point/af/list.nhn?st=mcode&sword=124212&target=after&page=%d' % n)
    soup = BeautifulSoup(html, "lxml")
    titles = soup.find_all("td", "title")
    m = 0
    for title in titles:
        review_num = 10*n + m+1
        review = str(title.contents[4].string)
        movie_review = str(review_num) + ". " + review.strip()
        m+=1
        
        if(movie_review.find("'") > -1):
            movie_review = movie_review.replace("'", " ")
            
        print(movie_review)
        db.execute("INSERT into game.temp2(review)VALUES('%s')" % (movie_review))
    time.sleep(0.1)
"""

#직접 짠 게임노트 주간순위 파싱
"""
import urllib.request as ur
from bs4 import BeautifulSoup

f = open("game_rating_1.txt", "w")

html = ur.urlopen('http://www.gamenote.com/rank_ongame/')
soup = BeautifulSoup(html, "lxml", from_encoding="euc-kr")

li = soup.find_all("li", "list100_list")
for l in li:
    p1 = l.find("p", "list100_0")
    p2 = l.find("p", "list100_2")
    rate = str(p1.string) + "위. "
    game_rating = str(p2.a.string)
    f.write(rate + game_rating + "\n")
    print (rate + game_rating)

f.close()
"""

#직접 짠 게임노트 게임뉴스 파싱
"""
import time
import urllib.request as ur
from bs4 import BeautifulSoup

f = open("news_game_titles.txt", "w")

html = 'http://www.gamenote.com/news_game'

for n in range(1,91001):
    soup = BeautifulSoup(ur.urlopen(html+str(n)), "lxml", from_encoding='utf-8')
    title = soup.find("div", {"id" : "read_title"})
    time.sleep(0.5)
    try:
        news_title = n, title.string
        print (n)
        f.write(str(news_title) + "\n")
    except AttributeError:
        print ("None")
        continue
    except UnicodeEncodeError:
        continue

f.close()
"""

print ("\\")