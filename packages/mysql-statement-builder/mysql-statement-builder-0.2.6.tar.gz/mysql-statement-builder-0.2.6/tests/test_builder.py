from random import randint
from mysqlsb.builder import MySQLStatementBuilder


def test_insert_statement():
    stmnt = MySQLStatementBuilder(None)
    val_a = randint(0, 100)
    val_b = randint(0, 100)
    val_c = randint(0, 100)
    stmnt.insert('test_table', ['col_a', 'col_b', 'col_c']).set_values([val_a, val_b, val_c])

    assert stmnt.query == 'INSERT INTO `test_table` (`col_a`, `col_b`, `col_c`) VALUES (%s, %s, %s) '
    assert stmnt.values == [val_a, val_b, val_c]
