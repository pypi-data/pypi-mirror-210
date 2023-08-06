"""
This module contains utility function to build time series report from template.
"""
# pylint: disable=too-many-instance-attributes, unused-import, eval-used, too-many-nested-blocks, broad-except
import logging
import os
import json
from tqdm import tqdm

logger = logging.getLogger(__name__)

def _load_ts_report_template(is_timestamp=True):
    if is_timestamp:
        report_template = os.path.join(os.path.dirname(__file__), "templates",
                                       "dataset_analysis_timestamp_template.json")
    else:
        report_template = os.path.join(os.path.dirname(__file__), "templates",
                                       "dataset_analysis_int_template.json")
    with open(report_template) as input_file:
        return json.load(input_file)

class TimeSeriesTemplateReportHelper:
    """
    Utility function to generate time series report from JSON template.
    """
    def __init__(self,
                 obj,
                 fit_data=None,
                 template=None,
                 name="HANA ML Timeseries Report"):
        if hasattr(obj, 'massive'):
            if obj.massive:
                raise NotImplementedError("Currently time series report doesn't support PAL massive mode.")
        if fit_data:
            self.fit_data = fit_data
        else:
            if hasattr(obj, "training_data"):
                self.fit_data = obj.training_data
            else:
                self.fit_data = obj.fit_args_[0]
        if hasattr(obj, "endog"):
            self.endog = obj.endog
        else:
            self.endog = self.fit_data.columns[1]
        if hasattr(obj, "exog"):
            self.exog = obj.exog
        else:
            self.exog = self.fit_data.columns[2:]
        if hasattr(obj, "key"):
            self.key = obj.key
        else:
            self.key = self.fit_data.columns[0]
        is_timestamp = True
        if 'INT' in self.fit_data.get_table_structure()[self.key]:
            is_timestamp = False
        if template is None:
            self.template = _load_ts_report_template(is_timestamp)
        self.pages = []
        self.name = name

    def build_report(self):
        """
        Build function.
        """
        from hana_ml.visualizers.time_series_report import DatasetAnalysis
        from hana_ml.visualizers.report_builder import Page
        from hana_ml.algorithms.pal.tsa.changepoint import BCPD #pylint: disable=unused-import
        if self.fit_data.hasna():
            self.fit_data = self.fit_data.fillna(0)
            logger.warning("Missing value has been replaced by 0.")
        pages = []
        dataset_analysis = DatasetAnalysis(data=self.fit_data, endog=self.endog, key=self.key)
        for page in tqdm(self.template["DatasetAnalysis"]):
            temp = Page(page["name"])
            for item in page["items"]:
                item_params = []
                for kkey, vval in item[list(item.keys())[0]].items():
                    if isinstance(vval, str):
                        if list(item.keys())[0] != 'change_points_item':
                            item_params.append("{}='{}'".format(kkey, vval))
                        else:
                            item_params.append("{}={}".format(kkey, vval))
                    else:
                        item_params.append("{}={}".format(kkey, vval))
                execute_str = "temp.addItems(dataset_analysis.{}({}))".format(list(item.keys())[0], ','.join(item_params))
                logger.info(execute_str)
                try:
                    eval(execute_str)
                except Exception as err:
                    logger.error(err)
                    pass
            pages.append(temp)
        self.pages = self.pages + pages
        return self

    def generate_html_report(self, filename=None):
        """
        Display function.
        """
        from hana_ml.visualizers.time_series_report import TimeSeriesReport
        report = TimeSeriesReport(self.name)
        report.addPages(self.pages)
        report.build()
        report.generate_html(filename)

    def generate_notebook_iframe_report(self):
        """
        Display function.
        """
        from hana_ml.visualizers.time_series_report import TimeSeriesReport
        report = TimeSeriesReport(self.name)
        report.addPages(self.pages)
        report.build()
        report.generate_notebook_iframe()

    def add_pages(self, pages):
        """
        Add pages to the existing report.
        """
        if isinstance(pages, (list, tuple)):
            self.pages = self.pages + pages
        else:
            self.pages.append(pages)
