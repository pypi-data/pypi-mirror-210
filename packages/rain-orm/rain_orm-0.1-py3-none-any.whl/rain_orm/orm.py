try:
    from rain_orm.error import DefineError, SqlBuildError
    from rain_orm.sql_builder import SqlBuilder
    from rain_orm.db import DB
except ImportError:
    from error import DefineError, SqlBuildError
    from sql_builder import SqlBuilder
    from db import DB
import threading


class RainORM(object):
    db = None
    __lock = threading.Lock()

    def __init__(self):
        if not isinstance(self.__table__, str):
            raise DefineError(f"type(__table__) should be str, but is {type(self.__table__)}")
        if not isinstance(self.__instance__, dict):
            raise DefineError(f"type(__instance__) should be dict, but is {type(self.__instance__)}")

        self.instance = self.__instance__.copy()
        self.sql_builder = SqlBuilder(self.__table__)

    def __str__(self):
        instance = "{\n"
        for k, v in self.instance.items():
            instance += f"\t\t{k}: {v},\n"
        instance += "\t}"
        return f"\033[0;36m<<{self.__class__.__name__} {id(self)}\033[0m\n" \
               f"\t\033[0;32m.table\033[0m = {self.__table__}\n" \
               f"\t\033[0;32m.instance\033[0m = {instance}\n" \
               f"\033[0;36m>>\033[0m\n"

    def __repr__(self):
        return str(self)

    def __getattr__(self, key):
        if key == "table":
            return self.__table__
        else:
            return self.instance.get(key)

    @classmethod
    def connect(cls, host, port, user, password, database):
        cls.db = DB(host=host, user=user, password=password, database=database, port=port)

    def select(self, *args):
        self.sql_builder.select(*args)
        return self

    def where(self, condition, value=None):
        self.sql_builder.where(condition, value)
        return self

    def set(self, **kwargs):
        self.sql_builder.set(**kwargs)
        for k, v in kwargs.items():
            self.instance[k] = v
        return self

    def one(self):
        self.sql_builder.set_operation("select")
        data = self.execute(num="one")
        target = sorted(self.instance.keys()) if len(self.sql_builder.target) == 0 else self.sql_builder.target
        if data is not None:
            for field, key in zip(data, target):
                self.instance[key] = field
            return self
        else:
            return None

    def all(self):
        self.sql_builder.set_operation("select")
        datas = self.execute(num="all")
        new_instances = []
        target = sorted(self.instance.keys()) if len(self.sql_builder.target) == 0 else self.sql_builder.target
        for data in datas:
            new_instance = self.__class__()
            for field, key in zip(data, target):
                new_instance.instance[key] = field
            new_instances.append(new_instance)
        return new_instances

    def create(self):
        self.sql_builder.set_operation("insert")
        return self.execute()

    def update(self):
        self.sql_builder.set_operation("update")
        return self.execute()

    def delete(self):
        self.sql_builder.set_operation("delete")
        return self.execute()

    def execute(self, num=None):
        if len(self.sql_builder.target) == 0:
            self.sql_builder.select(*list(self.instance.keys()))
        sql = self.sql_builder.generate_sql()
        data = None
        with self.__lock:
            try:
                if self.sql_builder.op == "select":
                    if num == "one":
                        self.db.cursor.execute(sql)
                        data = self.db.cursor.fetchone()
                    elif num == "all":
                        self.db.cursor.execute(sql)
                        data = self.db.cursor.fetchall()
                else:
                    r = self.db.cursor.execute(sql)
                    self.db.commit()
                    print(r)
                    return True
            except Exception as e:
                print(e)
                self.db.rollback()
                return False
        return data


if __name__ == "__main__":
    ORM.connect(host="localhost", port=3306, user="root", password='123456', database="student_management")
