import re
import urllib3
from typing import Tuple, Union, List, Dict
from urllib3 import HTTPResponse
from urllib3.util.ssl_ import create_urllib3_context

from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger

from .exceptions import BaseCaptureException, CreateSessionFailedException
from zordon.constants import LINE_STATUS
import robots.core.constants as robots_constants
from .dataclasses import RefinedLawsuitData

logger = get_task_logger(__name__)

ctx = create_urllib3_context()
ctx.load_default_certs()
ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT


class EsajCaptureRobot:
    def __init__(self, instances_urls: list, **kwargs) -> None:
        super().__init__(**kwargs)
        self.instances_urls = instances_urls

    def pool_get(self, url, headers={}):
        with urllib3.PoolManager(ssl_context=ctx) as http:
            return http.request("GET", url, headers=headers)

    def capture_pipeline(self, cnj: str) -> Tuple[LINE_STATUS, List[Dict]]:
        lawsuit_datas = []
        try:
            search_responses = []
            for instance in self.instances_urls:
                if instance["instance"] == 1:
                    session = self.get_first_instance_session(instance["url"])
                    headers = self.generate_headers(session)

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
                    headers = self.generate_headers(session)

                    for code in codes:
                        show_url = f"{instance['show_url']}{code}"
                        search_response = self.get_lawsuit_by_show_url(
                            show_url, headers
                        )
                        search_responses.append(
                            (
                                instance["instance"],
                                search_response,
                            )
                        )

            for instance, search_response in search_responses:
                status, capture_response = self.scrape_lawsuit_data(
                    search_response.data.decode("utf-8")
                )
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
            response: HTTPResponse = self.pool_get(url)
            if response.status != 200:
                raise Exception("Fails during get session request")

            session_id = re.match(r"JSESSIONID=(.*);", response.getheader("Set-Cookie"))
            if session_id:
                return session_id.groups(1)

            raise Exception("Failed to capture session_id")
        except Exception as e:
            raise CreateSessionFailedException(e)

    def generate_headers(self, session: str) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Cookie": f"JSESSIONID={session}",
        }

    def get_lawsuit_by_show_url(self, show_url: str, headers: dict) -> HTTPResponse:
        response = self.pool_get(show_url, headers)
        return response

    def scrape_lawsuit_data(
        self, search_response: HTTPResponse
    ) -> Tuple[LINE_STATUS, Union[RefinedLawsuitData, None]]:
        soup = BeautifulSoup(search_response, features="html.parser")
        return_message = soup.find(id="mensagemRetorno")
        if (
            return_message
            and return_message.get_text(strip=True)
            in robots_constants.NOT_FOUND_MESSAGES
        ):
            return LINE_STATUS.NOT_FOUND, None

        judge = soup.find(id="juizProcesso")
        parties_table = soup.find(id="tableTodasPartes")
        progress_table = soup.find(id="tabelaTodasMovimentacoes")

        refined_lawsuit = RefinedLawsuitData(
            value=soup.find(id="valorAcaoProcesso"),
            lawsuit_class=soup.find(id="classeProcesso"),
            subject=soup.find(id="assuntoProcesso"),
            distribution=soup.find(id="dataHoraDistribuicaoProcesso"),
            judge=judge if judge else soup.find(id="orgaoJulgadorProcesso"),
            area=soup.find(id="areaProcesso"),
            concerned_parties_table=parties_table
            if parties_table
            else soup.find(id="tablePartesPrincipais"),
            progress_table=progress_table
            if progress_table
            else soup.find("tabelaUltimasMovimentacoes"),
        )

        return LINE_STATUS.SUCCESS, refined_lawsuit

    def get_second_instance_session_and_codes(
        self, url
    ) -> Union[Tuple[str, list], bool]:
        try:
            response: HTTPResponse = self.pool_get(url)
            if response.status != 200:
                raise Exception("Fails during get session request")

            session_id = re.match(r"JSESSIONID=(.*);", response.getheader("Set-Cookie"))

            if not session_id:
                raise Exception("Failed to capture session_id")

            codes = []
            soup = BeautifulSoup(response.data.decode("utf-8"), features="html.parser")
            for code in soup.find_all(id="processoSelecionado"):
                codes.append(code.get("value"))

            return session_id.groups(1), codes
        except Exception as e:
            raise CreateSessionFailedException(e)
