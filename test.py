import unittest

from TM1py import TM1Service

from pyrock import cube_view_create_mdx_statement


class Test(unittest.TestCase):
    tm1: TM1Service

    def setUp(self):
        self.tm1 = TM1Service(address="", port=12354, ssl=True, user="admin", password="apple")

    def test_cube_view_create_mdx_statement_happy_case(self):
        cube_name = "c1"
        bedrock_filter = "d1:e1+e2&d2:e3"
        expected_mdx = "SELECT\r\n" \
                       "NON EMPTY {UNION({TM1FILTERBYLEVEL({DESCENDANTS([D1].[D1].[E1])},0)}" \
                       ",{TM1FILTERBYLEVEL({DESCENDANTS([D1].[D1].[E2])},0)})} * " \
                       "{TM1FILTERBYLEVEL({DESCENDANTS([D2].[D2].[E3])},0)} ON 0\r\n" \
                       "FROM [C1]"

        mdx = cube_view_create_mdx_statement(
            tm1=self.tm1,
            cube_name=cube_name,
            cube_filter=bedrock_filter)

        self.assertEquals(expected_mdx, mdx)

    def test_cube_view_create_mdx_statement_skip_one_dimension(self):
        cube_name = "c1"
        bedrock_filter = "d1:e1"
        expected_mdx = "SELECT\r\n" \
                       "NON EMPTY {TM1FILTERBYLEVEL({DESCENDANTS([D1].[D1].[E1])},0)} * " \
                       "{TM1FILTERBYLEVEL({TM1SUBSETALL([D2].[D2])},0)} ON 0\r\n" \
                       "FROM [C1]"

        mdx = cube_view_create_mdx_statement(
            tm1=self.tm1,
            cube_name=cube_name,
            cube_filter=bedrock_filter)

        self.assertEquals(expected_mdx, mdx)

    def test_cube_view_create_mdx_statement_skip_all_dimensions(self):
        cube_name = "c1"
        bedrock_filter = ""
        expected_mdx = "SELECT\r\n" \
                       "NON EMPTY {TM1FILTERBYLEVEL({TM1SUBSETALL([D1].[D1])},0)} * " \
                       "{TM1FILTERBYLEVEL({TM1SUBSETALL([D2].[D2])},0)} ON 0\r\n" \
                       "FROM [C1]"

        mdx = cube_view_create_mdx_statement(
            tm1=self.tm1,
            cube_name=cube_name,
            cube_filter=bedrock_filter)

        self.assertEquals(expected_mdx, mdx)