import mwparserfromhell


class PerWikiMapper(object):
    def __init__(self, pages_per_file_per_wiki):
        self.wikis = {}
        self.pages_per_file_per_wiki = pages_per_file_per_wiki

    def add(self, file, page):
        """
        @type page: pywikibot.Page
        @type file: str
        """
        wiki = page.site.dbName()
        if wiki not in self.wikis:
            self.wikis[wiki] = {}
        files = self.wikis[wiki]
        if file not in files:
            files[file] = []
        if len(files[file]) < self.pages_per_file_per_wiki:
            files[file].append(page)


    def files_per_page(self):
        for files in self.wikis.values():
            page_mapping = {}
            result = {}
            for file, pages in files.items():
                for page in pages:
                    title = page.title()
                    page_mapping[title] = page
                    if title not in result:
                        result[title] = []
                    result[title].append(file)

            for title in sorted(iter(result)):
                yield page_mapping[title], result[title]


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
