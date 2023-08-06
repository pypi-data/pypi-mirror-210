from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

import pdfplumber
from loguru import logger
from pdfplumber.page import Page
from pdfplumber.pdf import PDF

from .src import (
    Decision,
    DecisionPage,
    Opinion,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
    PositionOpinion,
    get_end_page_pos,
    get_start_page_pos,
)


class DecisionMeta(NamedTuple):
    """Metadata required to create a [decision][decision-document].

    Field | Type | Description
    --:|:--:|:--
    `start_index` | int | The zero-based integer `x`, i.e. get specific `pdfplumber.pages[x]`
    `start_page_num` | int | The 1-based integer to describe human-readable page number
    `start_indicator` | [PositionDecisionCategoryWriter][decision-category-writer] or [PositionNotice][notice] | Marking the [start of content proper][start-of-content]
    `writer` | str | When [PositionDecisionCategoryWriter][decision-category-writer]  is selected, the writer found underneath the category
    `notice` | bool | Will be marked `True`, if [PositionNotice][notice] is selected; default is `False`.
    `pages` | list[[DecisionPage][decision-pages]] | A list of pages having material content
    """  # noqa: E501

    start_index: int
    start_page_num: int
    start_indicator: PositionDecisionCategoryWriter | PositionNotice
    end_page_num: int
    end_page_pos: float | int

    @classmethod
    def prep(cls, path: Path):
        if not (starter := get_start_page_pos(path)):
            raise Exception("Could not detect start of content.")

        index, start_indicator = starter
        if not start_indicator:
            raise Exception("Could not detect start indicator.")

        ender = get_end_page_pos(path)
        if not ender:
            raise Exception("Could not detect end of content.")
        end_page_num, end_page_pos = ender

        return cls(
            start_index=index,
            start_page_num=index + 1,
            start_indicator=start_indicator,
            end_page_num=end_page_num,
            end_page_pos=end_page_pos,
        )

    def init(self, pdf: PDF) -> Decision:
        """Add the metadata of a [Decision][decision-document] and extract the first
        page of the content proper which may not necessarily be page 1.

        Returns:
            Decision: A Decision instance, if all elements match.
        """
        logger.debug(f"Initialize {self=}")
        composition = PositionCourtComposition.from_pdf(pdf).element
        start_page = pdf.pages[self.start_index]
        if isinstance(self.start_indicator, PositionNotice):
            return Decision(
                composition=composition,
                notice=True,
                pages=[
                    DecisionPage.set(
                        page=start_page,
                        start_y=self.start_indicator.position_pct_height
                        * start_page.height,
                    )
                ],
            )
        elif isinstance(self.start_indicator, PositionDecisionCategoryWriter):
            return Decision(
                composition=composition,
                category=self.start_indicator.element,
                writer=self.start_indicator.writer,
                pages=[
                    DecisionPage.set(
                        page=start_page,
                        start_y=self.start_indicator.writer_pct_height
                        * start_page.height,
                    )
                ],
            )
        raise Exception("Unexpected initialization of decision.")

    def add(self, pages: list[Page]) -> Iterator[DecisionPage]:
        for nxt in pages:
            if nxt.page_number <= self.start_page_num:
                continue
            if nxt.page_number == self.end_page_num:
                logger.debug(f"Finalize {nxt.page_number=}.")
                if page_valid := DecisionPage.set(page=nxt, end_y=self.end_page_pos):
                    yield page_valid
                else:
                    logger.warning("Detected blank page.")
                break
            else:
                logger.debug(f"Initialize {nxt.page_number=}.")
                if page_valid := DecisionPage.set(page=nxt):
                    yield page_valid
                else:
                    logger.warning("Detected blank page.")


def construct(obj: Decision | Opinion):
    for page in obj.pages:
        obj.body += f"\n\n\n\n{page.body_text}"
        obj.segments.extend(page.segments)
        if page.annex_text:
            obj.annex += f"\n\n\n\n{page.annex_text}"
            obj.footnotes.extend(page.footnotes)
    return obj


def get_decision(path: Path) -> Decision:
    """From a _*.pdf_ file found in `path`, extract relevant [metadata][decisionmeta]
    to generate a [decision][decision-document] having [pages][decision-pages].
    Each of which will contain a body and, likely, an annex for footnotes.

    Examples:
        >>> from pathlib import Path
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> decision = get_decision(x)
        >>> decision.category
        <DecisionCategoryChoices.RESO: 'Resolution'>
        >>> decision.composition
        <CourtCompositionChoices.DIV2: 'Second Division'>
        >>> decision.writer
        'CARPIO. J.:'
        >>> len(decision.pages) # total page count
        5
        >>> isinstance(decision.pages[0], DecisionPage) # first page
        True
        >>> from corpus_unpdf.src import Footnote, Bodyline
        >>> isinstance(decision.segments[0], Bodyline)
        True
        >>> isinstance(decision.footnotes[0], Footnote)
        True
        >>> len(decision.footnotes) # TODO: limited number detected; should be 15
        7

    Args:
        path (Path): Path to the pdf file.

    Returns:
        Self: Instance of a Decision with pages populated
    """  # noqa: E501
    meta = DecisionMeta.prep(path)
    with pdfplumber.open(path) as pdf:
        # create all the pages of the decision
        caso = meta.init(pdf=pdf)
        content_pages = meta.add(pages=pdf.pages)
        caso.pages.extend(content_pages)
        # construct full decision
        obj = construct(caso)
        if isinstance(obj, Decision):
            return obj
        raise Exception("Bad construction of Decision.")


def get_opinion(path: Path) -> Opinion:
    """From a _*.pdf_ file found in `path`, extract relevant opinion metadata
    to generate an [opinion][opinion-document] having [pages][decision-pages].
    Each of which will contain a body and, likely, an annex for footnotes.

    Examples:
        >>> from pathlib import Path
        >>> x = Path().cwd() / "tests" / "data" / "opinion.pdf"
        >>> opinion = get_opinion(x)
        >>> opinion.writer
        'HERNANDO, J.:'
        >>> opinion.label
        'DISSENTING OPINION'
        >>> len(opinion.pages) # total page count
        28
        >>> isinstance(opinion.pages[0], DecisionPage) # first page
        True
        >>> from corpus_unpdf.src import Footnote, Bodyline
        >>> isinstance(opinion.segments[0], Bodyline)
        True
        >>> isinstance(opinion.footnotes[0], Footnote)
        True
        >>> len(opinion.footnotes)
        49

    Args:
        path (Path): Path to the pdf file.

    Returns:
        Self: Instance of an Opinion with pages populated
    """  # noqa: E501
    with pdfplumber.open(path) as pdf:
        meta = PositionOpinion.from_pdf(pdf)
        # initialize the opinion
        start_page = pdf.pages[0]
        start_y = meta.writer_pct_height * start_page.height
        opinion = Opinion(
            label=meta.label,
            writer=meta.writer,
            pages=[DecisionPage.set(page=start_page, start_y=start_y)],
        )
        # create all the pages of the opinion
        for page in pdf.pages[1:]:
            if page_valid := DecisionPage.set(page=page):
                opinion.pages.append(page_valid)
        # construct full opinion
        obj = construct(opinion)
        if isinstance(obj, Opinion):
            return obj
        raise Exception("Bad construction of Opinion.")
