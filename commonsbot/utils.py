import mwparserfromhell


class PerWikiCounter(object):
    def __init__(self, pages_per_file_per_wiki):
        self.wikis = {}
        self.pages_per_file_per_wiki = pages_per_file_per_wiki

    def next(self, wiki, page):
        if wiki not in self.wikis:
            self.wikis[wiki] = {}
        pages = self.wikis[wiki]
        if page not in pages:
            pages[page] = 0
        pages[page] += 1
        return pages[page] <= self.pages_per_file_per_wiki

def get_nomination_page(wikitext):
    code = mwparserfromhell.parse(wikitext)
    for template in code.filter_templates():
        if template.name.matches('Delete') \
            or template.name.matches('Test delete'):
                if template.has('subpage'):
                    subpage = str(template.get('subpage').value)
                    subpage = subpage.strip()
                    if subpage != '':
                        return subpage

    return None
