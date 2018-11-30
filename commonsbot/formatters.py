from datetime import datetime
from commonsbot.i18n import I18n
from abc import abstractmethod


def subst_plural(wikitext):
    """
    Substitutes {{PLURAL}} in wikitext

    @param wikitext: Wikitext to process
    @type wikitext: str
    @rtype: str
    """
    return wikitext.replace('{{PLURAL:', '{{subst:PLURAL:')


class Formatter(object):
    """
    Abstract base class for talk page message formatters
    """

    def __init__(self, deletion_type, i18n):
        """
        @param deletion_type: Deletion type
        @type deletion_type: str
        @param i18n: Localization provider
        @type i18n: commonsbot.i18n.I18n
        """
        self.deletion_type = deletion_type
        self.i18n = i18n
        self.time = datetime.utcnow()

    def format(self, files):
        """
        Formats a message for one talk page into wikitext

        @param files: A list of commonsbot.state.DeletionState objects to notify about
        @type files: list
        @rtype: str
        """
        if len(files) == 0:
            raise ValueError('Attempted to format a message about 0 files')
        params = (self.format_heading(files), self.format_body(files))
        return subst_plural('\n\n== %s ==\n%s —~~~~\n' % params)

    def format_summary(self):
        """
        Formats edit summary

        @rtype: str
        """
        return self.msg('summary')

    def format_heading(self, files):
        """
        Formats section heading for message

        @param files: A list of commonsbot.state.DeletionState objects to notify about
        @type files: list
        @rtype: str
        """
        return self.msg('header', len(files))

    @abstractmethod
    def format_body(self, files):
        """
        Formats message body

        @param files: A list of commonsbot.state.DeletionState objects to notify about
        @type files: list
        @rtype: str
        """
        pass

    def format_line(self, filename, discussion=None):
        """
        Formats one line listing a file nominated for deltion

        @param filename: Name of a file
        @type filename: str
        @param discussion: Title of deletion discussion page, if any
        @type discussion: str|None
        @rtype: str
        """
        result = '* '
        formatted = 'commons:File:{0}|{0}'.format(filename)
        if discussion is None:
            result += '[[%s]]' % formatted
        else:
            params = (formatted, 'commons:' + discussion)
            result += self.msg('line', params)
        ts = self.time.isoformat()
        result += '<!-- COMMONSBOT: %s | %s | %s -->\n' % (self.deletion_type, ts, filename)

        return result

    def msg(self, key, params=()):
        """
        Formats a localization message

        @param key: Message name
        @type key: str
        @param params: Optional message parameters
        @type params: tuple
        @rtype: str
        """
        key = 'commtech-commons-' + self.deletion_type + '-' + key
        return self.i18n.msg(key, params)


class DiscussionFormatter(Formatter):
    """
    Formats messages about discussion-based (non-speedy) deletion nominations
    """

    def __init__(self, i18n):
        """
        @type i18n: commonsbot.i18n.I18n
        """
        Formatter.__init__(self, 'discussion', i18n)

    def format_body(self, files):
        count = len(files)
        result = self.msg('body-start', count) + '\n'

        same_pages = True
        for file in files:
            same_pages = same_pages and file.discussion_page == files[0].discussion_page

        for file in files:
            result += self.format_line(file.file_name, None if same_pages else file.discussion_page)

        if same_pages:
            result += self.msg('body-end-matching', 'commons:' + files[0].discussion_page)
        else:
            result += self.msg('body-end-mismatching', len(files))

        return result


class PageTagFormatter(Formatter):
    """
    Base class for template-based deletion formatters
    """

    def format_body(self, files):
        result = self.msg('body-start', len(files)) + '\n'

        for file in files:
            result += self.format_line(file.file_name)

        result += self.msg('body-end', len(files))

        return result


class SpeedyFormatter(PageTagFormatter):
    """
    Formats messages about speedy deletion nominations
    """

    def __init__(self, i18n):
        """
        @type i18n: commonsbot.i18n.I18n
        """
        Formatter.__init__(self, 'speedy', i18n)


class NoPermissionFormatter(PageTagFormatter):
    """
    Formats messages about missing permissions
    """

    def __init__(self, i18n):
        """
        @type i18n: commonsbot.i18n.I18n
        """
        Formatter.__init__(self, 'nopermission', i18n)
