import httpx

from ..wiki import Entry, EntryInfoBase, WikiBase
from lxml import etree
from urllib.parse import quote

_client = httpx.AsyncClient()


class BaiduWiki(WikiBase):
    _base_url = "https://baike.baidu.com"
    _entry_url = _base_url + "/item/{}"

    async def get_entries(self, name: str) -> list[EntryInfoBase]:
        url = BaiduWiki._entry_url.format(quote(name))
        response = await _client.get(url)
        content = etree.HTML(response.text, etree.HTMLParser())

        # Whether request was successful.
        if content.xpath('/html/body/div[@id="bd"]/div[@class="errorBox"]'):
            return list[EntryInfoBase]()

        # Get other polysemies.
        others = content.xpath(
            '//ul[@class="polysemantList-wrapper cmn-clearfix"]/li'
        )

        # When the page contains main content.
        # (e.g. https://baike.baidu.com/item/%E8%8D%89/1717)
        if others:
            entries = list[EntryInfoBase]()

            for child in others:
                span = child.xpath('./span/text()')
                if span:
                    entries.append(BaiduEntryInfo(name, span[0], url))
                    continue

                entries.append(
                    BaiduEntryInfo(
                        name,
                        child.xpath('./a/text()')[0],
                        BaiduWiki._base_url + child.xpath('./a/@href')[0],
                    )
                )

            return entries

        # When the page does not contain main content.
        # (e.g. https://baike.baidu.com/item/scp-166)
        if content.xpath('//div[@class="lemmaWgt-subLemmaListTitle"]'):
            entries = list[EntryInfoBase]()

            # Get polysemies.
            entry_elements = content.xpath(
                '//ul[@class="custom_dot  para-list list-paddingleft-1"]'
                '/li/div/a'
            )

            for child in entry_elements:
                entries.append(
                    BaiduEntryInfo(
                        name,
                        child.xpath('./text()')[0].split('：')[-1],
                        BaiduWiki._base_url + child.xpath('./@href')[0]
                    )
                )

            return entries

        return [BaiduEntryInfo(name, "", url)]


class BaiduEntryInfo(EntryInfoBase):
    async def get_content(self) -> Entry:
        # Remove the sup elements
        # (the elements like [1] [2] which are used to reference).
        def remove_sup(parent: etree._Element) -> etree._Element:
            for child in parent.xpath('.//sup'):
                child.getparent().remove(child)
            return parent

        # Remove the toggle element shown when value of basic info is too long.
        def remove_toggle(parent: etree._Element) -> etree._Element:
            parent.remove(parent.xpath('./a[@class="toggle toCollapse"]')[0])
            return parent

        response = await _client.get(self.link)
        content = etree.HTML(response.text, etree.HTMLParser())

        paragraphs = [
            # Get texts in elements and delete excessive blank lines.
            " " * 4 + "".join(paragraph.xpath('.//text()'))
            .replace("\n", "")
            .strip()
            for paragraph in
            # Get summary paragraph elements and remove sup.
            remove_sup(content.xpath('//div[@class="lemma-summary"]')[0])
            .xpath('./div')
        ]  # Get summary paragraphs

        # Generate dict from key list and value list
        basic_infos = dict(map(
            lambda key, value: [key, value],
            [
                "".join(
                    # Remove sup and then get texts in elements.
                    remove_sup(key).xpath('.//text()')
                )
                .strip()
                # Remove excessive white spaces.
                .replace('\xa0', '')
                for key in
                # Get key elements
                content.xpath(
                    '//div[@class="basic-info J-basic-info cmn-clearfix"]'
                    '/dl/dt'
                )
            ],
            [
                "".join(
                    # Remove sup.
                    remove_sup(
                        # Get full value element and remove toggle.
                        remove_toggle(
                            value.xpath(
                                './/dd[@class="basicInfo-item value"]'
                            )[0]
                        )
                        # Get full value element if contains overlap.
                        if value.xpath('./div[@class="basicInfo-overlap"]')
                        # Otherwise, use value element.
                        else value
                    ).xpath('.//text()')  # Get texts in elements.
                )
                .strip()
                # Remove excessive white spaces.
                .replace('\xa0', '')
                # Remove excessive blank lines.
                .replace("\n", " ")
                for value in
                # Get value elements
                content.xpath(
                    '//div[@class="basic-info J-basic-info cmn-clearfix"]'
                    '/dl/dd'
                )
            ]
        ))

        return Entry(self.name, basic_infos, "\n".join(paragraphs))
