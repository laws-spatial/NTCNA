class Construct_columns:
  """
    Create columns for requesting data from "census"

    Attributes
    ---------------
    code_table: list

    List of racial codes from https:\\www.census.gov

    tables: list

    List of ACS tables to query

    race_col_suf: dict

    Dictionary of non-total population race suffixes

    totpop_col_suf: dict

    Dictionary of total population suffixes
  """
  def __init__(self, code_table, tables, race_col_suf, totpop_col_suf):
    self.code_table=code_table
    self.tables=tables 
    self.race_col_suf=race_col_suf 
    self.totpop_col_suf=totpop_col_suf

    assert isinstance(self.code_table, list), "code_table must be a list"
    assert isinstance(self.tables, list), "tables must be a list"
    assert isinstance(self.race_col_suf, dict), "race_col_suf must be a dictionary"
    assert isinstance(self.totpop_col_suf, dict), "totpop_col_suf must be a dictionary"

  def _totpop_columns(self):
    """Internal method to create total population columns"""
    col_suf_list = self.totpop_col_suf
    tables = self.tables

    # add columns to list
    cols = []
    for table in tables:
      col_suffixes = col_suf_list[table]
      new_cols = [f"{table}{col_suf}" for col_suf in col_suffixes]
      cols.extend(new_cols)

    return cols
  
  def _single_race_columns(self, table_code, race_code):
    """Create single race columns"""
    col_suffixes = self.race_col_suf[table_code]
    cols = [f"{table_code}{race_code}{suf}" for suf in col_suffixes]
    return cols

  def construct_columns(self):
    """Create complete list of columns including total population and race columns"""
    # Include name of geometry column
    cols = ["NAME"]

    # extend list with _totpop_columns method
    cols.extend(self._single_race_columns())

    # extend list with _totpop_columns method
    for table in self.tables:
      for code in self.code_table:
        new_cols = self._single_race_columns(table, code)
        cols.extend(new_cols)

    return cols