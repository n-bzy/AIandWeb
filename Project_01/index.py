# %%
import re
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, OrGroup


def create_index(index_dir: str):
    schema = Schema(url=ID(stored=True),
                    title=TEXT(stored=True),
                    content=TEXT(stored=True))

    # Create an index in the directory indexdir
    # (the directory must already exist!)
    _ = create_in(index_dir, schema)


def add_content(index_dir: str, url, content):
    ix = open_dir(index_dir)

    # TODO: For x in content: add ...
    # for content in contents:
    with ix.searcher() as searcher:
        query = QueryParser("url", ix.schema).parse(url)
        results = searcher.search(query)
        # Loop over the stored fields in the index
        if not results:
            writer = ix.writer()
            writer.add_document(url=url,
                                title=content[0],
                                content=content[1])
            # write the index to the disk
            writer.commit()


# Add limit?
def retrieve_content(index_dir: str, term):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        # find entries with the words 'first' AND 'last'
        term = re.sub(r"[^a-zA-Z0-9]+", ' ', term)
        query = QueryParser("content", schema=ix.schema, group=OrGroup
                            ).parse(term)
        results = searcher.search(query)
        corrected = searcher.correct_query(query, term)
        if corrected.query != query:
            # print("Did you mean:", corrected.string)
            corr = corrected.string
        else:
            corr = None
        # the search objects gets closed after the scope so you have to
        # transfer the content beforehand
        result_content = []

        # print all results
        for hit in results:
            highlight = hit.highlights("content")
            # creates a dictionary just like the search object
            # with title and url
            result_content.append({'title': hit['title'],
                                   'url': hit['url'],
                                   'text': highlight})

        return result_content, corr


# %%
if __name__ == "__main__":
    create_index("indexdir")

# %%
