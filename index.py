# %%
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser


def create_index(index_dir: str):
    # TODO: Add URL and freq
    schema = Schema(url=ID(stored=True), title=TEXT(stored=True), content=TEXT)

    # Create an index in the directory indexdir
    # (the directory must already exist!)
    _ = create_in(index_dir, schema)


def add_content(index_dir: str, url, content):
    ix = open_dir(index_dir)
    writer = ix.writer()

    # TODO: For x in content: add ...
    # for content in contents:
    writer.add_document(url=url,
                        title=content[0],
                        content=content[1])

    # write the index to the disk
    writer.commit()


def retrieve_content(index_dir: str, term):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        # find entries with the words 'first' AND 'last'
        query = QueryParser("content", ix.schema).parse(term)
        results = searcher.search(query)

        # print all results
        for r in results:
            print(r)


# %%
if __name__ == "__main__":
    create_index("indexdir")

# %%
