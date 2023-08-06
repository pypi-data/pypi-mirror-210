"""
这里会定义一系列的基础
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict
from we_report.interface.excel_reporter import ExcelReport


class PageData:
    """
    一个单独的图文混排的页面，长度可能是无限长，暂时不考虑这里的换页问题
    在生成这个数据之前，就需要保证对应文件夹里已经有了 .png 格式的图片放在那里了，
    这些图片是哪里来的？是其他代码生成的，你不用管
    """

    def __init__(self,
                 text: str = None,
                 tables: List[pd.DataFrame] = None,
                 fig_paths: List[str] = None,
                 fig_size: List[int] = [400, 600],
                 table_texts: List[str] = None,
                 appendix_texts: List[str] = [None],
                 appendix_tables: List[pd.DataFrame] = None,
                 ):
        """
        一个报告可以支持的数据类型
        Args:
            text: 页面文字描述，每个page 都容许有一段文字描述
            tables: 一系列主要表格，主要表格同时是统计表格，方式是在text 下面开始纵向一字排开输出
            table_texts：每个表格的文字描述，如果有的话，必须与 tables 一一对应
            fig_paths: 图片地址，相关图片会以相同的分别率被右侧进行纵向一字排开
            fig_size: 默认图片大小，每个图片的大小都是一样的
            appendix_tables: 附录表格，一系列的附录表格，在右侧进行横向一字排开输出
        """
        self.text = text  # 一段对本page的注释，每个page只有一段文字的机会，可以是None
        self.tables = tables
        self.figs = fig_paths
        self.fig_size = fig_size
        if table_texts is None:
            table_texts = [None] * len(tables)  # 如果没有文字描述，则生成一个等长的 None 列表
        self.table_texts = table_texts
        self.appendix_texts = appendix_texts
        self.appendix_tables = appendix_tables

    def output(self, output_file: str, page_name: str = "Sheet1"):
        ExcelReport.output_page(page_data=self, output_file=output_file, page_name=page_name)


class ReportData:
    """
    报告的数据类型
    """

    def __init__(self, all_pages: Dict[str, PageData]):
        self.all_pages = all_pages

    def merge_report(self, other_report: "ReportData") -> "ReportData":
        """
        合并两个报告
        Args:
            other_report:

        Returns:
        """
        all_pages = self.all_pages.copy()
        duplicate_keys = list(set(self.all_pages.keys()).intersection(set(other_report.all_pages.keys())))
        if len(duplicate_keys) != 0:
            raise ValueError(f"两个报告中存在重复的sheet名：{duplicate_keys}")
        all_pages.update(other_report.all_pages)
        return ReportData(all_pages)

    def output(self, output_file: str):
        """
        输出整个 Report
        Args:
            output_file: 输出文件路径
        Returns:
        """
        ExcelReport.output_report(report_data=self, output_file=output_file)


# --------------
# 一系列测试
def test_page():  # 测试page
    df1 = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["A1", "A2", "A3"])
    df2 = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["A1", "A2", "A3"])
    fig1 = "../../test/Snipaste1.png"
    print("check", df1)
    page1 = PageData(tables=[df1, df2], fig_paths=[fig1])
    page2 = PageData(tables=[df2])
    myreport = ReportData({"mysheet1": page1, "mysheet2": page2})
    print(myreport.all_pages)
    print(page1.tables, page1.figs)
    page1.output("test_page")
    myreport.output("test_report")


def test_excel_report():  # 测试 1 page report
    df1 = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["A1", "A2", "A3"])
    df2 = pd.DataFrame([[1.1, 2, 3], [4.4, 5, 6]], columns=["A1", "A2", "A3"])
    fig1 = "./../../test/Snipaste1.png"
    fig2 = "./../../test/Snipaste2.png"
    fig3 = "./../../test/Al_PE_history.png"
    text1 = "This is a test page."
    page1 = PageData(tables=[df1, df2], fig_paths=[fig1, fig2, fig3], text=text1)
    ExcelReport.output_page(page1, "test.xlsx")

    myreport = ReportData({"mysheet1": page1, "mysheet2": page1})  # 创造一个report，包含2个sheet
    ExcelReport.output_report(myreport, "test2.xlsx")


def test_df_containing_nan():
    df1 = pd.DataFrame([[1, 2, 3], [4, 5, None]], columns=["A1", "A2", "A3"])
    fig1 = "./../../test/Snipaste1.png"
    print(df1)
    page1 = PageData(tables=[df1], fig_paths=[fig1])
    ExcelReport.output_page(page1, "test3.xlsx")


def test_page_with_appendix_tables():
    text = "report with appendix tables"

    np.random.seed(123)
    x = np.random.randn(100)
    y = np.random.randn(100)
    z = np.random.randn(100)  # 用三个原始数据，组成一个数据集
    raw_data = pd.DataFrame(np.array([x, y, z]).T, columns=["x", "y", "z"])

    d_n = np.array([len(raw_data) for i in range(len(raw_data.columns))])
    d_mean = raw_data.mean(axis=0)
    d_sigma = raw_data.std(axis=0)

    tables = pd.DataFrame(np.array([d_n, d_mean, d_sigma]).T, columns=["N", "mu", "sigma"])  # 统计表

    ax = raw_data['y'].plot.hist(bins=20)
    ax.figure.savefig("../../test/hist1.png")
    mypage = PageData(text=text, tables=[tables, tables], fig_paths=["../../test/hist1.png", "../../test/hist1.png"],
                      appendix_tables=[raw_data, raw_data]  # 这里将附录数据复制2遍，检测可否做这个工作
                      )


#     mypage.output("test_report_with_appendix_tables")
def test_with_multi_text():
    np.random.seed(123)
    text = "report with appendix tables"
    x = np.random.randn(100)
    y = np.random.randn(100)
    z = np.random.randn(100)  # 用三个原始数据，组成一个数据集
    raw_data = pd.DataFrame(np.array([x, y, z]).T, columns=["x", "y", "z"])

    d_n = np.array([len(raw_data) for i in range(len(raw_data.columns))])
    d_mean = raw_data.mean(axis=0)
    d_sigma = raw_data.std(axis=0)

    tables = pd.DataFrame(np.array([d_n, d_mean, d_sigma]).T, columns=["N", "mu", "sigma"])  # 统计表

    ax = raw_data['y'].plot.hist(bins=20)
    ax.figure.savefig("../../test/hist1.png")

    # one sheet = 逐个sheet中的内容打包
    mypage1 = PageData(text=text, tables=[tables, tables], fig_paths=["../../test/hist1.png", "../../test/hist1.png"],
                       fig_size=[400, 600], appendix_tables=[raw_data, raw_data],
                       table_texts=['first table :', 'second table :'],
                       appendix_texts=['first table :', 'second table :']  # 这里将附录数据复制2遍，检测可否做这个工作
                       )

    # one report = 多个sheet，直接用dict来封装成 report
    myreport = ReportData({"mysheet1": mypage1, "mysheet2": mypage1})  # 创造一个report，包含2个sheet

    # report 的输出
    ExcelReport.output_report(myreport, "test_report_with_multi_text.xlsx")


if __name__ == '__main__':
    test_page()
    test_excel_report()
    test_df_containing_nan()
    test_page_with_appendix_tables()
    test_with_multi_text()
