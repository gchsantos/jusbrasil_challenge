import re
from typing import Union, List

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from bs4 import Tag, NavigableString

value_pattern = re.compile(r"R?\$?\W*([\d, \W]+)")
part_lawyer_pattern = re.compile(r"adv\w*:", re.IGNORECASE)


@dataclass_json
@dataclass
class LawsuitProgress:
    date: str
    description: str


@dataclass_json
@dataclass
class LawsuitConcernedParts:
    participation: str
    person: str
    lawyers: List[str]


@dataclass_json
@dataclass
class RefinedLawsuitData:
    value: Union[Tag, NavigableString, None] = ""
    lawsuit_class: Union[Tag, NavigableString, None] = ""
    subject: Union[Tag, NavigableString, None] = ""
    distribution: Union[Tag, NavigableString, None] = ""
    area: Union[Tag, NavigableString, None] = ""
    judge: Union[Tag, NavigableString, None] = ""
    concerned_parties_table: Union[Tag, NavigableString, None] = ""
    progress_table: Union[Tag, NavigableString, None] = ""

    def __init__(
        self,
        value,
        lawsuit_class,
        subject,
        distribution,
        area,
        judge,
        concerned_parties_table,
        progress_table,
    ):
        refine = lambda text, pattern: re.match(pattern, text)

        self.value = refine(self.get_bs_text(value), value_pattern)
        self.value = self.value.group(1) if self.value else ""
        self.lawsuit_class = self.get_bs_text(lawsuit_class)
        self.subject = self.get_bs_text(subject)
        self.distribution = self.get_bs_text(distribution)
        self.area = self.get_bs_text(area)
        self.judge = self.get_bs_text(judge)
        self.concerned_parties_table: List[
            LawsuitConcernedParts
        ] = self.get_concerned_parties(concerned_parties_table)
        self.progress_table: List[LawsuitProgress] = self.get_progress(progress_table)

    def get_concerned_parties(self, concerned_parties_table):
        concerned_parties = []
        if concerned_parties_table:
            for row in concerned_parties_table.findAll("tr"):
                participation = row.find("span", {"class": "tipoDeParticipacao"})
                participation = (
                    participation.get_text(strip=True) if participation else ""
                )

                part_and_lawyer = row.find("td", {"class": "nomeParteEAdvogado"})
                if part_and_lawyer:
                    splitted_parts = re.split(
                        part_lawyer_pattern, part_and_lawyer.get_text(strip=True)
                    )

                    if splitted_parts:
                        concerned_parties.append(
                            LawsuitConcernedParts(
                                participation=participation,
                                person=splitted_parts.pop(0),
                                lawyers=splitted_parts if splitted_parts else [],
                            )
                        )
                    else:
                        concerned_parties.append(
                            LawsuitConcernedParts(
                                participation=participation,
                                person=part_and_lawyer.get_text(strip=True),
                                lawyers="",
                            )
                        )
        return concerned_parties

    def get_progress(self, progress_table) -> List[LawsuitProgress]:
        progress = []
        if progress_table:
            rows = progress_table.findAll(
                "tr", {"class": ["containerMovimentacao", "movimentacaoProcesso"]}
            )
            for row in rows:
                progress_date = row.find(
                    "td", {"class": ["dataMovimentacao", "dataMovimentacaoProcesso"]}
                )
                progress_date = (
                    progress_date.get_text(strip=True) if progress_date else ""
                )
                progress_description = row.find(
                    "td",
                    {
                        "class": [
                            "descricaoMovimentacao",
                            "descricaoMovimentacaoProcesso",
                        ]
                    },
                )
                progress_description = (
                    progress_description.get_text(strip=True)
                    if progress_description
                    else ""
                )

                progress.append(
                    LawsuitProgress(
                        progress_date,
                        progress_description.replace("\r", " ").replace("\n", ""),
                    ),
                )

        return progress

    def get_bs_text(self, bs_element: Union[Tag, NavigableString, None], default=""):
        return bs_element.get_text(strip=True) if bs_element else default
