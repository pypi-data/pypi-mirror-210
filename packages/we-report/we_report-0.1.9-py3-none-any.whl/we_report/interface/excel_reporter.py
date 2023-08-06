"""
接受data_type中的数据，将数据完成图文混排输出
"""

import numpy as np
import pandas as pd
# from we_report.data_type.report_data import PageData, ReportData
from typing import Union, Dict, List, Tuple
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range
import xlsxwriter
from openpyxl import load_workbook
from PIL import Image
import io


class ExcelReport:

    @classmethod
    def output_page(cls, page_data: "PageData", output_file: str, page_name: str = "Sheet1"):
        """
        将一个Page输出到一个excel文件中
        Args:
            page_data:
            output_file:
        Returns:
        """
        wb = cls.create_file(output_file)  # 创建一个workbook
        # 完成实际插入数据
        cls.insert_page_contents(workbook=wb, page_data=page_data, page_name=page_name)
        # 完成所有写入，关闭worksheet
        wb.close()

    @classmethod
    def output_report(cls, report_data: "ReportData", output_file: str):
        """
        将一个report输出到excel中
        Args:
            output_file:
            report_data: 本质上是一个dict of pages过程，所以不断创建这个sheet即可
        Returns:
        """
        wb = cls.create_file(output_file)  # 创建一个workbook
        # 完成实际插入数据
        page_names = list(report_data.all_pages.keys())
        page_datas = list(report_data.all_pages.values())
        for i in range(len(page_names)):
            cls.insert_page_contents(workbook=wb, page_data=page_datas[i], page_name=page_names[i])
        # 完成所有写入，关闭worksheet
        wb.close()

    @classmethod
    def create_file(cls, file_name: str):  # 返回一个workbook
        # 先创建一个excel文件
        if file_name[-5:] != ".xlsx":
            file_name = file_name + ".xlsx"  # 文件名必须是xlsx格式

        wb = xlsxwriter.Workbook(file_name, {'nan_inf_to_errors': True, 'default_date_format': 'yyyy/mm/dd'})
        return wb

    @classmethod
    def insert_page_contents(cls, workbook, page_data: "PageData", page_name: str):
        ws = workbook.add_worksheet(page_name)  # 不需要名字的sheet，自动命名
        if page_data.text is not None:
            ws.write(0, 0, page_data.text)

        max_df_col = np.max([page_data.tables[i].shape[1] for i in range(len(page_data.tables))])  # 求表格的最宽的列

        # 开始输出所有表格，方法是纵向一字排开
        cls.write_all_tables(dfs=page_data.tables, table_texts=page_data.table_texts, work_sheet=ws)

        # 开始输出所有图片，方法也是纵向一字排开
        cls.write_all_figs(figs=page_data.figs, work_sheet=ws, start_col=max_df_col + 2,
                           fig_height=page_data.fig_size[0],
                           fig_width=page_data.fig_size[1])  # 向右侧移动两列

        # 写入附录表格
        if page_data.appendix_tables is not None:
            cls.write_appendix_tables(tables=page_data.appendix_tables, work_sheet=ws,
                                      start_col=max_df_col + int(page_data.fig_size[1] / 70) + 4,
                                      appendix_texts=page_data.appendix_texts)

    @classmethod
    def write_all_tables(cls, dfs: List[pd.DataFrame], table_texts: List[str], work_sheet: str):
        """
        将多个表格沿着顺序逐次插入进来
        Args:
            dfs: 需要插入的表格
            table_texts: 表格的说明文字，必须与表格一一对应
            work_sheet: 在哪个sheet中插入
        Returns:
        """
        start_col = 0
        row = 3
        if dfs is not None:  # 存在就输出
            for i in range(len(dfs)):
                if len(table_texts) > 0:
                    if table_texts[i] is not None:
                        work_sheet.write(row - 1, start_col, table_texts[i])
                temp_df = dfs[i].T.reset_index().values.T.tolist()  # 这样能够保留住column列
                m, n = np.array(temp_df).shape
                region = xl_range(row, start_col, row + m - 1, start_col + n - 1)
                work_sheet.add_table(region, {"data": temp_df, 'style': None, 'header_row': False})
                row += (m + 3)  # 多空出来3行

    @classmethod
    def write_all_figs(cls,
                       figs: List[str],
                       work_sheet: str,
                       start_col: int = 0,
                       fig_width=500,
                       fig_height=500):
        """
        将一系列的图片在右侧一字排开
        Args:
            figs:
            work_sheet:
            start_col: 默认从某个列开始画这个图
        Returns:
        """
        row = 2  # 输出图形也从第2行开始
        Cell_width = 70.0  # excel的每个格子cell的宽度大概是70个点
        Cell_height = 22.0  # excel的每个格子的高度大概是22个点；但是这个参数会导致图形不清晰
        if figs is not None:  # 如果有图可以输出
            for i in range(len(figs)):
                # loc = xl_rowcol_to_cell(row, start_col)
                # 不想写入到disk上，但是可以写入到buffer里，缩放；然后写入excel
                image_buffer, image = cls._resize(figs[i], size=(fig_width, fig_height))  # 所有图片进行了同比例缩放，都转变为同一个分辨率
                data = {'x_scale': fig_width / image.width,
                        'y_scale': fig_height / image.height,
                        "boject_position": 1}
                work_sheet.insert_image(row, start_col, figs[i], options={"image_data": image_buffer, **data})

                row += 18

    @classmethod
    def write_appendix_tables(cls, appendix_texts, tables: [pd.DataFrame], work_sheet: str, start_col: int = 14):
        """
        从第14列开始，横向一字排开，写入所有的excel文档
        Args:
            tables:
            work_sheet:
            start_col:
        Returns:
        """
        current_start_col = start_col  # 从这个位置出发，横向一字排开写入所有表格，中间间隔2个col
        for k in range(len(tables)):
            if len(appendix_texts) != 0:
                txt = appendix_texts[k]
                if txt is not None:
                    work_sheet.write(0, current_start_col, txt)

            tb = tables[k]
            temp_df = tb.T.reset_index().values.T.tolist()  # 这样能够保留住column列
            m, n = np.array(temp_df).shape
            region = xl_range(1, current_start_col, m - 1, current_start_col + n - 1)
            work_sheet.add_table(region, {"data": temp_df, 'header_row': False, 'style': None})
            current_start_col += n + 2  # 多空2列

    @classmethod
    def _buffer_image(cls, image: Image):
        buffer = io.BytesIO()
        image.save(buffer, format="png")
        return buffer, image

    @classmethod
    def _resize(cls, fig_path: str, size: Tuple[int, int]):
        image = Image.open(fig_path)
        image = image.resize(size)
        return cls._buffer_image(image)
