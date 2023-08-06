try:
    from rain_orm.error import SqlBuildError
except ImportError:
    from error import SqlBuildError


class SqlBuilder:
    operations = ["select", "insert", "update", "delete"]

    def __init__(self, table, op=None):
        self.sql_str = ""
        self.table = table
        self.op = op
        self.target = []
        self.condition = []
        self.fields_values = {}
        self.limit_num = None
        self.offset_num = None
        self.order = []

    def __str__(self):
        return self.sql_str

    def __repr__(self):
        return self.sql_str

    def set_operation(self, op):
        self.op = op

    def select(self, *args):
        for t in args:
            if not isinstance(t, str):
                raise SqlBuildError("args should be str")
        for t in args:
            self.target.append(t)
        return self

    def where(self, condition, value=None):
        if isinstance(value, str):
            value = f"'{value}'"
        cond_str = condition.replace("?", str(value))
        self.condition.append(cond_str)
        return self

    def set(self, **kwargs):
        self.fields_values = kwargs
        return self

    def limit(self, num=None):
        if isinstance(num, int):
            self.limit_num = num
        elif num is not None:
            raise SqlBuildError("limit num should be int or None")
        return self

    def offset(self, num=None):
        if isinstance(num, int):
            self.offset_num = num
        elif num is not None:
            raise SqlBuildError("limit num should be int or None")
        return self

    def order_by(self, by=None, asc=True):
        if isinstance(by, str) and isinstance(asc, bool):
            self.order.append({
                "by": by,
                "asc": asc
            })
        elif by is not None:
            raise SqlBuildError("by should be str or None")
        return self

    def generate_sql(self):
        if self.op not in self.operations:
            raise SqlBuildError("operation should be in ['select', 'insert', 'update', 'delete']")
        table = self.table
        if self.op == "select":
            self.target.sort()
            target_str = "*" if len(self.target) == 0 else f"{', '.join(self.target)}"
            condition_str = "" if len(self.condition) == 0 else f"where {' and '.join(self.condition)}"
            order_str = "" if len(self.order) == 0 else "order by " + ' ,'.join(
                [f"{item['by']} {'asc' if item['asc'] else 'desc'}" for item in self.order])
            limit_str = "" if self.limit_num is None else f"limit {self.limit_num}"
            offset_str = "" if self.limit_num is None or self.offset_num is None else f"offset {self.offset_num}"
            self.sql_str = f"select {target_str} from {table} {condition_str} {order_str} {limit_str} {offset_str};"
        elif self.op == "insert":
            if len(self.fields_values) == 0:
                raise SqlBuildError("insert operation should take fields and values, but there are not defined")
            fields = ', '.join([item for item in self.fields_values.keys() if self.fields_values.get(item) is not None])
            values = ', '.join(list(
                map(
                    lambda item: f"'{item}'" if isinstance(item, str) else str(item),
                    [item for item in self.fields_values.values() if item is not None]
                )))
            self.sql_str = f"insert into {table} ({fields}) values ({values});"
        elif self.op == "update":
            if len(self.fields_values) != 1:
                raise SqlBuildError("update operation should only set 1 field")
            condition_str = "" if len(self.condition) == 0 else f"where {' and '.join(self.condition)}"
            field = list(self.fields_values.keys())[0]
            value = list(self.fields_values.values())[0]
            if isinstance(value, str):
                value = f"'{value}'"
            self.sql_str = f"update {table} set {field}={value} {condition_str}"
        elif self.op == "delete":
            if len(self.condition) == 0:
                raise SqlBuildError("delete operation should take at least 1 condition")
            condition_str = f"where {' and '.join(self.condition)}"
            self.sql_str = f"delete from {table} {condition_str}"
        return self.sql_str


if __name__ == "__main__":
    S1 = SqlBuilder("table", "select")
    S2 = SqlBuilder("table", "select")
    S1.where("id = ?", 1).where("name='cgy'").select("name").select("id").generate_sql()
    S2.generate_sql()

    S3 = SqlBuilder("table", "insert")
    S4 = SqlBuilder("table", "insert")
    S3.set(name="cgy", gender="male").generate_sql()
    # S4.generate_sql()

    S5 = SqlBuilder("table", "delete")
    S6 = SqlBuilder("table", "delete")
    S5.where("id = ?", 1).generate_sql()
    # S6.generate_sql()

    S7 = SqlBuilder("table", "update")
    S8 = SqlBuilder("table", "update")
    S9 = SqlBuilder("table", "update")
    S7.set(name="cgy").where("id = ?", 1).generate_sql()
    # S8.set(name="cgy", age=18).generate_sql()
    S9.set(gender="female").generate_sql()

    # print(S1)
    # print(S2)
    # print(S3)
    # # print(S4)
    # print(S5)
    # # print(S6)
    # print(S7)
    # print(S8)
    # print(S9)
    s = SqlBuilder("table", "select")
    s.select("id", "name", "age").where("id < 5").order_by("id", False).limit(2).offset(1).generate_sql()
    print(s)
