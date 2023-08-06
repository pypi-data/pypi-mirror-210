"""Tests for mysql_tools.
"""

import pytest
from pykn_mysqltools import utilities as ut

class TestCSVObject:
    """Test CSVObject class.
    """
    def test_csvobject(self):
        csv_object = ut.CSVObject("src/tests/resources/csvobject.csv")
        assert csv_object.headers == ["col1", "col2", "col3"]
        assert csv_object.rows == [
            ["a", "b", "c"],
            ["d", "e", "f"],
            ["g", "h", "i"]
        ]
        assert csv_object.columns == [
            ["a", "d", "g"],
            ["b", "e", "h"],
            ["c", "f", "i"]
        ]


    def test_clean_headers(self):
        csv_object = ut.CSVObject("src/tests/resources/csvobject_dirty.csv")
        assert csv_object.clean_headers == ["col1", "col2", "col3"]


class TestGetValueType:
    """Test get_value_type function.
    """
    def test_nums(self):
        assert ut.get_value_type("0") == "TINYINT"
        assert ut.get_value_type("1") == "TINYINT"
        assert ut.get_value_type("10") == "INT"
        assert ut.get_value_type("1.0") == "FLOAT"


    def test_text(self):
        varchar_255 = ""
        for _ in range(0,255):
            varchar_255 += "A"
        assert ut.get_value_type(varchar_255) == "VARCHAR(255)"
        text = ""
        for _ in range(0,65535):
            text += "A"
        assert ut.get_value_type(text) == "TEXT"


    @pytest.mark.skip(reason="Typically freezes up.")
    def test_big_text(self):
        medium_text = ""
        for _ in range(0,16777215):
            medium_text += "A"
        assert ut.get_value_type(medium_text) == "MEDIUMTEXT"
        long_text = ""
        for _ in range(0,4294967295):
            long_text += "A"
        assert ut.get_value_type(long_text) == "LONGTEXT"
        with pytest.raises(Exception):
            too_big = ""
            for _ in range(0,4294967296):
                too_big += "A"


class TestGetColumnType:
    """Test get_column_type function.
    """
    def test_one_type(self):
        values = ["ABCDEFG", "ABCDEFG", "ABCDEFG"]
        assert ut.get_column_type(values) == "VARCHAR(255)"
        values = ["10", "11", "12"]
        assert ut.get_column_type(values) == "INT"


    def test_one_varchar(self):
        values = ["ABCDEFG", "10", "11"]
        assert ut.get_column_type(values) == "VARCHAR(255)"


    def test_one_float(self):
        values = ["1.0", "10", "11"]
        assert ut.get_column_type(values) == "FLOAT"


    def test_one_int(self):
        values = ["10", "0", "1"]
        assert ut.get_column_type(values) == "INT"


    def test_just_tinyint(self):
        values = ["0", "1", "0", "1"]
        assert ut.get_column_type(values) == "TINYINT"
