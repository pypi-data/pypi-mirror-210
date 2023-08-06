from __future__ import annotations

import logging
import os
import re
from os.path import getmtime, normpath
from posixpath import join

from jinja2 import FileSystemLoader as JinjaFileSystemLoader, TemplateNotFound
from jinja2.loaders import split_template_path
from jinja2.utils import open_if_exists

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Tuple, Callable

if TYPE_CHECKING:
    pass

class FileSystemLoader(JinjaFileSystemLoader):
    def get_source(
            self, environment: "Environment", template: str
    ) -> Tuple[str, str, Callable[[], bool]]:
        """
        Copy of the original get_source method from Jinja2 FileSystemLoader
        only change is the call to add_version_to_static_files which preprocesses
        templates to add a version number to static files before they are loaded into cache.

        :param environment:
        :param template:
        :return:
        """
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            # Use posixpath even on Windows to avoid "drive:" or UNC
            # segments breaking out of the search directory.
            filename = join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            # Add version number to static files
            contents = add_version_to_static_files(contents, app_root=f"{searchpath}/..")
            # Remove irrelevant whitespaces
            contents = remove_irrelevant_whitespaces(contents)
            # Remove HTML comments
            contents = remove_html_comments(contents)

            mtime = getmtime(filename)

            def uptodate() -> bool:
                try:
                    return getmtime(filename) == mtime
                except OSError:
                    return False

            # Use normpath to convert Windows altsep to sep.
            return contents, normpath(filename), uptodate
        raise TemplateNotFound(template)


def add_version_to_static_files(html: str, app_root: str) -> str:
    """
    This function takes in the HTML content of a page and the root directory of the app,
    and adds a "v" parameter to the URLs of static entries in the HTML content.
    The value of the "v" parameter is set to the modification time of the static file.
    A static entry is defined as a URL starting with "/static".

    :param html: The HTML content of a page
    :type html: str
    :param app_root: The root directory of the app
    :type app_root: str
    :return: The modified HTML content
    :rtype: str
    """
    def repl(match):
        url = match.group(1)
        file_path = os.path.join(app_root, url.lstrip('/'))
        if os.path.exists(file_path):
            mtime = int(os.path.getmtime(file_path))
            return f'{match.group(0)}?v={mtime}'
        return match.group(0)

    pattern = r'(?:(?:src|href)=["\'])(/static[^"\']+)'
    html = re.sub(pattern, repl, html)
    return html

def remove_irrelevant_whitespaces(html: str) -> str:
    """
     This function takes an HTML string as input and removes all whitespaces that are not relevant for display.

    :param html: The HTML string to process.
    :type html: str
    :return: The processed HTML string with irrelevant whitespaces removed.
    :rtype: str
    """
    # Remove whitespaces before or after tags
    html = re.sub(r'>\s+<', '><', html)
    return html


def remove_html_comments(html: str) -> str:
    """
    This function takes an HTML string as input and removes all HTML comments, except for those that contain copyright or license information.

    :param html: The HTML string to process.
    :type html: str
    :return: The processed HTML string with irrelevant comments removed.
    :rtype: str
    """
    # Remove comments that do not contain copyright or license information
    html = re.sub(r'<!--(?![\s\S]*?(copyright|license)[\s\S]*?-->)[\s\S]*?-->', '', html, flags=re.IGNORECASE)
    return html
