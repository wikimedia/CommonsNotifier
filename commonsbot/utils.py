from datetime import datetime, timezone
from dateutil import parser
import re
import mwparserfromhell


"""
No more than this number of days between posts about the same file
"""
REPOST_DAYS = 180


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
                yield page_mapping[title], sorted(result[title])


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


def check_already_posted(text, filename, deletion_type, now=datetime.utcnow()):
    """
    @type text: str
    @type filename: str
    @type deletion_type: str
    """
    params = (re.escape(deletion_type), re.escape(filename))
    regexp = '<!-- COMMONSBOT: %s \\| (?P<date>\\S+) \\| %s -->' % params
    for match in re.finditer(regexp, text):
        try:
            date = parser.parse(match.group('date'))
            # Convert from TZ-aware datetime
            date = datetime.utcfromtimestamp(date.timestamp())
            diff = now - date
            if diff.days < REPOST_DAYS:
                return True
        except:
            # Did someone mess with the bot-readable string?
            # Better be safe than sorry and not post again
            return True
        pass

    return False
