from openpyxl import load_workbook


def reader(*, fpath: str = None, header: bool = True, sheet_name: str = None, cols: list = None):
    """
    使用条件：任务对象和函数上都可以添加
    函数参数需带 xlsx_data
    eg:
    @reader .....
    def read(xlsx_data=None): ...
        fpath: xlsx文件的绝对路径
        header: 是否带有列名，默认是有的
        sheet_name: 要带去的 Sheet 名， 不指定的话默认读取第一个
        cols: 期望读取的列
            [1,2,3] 通过序号获取
            ["id","name","desc"] 通过列名获取
        @reader(fpath="", header=True, sheet_name="result", cols=["id","name"])
        返回字典列表: [{},{},{}]
        @reader(fpath="", header=True, sheet_name="result", cols=[0,1])
        返回2维列表: [[],[],[]]
        @reader(fpath="", header=False, sheet_name="result")
        返回2维列表，所有的数据: [[],[],[]]
        @reader(fpath="", header=True, sheet_name="result")
        返回2维列表，所有的数据: [[],[],[]]
    """
    if cols is None: cols = []

    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            xls_path = fpath if fpath is not None else kwargs.get("fpath")
            work_book = load_workbook(filename=xls_path)
            work_sheet = work_book.worksheets[0] if not sheet_name else \
                list(filter(lambda s: s.title == sheet_name, work_book.worksheets))[0]
            cells = [[cell.value for cell in row] for row in work_sheet.rows]
            if not header and not cols: return cells
            if header:
                if not cols: return cells
                if type(cols[0]) == int:
                    kwargs["xlsx_data"] = [[cell[col] for col in cols] for cell in cells]
                    func(*args, **kwargs)
                if type(cols[0]) == str:
                    header_dict = {}
                    for col in cols:
                        header_dict[col] = cells[0].index(col)
                    res = []
                    for cell in cells[1:]:
                        temp = {}
                        for key, index in header_dict.items():
                            temp[key] = cell[index]
                        res.append(temp)
                    kwargs["xlsx_data"] = res
                    func(*args, **kwargs)

        return __inner__

    return __wrapper__
