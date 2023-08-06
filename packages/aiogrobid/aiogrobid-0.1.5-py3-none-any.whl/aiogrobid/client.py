from aiobaseclient import BaseClient
from lxml import etree

from .exceptions import BadRequestError


class GrobidClient(BaseClient):
    def __init__(self, base_url):
        super().__init__(base_url=base_url)

    def _get_text_for_one(self, root, name):
        r = root.find(name)
        return self._get_text(r)

    def _get_text(self, node):
        result = ''
        if node is not None:
            if node.text:
                result = node.text.strip()
            for child in node:
                if child is not None and child.tail is not None and child.tail.strip():
                    result += ' ' + child.tail.strip()
        return result

    def _extract(self, node):
        result = ''
        for possibly_div in node.getchildren():
            if possibly_div.tag == '{http://www.tei-c.org/ns/1.0}div':
                for child in possibly_div.getchildren():
                    if child.tag == '{http://www.tei-c.org/ns/1.0}head':
                        result += ('\n\n' + self._get_text(child) + '\n')
                    if child.tag == '{http://www.tei-c.org/ns/1.0}p':
                        result += self._get_text(child)
        return result.strip()

    def _extract_references(self, node):
        bibliography = node.find('.//{http://www.tei-c.org/ns/1.0}listBibl')
        references = []
        for bibl_struct in bibliography:
            analytic = bibl_struct.find('.//{http://www.tei-c.org/ns/1.0}analytic')
            idno = analytic.find(".//{http://www.tei-c.org/ns/1.0}idno[@type='DOI']")
            if idno:
                references.append(idno.text.lower().strip())
        return references

    def _exract_authors(self, node):
        node = node.find(".//{http://www.tei-c.org/ns/1.0}sourceDesc")
        authors = []
        for author in node.findall('.//{http://www.tei-c.org/ns/1.0}author'):
            pers_name = author.find('.//{http://www.tei-c.org/ns/1.0}persName')
            if pers_name:
                surname = pers_name.find('.//{http://www.tei-c.org/ns/1.0}surname')
                forename = pers_name.find('.//{http://www.tei-c.org/ns/1.0}forename')
                name = None
                if surname is not None and forename is not None:
                    name = f"{surname.text.strip()}, {forename.text.strip()}"
                else:
                    if surname:
                        name = surname.text.strip()
                    if forename:
                        name = forename.text.strip()
                if name:
                    authors.append(name)
        return authors

    async def process_fulltext_document(self, pdf_file):
        return await self.post(
            '/api/processFulltextDocument',
            data={
                'input': pdf_file,
            },
        )

    async def response_processor(self, response):
        content = await response.read()
        if response.status != 200:
            raise BadRequestError(status=response.status)
        try:
            root = etree.XML(content)
        except etree.XMLSyntaxError as e:
            raise BadRequestError(nested_error=e)
        return {
            'authors': self._exract_authors(root),
            'doi': self._get_text_for_one(root, ".//{http://www.tei-c.org/ns/1.0}idno[@type='DOI']"),
            'title': self._get_text_for_one(root, ".//{http://www.tei-c.org/ns/1.0}title[@level='a'][@type='main']"),
            'abstract': self._extract(root.find(".//{http://www.tei-c.org/ns/1.0}abstract")),
            'body': self._extract(root.find(".//{http://www.tei-c.org/ns/1.0}body")),
            'references': self._extract_references(root)
        }
