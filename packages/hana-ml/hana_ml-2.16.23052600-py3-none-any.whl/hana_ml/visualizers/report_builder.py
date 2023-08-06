"""
This module represents the whole report builder.
A report can contain many pages, and each page can contain many items.
You can assemble different items into different pages.

The following classes are available:
    * :class:`ReportBuilder`
    * :class:`Page`
    * :class:`ChartItem`
    * :class:`TableItem`
    * :class:`DescriptionItem`
    * :class:`DigraphItem`
    * :class:`LocalImageItem`
    * :class:`RemoteImageItem`
    * :class:`ForcePlotItem`
"""

# pylint: disable=invalid-name
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=no-member
# pylint: disable=too-few-public-methods
# pylint: disable=super-init-not-called
# pylint: disable=attribute-defined-outside-init
from typing import List
import base64
from urllib.parse import quote
from hana_ml.visualizers.template_utils import TemplateUtil
from hana_ml.visualizers.ui_components import HTMLUtils, HTMLFrameUtils


class Item(object):
    def __init__(self):
        pass

    def to_json(self):
        temp_json = {
            'title': self.title,
            'type': self.type,
            'config': self.config
        }
        if self.type == 'chart':
            if self.height is not None:
                temp_json['height'] = float(self.height)
            if self.width is not None:
                temp_json['width'] = float(self.width)
        return temp_json

class DescriptionItem(Item):
    """
    This item represents an description type, it contains multiple key and value values.

    Parameters
    ----------
    title : str
        The description item name.
    """
    def __init__(self, title: str):
        self.title: str = title
        self.type = 'description'
        self.config = []

    def add(self, key: str, value: str):
        """
        Add a key-value pair.

        Parameters
        ----------
        key : str
            The key of description item.

        value : str
            The value of description item.
        """
        if key is not None and value is not None:
            self.config.append({
                'name': key,
                'value': value
            })
        else:
            raise ValueError('Added key or value is none!')


class ChartItem(Item):
    """
    This item represents an chart type.

    Parameters
    ----------
    title : str
        The chart item name.

    config : json
        The chart item config.

    width : int, optional
        The chart's width.

    height : int, optional
        The chart's height.
    """
    def __init__(self, title: str, config, width=None, height=None):
        self.title: str = title
        self.type = 'chart'
        self.config = config
        self.width = width
        self.height = height


class TableItem(Item):
    """
    This item represents an table type.

    Parameters
    ----------
    title : str
        The table item name.
    """
    def __init__(self, title: str):
        self.title: str = title
        self.type = 'table'
        self.config = {
            'columns': [],
            'data': {}
        }
        self.data_count = -1

    def addColumn(self, name: str, data: List):
        """
        Add a dataset of single column.

        Parameters
        ----------
        name : str
            The column name of the single dataset.

        data : List
            The single dataset.
        """
        if name and data:
            if self.data_count == -1:
                self.data_count = len(data)
            elif len(data) != self.data_count:
                raise ValueError('Added data length is incorrect!')
            self.config['columns'].append(name)
            self.config['data'][name] = data
        else:
            raise ValueError('Added name or data is none!')


class RemoteImageItem(Item):
    """
    This item represents an remote image type.

    Parameters
    ----------
    title : str
        The image item name.

    url : str
        The image address.

    width : int, optional
        The image width.

        Default to original width of image.

    height : int, optional
        The image height.

        Default to original height of image.
    """
    def __init__(self, title: str, url: str, width: int = None, height: int = None):
        if title is None or url is None:
            raise ValueError('The title or url is none!')

        self.title: str = title
        self.type = 'image'
        self.config = {
            'url': url
        }

        if width:
            self.config['width'] = width
        if height:
            self.config['height'] = height


class LocalImageItem(Item):
    """
    This item represents an local image type.

    Parameters
    ----------
    title : str
        The image item name.

    file_path : str
        The image file path.

    width : int, optional
        The image width.

        Default to original width of image.

    height : int, optional
        The image height.

        Default to original height of image.
    """
    def __init__(self, title: str, file_path: str, width: int = None, height: int = None):
        if title is None or file_path is None:
            raise ValueError('The title or file path is none!')
        file = open(file_path, 'rb')
        imageContent = file.read()
        file.close()
        self.title: str = title
        self.type = 'image'
        base64_data = base64.b64encode(imageContent)
        image_str = "data:{mime_type};base64,{image_data}".format(mime_type="image/png", image_data=quote(base64_data))

        self.config = {
            'content': image_str
        }

        if width:
            self.config['width'] = width
        if height:
            self.config['height'] = height


class ForcePlotItem(Item):
    def __init__(self, title: str, config):
        self.title: str = title
        self.type = 'sp.force-plot'
        self.config = config


class DigraphItem(Item):
    def __init__(self, title: str, digraph):
        def escape(s):
            s = s.replace("&", "&amp;") # Must be done first!
            s = s.replace("<", "&lt;")
            s = s.replace(">", "&gt;")
            s = s.replace('"', "&quot;")
            s = s.replace('\'', "&quot;")
            return s
        self.title: str = title
        self.type = 'sp.digraph'
        self.config: str = escape(digraph.embedded_unescape_html)


class Page(object):
    """
    Every report consists of many pages. Each page contains multiple items.

    Parameters
    ----------
    title : str
        The page name.
    """
    def __init__(self, title: str):
        self.title: str = title
        self.items: List[Item] = []

    def addItem(self, item: Item):
        """
        Add a item instance to page instance.

        Parameters
        ----------
        item : Item
            Each page contains multiple items.
        """
        if item is not None:
            if item.config is not None:
                self.items.append(item.to_json())
        else:
            raise ValueError('Added item is none!')

    def addItems(self, items):
        """
        Add many item instances to page instance.

        Parameters
        ----------
        items : Item or List[Item]
            Each page contains multiple items.
        """
        if isinstance(items, (list, tuple)):
            if items and len(items) > 0:
                for item in items:
                    self.addItem(item)
            else:
                raise ValueError('Added items is none or no data items!')
        else:
            self.addItem(items)

    def to_json(self):
        """
        Return the config data of single page.
        This method is automatically called by the internal framework.
        """
        return {
            'title': self.title,
            'items': self.items
        }


class ReportBuilder(object):
    __TEMPLATE = TemplateUtil.get_template('report_builder.html')

    """
    This class is a report builder and the base class for report building. Can be inherited by custom report builder classes.

    Parameters
    ----------
    title : str
        The report name.
    """
    def __init__(self, title: str):
        self.__build_error_msg = 'To generate a report, you must call the build method firstly.'
        self.title: str = title
        self.pages: List[Page] = []
        self.html = None
        self.frame_src = None
        self.frame_id = ''
        self.frame_html = None

    def getHTMLText(self):
        if self.html is None:
            raise Exception(self.__build_error_msg)
        return self.html

    def getIframeHTMLText(self):
        if self.frame_src is None:
            raise Exception(self.__build_error_msg)
        return self.frame_html

    def addPage(self, page: Page):
        """
        Add a page instance to report instance.

        Parameters
        ----------
        page : Page
            Every report consists of many pages.
        """
        if page:
            self.pages.append(page.to_json())
        else:
            raise ValueError('Added page is none!')

    def addPages(self, pages: List[Page]):
        """
        Add many page instances to report instance.

        Parameters
        ----------
        pages : List[Page]
            Every report consists of many pages.
        """
        if pages and len(pages) > 0:
            for page in pages:
                self.addPage(page)
        else:
            raise ValueError('Added pages is none or no data items!')

    def to_json(self):
        """
        Return the all config data of report.
        This method is automatically called by the internal framework.
        """
        return {
            'title': self.title,
            'pages': self.pages
        }

    def build(self, debug=False):
        """
        Build HTML string based on current config.

        Parameters
        ----------
        debug : bool
            Whether the log should be printed to the console.

            Defaults to False.
        """
        if debug is False:
            debug = 'false'
        else:
            debug = 'true'
        self.html = HTMLUtils.minify(ReportBuilder.__TEMPLATE.render(debug=debug, reportConfig=self.to_json()))
        self.frame_src = HTMLFrameUtils.build_frame_src(self.html)
        self.pages = []

    def generate_html(self, filename):
        """
        Save the report as a html file.

        Parameters
        ----------
        filename : str
            HTML file name.
        """
        if self.html is None:
            raise Exception(self.__build_error_msg)
        TemplateUtil.generate_html_file('{}_report.html'.format(filename), self.html)

    def generate_notebook_iframe(self, iframe_height=600):
        """
        Render the report as a notebook iframe.

        Parameters
        ----------
        iframe_height : int
            iframe height.

            Defaults to 600.
        """
        if self.frame_src is None:
            raise Exception(self.__build_error_msg)
        HTMLFrameUtils.check_frame_height(iframe_height)
        self.frame_html = HTMLFrameUtils.build_frame_html_with_id(self.frame_id, self.frame_src, iframe_height)
        HTMLFrameUtils.display(self.frame_html)
