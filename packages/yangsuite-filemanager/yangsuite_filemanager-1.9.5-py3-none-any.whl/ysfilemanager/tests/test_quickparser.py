# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import errno
import os
import re
import unittest2 as unittest
import tempfile

from ysfilemanager.quickparser import (
    MODULE_STATEMENT,
    MODULE_SECOND_PART_STATEMENT,
    AUGMENT_STATEMENT,
    BASE_STATEMENT,
    IDENTIFIER,
    IDENTITY_STATEMENT,
    IMPORT_STATEMENT,
    INCLUDE_STATEMENT,
    REVISION_STATEMENT,
    name_and_revision_from_file,
    quick_parse,
)


class TestQuickParserRegex(unittest.TestCase):
    """Tests for Regex used in quickparser."""

    def test_re_module_statement(self):
        for positive, match in [
                ('module "Cisco-IOS-XR-types-splitted"+', "Cisco-IOS-XR-types-splitted"),
                ('module "Cisco-IOS-XR-types-splitted" +', "Cisco-IOS-XR-types-splitted"),
                ('module "Cisco-IOS-XR-types-splitted"', "Cisco-IOS-XR-types-splitted"),
                ('module Cisco-IOS-XR-types {', "Cisco-IOS-XR-types"),
        ]:
            with self.subTest(positive=positive, match=match):
                self.assertRegex(positive, MODULE_STATEMENT)
                self.assertEqual(match,
                                 MODULE_STATEMENT.match(positive).group(2))

        for positive, match in [
                ('module "Cisco-IOS-XR-types-splitted"+', "module"),
                ('module "Cisco-IOS-XR-types-splitted" +', "module"),
                ('module "Cisco-IOS-XR-types-splitted"', "module"),
                ('module Cisco-IOS-XR-types {', "module"),
                ('submodule "Cisco-IOS-XR-types-splitted"+', "submodule"),
                ('submodule "Cisco-IOS-XR-types-splitted" +', "submodule"),
                ('submodule "Cisco-IOS-XR-types-splitted"', "submodule"),
                ('submodule Cisco-IOS-XR-types {', "submodule"),
        ]:
            with self.subTest(positive=positive, match=match):
                self.assertRegex(positive, MODULE_STATEMENT)
                self.assertEqual(match,
                                 MODULE_STATEMENT.match(positive).group(1))

        for negative in [
                'submodule -Cisco-IOS-XR-types',
                'submodule Cisco-IOS-XR-types{'
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, MODULE_STATEMENT)

    def test_re_module_second_part_statement(self):
        for positive, match in [
                ('"Cisco-IOS-XR-types-splitted" {', "Cisco-IOS-XR-types-splitted"),
                ('"Cisco-IOS-XR-types-splitted"      {', "Cisco-IOS-XR-types-splitted"),
                ("'Cisco-IOS-XR-types-splitted' {", "Cisco-IOS-XR-types-splitted"),
                ("'Cisco-IOS-XR-types-splitted'      {", "Cisco-IOS-XR-types-splitted"),
        ]:
            with self.subTest(positive=positive, match=match):
                self.assertRegex(positive, MODULE_SECOND_PART_STATEMENT)
                self.assertEqual(match,
                                 MODULE_SECOND_PART_STATEMENT.match(positive).group(1))

        for negative in [
                '"Cisco-IOS-XR-types"{',
                'Cisco-IOS-XR-types{'
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, MODULE_SECOND_PART_STATEMENT)

    def test_re_identifier(self):
        """Test the IDENTIFIER regexp."""
        # identifier is a substring so it's not itself anchored;
        # let's anchor it as a self-contained regexp for testing
        ident = re.compile("^" + IDENTIFIER + "$")

        # Positive tests

        for positive in [
                "openconfig-interfaces",     # unquoted string
                "'openconfig-interfaces'",   # single-quoted string
                '"openconfig-interfaces"',   # double-quoted string
        ]:
            with self.subTest(positive=positive):
                self.assertEqual("openconfig-interfaces",
                                 ident.match(positive).group(1))

        for positive in [
                "ietf-yang-smiv2",    # contains numeric character
                "confd_dyncfg",       # contains underscore character
                "_temp",              # starts with underscore character
                "SNMPv2-MIB",         # mixed-case plus numeric
        ]:
            with self.subTest(positive=positive):
                self.assertRegex(positive, ident)
                self.assertEqual(positive, ident.match(positive).group(1))

        # Negative tests

        for negative in [
                "0modulename",     # cannot start with numeric character
                "-modulename",     # cannot start with dash character
                "hello world",     # cannot contain whitespace
                "hmm;invalid",     # cannot contain semicolon
                "  spaces   ",     # leading/trailing space not ignored
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, ident)

    def test_re_revision(self):
        """Test the REVISION_STATEMENT regular expression."""
        for positive, match in [
                ("revision 2017-11-20", "2017-11-20"),
                ("revision\t'2017-01-01'\t{", "2017-01-01"),
                ("revision 2017-01-01 { description foo; }",
                 "2017-01-01"),
                ('revision    "1999-12-31";', "1999-12-31"),
        ]:
            with self.subTest(positive=positive, match=match):
                self.assertRegex(positive, REVISION_STATEMENT)
                self.assertEqual(match,
                                 REVISION_STATEMENT.match(positive).group(1))

        for negative in [
                'revision 09-08-2010',       # wrong format
                'revision;'                  # no date
                'revision alpha',            # not a date
                'revision 2001-01-01 test',  # extra arg
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, REVISION_STATEMENT)

    def test_re_import(self):
        """Test the IMPORT_STATEMENT regular expression."""
        for positive, match, pfx in [
                ("import foobar {", "foobar", None),
                ("import foobar", "foobar", None),
                ("import openconfig-interfaces { prefix ocif; }",
                 "openconfig-interfaces", "ocif"),

        ]:
            with self.subTest(positive=positive, match=match, pfx=pfx):
                self.assertRegex(positive, IMPORT_STATEMENT)
                self.assertEqual(match,
                                 IMPORT_STATEMENT.match(positive).group(1))
                self.assertEqual(pfx,
                                 IMPORT_STATEMENT.match(positive).group(2))

        for negative in [
                'import {',        # missing argument
                'import foo;'      # missing substatements
                'import foo bar',  # extra arg
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, IMPORT_STATEMENT)

    def test_re_include(self):
        """Test the INCLUDE_STATEMENT regular expression."""
        for positive, match in [
                ("include foo ", "foo"),
                ("include ietf-snmp-ssh {", "ietf-snmp-ssh"),
                ("include ietf-snmp-common;", "ietf-snmp-common"),
        ]:
            with self.subTest(positive=positive, match=match):
                self.assertRegex(positive, INCLUDE_STATEMENT)
                self.assertEqual(match,
                                 INCLUDE_STATEMENT.match(positive).group(1))

        for negative in [
                "include the name",   # coincidental string
                "include {",          # missing arg
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, INCLUDE_STATEMENT)

    def test_re_identity(self):
        """Test the IDENTITY_STATEMENT regular expression."""
        for positive, match in [
                ("identity iana-interface-type {", "iana-interface-type"),
                ("identity shutdown-rpc;", "shutdown-rpc"),
        ]:
            with self.subTest(positive=positive, match=match):
                self.assertRegex(positive, IDENTITY_STATEMENT)
                self.assertEqual(match,
                                 IDENTITY_STATEMENT.match(positive).group(1))

        for negative in [
                "type identityref {",
                "Base identity from which specific interface types are",
                "identity {",    # missing arg
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, IDENTITY_STATEMENT)

    def test_re_base(self):
        """Test the BASE_STATEMENT regular expression."""
        for positive, match in [
                ("base if:interface-type;", "if:interface-type"),
                ("base iana-interface-type;", "iana-interface-type"),
                ("base ADDRESS_FAMILY;", "ADDRESS_FAMILY"),
                ("base oc-pkt-match-types:TCP_FLAGS;",
                 "oc-pkt-match-types:TCP_FLAGS"),
                ('base "oc-ni-types:ENDPOINT_TYPE";',
                 "oc-ni-types:ENDPOINT_TYPE"),
        ]:
            with self.subTest(positive=positive, match=match):
                self.assertRegex(positive, BASE_STATEMENT)
                self.assertEqual(match,
                                 BASE_STATEMENT.match(positive).group(1))

        for negative in [
                "base is being queried.",
                "base;",
                'based on value";',
                "base if:interface-type {",
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, BASE_STATEMENT)

    def test_re_augment(self):
        """Test the AUGMENT_STATEMENT regular expression."""
        for positive, match in [
            ('augment "/ocif:interfaces/ocif:interface/ocif:subinterfaces/" +',
             "/ocif:interfaces/ocif:interface/ocif:subinterfaces/"),
            ('augment "/ocif:interfaces/ocif:interface/lag:aggregation" {',
             "/ocif:interfaces/ocif:interface/lag:aggregation"),
            ('augment /ncm:netconf-state {', "/ncm:netconf-state"),
        ]:
            with self.subTest(positive=positive, match=match):
                self.assertRegex(positive, AUGMENT_STATEMENT)
                self.assertEqual(match,
                                 AUGMENT_STATEMENT.match(positive).group(1))

        for negative in [
            "// augment statements",                # comment
            "augment, or a '*'.  It identifies ",   # coincidental string
        ]:
            with self.subTest(negative=negative):
                self.assertNotRegex(negative, AUGMENT_STATEMENT)


class TestQuickParser(unittest.TestCase):
    """Sanity tests."""

    def test_name_and_revision_from_file(self):
        """Test the name_and_revision_from_file function."""
        with self.assertRaises(OSError) as cm:
            name_and_revision_from_file("/foo")
        self.assertEqual(cm.exception.errno, errno.ENOENT)

        with self.assertRaises(OSError) as cm:
            name_and_revision_from_file(os.path.dirname(__file__))
        self.assertEqual(cm.exception.errno, errno.EINVAL)

        DATA_DIR = os.path.join(
            os.path.dirname(__file__),
            'data', 'users', 'badfiles', 'repositories', 'badrepo')

        self.assertEqual(('cp1252', 'unknown'),
                         name_and_revision_from_file(
                             os.path.join(DATA_DIR, 'cp1252.yang'),
                             assume_correct_name=False))

        self.assertEqual(('openconfig-if-ethernet', '2015-11-20'),
                         name_and_revision_from_file(
                             os.path.join(DATA_DIR,
                                          'truncated@2015-11-20.yang'),
                             assume_correct_name=False))

        self.assertEqual(('nomodule', 'unknown'),
                         name_and_revision_from_file(
                             os.path.join(DATA_DIR, 'nomodule@unknown.yang'),
                             assume_correct_name=False))

    def test_quick_parse(self):
        """Test the quick_parse function."""
        DATA_DIR = os.path.join(
            os.path.dirname(__file__),
            'data', 'users', 'test', 'repositories', 'testrepo')

        filename = "openconfig-if-ethernet@2015-11-20.yang"
        with self.subTest(file=filename):
            path = os.path.join(DATA_DIR, filename)
            data = quick_parse(path)

            self.assertEqual("openconfig-if-ethernet", data['name'])
            self.assertEqual("module", data['kind'])
            self.assertEqual(["2015-11-20", "2015-10-09", "2015-08-20"],
                             data['revisions'])
            self.assertEqual({
                "iana-if-type": "ift",
                "ietf-yang-types": "yang",
                "openconfig-extensions": "oc-ext",
                "openconfig-interfaces": "ocif",
            }, data['imports'])
            self.assertEqual([], data['includes'])
            self.assertEqual(["openconfig-interfaces"], data['augments'])
            self.assertEqual([], data['derives-identities-from'])

        filename = "Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1@2015-11-09.yang"
        with self.subTest(file=filename):
            path = os.path.join(DATA_DIR, filename)
            data = quick_parse(path)

            self.assertEqual("Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1",
                             data['name'])
            self.assertEqual("submodule", data['kind'])
            self.assertEqual(["2015-11-09"], data['revisions'])
            self.assertEqual({
                "Cisco-IOS-XR-types": "xr",
                "ietf-inet-types": "inet",
                "ietf-yang-types": "yang",
            }, data['imports'])
            self.assertEqual([], data['includes'])
            self.assertEqual([], data['augments'])
            self.assertEqual('Cisco-IOS-XR-ipv4-bgp-oc-oper',
                             data['belongs-to'])
            self.assertEqual([], data['derives-identities-from'])

        filename = "Cisco-IOS-XR-ipv4-bgp-oc-oper@2015-11-09.yang"
        with self.subTest(file=filename):
            path = os.path.join(DATA_DIR, filename)
            data = quick_parse(path)

            self.assertEqual("Cisco-IOS-XR-ipv4-bgp-oc-oper", data['name'])
            self.assertEqual("module", data['kind'])
            self.assertEqual(["2015-11-09"], data['revisions'])
            self.assertEqual({
                "Cisco-IOS-XR-ipv4-bgp-datatypes": "dt1",
                "Cisco-IOS-XR-types": "xr",
                "ietf-inet-types": "inet",
            }, data['imports'])
            self.assertEqual(["Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1"],
                             data['includes'])
            self.assertEqual([], data['augments'])
            self.assertEqual([], data['derives-identities-from'])

        filename = "iana-if-type@2015-06-12.yang"
        with self.subTest(file=filename):
            path = os.path.join(DATA_DIR, filename)
            data = quick_parse(path)

            self.assertEqual("iana-if-type", data['name'])
            self.assertEqual("module", data['kind'])
            self.assertEqual(['2015-06-12', '2014-09-24', '2014-09-19',
                              '2014-07-03', '2014-05-19', '2014-05-08'],
                             data['revisions'])
            self.assertEqual({'ietf-interfaces': 'if'}, data['imports'])
            self.assertEqual([], data['includes'])
            self.assertEqual([], data['augments'])
            self.assertEqual(['ietf-interfaces'],
                             data['derives-identities-from'])


class TestQuickParserCornerCases(unittest.TestCase):
    """Tests for cornercases files."""

    empty_lines = [
        "\n\n\n",
        "\n\n\n\n\n\n",
        "\n\n\n\n\n\t\t\n",
        "",
        "   \t   \n\n   ",
        "   abc   def   \t\t\t\n\n\n\nghi\n  ",
        "\n",
        "abc\ndef\nghi\n\njkl\n\n\n",
        "\r\n",
        "\v",
        "\r",
    ]

    def test_quick_parse_for_split_module_name(self):
        """Test the quick_parse function for
            splitted Yang module/submodule name."""
        DATA_DIR = os.path.join(
            os.path.dirname(__file__),
            'data', 'users', 'test', 'corner-case-yang-modules')

        filename = "Cisco-IOS-XR-types-splitted-name@2015-06-29.yang"
        with self.subTest(file=filename):
            path = os.path.join(DATA_DIR, filename)
            data = quick_parse(path)

            self.assertEqual("Cisco-IOS-XR-types-splitted-name", data['name'])
            self.assertEqual("module", data['kind'])
            self.assertEqual(['2015-06-29', '2015-05-18',
                              '2015-01-19', '2013-07-22'],
                             data['revisions'])
            self.assertEqual({}, data['imports'])
            self.assertEqual([], data['includes'])
            self.assertEqual([], data['augments'])
            self.assertEqual([], data['derives-identities-from'])

        filename = "Cisco-IOS-XR-types-splitted-name2@2015-06-29.yang"
        with self.subTest(file=filename):
            path = os.path.join(DATA_DIR, filename)
            data = quick_parse(path)

            self.assertEqual("Cisco-IOS-XR-types-splitted-name2", data['name'])
            self.assertEqual("module", data['kind'])
            self.assertEqual(['2015-06-29', '2015-05-18',
                              '2015-01-19', '2013-07-22'],
                             data['revisions'])
            self.assertEqual({}, data['imports'])
            self.assertEqual([], data['includes'])
            self.assertEqual([], data['augments'])
            self.assertEqual([], data['derives-identities-from'])

        filename = "Cisco-IOS-XR-types-splitted-name3@2015-06-29.yang"
        with self.subTest(file=filename):
            path = os.path.join(DATA_DIR, filename)
            data = quick_parse(path)

            self.assertEqual("Cisco-IOS-XR-types-splitted-name3", data['name'])
            self.assertEqual("module", data['kind'])
            self.assertEqual(['2015-06-29', '2015-05-18',
                              '2015-01-19', '2013-07-22'],
                             data['revisions'])
            self.assertEqual({}, data['imports'])
            self.assertEqual([], data['includes'])
            self.assertEqual([], data['augments'])
            self.assertEqual([], data['derives-identities-from'])

    def test_quick_parse_for_files_starting_with_comments(self):
        """Test the quick_parse function for
            Yang modules that start with comments."""
        DATA_DIR = os.path.join(
            os.path.dirname(__file__),
            'data', 'users', 'test', 'corner-case-yang-modules')

        filename = "CISCO-IPSEC-MIB-file-starts-with-comments@2000-08-07.yang"
        path = os.path.join(DATA_DIR, filename)
        data = quick_parse(path)
        self.assertEqual("CISCO-IPSEC-MIB", data['name'])
        self.assertEqual("module", data['kind'])
        self.assertEqual(['2000-08-07'], data['revisions'])
        self.assertEqual({
            'IF-MIB': 'if-mib',
            'SNMPv2-TC': 'snmpv2-tc',
            'ietf-yang-smiv2': 'smiv2',
            'ietf-yang-types': 'yang'
        },
            data['imports'])
        self.assertEqual([], data['includes'])
        self.assertEqual([], data['augments'])
        self.assertEqual([], data['derives-identities-from'])

    def test_quick_parse_for_files_with_empty_first_lines(self):
        """Test the quick_parse function for
            Yang module/submodule with empty first lines."""
        DATA_DIR = os.path.join(
            os.path.dirname(__file__),
            'data', 'users', 'test', 'corner-case-yang-modules')

        filename = "cisco-nx-openconfig-acl-deviations.yang"
        path = os.path.join(DATA_DIR, filename)
        file = open(path, 'r')
        simple_yang_module = file.read()
        file.close()

        for empty_line in self.empty_lines:
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(empty_line.encode())
                temp_file.write(simple_yang_module.encode())
                temp_file.flush()
                with self.subTest(file_name=temp_file.name):
                    data = quick_parse(temp_file.name)
                    self.assertEqual("cisco-nx-openconfig-acl-deviations", data['name'])
