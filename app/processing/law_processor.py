import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import re


OC = "chetera"
BASE = "http://www.law.go.kr"

def get_law_list_from_api(search_term):
    exact_query = f'\"{search_term}\"'
    encoded_query = quote(exact_query)
    page = 1
    laws = []

    while True:
        url = f"{BASE}/DRF/lawSearch.do?OC={OC}&target=law&type=XML&display=100&page={page}&search=2&knd=A0002&query={encoded_query}"
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            break

        root = ET.fromstring(res.content)
        for law in root.findall("law"):
            name = law.findtext("법령명한글", "").strip()
            mst = law.findtext("법령일련번호", "")
            detail = law.findtext("법령상세링크", "")
            full_link = BASE + detail
            laws.append({"법령명": name, "MST": mst, "URL": full_link})

        if len(root.findall("law")) < 100:
            break
        page += 1

    return laws

def get_law_text_by_mst(mst):
    url = f"{BASE}/DRF/lawService.do?OC={OC}&target=law&MST={mst}&type=XML"
    try:
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8'
        return res.content if res.status_code == 200 else None
    except:
        return None

def clean(text):
    return re.sub(r"\s+", "", text or "")

def highlight(text, search_term):
    if not text:
        return ""
    return text.replace(search_term, f"<span style='color:red'>{search_term}</span>")

def get_highlighted_articles(mst, search_term):
    xml_data = get_law_text_by_mst(mst)
    if not xml_data:
        return "⚠️ 본문을 불러올 수 없습니다."

    tree = ET.fromstring(xml_data)
    articles = tree.findall(".//조문단위")
    search_term_clean = clean(search_term)
    results = []

    for article in articles:
        조내용 = article.findtext("조문내용", "") or ""
        항들 = article.findall("항")

        include = False
        항출력들 = []

        for 항 in 항들:
            항번호 = 항.findtext("항번호", "").strip()
            항내용 = 항.findtext("항내용", "") or ""
            if search_term_clean in clean(항내용):
                include = True

            for 호 in 항.findall("호"):
                호내용 = 호.findtext("호내용", "") or ""
                if search_term_clean in clean(호내용):
                    include = True
                for 목 in 호.findall("목"):
                    목내용 = 목.findtext("목내용", "") or ""
                    if search_term_clean in clean(목내용):
                        include = True

            항출력들.append((항번호, 항내용))

        if search_term_clean in clean(조내용):
            include = True

        if include:
            output = ""
            if 조내용:
                output += f"{highlight(조내용, search_term)}<br>"
            for 항번호, 항내용 in 항출력들:
                항텍스트 = highlight(항내용, search_term)
                output += f"<div style='text-indent:-1.8em; padding-left:1.8em;'>ⓞ{항번호} {항텍스트}</div>"
            results.append(output)

    return "".join(results) if results else "🔍 해당 검색어를 포함한 조문이 없습니다."
