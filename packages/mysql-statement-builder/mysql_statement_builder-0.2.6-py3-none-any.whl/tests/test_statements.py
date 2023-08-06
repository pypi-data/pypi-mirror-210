from mysqlsb.statements import create_insert_statement


def test_create_insert_statement_backticks():
    stmnt = create_insert_statement('test_table', ['test_col_a', 'test_col_b'], backticks=True)
    assert stmnt == "INSERT INTO `test_table` (`test_col_a`, `test_col_b`) "


def test_create_insert_statement_no_backticks():
    stmnt = create_insert_statement('test_table', ['test_col_a', 'test_col_b'], backticks=False)
    assert stmnt == "INSERT INTO test_table (test_col_a, test_col_b) "
