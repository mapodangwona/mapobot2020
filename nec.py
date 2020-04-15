# coding: utf-8
import functools
import pprint
import datetime

import pytz
import requests
import bs4
DATA = [x.split(': ') for x in """electionId: 0020200415
requestURI: /WEB-INF/jsp/electioninfo/0020200415/vc/vccp09.jsp
topMenuId: VC
secondMenuId: VCCP09
menuId: VCCP09
statementId: VCCP09_#7
electionCode: 7
cityCode: 0
sggCityCode: 0
townCode: -1
x: 31
y: 4""".split('\n')]
DATA = dict(DATA)

@functools.lru_cache(maxsize=128)
def fetch(timestamp):
    req = requests.post(url='http://info.nec.go.kr/electioninfo/electionInfo_report.xhtml', data=DATA)
    assert req.status_code == 200
    res = bs4.BeautifulSoup(req.content, "lxml")
    sel0 = '#table01 > thead > tr'
    sel1 = '#table01 > tbody > tr:nth-child(1)'
    sel2 = '#table01 > tbody > tr:nth-child(2)'
    heads = res.select(sel0)[0]
    names = res.select(sel1)[0].find_all('td')
    votes = res.select(sel2)[0].find_all('td')
    results = []
    for idx, (name, vote) in enumerate(zip(names, votes)):
        if name.contents:
            if str(name.contents[0]).strip()[0] == '<':
                name = '\n'.join(str(x.contents[0]).strip() for x in name.contents)
            else:
                name = '\n'.join(str(x).strip() for x in name.contents)
        else:
            name = {1: '선거인수', 2:'투표수', len(names) - 3: '무효투표수', len(names) - 2: '기권수', len(names) - 1: '개표율'}.get(idx, '')
        if vote.contents:
            vote = '\n'.join(str(x).strip() for x in vote.contents)
            vote = vote.split('\n')
            if len(vote) == 1:
                try:
                    vote = (int(vote[0].replace(',', '')), 0.0)
                except ValueError:
                    if '.' in vote[0]:
                        vote = (0, float(vote[0]))
                    else:
                        name = vote[0]
                        vote = (0, 0.0)
            else:
                vote0 = int(vote[0].replace(',', ''))
                vote1 = float(vote[2].replace('(', '').replace(')', ''))
                vote = (vote0, vote1)
        else:
            vote = (0, 0.0)
        results.append([name, vote])
    return timestamp, results

all_citizens = 43994247
voted_citizens = 29127637


def stat():
    timestamp = datetime.datetime.isoformat(datetime.datetime.now(pytz.timezone('Asia/Seoul'))).split('.')[0][:-3]
    timestamp, results = fetch(timestamp)
    results = dict(results)
    result = []
    beautify = [
        [['선거인수'], ['투표수']],
        [['더불어시민당'], ['미래한국당'], ['정의당'], ['열린민주당'], ['국민의당'], ['민생당']],
        [['민중당'], ['노동당'], ['녹색당'], ['미래당'], ['여성의당']], 
        [['우리공화당'], ['친박신당'], ['국가혁명배당금당'], ['기독자유통일당']],
        [['코리아', '가자!평화인권당', '가자환경당', '국민새정당', '국민참여신당', '깨어있는시민연대당', '남북통일당', '대한당', '대한민국당', '미래민주당', '새누리당', '우리당', '자유당', '자영업당', '충청의미래당', '통일민주당', '한국복지당', '홍익당', '새벽당', '한국경제당']],
        [['계'], ['무효투표수'], ['개표율']]]
    alias = {'국가혁명배당금당': '허경영당', '기독자유통일당': '김문수당'}
    result.append(f'득표율 {timestamp}')
    for section in beautify:
        for element in section:
            number_1 = 0
            number_2 = 0.0
            for each_element in element:
                number_1 += results[each_element][0]
                number_2 += results[each_element][1]
            name = element[0] if len(element) == 1 else '기타신생정당'
            result.append((name, number_1, number_2))
    # pprint.pprint(result)
    result_strs = []
    htmls = []
    htmls.append(f'<html><body>')
    htmls.append(f'<h1>득표율 {timestamp}')
    htmls.append('</h1><table style="td {border: 1px solid black}"><tr><td>정당명</td><td>득표율</td><td>득표수</td></tr>')
    for name, no1, no2 in result:
        kakao = False
        ts = 5 if kakao else 4  # Kakao
        tabs = '' if len(name) >= ts else '\t'
        zero = ' ' if no2 < 10 else ''
        result_str = '%s%s\t%s%.2f\t%d' % (alias.get(name, name), tabs, zero, no2, no1) if no2 != 0.0 else '%s%s\t\t%d' % (name, tabs, no1)
        result_strs.append(result_str)
        htmls.append(f'<tr><td>{name}</td><td>{"%.2f" % no2}</td><td>{no1}</td></tr>')
    htmls.append('</table>')
    htmls.append('</html>')
    return result_strs, htmls
    

if __name__ == '__main__':
    res, htmls = stat()
    print('\n'.join(res))
    with open('/Users/khbyun/Downloads/a.html', 'w') as ofile:
        ofile.write('\n'.join(htmls))
