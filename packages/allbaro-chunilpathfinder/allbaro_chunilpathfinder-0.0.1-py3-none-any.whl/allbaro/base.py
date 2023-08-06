import csv
import datetime
import json
import math
from dateutil.relativedelta import relativedelta
import xmltodict
import requests
from bs4 import BeautifulSoup
import pytz

from allbaro.errors import AlreadyAuthenticationError, AllbaroResponseError, LoginFailedError, AllbaroError, \
    UnauthenticatedError, ParsingError
from allbaro.helpers import generate_header, handover_process_list_keys


class Allbaro(object):
    base_url = 'https://www.allbaro.or.kr/index.jsp'
    login_url = 'https://www.allbaro.or.kr/main.login.do'
    system_intro_url = 'https://www.allbaro.or.kr/login.intro.do'
    handover_process_list_url = 'https://www.allbaro.or.kr/man/man100.searchManfProcessByEntn.do'
    handover_process_search_url = 'https://www.allbaro.or.kr/man/man100.XML.searchManfProcessByEntn.do?exec'

    def __init__(self):
        self.session = requests.session()
        self.username = None
        self.password = None
        self.is_authenticated = False
        self.manager_name = None
        self.entn_name = None
        self.headers = generate_header(self.system_intro_url)
        self.entn = None
        self.emis_chrg = None


    def __now(self):
        KST = pytz.timezone('Asia/Seoul')
        return datetime.datetime.now(tz=KST)

    def __temp_save(self, contents):
        # 디버깅 용으로 Html 파일 저장하는 메서드
        with open(f"{datetime.datetime.now().__str__()}.html", 'w') as file:
            file.write(contents.decode())

    def __find_text(self, soup_instance, selector, target):
        # bs 객체 안에서 지정한 Selector의 텍스트를 찾는 메서드
        element = soup_instance.select_one(selector)
        if element is None:
            raise ParsingError([target])
        return element.text.strip()

    def __set_header(self, referer):
        self.headers['Referer'] = referer

    def get_login_info(self):
        if self.is_authenticated is False:
            raise UnauthenticatedError()
        response = self.session.get(self.system_intro_url, headers=self.headers)
        if response.status_code != 200:
            raise AllbaroResponseError()
        soup = BeautifulSoup(response.content, 'html.parser')
        manager_name_selector = 'nav > div.abr-nav-content.abr-nav-cnt1 > strong'
        self.manager_name = self.__find_text(soup, manager_name_selector, '담당자명')
        # 세부 정보
        base_response = self.session.get(self.handover_process_list_url, headers=self.headers)
        if base_response.status_code != 200:
            raise AllbaroResponseError()
        soup = BeautifulSoup(base_response.content, 'html.parser')
        # 로그인 업체번호
        entn_input = soup.find('input', {'name': 'entn'})
        if entn_input is None:
            raise ParsingError(['entn 값'])
        self.entn = entn_input.attrs.get('value').strip()
        # 로그인 업체명
        entn_name_input = soup.find('input', {'name': 'entn_name'})
        if entn_name_input is None:
            raise ParsingError(['entn_name 값'])
        self.entn_name = entn_name_input.attrs.get('value').strip()
        # 배출자 번호라는데... 일단 모르겠음
        # emis_chrg_input = soup.find('input', {'name': 'emis_chrg'})
        # if emis_chrg_input is None:
        #     raise ParsingError(['emis_chrg 값'])
        # self.emis_chrg = emis_chrg_input.attrs.get('value').strip()
        # print(self.emis_chrg)

    def authenticate(self, username, password):
        if self.is_authenticated is True:
            raise AlreadyAuthenticationError()
        try:
            base_response = self.session.get(self.base_url)
            if base_response.status_code != 200:
                raise AllbaroResponseError()
            self.username = username
            self.password = password
            login_data = {
                'signed_data': '',
                'exec': 'Y',
                'goURL': 'M',
                'usid': self.username,
                'uspw': self.password
            }
            self.__set_header('https://www.allbaro.or.kr/main.login.do')
            login_response = self.session.post(
                'https://www.allbaro.or.kr/main.login.do', headers=self.headers, data=login_data
            )
            if login_response.status_code != 200:
                raise AllbaroResponseError()
            cookie_dict = login_response.cookies.get_dict()
            # 로그인 응답의 status code는 성공 여부와 관계 없이 200으로 떨어진다.
            # 따라서 쿠키 값을 보고 로그인 성공 여부를 판단해야한다.
            if cookie_dict.get('XTLID', None) != self.username:
                raise LoginFailedError()
            self.password = None
            self.is_authenticated = True
            self.get_login_info()
        except Exception as e:
            self.username = None
            self.password = None
            raise e

    def __handover_process_list(self, data):
        query = "&".join([f"{key}={value}" for key, value in data.items()]).encode()
        response = self.session.post(
            self.handover_process_search_url, headers=self.headers, data=query
        )
        parsed_response = xmltodict.parse(response.text)
        response_data = parsed_response.get('SHEET').get('DATA')
        if response_data is None:
            # 기간 내 데이터 없음
            return 0, []
        # 첫번째 페이지에 대한 응답에서만 total_count가 온다.
        # 그 외의 경우엔 빈 스트링이 반환되므로 1페이지 응답과, 2페이지가 아닌 응답을 구분해서 처리해야한다.
        _total_count_string = response_data.get('@TOTAL', '')
        total_count = None if _total_count_string == '' else int(_total_count_string)
        tr = response_data.get('TR')
        if isinstance(tr, list):
            rows = [row.get('TD') for row in tr]
        else:
            print(tr)
            rows = [tr.get('TD')]
        return total_count, rows


    def handover_process_list(self, start_date: datetime.date, end_date: datetime.date):
        # 인계서진행상황확인 - 인계서진행상황
        if self.is_authenticated is False:
            raise UnauthenticatedError()
        self.__set_header(self.handover_process_list_url)
        now = self.__now()
        end_date = end_date if end_date <= now.date() else now.date()
        result_list = []
        partial_start_date = start_date
        while True:
            page = 1
            one_page_rows = 500
            max_page = 1
            total_count = None
            _partial_end_date = partial_start_date + relativedelta(days=30)
            partial_end_date = min(end_date, _partial_end_date)
            while True:
                # pageNo 은 결과와 무관하다.(추측)
                data = {
                    'entn': self.entn, 'entn_name': self.entn_name, 'S_CONTROLLER': '', 'S_METHOD': 'search',
                    'S_SAVENAME': '', 'S_FORWARD': '', 'S_TREECOL': '', 'cls_yn': '', 'agency_yn': '', 'agency_entn': '',
                    'agency_firm_name': '', 'err': '', 'myPage': '',
                    'start_date': partial_start_date.strftime("%Y/%m/%d"),
                    'end_date': partial_end_date.strftime("%Y/%m/%d"),
                    'search_agency_yn': '', 'wste_name_1': '', 'wste_code_1': '', 'manf_type_1': '1', 'rfid_yn_1': '',
                    'manf_nums_1': '', 'emis_firm_name': self.entn_name, 'emis_chrg': self.entn, 'tran_firm_name': '',
                    'tran_chrg': '', 'trtm_firm_name': '', 'trtm_chrg': '', 'emis_vehc_nums_1': '', 'tran_vehc_nums_1': '',
                    'trtm_vehc_nums_1': '', 'ibTabTop1': '', 'tmpinput1': '', 'editpage1': '', 'ibTabBottom1': '',
                    'ibTabTop2': '', 'editpage2': '', 'ibTabBottom2': '', 'ibTabTop3': '', 'editpage3': '', 'ibTabBottom3': '',
                    'pageNum': str(page), 'pageNo': 1, 'onePageRows': str(one_page_rows)
                }
                _total_count, rows = self.__handover_process_list(data)
                if page == 1:
                    # __handover_process_list 주석 참고
                    total_count = _total_count
                    max_page = math.ceil(total_count/one_page_rows)
                if total_count == 0:
                    break
                result_list += rows
                if max_page == page:
                    break
                else:
                    page += 1
            if partial_end_date == end_date:
                break
            else:
                partial_start_date = partial_end_date + relativedelta(days=1)
        return [dict(zip(handover_process_list_keys, result)) for result in result_list]

