import fire
from aiokit.utils import sync_fu

from .client import GrobidClient


async def process(base_url, pdf_file):
    grobid_client = GrobidClient(base_url=base_url)
    await grobid_client.start()
    with open(pdf_file, 'rb') as f:
        return await grobid_client.process_fulltext_document(f.read())


def main():
    fire.Fire(sync_fu(process))


if __name__ == '__main__':
    main()
