from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import odbc
import re


try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

"DB연결"
connect = odbc.odbc('Test')
db = connect.cursor()

gallList = []
gallUpDateList = []
listNumber = 3

def createGallListWithSelenium():

    binary = 'C:\ProgramData\Anaconda3\selenium\webdriver\chrome\chromedriver.exe'
    browser = webdriver.Chrome(binary)

    "크롬드라이버 첫 시작 URL 입력 및 동작 순차적 수행"
    browser.get('http://gall.dcinside.com/m/')

    "더보기 버튼 클릭"
    search = browser.find_element_by_id('btn_upmgall_more').click()

    "3페이지로 이동"
    search = browser.find_element_by_id('btn_upminor_next').click()
    search = browser.find_element_by_id('btn_upminor_next').click()

    "해당 페이지 소스 저장"
    resultHtml = browser.page_source

    page = BeautifulSoup(resultHtml, "html.parser")
    "리스트 id 하위 소스 저장"
    ul = page('ul', {'id': 'up_mgallery_list_more_ul'})

    ul_li = ul[0].find_all('li')

    i = 0

    while i in range(len(ul_li)):
        ul_li_a = ul_li[i].a['href']
        ul_li_span = ul_li[i].find_all('span')
        ul_li_span_date = ul_li_span[1].string

        "url 정규화"
        ul_li_a_split = ul_li_a.split('/')[2] + "/" + ul_li_a.split('/')[3] + ul_li_a.split('/')[4]
        ul_li_a_split = "http://gall.dcinside.com/" + ul_li_a_split + "&page="

        "리스트에 갤러리 url 추가 및 승격 일자 추가"
        gallList.append(ul_li_a_split)
        gallUpDateList.append(ul_li_span_date)

        i = i + 1

    time.sleep(5)

    browser.quit()

##################################################################################################################################################################################################

"문자열 내 특수문자 제거"
def removePunctuation(_string):
    resultString = ""

    for c in _string:
        "True 이면 특수문자가 아님"
        if c.isalnum():
            resultString += c

    return resultString
##################################################################################################################################################################################################
def insertDB_article(_db, _galleryName, _numVal, _typeVal, _titleVal, _commentVal, _writerVal, _noMemberVal, _dateVal, _viewVal, _likeVal):

    print(
        '번호:', _numVal,
        '개념/글/그림:', _typeVal,
        '제목:', _titleVal,
        '댓글수:', _commentVal,
        '작성자:', _writerVal,
        '유/고정닉넴:', _noMemberVal,
        '날짜:', _dateVal,
        '조회수:', _viewVal,
        '추천수:', _likeVal
    )

    _db.execute(
        "insert into test.dcinside_gall (gallname_, num_, type_, title_, comment_, writer_, member_, date_, view_, recommend_) " \
        "Values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            _galleryName, _numVal, _typeVal, _titleVal, _commentVal, _writerVal, _noMemberVal, _dateVal, _viewVal, _likeVal))

##################################################################################################################################################################################################

"갤러리의 월별 게시글 수, 조회 수를 저장"
def insert_SumCnt_ArticleAndView_FromDB(_db, _galleryName, _dateList):

    _i = 0

    while _i in range(len(_dateList)):

        "dcinsde_gall 테이블에서 월별로 게시글 조회수를 가져옴"
        _db.execute("select SUM(view_) as sum_view_ from test.dcinside_gall where gallname_ = '" + _galleryName + "' and date_ like '"+_dateList[_i]+"%'")
        _view = _db.fetchall()

        "dcinsde_gall 테이블에서 월별로 게시글 수를 가져옴"
        _db.execute("select COUNT(*) from test.dcinside_gall where gallname_ = '" + _galleryName + "' and date_ like '"+_dateList[_i]+"%'")
        _articleCnt = _db.fetchall()

        "갤러리 이름과 함께 월별 게시글 조회 수, 게시글 수를 삽입"
        _db.execute(
            "insert into test.dcinside_count (_gallery, _date, _view, _articleCnt) " \
            "Values ('%s', '%s', '%s', '%s')"% (_galleryName, _dateList[_i], _view[0][0], _articleCnt[0][0]))

        _i = _i + 1

"웹크롤링 수행"
def crawling(_gallList, _gallUpDateList):
    k = 13
    i = 0
    j = 0

    year = 0
    month = 0
    monthCnt = 0

    "IsDoneReadPage = 게시글을 모두 읽었는지 여부 저장"
    IsDoneReadPage = False

    while k in range(len(_gallList)):
        dateList = []

        "갤러리이름을 url에서 추출"
        galleryName = _gallList[k].split('=')[1]
        galleryName = galleryName.split('&')[0]

        "갤러리의 첫 페이지를 읽어옴 / 맨 마지막 페이지 번호를 알기 위함"
        page = BeautifulSoup(urllib2.urlopen(_gallList[k] + str(1)), 'lxml')

        "해당 갤러리의 승격일을 년,월,일 구분함"
        gallUpDate_split = _gallUpDateList[k].split("-")

        "맨 뒤 링크에서 맨 마지막 페이지 번호를 식별함"
        endPageTag = page('a', 'b_next')[1]['href']
        endPageNum = endPageTag
        endPageNum = endPageNum.split('&')[1]
        endPageNum = int(endPageNum.split('=')[1])


        "맨 마지막 페이지 부터 크롤링"
        i = endPageNum

        while True:

            "게시글을 모두 읽으면 종료"
            if i == 0 or IsDoneReadPage == True:
                IsDoneReadPage = False
                break

            "페이지 읽어들임"
            page = BeautifulSoup(urllib2.urlopen(_gallList[k] + str(i)), 'lxml')

            "게시글 번호 태그 리스트의 크기로 게시글 수를 찾음"
            articleRange = range(len(page('td', 't_notice')))

            hitCnt = 0;
            for j in articleRange:

                "상단 공지글은 제외"
                if page('td', 't_notice')[j].string == '공지':
                    hitCnt = hitCnt + 1
                    continue

                "작성날짜"
                dateVal = page('td', 't_date')[j].string
                date_split = dateVal.split(".")

                "년-월일 형식을 만듦"
                date_yearAndMonth = date_split[0]+ "-" +date_split[1]

                "현재 게시글 작성 월이 리스트에 없다면 추가"
                if date_yearAndMonth not in dateList:
                    dateList.append(date_yearAndMonth)


                "승격 전날까지 수집"
                limitDate = int(gallUpDate_split[0] + gallUpDate_split[1] + gallUpDate_split[2]) - 1
                articleDate = int(date_split[0] + date_split[1] + date_split[2])
                if limitDate < articleDate:
                    IsDoneReadPage = True
                    continue

                "댓글 수를 0으로 초기화"
                commentCnt = '[0]'

                "댓글 여부, em 태그가 있으면 댓글이 존재하는 글임"
                allFind_A = page('td', 't_subject')[j].find_all('a')
                if len(allFind_A) != 1:
                    "존재하는 댓글 수로 초기화"
                    commentCnt = allFind_A[1].em.string

                    "보이스리플 존재 시에 제거하고 댓글 수로 초기화한다"
                    if '/' in commentCnt:
                        commentCnt = "[" + commentCnt.split("/")[1]

                td_Subject_A = page('td', 't_subject')[j].a

                "글번호"
                numVal = page('td', 't_notice')[j].string

                "글종류 (개념글, 그림글, 그림없는글)"
                typeVal = td_Subject_A['class'][0]

                "글제목"
                titleVal = td_Subject_A.string
                titleVal = removePunctuation(titleVal)

                "댓글수"
                commentVal = commentCnt[1:len(commentCnt) - 1]

                td_Writer_Child = page('td', 't_writer user_layer')
                "작성자"
                writerVal = td_Writer_Child[j].span.string
                writerVal = removePunctuation(writerVal)

                "유/고정 닉네임 식별"
                if len(td_Writer_Child[j].find_all('a')):
                    "고정닉네임"
                    noMemberVal = 1
                else:
                    "유동닉네임"
                    noMemberVal = 0


                td_Hits = page('td', 't_hits')
                "조회수 저장"
                viewVal = td_Hits[j + hitCnt].string
                "추천수 저장"
                likeVal = str(td_Hits[j + hitCnt + 1].string)

                "다음 게시글의 조회수와의 인덱스 차이(조회수, 추천수)를 더함"
                hitCnt += 1

                insertDB_article(db, galleryName, numVal, typeVal, titleVal, commentVal, writerVal, noMemberVal, dateVal, viewVal, likeVal)

            print("갤러리 번호:", k, "갤러리 이름:", galleryName, "페이지 번호:", i)
            i = i - 1

        insert_SumCnt_ArticleAndView_FromDB(db, galleryName, dateList)
        k = k + 1

##################################################################################################################################################################################################
"동적 웹 크롤링 (셀리니움) / 갤러리 리스트 및 승격일 리스트 생성"
createGallListWithSelenium()

"웹크롤링 수행"
crawling(gallList, gallUpDateList)
    # db.execute("select * from test.dcinside_gall where date_ like '" + dateList + "%'")
    #
    # table = db.fetchall()
    # len(table)
    #
    # db.execute("insert into test.dcinside_count (_gallery, _month, _article_count) " \
    #            "Values ('%s', '%s', '%s')" % (galleryName, str(year) + str(month), len(table)))