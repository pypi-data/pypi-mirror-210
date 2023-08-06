import os
import glob
import re
import threading
import pyarrow.parquet as pq


characteristic_list = ['characteristic_exposure', 'characteristic_return', 'characteristic_covariance',
                       'characteristic_idiosyncratic_variance', 'characteristic_scale',
                       'factor_mimicking_portfolio_weights', 'daily_excess_return', 'factor_return']


class BaseClient(object):
    _threading_local = threading.local()

    def __init__(self):
        self._instance = None

    @classmethod
    def instance(cls):
        _instance = getattr(cls._threading_local, '_instance', None)
        if _instance is None:
            _instance = cls()
            cls._threading_local._instance = _instance
        return _instance


class LocalClient(BaseClient):
    def __init__(self, path):
        super().__init__()
        if not os.path.isdir(path):
            raise Exception(f"{path} is not a valid directory")
        self.storage_path = path
        self.filter_format = r'^\s*(=|==|!=|<|>|<=|>=|in|not in)\s*(.*)\s*$'

    def query(self, param):
        if param.get("domain") == "descriptor" and param.get("phylum") == "characteristic":
            return self.query_descriptor(param)
        else:
            raise Exception("Parameter error, domain or phylum error")

    def query_descriptor(self, param):
        self._check_storage_path()
        self._check_query_descriptor(param)
        self._check_date(param.get("start_date"))
        self._check_date(param.get("end_date"))
        self._check_extra_filters(param.get('filters'))

        parquet_files = list()
        # 先找目录+文件
        file_path = os.path.join(self.storage_path, f'**{param.get("case")}', f'{param.get("class")}*.parquet')
        parquet_files += glob.glob(file_path)
        if not parquet_files:
            # 如果找不到，直接找文件
            file_path = os.path.join(self.storage_path, f'{param.get("class")}*.parquet')
            parquet_files += glob.glob(file_path)
        print(f'loading {parquet_files} files')
        if not parquet_files:
            raise Exception(f"Parameter error, parquet files does not exist")
        filters = self._gen_query_filters(param)
        dataset = pq.ParquetDataset(parquet_files, use_legacy_dataset=False, filters=filters)
        df = dataset.read().to_pandas()
        df.sort_values(by=['date'])
        return df

    def _to_pyarrow_filters(self, filters):
        pyarrow_filters = [[]]
        for column, conditions in filters.items():
            for condition in conditions:
                ret = re.search(self.filter_format, condition, re.IGNORECASE)
                op = ret.group(1)
                vl = eval(ret.group(2))
                pyarrow_filters[0].append((column, op, vl))
        return pyarrow_filters

    def _gen_query_filters(self, param):
        # pyarrow的filters为嵌套列表，外层列表是或（or）关系，内层列表是与（and）关系
        basic_filter = []
        if param.get("start_date") and param.get("start_date") != "":
            basic_filter.append(('date', '>=', param.get('start_date')))
        if param.get("end_date") and param.get("end_date") != "":
            basic_filter.append(('date', '<=', param.get('end_date')))
        if param.get("case"):
            basic_filter.append(('case', '==', param.get('case')))

        filters = param.get("filters")
        if not filters:
            return [basic_filter]

        pyarrow_filters = self._to_pyarrow_filters(filters)
        if pyarrow_filters:
            # pyarrow_filters，需要融合basic_filters
            for every_filter in pyarrow_filters:
                every_filter += basic_filter
            filters = pyarrow_filters
        return filters

    def _check_extra_filters(self, extra_filters):
        if extra_filters is None:
            return
        for column, conditions in extra_filters.items():
            for condition in conditions:
                if not re.search(self.filter_format, condition, re.IGNORECASE):
                    raise Exception(f"condition expression {condition} format error")

    def _check_date(self, date: str):
        if date is None or date == "":
            return

    def _check_storage_path(self):
        if not os.path.isdir(self.storage_path):
            raise Exception(f"{self.storage_path}该目录不存在")

    def _check_query_descriptor(self, param):
        if param.get("class") not in characteristic_list:
            raise Exception("Parameter error, class error")
        if param.get("case") is None:
            raise Exception("Parameter error, case error")

    def extract(self, param):
        pass
