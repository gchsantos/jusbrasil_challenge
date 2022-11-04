from typing import Tuple, Union

import requests
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger

from .exceptions import BaseCaptureException, CreateSessionFailedException
from zordon.constants import LINE_STATUS
import robots.core.constants as robots_constants
from .dataclasses import RefinedLawsuitData

logger = get_task_logger(__name__)


class EsajCaptureRobot:
    def __init__(self, url, search_url: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.url = url
        self.search_url = search_url

    def capture_pipeline(self, cnj: str):
        try:
            session = self.get_session()
            headers = self.generate_header(session)
            search_response = self.search_lawsuit_by_cnj(cnj, headers)
            return self.scrape_lawsuit_data(search_response)

        except CreateSessionFailedException:
            raise
        except Exception as e:
            raise BaseCaptureException(e)

    def append_search_url(self, cnj):
        return f"{self.search_url}{cnj}"

    def get_session(self) -> str:
        try:
            response = requests.get(self.url)
            response.raise_for_status()

            for cookie in response.cookies:
                if "sessionid" in cookie.name.lower():
                    return cookie.value
        except Exception as e:
            raise CreateSessionFailedException(e)

    def generate_header(self, session: str) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Cookie": f"JSESSIONID={session}",
        }

    def search_lawsuit_by_cnj(self, cnj: str, headers: dict) -> requests.Response:
        search_url = self.append_search_url(cnj)
        response = requests.get(search_url, headers)
        return response

    def scrape_lawsuit_data(
        self, search_response: requests.Response
    ) -> Tuple[LINE_STATUS, Union[RefinedLawsuitData, None]]:
        soup = BeautifulSoup(search_response.text, features="html.parser")
        return_message = soup.find(id="mensagemRetorno")
        if (
            return_message
            and return_message.get_text(strip=True)
            in robots_constants.NOT_FOUND_MESSAGES
        ):
            return LINE_STATUS.NOT_FOUND, None

        refined_lawsuit = RefinedLawsuitData(
            value=soup.find(id="valorAcaoProcesso"),
            lawsuit_class=soup.find(id="classeProcesso"),
            subject=soup.find(id="assuntoProcesso"),
            distribution=soup.find(id="dataHoraDistribuicaoProcesso"),
            judge=soup.find(id="juizProcesso"),
            concerned_parties_table=soup.find(id="tableTodasPartes"),
            progress_table=soup.find(id="tabelaTodasMovimentacoes"),
        )

        return LINE_STATUS.SUCCESS, refined_lawsuit
