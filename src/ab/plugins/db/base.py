from pymysql import escape_string


class DataBase:
    # prevent sql injection
    # TODO not sure whether this is 100% safe
    @staticmethod
    def escape(s: str):
        return '`' + escape_string(s.strip()).replace('`', '') + '`'

    def table_sql(self, sql, table_name, column_names: list=None):
        """
        return sql result over table
        """
        table_info = self.table_info(table_name)
        rows = self.execute(sql)
        if not rows:
            return rows

        # convert decimal to float
        column_names = column_names or rows[0].keys()
        for c in table_info['columns']:
            column_name = c['field']
            if 'decimal' in c['type'] and column_name in column_names:
                for row in rows:
                    if row[column_name] is not None:
                        row[column_name] = float(row[column_name])
        return rows

    def set_sampler(self, sampler_config: dict):
        self.sampler = self.sampler_class.get_instance(self, sampler_config)
