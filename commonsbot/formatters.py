from commonsbot.i18n import I18n
from abc import abstractmethod


class Formatter(object):
    def __init__(self, deletion_type, i18n):
        """
        @type deletion_type: str
        @type i18n: commonsbot.i18n.I18n
        """
        self.deletion_type = deletion_type
        self.i18n = i18n

    def format(self, files):
        if len(files) == 0:
            raise ValueError('Attempt to format a message about 0 files')
        params = (self.format_heading(files), self.format_body(files))
        return '\n\n== %s ==\n%s ~~~~\n' % params

    def format_summary(self):
        return self.msg('summary')

    def format_heading(self, files):
        return self.msg('header', len(files))

    @abstractmethod
    def format_body(self, files):
        pass

    def msg(self, key, params=()):
        key = self.deletion_type + '-' + key
        return self.i18n.msg(key, params)

class DiscussionFormatter(Formatter):
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
            result += '* '
            filename ='commons:File:{0}|{0}'.format(file.file_name)
            if same_pages:
                result += '[[%s]]' % filename
            else:
                params = (filename, 'commons:' + file.discussion_page)
                result += self.msg('line', params)
            result += '\n'

        if same_pages:
            result += self.msg('body-end-matching', 'commons:' + files[0].discussion_page)
        else:
            result += self.msg('body-end-mismatching', len(files))

        return result


class SpeedyFormatter(Formatter):
    def __init__(self, i18n):
        """
        @type i18n: commonsbot.i18n.I18n
        """
        Formatter.__init__(self, 'speedy', i18n)

    def format_body(self, files):
        result = self.msg('body-start', len(files)) + '\n'

        for file in files:
            result += '* [[commons:File:{0}|{0}]]\n'.format(file.file_name)

        result += self.msg('body-end', len(files))

        return result