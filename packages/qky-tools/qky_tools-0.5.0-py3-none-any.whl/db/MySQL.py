import typing
import pymysql


def getSQLByObjectKey(item: str,
                      tableName: str,
                      itemKeys: typing.Iterable = None,
                      itemKeyToMysqlKeyMap: typing.Dict = None,
                      notEscapeKeys: typing.Iterable = None) -> str:
    """
    根据 dict 对象生成sql语句
    :param item: 目标对象
    :param tableName: 对应表名
    :param itemKeys: item 中保存哪些key。默认为空（所有key）
    :param itemKeyToMysqlKeyMap: item中key和mysql中列名对应关系（为空或者对应为空时取 item的key名称）
    :param notEscapeKeys: 不需要加引号且转码的key（默认全部加引号并转码）
    :return: 生成的sql语句
    """
    # item 必须是 dict 类型
    assert isinstance(item, dict), '自定义错误：item 必须是字典类型，请检查传入的是否为对象，如果是对象，请用 __dict__ 转化为字典'

    # 获取 要插入 的item 的key 集合
    itemKeys = itemKeys or item.keys()

    # 生成map 集合
    itemKeyToMysqlKeyMap = itemKeyToMysqlKeyMap or {_: _ for _ in itemKeys}

    # 生成 insert 中 key 部分
    sql_key_part = f"({','.join([itemKeyToMysqlKeyMap.get(_, _) for _ in itemKeys])})"

    # 生成 insert 中 value 部分
    notEscapeKeys = notEscapeKeys or []
    save_values = [str(item.get(_)) if _ in notEscapeKeys else f"'{pymysql.converters.escape_string(str(item.get(_)))}'"
                   for _ in
                   itemKeys]
    sql_value_part = f"({','.join(save_values)})"

    sql = f"INSERT INTO {tableName} {sql_key_part} VALUES {sql_value_part}"

    return sql


def getExecuteManyParameters(items: typing.Iterable,
                             tableName: str,
                             itemKeys=None,
                             itemKeyToMysqlKeyMap=None,
                             notEscapeKeys=None):
    """
    根据 dict 对象生成sql语句
    :param items: 目标对象集合
    :param tableName: 对应表名
    :param itemKeys: item 中保存哪些key。默认为空（所有key）
    :param itemKeyToMysqlKeyMap: item中key和mysql中列名对应关系（为空或者对应为空时取 item的key名称）
    :param notEscapeKeys: 不需要加引号且转码的key（默认全部加引号并转码）
    :return: 生成的insertmany语句和对应的参数
    """
    # item 必须是 dict 类型
    assert isinstance(items, list), 'items 必须为list'
    assert len(items) > 0, 'items中元素个数必须大于1'

    # 待返回的参数
    paras = []
    notEscapeKeys = notEscapeKeys or []

    # 取出第一个作为样例
    item_sample = items[0]

    # 获取 要插入 的item 的key 集合
    itemKeys = itemKeys or item_sample.keys()

    # 对items 中每个item 生成参数
    for item in items:
        para = [str(item.get(_)) if _ in notEscapeKeys else f"{pymysql.converters.escape_string(str(item.get(_)))}"
                for _ in
                itemKeys]

        paras.append(para)

    # 生成insert 部分
    itemKeyToMysqlKeyMap = itemKeyToMysqlKeyMap or {_: _ for _ in itemKeys}
    sql_key_part = f"({','.join([itemKeyToMysqlKeyMap.get(_, _) for _ in itemKeys])})"
    sql_value_part = f"({','.join(['%s' for _ in para])})"
    sql = f"INSERT INTO {tableName} {sql_key_part} VALUES {sql_value_part}"
    return sql, paras


def getInitTableSQLByItem(item,
                          table_name="",
                          int_cols: typing.Iterable = None,
                          text_cols: typing.Iterable = None,
                          date_cols: typing.Iterable = None,
                          primary_key: str = None,
                          varchar_length=255,
                          int_length=10,
                          energy="InnoDB") -> str:
    """
    基于给定的对象（必须是dict）生成创建mysql表的sql
    :param item: 对象
    :param table_name: 表名
    :param int_cols: 映射为 int 的列集合
    :param text_cols: 映射为 text 的列集合
    :param date_cols: 映射为 日期（datetime）的列集合
    :param primary_key: 映射为主键的列集合
    :param varchar_length: 映射到表中 varchar 长度（默认255）
    :param int_length: 映射到表中 int 长度（默认10）
    :param energy: 引擎（默认InnoDB）
    :return:
    """
    # 表名不能为空
    assert table_name, "table_name 不能为空"

    int_cols = int_cols or [],
    text_cols = text_cols or [],
    date_cols = date_cols or [],

    # 生成表中的所有列
    cols = item.keys()

    def get_col_desc(col):
        if col in int_cols:
            return f"int({int_length})"
        elif col in text_cols:
            return "text"
        elif col in date_cols:
            return "datetime"
        else:
            return f"varchar({varchar_length})"

    # 列定义部分
    cols = [f"{col} {get_col_desc(col)}" for col in cols]

    # 主键部分
    if primary_key:
        cols.append(f"PRIMARY KEY ({primary_key})")

    # 生成sql
    sql = f"""CREATE TABLE {table_name} ( {','.join(cols)} ) ENGINE={energy} DEFAULT CHARSET=utf8 COLLATE=utf8_bin"""

    return sql
