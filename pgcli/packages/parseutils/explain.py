import sqlparse

def strip_explain(sql):
    """
    Strip existing EXPLAIN section from query.

    We need to handle these scenarios:
      1. EXPLAIN                  --> sqlparse [keyword]
      2. EXPLAIN ANALYZE          --> sqlparse [keyword, keyword]
      2. EXPLAIN ANALYZE VERBOSE  --> sqlparse [keyword, keyword, keyword]
      4. EXPLAIN (...)            --> sqlparse [keyword, parenthesis]
      5. EXPLAIN(...)             --> sqlparse [function]
    """

    # Helper function to check for SQL keyword / function name
    keyword = lambda tok, kw: tok.is_keyword and tok.normalized == kw.upper()
    fn_name = lambda tok, fn: type(tok) == sqlparse.sql.Function \
                              and t1.get_name().upper() == fn.upper()

    # Fetch the first three "real" tokens (not whitespace or comment)
    stmt = sqlparse.parse(sql.strip())[0]
    t1_idx, t1 = stmt.token_next(-1,     skip_ws=True, skip_cm=True)
    t2_idx, t2 = stmt.token_next(t1_idx, skip_ws=True, skip_cm=True)
    t3_idx, t3 = stmt.token_next(t2_idx, skip_ws=True, skip_cm=True)

    if keyword(t1, 'EXPLAIN'):
        # EXPLAIN [ANALYZE] [VERBOSE]
        stmt.tokens.pop(t1_idx)
        if keyword(t2, 'ANALYZE'):
            stmt.tokens.pop(t2_idx-1)
            if keyword(t3, 'VERBOSE'):
                stmt.tokens.pop(t3_idx-2)
        # EXPLAIN (...)
        elif type(t2) == sqlparse.sql.Parenthesis:
            stmt.tokens.pop(t2_idx-1)
    elif type(t1) == sqlparse.sql.Function and t1.get_name().upper() == 'EXPLAIN':
        # EXPLAIN(...)
        stmt.tokens.pop(t1_idx)
    else:
        # Not EXPLAIN
        return sql

    # return modified query
    sql = str(sqlparse.sql.TokenList(stmt.tokens))
    return sql
