import re
import requests
import logging
import traceback
import time
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from cache import AdtCache, MemoryCache
from cache.filecache import FileCache

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

URLS = {
    "DART_BASE": "https://dart.fss.or.kr",
    "DART_LIST": "https://dart.fss.or.kr/dsab007/detailSearch.ax",
    "DART_VIEWER": "https://dart.fss.or.kr/report/viewer.do",
    "DART_DSAF": "https://dart.fss.or.kr/dsaf001/main.do",
}
logger = logging.getLogger("dartrig")


class DartWeb:
    def __init__(self, cache: AdtCache = None, file_cache: FileCache = None):
        self.logger = logging.getLogger("dart_web")
        self.session = requests.Session()
        self.session.get(URLS["DART_BASE"], headers=HEADERS)

        if cache is None:
            self.logger.info("Cache is not provided. Use MemoryCache")
            cache = MemoryCache()

        self.cache: AdtCache = cache

        self.file_cache = file_cache
        if self.file_cache is not None:
            self.logger.info(f"File cache is enabled. Cache directory: {file_cache.base_dir}")

    def request_detail(self, rcp_no: str, dtd: str, ele_id: int = 0, offset: int = 0) -> str:
        """
        :param rcp_no:
        :param dtd: html | dart3.xsd
        :param ele_id:
        :param offset:
        :return:
        """
        dcm_no = self._get_dcm_no_by_rcp_no(rcp_no)
        return self._request_detail_with_dcm(rcp_no, dtd, dcm_no, ele_id, offset)

    def _try_file_cache_request(self, url, prefix, file_cache_key, ext="html"):
        if self.file_cache is not None:
            cached = self.file_cache.get_file(prefix=prefix, key=file_cache_key, ext=ext)
            if cached is not None:
                self.logger.debug(f"file cache hit for key {file_cache_key}")
                return cached

        response = self.session.get(url, headers=HEADERS)
        self.logger.info(response.headers)
        content_type = response.headers["Content-Type"]
        if content_type is not None and "MS949" in content_type.upper():
            self.logger.debug(f"response encoding is MS949. change to utf-8")
            response.encoding = "ms949"
            text = response.text
        else:
            text = response.text

        # self.logger.debug(f"_try_file_cache_request response text : {text}")

        if self.file_cache is not None:
            self.file_cache.save_file(prefix=prefix, key=file_cache_key, ext=ext, data=text)
            self.logger.debug(f"file cache set for key {file_cache_key}")
        return text

    def _request_detail_with_dcm(self, rcp_no, dtd, dcm_no, ele_id=0, offset=0):
        dtd_split = dtd.split(".")[0]
        file_cache_key = f"{rcp_no}_{dcm_no}_{dtd_split}_{ele_id}_{offset}"

        url = f"{URLS['DART_VIEWER']}?rcpNo={rcp_no}&dcmNo={dcm_no}&eleId={ele_id}&offset={offset}&length=0&dtd={dtd}"
        self.logger.info(f"request_detail_with_dcm url : {url}")
        return self._try_file_cache_request(url, "viewer", file_cache_key, ext="html" if dtd.lower() == "html" else "xml")

    def _get_dcm_no_by_rcp_no(self, rcp_no):
        cache_key = f"dcm_no_{rcp_no}"
        try:
            if self.cache is not None:
                cached = self.cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"dsaf001_report cache hit for rcp_no {rcp_no}")
                    return cached

            url = f"{URLS['DART_DSAF']}?rcpNo={rcp_no}"
            html_text = self._try_file_cache_request(url, "dsaf", rcp_no)
            numbers = re.findall("\d{7}", html_text)
            dcm_no = numbers[2]

            if self.cache is not None:
                self.cache.set(cache_key, dcm_no)
                logger.debug(f"dsaf001_report cache set for rcp_no {rcp_no}")
        except Exception as ex:
            logger.exception(ex)
            raise ValueError(f"dcm number fetch failed for rcp_no : [{rcp_no}]")

        return dcm_no

    def _deprecated_get_dsaf_html(self, rcp_no):
        return self.session.get(f"{URLS['DART_DSAF']}?rcpNo={rcp_no}", headers=HEADERS).text

    def get_document(self, rcp_no, dtd, ele_id=0, offset=0):
        """
        문서 리턴
        :param rcp_no:
        :param dtd:
        :param ele_id:
        :param offset:
        :return: (content_type, content)
        """
        dcm_no = self._get_dcm_no_by_rcp_no(rcp_no)
        url = f"{URLS['DART_VIEWER']}?rcpNo={rcp_no}&dcmNo={dcm_no}&eleId={ele_id}&offset={offset}&length=0&dtd={dtd}"
        response = self.session.get(url, headers=HEADERS)
        content_type = response.headers.get("Content-Type")
        return content_type, response.content

    def search_report(self, num, start, end, srch_txt):
        data = {
            'currentPage': str(num),
            'maxResults': '100',
            'maxLinks': '10',
            'sort': 'date',
            'series': 'desc',
            'textCrpCik': '',
            'lateKeyword': '',
            'keyword': '',
            'reportNamePopYn': 'N',
            'textkeyword': '',
            'businessCode': 'all',
            'autoSearch': 'N',
            'option': 'report',
            'textCrpNm': '',
            'reportName': srch_txt,
            'tocSrch': '',
            'textCrpNm2': '',
            'textPresenterNm': '',
            'startDate': start,
            'endDate': end,
            'finalReport': 'recent',
            'businessNm': '전체',
            'corporationType': 'all',
            'closingAccountsMonth': 'all',
            'tocSrch2': ''
        }

        return self.session.post(URLS["DART_LIST"], data=data, headers=HEADERS)


class DartAPI:
    def __init__(self, keys: List, cache: AdtCache):
        """

        :param keys: dart_api key
        :param cache: MemoryCache or RedisCache
        """
        self.keys: DartKeys = DartKeys(keys)
        self.cache = cache
        logger.info(f"cache keys : {self.cache.keys()}")

    def get_disclosure_list(self, end_de, max_page=1, use_cache=False, pause=0.5):
        """
        :param end_de: YYYYMMDD 요청 종료일
        :param max_page: 최대 요청 페이지 생략시 1
        :param use_cache: 캐시 사용여부
        :param pause: 요청간 쉬는 시간(단위 초)
        :return: 공시목록
        """
        results = []
        page = 1
        total_page = 1
        page_no = 0

        while page <= total_page:
            response_items = None
            json_data = self.get_disclosure(end_de=end_de, page=page)
            status = json_data.get("status")

            if status == '013':  # 조회된 데이터가 없습니다
                logger.info("no data")
                break
            elif status == '012':  # 접근할 수 없는 IP입니다.
                logger.error(f"접근할 수 없는 IP key")
                # self.dart_api.disable_key(key)
                # not increase page
            elif status == '020':  # API key 한도 초과
                logger.error(f"{status} API key 한도 초과 key")
                # self.dart_api.disable_key(key)
                # not increase page
            elif status == '021':
                logger.error(f"{status} 조회 가능한 회사 개수가 초과하였습니다.(최대 100건)")
            elif status == '100':
                logger.error(f"{status} 조회 가능한 회사 개수가 초과하였습니다.(최대 100건)")
            elif status == '101':
                logger.error(f"{status} 부적절한 접근입니다.")
            elif status == '800':
                logger.error(f"{status} 시스템 점검으로 인한 서비스가 중지 중입니다.")
                break
            elif status == '900':
                logger.error(f"{status} 정의되지 않은 오류가 발생하였습니다.")
            elif status == '901':
                logger.error(f"{status} 사용자 계정의 개인정보 보유기간이 만료되어 사용할 수 없는 키입니다. 관리자 이메일(opendart@fss.or.kr)로 문의하시기 바랍니다.")
            elif status == '000':  # 정상조회
                page_no = json_data.get("page_no")
                page_count = json_data.get("page_count")
                total_count = int(json_data.get("total_count"))
                total_page = int(json_data.get("total_page"))
                page = page + 1
                logger.info(f"정상조회 total_count : {total_count}, total_page : {total_page}, page_count : {page_count}, page_no : {page_no}")
                response_items = json_data.get("list")
            else:
                logger.error(f"처리안된 예외 케이스 status : {status}")

            if use_cache:
                cache_key = f"dartapi_list_{end_de}"
                keys = [x.get("rcept_no") for x in response_items]
                diff = self.cache.differential(cache_key, keys)
                logger.debug(f"diff : {diff}, cached keys : {len(self.cache.keys())}")
                diff_ratio = float(len(diff)) / float(len(response_items)) * 100 if len(response_items) > 0 else float(0)

                if diff_ratio == float(0):
                    logger.info(f"diff ratio is {diff_ratio}% => break")
                    break
                else:
                    logging.info(f"diff ratio is {diff_ratio}%")
                    results.extend([x for x in response_items if x.get("rcept_no") in diff])
                    self.cache.push_values(cache_key, keys)

                    if diff_ratio < 80:
                        logger.info(f"break")
                        break
                    else:
                        logger.info(f"pause {pause} secs for continue")
                        time.sleep(pause)
                        continue
            else:
                results.extend(response_items)

                logger.info(f"pause {pause} secs for continue")
                time.sleep(pause)

            if total_page == page_no:
                logger.info(f"total page reached {total_page}")
                break

            if max_page <= page_no:
                logger.info(f"max page reached {max_page}")
                break

        list_items = []

        for item in results:
            logger.debug(f"item : {item}")
            # 각 항목별로 데이터 추출
            data = {
                "company": item.get('corp_name', ''),
                "market": item.get('corp_cls', ''),
                "title": item.get('report_nm', ''),
                "code": item.get('stock_code', ''),
                "rcp_no": item.get('rcept_no', ''),
                "rcept_dt": item.get('rcept_dt', ''),
                "remark": item.get('rm', ''),
                "flr_nm": item.get('flr_nm', ''),
            }
            list_items.append(data)

        return list_items

    def get_disclosure(self, end_de, page=1, page_count=100):
        key = self.keys.next_key()
        logger.info(f"fetching data  date : {end_de}, page : {page}, withkey : {key}")
        param = {
            'crtfc_key': key,
            'page_count': page_count,
            'page_no': page,
            'end_de': end_de
        }
        return requests.get("https://opendart.fss.or.kr/api/list.json", params=param).json()

    def get_document_zip_bytes(self, rcp_no):
        key = self.keys.next_key()
        logger.info(f"fetching data  rcp_no : {rcp_no}, withkey : {key}")
        param = {
            'crtfc_key': key,
            'rcept_no': rcp_no
        }
        response = requests.get("https://opendart.fss.or.kr/api/document.xml", params=param)
        content_type = response.headers.get("Content-Type")
        if "xml" in content_type:
            logger.info(f"rcp_no : {rcp_no} Content-Type is XML")
            try:
                soup = BeautifulSoup(response.text, "html.parser")
                status = soup.find("status").text
                message = soup.find("message").text
                logger.info(f"status : [{status}], message : {message}")
            except Exception as ex:
                traceback.print_exc()
                logger.error(ex)
            return None
        else:
            return response.content

    def disable_key(self, key):
        self.keys.disable_key(key)


class DartKey:
    def __init__(self, key: str, disabled=False, disabledAt=None):
        self.key = key
        self.disabled = disabled
        self.disabledAt = disabledAt

    def __str__(self):
        return f"key : {self.key}, disabled : {self.disabled}, at : {self.disabledAt}"


class DartKeys:
    def __init__(self, keys: List):
        self.current = 0
        self.keys = list(map(lambda key: DartKey(key), keys))
        logger.info(f"keys {self}")

    def next_key(self):
        available_keys = list(filter(lambda x : not x.disabled, self.keys))
        logger.debug(f"available keys : {(','.join([str(elem) for elem in available_keys]))}")

        if self.current >= len(available_keys) - 1:
            self.current = 0

        key = available_keys[self.current].key
        self.current = self.current + 1
        return key

    def disable_key(self, keycode):
        for dartkey in self.keys:
            if dartkey.key == keycode:
                dartkey.disabled = True
                dartkey.disabledAt = datetime.now()
                logger.info(f"dart key {keycode} DISABLED")

    def __str__(self):
        return "\n".join(list(map(lambda key: f"{key}", self.keys)))