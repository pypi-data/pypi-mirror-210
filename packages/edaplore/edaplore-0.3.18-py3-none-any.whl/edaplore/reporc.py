from src.edaplore.separator.data_separator import Separator
from src.edaplore.overview.overview_class import Overview
from src.edaplore.interactions.interaction_comb import ComparatorU
from src.edaplore.html_templates.template_loader import find_template
from src.edaplore.interactions.genmap import GenMap

import time


class Report:
    def render(self):
        """
        Renders a Jinja template using the report data.

        :return: A string containing the rendered HTML template.
        """
        template = find_template('report_dreop.html').render(over=self.overview,
                                                             sep=self.separ,
                                                             comp=self.compar,
                                                             gm=self.genmap)
        return template

    def save_html(self, path):
        """
        Writes the rendered template into an HTML file.

        :param path: A string containing the path where the HTML file will be saved.
        """
        with open(path, 'w') as f:
            f.write(self.rendered)

    def __init__(self, df, path, fill_mis=False, drop_outliers=False, threshold=0.95, ohe=False):
        """
        Initializes the Report class, performing data separation, overview, comparison, and generation of a correlation map.

        :param df: The DataFrame to be used in the report.
        :param path: The path where the generated HTML report will be saved.
        :param fill_mis: Boolean indicating whether missing values should be filled.
        :param drop_outliers: Boolean indicating whether outliers should be dropped.
        :param threshold: The quantile at which a value is considered an outlier.
        :param ohe: Boolean indicating whether one-hot encoding should be performed.
        """
        start_time = time.time()
        full_time = time.time()
        self.separ = Separator(data=df,
                               fill_mis=fill_mis,
                               drop_outliers=drop_outliers,
                               threshold=threshold,
                               ohe=ohe)
        print(f'separ done {time.time() - start_time}')
        start_time = time.time()

        self.overview = Overview(self.separ.data_classes)
        print(f'overview done {time.time() - start_time}')
        start_time = time.time()

        self.compar = ComparatorU(self.separ, cols=self.separ.col_names)
        print(f'compU done {time.time() - start_time}')
        start_time = time.time()

        self.genmap = GenMap(self.separ.data)
        print(f'genmap done {time.time() - start_time}')
        start_time = time.time()

        self.rendered = self.render()
        self.save_html(path)
        print(f'full done {time.time() - full_time}')
