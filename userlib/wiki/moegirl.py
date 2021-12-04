from dataclasses import dataclass
# import re

from mwclient.page import Page

from ..wiki import Entry, EntryInfoBase, WikiBase
from mwclient import Site
from opencc import OpenCC
from urllib.parse import quote


class MoegirlWiki(WikiBase):
    _scheme = "https"
    _host = "zh.moegirl.org.cn"
    _base_url = "%s://%s" % (_scheme, _host)
    _site = Site(_host, "/")

    async def get_entries(self, name: str) -> list[EntryInfoBase]:
        page = MoegirlWiki._site.pages[name]

        if page.exists:
            page = page.redirects_to() if page.redirect else page

            return [
                MoegirlEntryInfo(
                    page.base_name,
                    "",
                    MoegirlWiki._base_url + "/" + quote(page.base_name),
                    page
                )
            ]

        return list[EntryInfoBase]()


@dataclass
class MoegirlEntryInfo(EntryInfoBase):
    page: Page

    _opencc = OpenCC("t2s")

    _special_keys = [
        "image", "tag", "图片大小", "图片信息"
    ]

    _marks = {
        "<br>": "\n", "<br/>": "\n", "<br />": "\n",
        "<ref>": "（", "</ref>": "）",
        "'": "", "[[": "", "]]": ""
    }.items()

    _info_box_names = [
        "Comic Infobox", "人物信息"
    ]

    @staticmethod
    def _parse_text(text: str) -> str:
        for key, value in MoegirlEntryInfo._marks:
            text = text.replace(key, value)

        # text = re.sub(
        #     r"\{\{[\w\-]+\|(?P<value>[\w\s]*)\}\}",
        #     r"\g<value>",
        #     text
        # )

        return text

    async def get_content(self) -> Entry:
        content = MoegirlEntryInfo._opencc.convert(self.page.text(0))

        lines = [
            line.strip()
            for line in content.splitlines(False)
            if line and not line.isspace()
        ]

        start = -1

        for name in MoegirlEntryInfo._info_box_names:
            mark = "{{" + name
            if mark in lines:
                start = lines.index(mark)

        if start == -1:
            raise Exception("Get basic info failed.\nContent:\n" + content)

        end = lines.index("}}")

        info = "\n".join(lines[start + 1:end])
        summary = MoegirlEntryInfo._parse_text("\n".join(lines[end + 1:]))

        basic_infos = dict([
            pair
            for pair in
            [
                [
                    section.strip()
                    for section in
                    MoegirlEntryInfo._parse_text(line)[1:].split("=", 2)
                ]
                for line in info.splitlines(False)
                if line[0] == "|"
            ]
            if pair[0] not in MoegirlEntryInfo._special_keys and
            len(pair) == 2 and pair[1]
        ])

        return Entry(self.name, basic_infos, summary)
