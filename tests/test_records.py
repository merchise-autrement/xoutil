# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# test_records
#----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-09-22

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


import unittest
from mock import patch
from datetime import datetime, date

from xoutil.records import record, datetime_reader, date_reader


class _table(record):
    ID = 0
    _id_reader = lambda val: int(val)


class person(_table):
    NAME = 1
    LASTNAME = 2
    BIRTHDATE = 3

    _birthdate_reader = datetime_reader('%Y-%m-%d')

    @property
    def current_age(self):
        from datetime import datetime
        today = datetime.today()
        return self.age_when(today)

    def age_when(self, today):
        res = today - self.birthdate
        return int(res.days//365.25)


class TestRecords(unittest.TestCase):
    def test_records(self):
        from datetime import datetime
        _manu = ('1', 'Manuel', 'Vazquez', '1978-10-21')
        manu = person(_manu)

        self.assertEqual(1, person.get_field(_manu, person.ID))
        self.assertEqual(1, manu.id)
        self.assertEqual(11, manu.age_when(datetime(1989, 10, 21)))
        self.assertEqual(35, manu.age_when(datetime(2014, 9, 22)))

    def test_descriptor(self):
        class INVOICE(record):
            ID = 0
            REFERER = 1

            # The following attribute will be overwritten by the fields
            # descriptor for REFERER.
            referer = 'overwritten'

        assert INVOICE.referer and INVOICE.id
        line = (1, 'MVA.98')
        self.assertEqual(INVOICE.get_field(line, INVOICE.ID), 1)
        invoice = INVOICE(line)
        self.assertEqual(invoice.referer, 'MVA.98')
        self.assertEqual(invoice[INVOICE.REFERER], invoice.referer)

    def test_readers(self):
        from datetime import datetime, timedelta

        class INVOICE(record):
            ID = 0
            REFERER = 1
            CREATED_DATETIME = 2
            UPDATE_DATETIME = 3
            _DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

            @staticmethod
            def _created_datetime_reader(value):
                return datetime.strptime(value, INVOICE._DATETIME_FORMAT)

            # implicit staticmethod
            def _update_datetime_reader(value):
                return datetime.strptime(value, INVOICE._DATETIME_FORMAT)

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        line = (1, 'MVA.98',
                yesterday.strftime(INVOICE._DATETIME_FORMAT),
                tomorrow.strftime(INVOICE._DATETIME_FORMAT))
        self.assertEqual(
            INVOICE.get_field(line, INVOICE.CREATED_DATETIME),
            yesterday
        )
        self.assertEqual(
            INVOICE.get_field(line, INVOICE.UPDATE_DATETIME),
            tomorrow
        )

        invoice = INVOICE(line)
        self.assertEqual(invoice.created_datetime, yesterday)
        self.assertEqual(invoice.update_datetime, tomorrow)

    def test_default_values(self):
        from xoutil.records import float_reader

        class LINE(record):
            DEBIT = 'Debit'
            CREDIT = 'Credit'
            _debit_reader = float_reader(nullable=True, default=0)
            _credit_reader = float_reader(nullable=True)

        nodata = {}
        partialdata = {'Credit': 0}
        nulls = {'Debit': ''}
        self.assertEqual(LINE.get_field(nodata, LINE.DEBIT), 0)
        self.assertIsNone(LINE.get_field(nodata, LINE.CREDIT))
        self.assertEqual(LINE.get_field(partialdata, LINE.DEBIT), 0)
        self.assertEqual(LINE.get_field(partialdata, LINE.CREDIT), 0)
        self.assertEqual(LINE.get_field(nulls, LINE.DEBIT), 0)


FMT = '%Y-%m-%d'


class TestDateTimeReader(unittest.TestCase):
    def setUp(self):
        # clear lru caches for each test... Needed so that imports done inside
        # datetime_reader are mockable.
        datetime_reader.cache_clear()

    def test_strict(self):
        class rec(record):
            MOMENT = 0
            _moment_reader = datetime_reader(FMT)

        inst = rec(['2014-12-17'])
        self.assertEquals('2014-12-17', inst.moment.strftime(FMT))

        inst = rec(['201-12-17'])
        with self.assertRaises(ValueError):
            self.assertEquals('201-12-17', inst.moment.strftime(FMT))

    def test_relaxed_but_nonnullable_with_dateutil(self):
        class rec(record):
            MOMENT = 0
            _moment_reader = datetime_reader(FMT, nullable=False, strict=False)

        inst = rec(['201-12-17'])
        self.assertEquals(inst.moment, datetime(201, 12, 17))

    @patch('dateutil.parser.parse', None)
    def test_relaxed_but_nonnullable_without_dateutil(self):
        class rec(record):
            MOMENT = 0
            _moment_reader = datetime_reader(FMT, nullable=False, strict=False)

        inst = rec(['201-12-17'])
        with self.assertRaises(ValueError):
            self.assertIsNone(inst.moment)

    @patch('dateutil.parser.parse', None)
    def test_relax_with_default(self):
        class rec(record):
            MOMENT = 0
            _moment_reader = datetime_reader(FMT, default=0, strict=False)

        inst = rec(['201-12-17'])
        self.assertEquals(inst.moment, 0)


class TestDateReader(unittest.TestCase):
    def setUp(self):
        # clear lru caches for each test... Needed so that imports done inside
        # date_reader are mockable.
        date_reader.cache_clear()
        datetime_reader.cache_clear()

    def test_date_reader_nullable(self):
        class rec(record):
            WHEN = 'date'
            _when_reader = date_reader(FMT, nullable=True)

        inst = rec({'date': '2015-01-01'})
        self.assertEquals(inst.when, date(2015, 1, 1))

        inst = rec({})
        self.assertIsNone(inst.when)

        inst = rec({'date': '201-01-01'})
        with self.assertRaises(ValueError):
            inst.when

    def test_date_reader_relaxed_with_dateutil(self):
        class rec(record):
            WHEN = 'date'
            _when_reader = date_reader(FMT, strict=False)

        inst = rec({'date': '201-01-01'})
        self.assertEquals(inst.when, date(201, 1, 1))

    @patch('dateutil.parser.parse', None)
    def test_date_reader_relaxed_nullable_no_dateutil(self):
        class rec(record):
            WHEN = 'date'
            _when_reader = date_reader(FMT, nullable=True, strict=False)

        inst = rec({'date': '201-01-01'})
        self.assertIsNone(inst.when)

    @patch('dateutil.parser.parse', None)
    def test_date_reader_relaxed_no_dateutil(self):
        class rec(record):
            WHEN = 'date'
            _when_reader = date_reader(FMT, strict=False)

        inst = rec({'date': '201-01-01'})
        with self.assertRaises(ValueError):
            self.assertIsNone(inst.when)
