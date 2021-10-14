from ab.utils.algorithm import algorithm


# 会自动暴露为/api/algorithms/head接口
@algorithm()
def head(data, table_info, sample_count, sample_rate):
    """
    :param data:  表的DataFrame
    :param table_info:  表的meta信息
        {
            # 每个列的meta信息
            'columns': [
                {'field': 列名,
                'xlabType': 列类型。框架做了统一处理，目前有String/Boolean/Long/Double/Date这几种,
                'comment': 列注释
                },
            ],
            # 表大小，单位KB
            'size': 80.0,
            # 表类型。目前支持mysql/odps/hive
            'type': 'mysql'
        }
    :param sample_count: 采样条数，即len(data)
    :param sample_rate: 采样率，即 len(result) / 表中总行数。
                        对于size极大的表，比如hive/odps等，获取表中总行数要执行全表扫描，速度非常慢，因此不计算采样率，此字段保留为None
    """
    return data.head(10)
