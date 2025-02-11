# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#

from __future__ import absolute_import, division, unicode_literals

from mo_testing.fuzzytestcase import FuzzyTestCase

from mo_sql_parsing import parse, format


class TestErrors(FuzzyTestCase):
    def test_dash_in_tablename(self):
        with self.assertRaises(["group", "order", "having", "limit", "where"]):
            #              012345678901234567890123456789012345678901234567890123456789
            parse("select * from coverage-summary.source.file.covered limit 20")

    def test_join_on_using_together(self):
        with self.assertRaises(["union", "order", "having", "limit", "where"]):
            parse("SELECT * FROM t1 JOIN t2 ON t1.id=t2.id USING (id)")

    def test_dash_in_tablename_general(self):
        with self.assertRaises(Exception):
            #              012345678901234567890123456789012345678901234567890123456789
            parse("select * from coverage-summary.source.file.covered limit 20")

    def test_join_on_using_together_general(self):
        with self.assertRaises(Exception):
            parse("SELECT * FROM t1 JOIN t2 ON t1.id=t2.id USING (id)")

    def test_bad_join_name(self):
        bad_json = {
            "select": {"value": "t1.field1"},
            "from": ["t1", {"left intro join": "t2", "on": {"eq": ["t1.id", "t2.id"]}}],
        }
        with self.assertRaises():
            format(bad_json)

    def test_order_by_must_follow_union(self):
        with self.assertRaises(["limit", "offset", "(at char 27"]):
            #      012345678901234567890123456789012345678901234567890123456789
            parse("select a from b order by a union select 2")

    def test_bad_order_by(self):
        with self.assertRaises(
            'Expecting {offset} | {StringEnd}, found "INTERSECT " (at char 95),'
            " (line:1, col:96)"
        ):
            parse(
                """SELECT document_name FROM documents GROUP BY document_type_code ORDER BY COUNT(*) DESC LIMIT 3 INTERSECT SELECT document_name FROM documents GROUP BY document_structure_code ORDER BY COUNT(*) DESC LIMIT 3"""
            )
