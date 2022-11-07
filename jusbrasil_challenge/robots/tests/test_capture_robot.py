from json import loads

from django.test import TestCase

from robots.core.esaj_capture_robot import EsajCaptureRobot
from robots.core.exceptions import CreateSessionFailedException
from zordon.constants import LINE_STATUS


class EsajCaptureRobotTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cnj = "0710802-55.2018.8.02.0001"
        cls.first_instance_url = {
            "instance": 1,
            "url": "https://www2.tjal.jus.br/cpopg/open.do",
            "show_url": "https://www2.tjal.jus.br/cpopg/show.do?processo.numero=",
        }
        cls.second_instance_url = {
            "instance": 2,
            "url": "https://www2.tjal.jus.br/cposg5/search.do?cbPesquisa=NUMPROC&tipoNuProcesso=UNIFICADO&dePesquisaNuUnificado=",
            "show_url": "https://www2.tjal.jus.br/cposg5/show.do?processo.codigo=",
        }

        cls.esaj_capture = EsajCaptureRobot([])
        cls.response = ""

    def setUp(self):
        ...

    def test_get_first_instance_session(self):
        """
        When execute get first instance session function \
        Then returns session code sucessfuly \
        """

        session = self.esaj_capture.get_first_instance_session(
            self.first_instance_url["url"]
        )

        self.assertTrue(session)

    def test_get_first_instance_session_failed(self):
        """
        When execute get first instance session function with wrong url \
        Then failed with CreateSessionFailedException \
        """
        wrong_url = "https://www4.tjmg.jus.br/juridico/sf/proc_nome.jsp"

        self.esaj_capture.get_first_instance_session(wrong_url)
        self.assertRaises(CreateSessionFailedException)

    def test_get_second_instance_session_and_codes(self):
        """
        When execute get second instance session function \
        Then returns session code sucessfuly \
        """

        session, codes = self.esaj_capture.get_second_instance_session_and_codes(
            self.second_instance_url["url"]
        )

        self.assertTrue(session)

    def test_get_second_instance_session_and_codes_failed(self):
        """
        When execute get first instance session function with wrong url \
        Then failed with CreateSessionFailedException \
        """
        wrong_url = "https://www4.tjmg.jus.br/juridico/sf/proc_nome.jsp"

        self.esaj_capture.get_second_instance_session_and_codes(wrong_url)
        self.assertRaises(CreateSessionFailedException)

    def test_generate_headers(self):
        """
        When execute generate headers function passing session parameter \
        Then returns headers information sucessfuly \
        """
        session = "DF723DE5B1AE38F0879CAEB2D2F5B156.cpopg6"
        headers = self.esaj_capture.generate_headers(session)

        self.assertIn("User-Agent", headers)
        self.assertIn("Cookie", headers)

    def test_scrape_lawsuit_data(self):
        """
        When execute scrape lawsuit function \
        Then capture, scrape and refine lawsuit's informations sucessfuly \
        """

        show_url = f"{self.first_instance_url['show_url']}{self.cnj}"
        expected_lawsuit_class = "Procedimento Comum Cível"
        expected_subject = "Dano Material"
        expected_distribution = "02/05/2018 às 19:01 - Sorteio"
        expected_area = "Cível"
        expected_judge = "José Cícero Alves da Silva"

        session = self.esaj_capture.get_first_instance_session(
            self.first_instance_url["url"]
        )
        headers = self.esaj_capture.generate_headers(session)
        search_response = self.esaj_capture.get_lawsuit_by_show_url(show_url, headers)
        status, lawsuit = self.esaj_capture.scrape_lawsuit_data(
            search_response.data.decode("utf-8")
        )

        self.assertEqual(LINE_STATUS.SUCCESS, status)
        self.assertEqual(expected_lawsuit_class, lawsuit.lawsuit_class)
        self.assertEqual(expected_subject, lawsuit.subject)
        self.assertEqual(expected_distribution, lawsuit.distribution)
        self.assertEqual(expected_area, lawsuit.area)
        self.assertEqual(expected_judge, lawsuit.judge)
        self.assertTrue(lawsuit.progress_table)
        self.assertTrue(lawsuit.concerned_parties_table)

    def test_scrape_lawsuit_data_not_found(self):
        """
        When execute scrape lawsuit function and lawsuit is not found \
        Then returns not found line status and not returns lawsuit \
        """

        wrong_cnj = "0005691-75.2019.8.06.0134"
        show_url = f"{self.first_instance_url['show_url']}{wrong_cnj}"

        session = self.esaj_capture.get_first_instance_session(
            self.first_instance_url["url"]
        )
        headers = self.esaj_capture.generate_headers(session)
        search_response = self.esaj_capture.get_lawsuit_by_show_url(show_url, headers)
        status, lawsuit = self.esaj_capture.scrape_lawsuit_data(
            search_response.data.decode("utf-8")
        )

        self.assertEqual(LINE_STATUS.NOT_FOUND, status)
        self.assertFalse(lawsuit)
