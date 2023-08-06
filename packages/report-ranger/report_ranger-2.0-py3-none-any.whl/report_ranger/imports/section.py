# from .mdread import markdown_from_directory, process_template
from report_ranger.utils import mdread
import logging
import traceback
import jinja2

from report_ranger.utils.jinja_helpers import log_jinja2_error

log = logging.getLogger(__name__)


def int_to_rn(num, uppercase=True):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    uppercase = ["M", "CM", "D", "CD", "C", "XC",
                 "L", "XL", "X", "IX", "V", "IV", "I"]
    lowercase = ["m", "cm", "d", "cd", "c", "xc",
                 "l", "xl", "x", "ix", "v", "iv", "i"]
    numeral = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            if uppercase:
                numeral += uppercase[i]
            else:
                numeral += lowercase[i]
            num -= val[i]
        i += 1
    return numeral


class Section:
    def __init__(self, directory, ordinal='1', watcher=None):
        try:
            chaptersmd = mdread.markdown_from_directory(directory, watcher=watcher)
            if watcher:
                watcher.add_path(directory)
        except FileNotFoundError as e:
            log.warn(e.args[0])
            self.chapters = []
            return
        except Exception as e:
            log.error(
                "Received exception when processing directory {}: {}".format(directory, e.args))
            # log.error(traceback.format_exc()) Not displaying traceback because it's usually just a missing directory
            self.chapters = []
            return

        # Sort the chapters by weight
        for i in chaptersmd:
            if 'weight' not in i[0]:
                i[0]['weight'] = 1
        chaptersmd = sorted(
            chaptersmd, key=lambda x: float(x[0]['weight']) * -1)

        nchapter = 0
        chapters = []

        for i in range(len(chaptersmd)):
            if ordinal == 'a':
                ref = chr(ord('a') + nchapter)
            elif ordinal == 'A':
                ref = chr(ord('A') + nchapter)
            elif ordinal == 'I':
                ref = int_to_rn(nchapter + 1)
            elif ordinal == 'i':
                ref = int_to_rn(nchapter + 1, False)
            else:
                ref = nchapter + 1

            chapters.append(
                Chapter(ref, chaptersmd[i]))
            nchapter += 1

        self.chapters = chapters

    def get_chapters(self, env):
        chapters = []
        for chapter in self.chapters:
            chapters.append(chapter.get_chapter(env))
        return chapters


class Chapter:
    def __init__(self, ref, chaptermd, filename="name"):
        self.headers = chaptermd[0]
        self.headers['ref'] = ref
        self.chapter_markdown = chaptermd[1]
        self.ref = ref
        self.filename = self.headers['filename']
        self.filename_noext = self.headers['filename_noext']

        if 'name' not in self.headers:
            if 'Name' in self.headers:
                self.headers['name'] = self.headers['Name']
            else:
                log.warn(f"Chapter from file '{self.filename}' does not have a name. Setting it to '{self.filename_noext}''")
                self.headers['name'] = 'Chapter'

        self.name = self.headers['name']

    def markdown(self, env):
        try:
            output = mdread.process_template(
                self.headers, self.chapter_markdown, env)
            return output
        except jinja2.exceptions.TemplateSyntaxError as error:
            log.error("Jinja2 error processing chapter {}: {} at lineno {} for file {}".format(
                self.name, error.message, error.lineno, filename=error.filename))
            log.error("Removing markdown for chapter {}".format(self.name))
            log_jinja2_error(self.chapter_markdown, error)
            return ""
        except Exception as e:
            log.error(
                "Received exception when processing markdown for section {}: {}".format(self.name, e.args))
            log.error(traceback.format_exc())
            log.error(
                "Removing markdown for chapter {}".format(self.name))
            return ""

    def get_chapter(self, env):
        chapter = {}
        chapter['name'] = self.name
        chapter['headers'] = self.headers
        chapter['ref'] = self.ref
        chapter['markdown'] = self.markdown(env)
        return chapter
