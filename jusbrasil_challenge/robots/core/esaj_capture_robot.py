from typing import Tuple, Union, List, Dict

import requests
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger

from .exceptions import BaseCaptureException, CreateSessionFailedException
from zordon.constants import LINE_STATUS
import robots.core.constants as robots_constants
from .dataclasses import RefinedLawsuitData

logger = get_task_logger(__name__)


class EsajCaptureRobot:
    def __init__(self, instances_urls: list, **kwargs) -> None:
        super().__init__(**kwargs)
        self.instances_urls = instances_urls

    def capture_pipeline(self, cnj: str) -> Tuple[LINE_STATUS, List[Dict]]:
        lawsuit_datas = []
        try:
            search_responses = []
            for instance in self.instances_urls:
                if instance["instance"] == 1:
                    session = self.get_first_instance_session(instance["url"])
                    headers = self.generate_header(session)

                    show_url = f"{instance['show_url']}{cnj}"
                    search_responses.append(
                        (
                            instance["instance"],
                            self.get_lawsuit_by_show_url(show_url, headers),
                        )
                    )

                elif instance["instance"] == 2:
                    url = f"{instance['url']}{cnj}"
                    session, codes = self.get_second_instance_session_and_codes(url)
                    headers = self.generate_header(session)

                    for code in codes:
                        show_url = f"{instance['show_url']}{code}"
                        search_response = self.get_lawsuit_by_show_url(
                            show_url, headers
                        )
                        search_responses.append(
                            (
                                instance["instance"],
                                self.get_lawsuit_by_show_url(show_url, headers),
                            )
                        )

            for instance, search_response in search_responses:
                status, capture_response = self.scrape_lawsuit_data(search_response)
                if status == LINE_STATUS.SUCCESS:
                    lawsuit_datas.append(
                        {
                            "instance": instance,
                            "capture_response": capture_response,
                        }
                    )

            return (
                LINE_STATUS.SUCCESS if lawsuit_datas else LINE_STATUS.NOT_FOUND,
                lawsuit_datas,
            )

        except CreateSessionFailedException:
            raise
        except Exception as e:
            raise BaseCaptureException(e)

    def get_first_instance_session(self, url) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()

            for cookie in response.cookies:
                if "sessionid" in cookie.name.lower():
                    return cookie.value
            raise Exception("Failed to capture session_id")
        except Exception as e:
            raise CreateSessionFailedException(e)

    def generate_header(self, session: str) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Cookie": f"JSESSIONID={session}",
        }

    def get_lawsuit_by_show_url(
        self, show_url: str, headers: dict
    ) -> requests.Response:
        response = requests.get(show_url, headers)
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

        judge = soup.find(id="juizProcesso")

        refined_lawsuit = RefinedLawsuitData(
            value=soup.find(id="valorAcaoProcesso"),
            lawsuit_class=soup.find(id="classeProcesso"),
            subject=soup.find(id="assuntoProcesso"),
            distribution=soup.find(id="dataHoraDistribuicaoProcesso"),
            judge=judge if judge else soup.find(id="orgaoJulgadorProcesso"),
            area=soup.find(id="areaProcesso"),
            concerned_parties_table=soup.find(id="tableTodasPartes"),
            progress_table=soup.find(id="tabelaTodasMovimentacoes"),
        )

        return LINE_STATUS.SUCCESS, refined_lawsuit

    def get_second_instance_session_and_codes(
        self, url
    ) -> Union[Tuple[str, list], bool]:
        try:
            response = requests.get(url)
            response.raise_for_status()

            session = None
            for cookie in response.cookies:
                if "sessionid" in cookie.name.lower():
                    session = cookie.value

            if not session:
                raise Exception("Failed to capture session_id")

            codes = []
            soup = BeautifulSoup(response.text, features="html.parser")
            for code in soup.find_all(id="processoSelecionado"):
                codes.append(code.get("value"))

            return session, codes
        except Exception as e:
            raise CreateSessionFailedException(e)
