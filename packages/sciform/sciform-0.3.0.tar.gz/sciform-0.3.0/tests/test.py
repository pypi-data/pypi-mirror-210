from dataclasses import dataclass
import unittest

from sciform import sfloat


@dataclass
class SingleFloatCase:
    num: float
    fmt_spec_result_mapping: dict[str, str]


fmtcases: dict[float, dict[str, str]] = {
    123.456: {'': '123.456',
              'f': '123.456',
              'e': '1.23456e+02',
              'r': '123.456e+00',
              '#r': '0.123456e+03',
              '.3': '123.456',
              '.3f': '123.456',
              '.3e': '1.235e+02',
              '.3r': '123.456e+00',
              '#.3r': '0.123e+03',
              '!3': '123',
              '!3f': '123',
              '!3e': '1.23e+02',
              '!3r': '123e+00',
              '#!3r': '0.123e+03',
              '+': '+123.456',
              '+f': '+123.456',
              '+e': '+1.23456e+02',
              '+r': '+123.456e+00',
              '+#r': '+0.123456e+03',
              ' ': ' 123.456',
              ' f': ' 123.456',
              ' e': ' 1.23456e+02',
              ' r': ' 123.456e+00',
              ' #r': ' 0.123456e+03',
              '4': '  123.456',
              '4f': '  123.456',
              '4e': '    1.23456e+02',
              '4r': '  123.456e+00',
              '#4r': '    0.123456e+03',
              },
    -0.031415: {'': '-0.031415',
                'f': '-0.031415',
                'e': '-3.1415e-02',
                'r': '-31.415e-03',
                '#r': '-31.415e-03',
                '.3': '-0.031',
                '.3f': '-0.031',
                '.3e': '-3.141e-02',
                '.3r': '-31.415e-03',
                '#.3r': '-31.415e-03',
                '!3': '-0.0314',
                '!3f': '-0.0314',
                '!3e': '-3.14e-02',
                '!3r': '-31.4e-03',
                '#!3r': '-31.4e-03',
                '+': '-0.031415',
                '+f': '-0.031415',
                '+e': '-3.1415e-02',
                '+r': '-31.415e-03',
                '+#r': '-31.415e-03',
                ' ': '-0.031415',
                ' f': '-0.031415',
                ' e': '-3.1415e-02',
                ' r': '-31.415e-03',
                ' #r': '-31.415e-03',
                '4': '-    0.031415',
                '4f': '-    0.031415',
                '4e': '-    3.1415e-02',
                '4r': '-   31.415e-03',
                '#4r': '-   31.415e-03',
                '%': '-3.1415%'
                },
    0: {'': '0',
        'f': '0',
        'e': '0e+00',
        'r': '0e+00',
        '#r': '0e+00',
        '.3': '0.000',
        '.3f': '0.000',
        '.3e': '0.000e+00',
        '.3r': '0.000e+00',
        '#.3r': '0.000e+00',
        '!3': '0.00',
        '!3f': '0.00',
        '!3e': '0.00e+00',
        '!3r': '0.00e+00',
        '#!3r': '0.00e+00',
        '0=2.3': '000.000',
        '0=2.3f': '000.000',
        '0=2.3e': '000.000e+00',
        '0=2.3r': '000.000e+00',
        '0=#2.3r': '000.000e+00',
        '0=2!3': '000.00',
        '0=2!3f': '000.00',
        '0=2!3e': '000.00e+00',
        '0=2!3r': '000.00e+00',
        '0=#2!3r': '000.00e+00'},
    float('nan'): {'': 'nan',
                   'E': 'NAN'},
    float('inf'): {'': 'inf',
                   'E': 'INF'},
    float('-inf'): {'': '-inf',
                    'E': '-INF'}
}


class TestFormatting(unittest.TestCase):
    # TODO: exp symbol capitalization
    def test_fixed_point(self):
        cases: dict[float, dict[str, str]] = {
            123.456: {
                'f': '123.456',
                '.-3f': '0',
                '.-2f': '100',
                '.-1f': '120',
                '.0f': '123',
                '.1f': '123.5',
                '.2f': '123.46',
                '.3f': '123.456',
                '.4f': '123.4560',
                '!1f': '100',
                '!2f': '120',
                '!3f': '123',
                '!4f': '123.5',
                '!5f': '123.46',
                '!6f': '123.456',
                '!7f': '123.4560'
            },
            0.00062607: {
                'f': '0.00062607',
                '.-1f': '0',
                '.0f': '0',
                '.1f': '0.0',
                '.2f': '0.00',
                '.3f': '0.001',
                '.4f': '0.0006',
                '.5f': '0.00063',
                '.6f': '0.000626',
                '.7f': '0.0006261',
                '.8f': '0.00062607',
                '.9f': '0.000626070',
                '!1f': '0.0006',
                '!2f': '0.00063',
                '!3f': '0.000626',
                '!4f': '0.0006261',
                '!5f': '0.00062607',
                '!6f': '0.000626070',
            }
        }
        for num, fmt_dict in cases.items():
            for format_spec, expected_num_str in fmt_dict.items():
                snum = sfloat(num)
                snum_str = f'{snum:{format_spec}}'
                with self.subTest(num=num, format_spec=format_spec,
                                  expected_num_str=expected_num_str,
                                  actual_num_str=snum_str):
                    self.assertEqual(snum_str, expected_num_str)

    def test_scientific(self):
        cases: dict[float, dict[str, str]] = {
            123.456: {
                'e': '1.23456e+02',
                '.-3e': '0e+02',  # TODO: What actually is expected here?
                '.-2e': '0e+02',  # TODO: What actually is expected here?
                '.-1e': '0e+02',  # TODO: What actually is expected here?
                '.0e': '1e+02',
                '.1e': '1.2e+02',
                '.2e': '1.23e+02',
                '.3e': '1.235e+02',
                '.4e': '1.2346e+02',
                '!1e': '1e+02',
                '!2e': '1.2e+02',
                '!3e': '1.23e+02',
                '!4e': '1.235e+02',
                '!5e': '1.2346e+02',
                '!6e': '1.23456e+02',
                '!7e': '1.234560e+02'
            },
            0.00062607: {
                'e': '6.2607e-04',
                '.-2e': '0e-04',  # TODO: What actually is expected here?
                '.-1e': '10e-04',  # TODO: This is a problem I think
                '.0e': '6e-04',
                '.1e': '6.3e-04',
                '.2e': '6.26e-04',
                '.3e': '6.261e-04',
                '.4e': '6.2607e-04',
                '.5e': '6.26070e-04',
                '.6e': '6.260700e-04',
                '!1e': '6e-04',
                '!2e': '6.3e-04',
                '!3e': '6.26e-04',
                '!4e': '6.261e-04',
                '!5e': '6.2607e-04',
                '!6e': '6.26070e-04',
            }
        }
        for num, fmt_dict in cases.items():
            for format_spec, expected_num_str in fmt_dict.items():
                snum = sfloat(num)
                snum_str = f'{snum:{format_spec}}'
                with self.subTest(num=num, format_spec=format_spec,
                                  expected_num_str=expected_num_str,
                                  actual_num_str=snum_str):
                    self.assertEqual(snum_str, expected_num_str)

    def test_engineering(self):
        cases: dict[float, dict[str, str]] = {
            123.456: {
                'r': '123.456e+00',
                '.-3r': '0e+00',  # TODO: What actually is expected here?
                '.-2r': '100e+00',  # TODO: What actually is expected here?
                '.-1r': '120e+00',  # TODO: What actually is expected here?
                '.0r': '123e+00',
                '.1r': '123.5e+00',
                '.2r': '123.46e+00',
                '.3r': '123.456e+00',
                '.4r': '123.4560e+00',
                '!1r': '100e+00',
                '!2r': '120e+00',
                '!3r': '123e+00',
                '!4r': '123.5e+00',
                '!5r': '123.46e+00',
                '!6r': '123.456e+00',
                '!7r': '123.4560e+00'
            },
            1234.56: {
                'r': '1.23456e+03',
                '.-3r': '0e+03',  # TODO: What actually is expected here?
                '.-2r': '0e+03',  # TODO: What actually is expected here?
                '.-1r': '0e+03',  # TODO: What actually is expected here?
                '.0r': '1e+03',
                '.1r': '1.2e+03',
                '.2r': '1.23e+03',
                '.3r': '1.235e+03',
                '.4r': '1.2346e+03',
                '.5r': '1.23456e+03',
                '!1r': '1e+03',
                '!2r': '1.2e+03',
                '!3r': '1.23e+03',
                '!4r': '1.235e+03',
                '!5r': '1.2346e+03',
                '!6r': '1.23456e+03',
                '!7r': '1.234560e+03'
            },
            12345.6: {
                'r': '12.3456e+03',
                '.-3r': '0e+03',  # TODO: What actually is expected here?
                '.-2r': '0e+03',  # TODO: What actually is expected here?
                '.-1r': '10e+03',  # TODO: What actually is expected here?
                '.0r': '12e+03',
                '.1r': '12.3e+03',
                '.2r': '12.35e+03',
                '.3r': '12.346e+03',
                '.4r': '12.3456e+03',
                '.5r': '12.34560e+03',
                '!1r': '10e+03',
                '!2r': '12e+03',
                '!3r': '12.3e+03',
                '!4r': '12.35e+03',
                '!5r': '12.346e+03',
                '!6r': '12.3456e+03',
                '!7r': '12.34560e+03'
            }
        }
        for num, fmt_dict in cases.items():
            for format_spec, expected_num_str in fmt_dict.items():
                snum = sfloat(num)
                snum_str = f'{snum:{format_spec}}'
                with self.subTest(num=num, format_spec=format_spec,
                                  expected_num_str=expected_num_str,
                                  actual_num_str=snum_str):
                    self.assertEqual(snum_str, expected_num_str)

    def test_engineering_shifted(self):
        cases: dict[float, dict[str, str]] = {
            123.456: {
                '#r': '0.123456e+03',
                '#.-3r': '0e+03',  # TODO: What actually is expected here?
                '#.-2r': '0e+03',  # TODO: What actually is expected here?
                '#.-1r': '0e+03',  # TODO: What actually is expected here?
                '#.0r': '0e+03',
                '#.1r': '0.1e+03',
                '#.2r': '0.12e+03',
                '#.3r': '0.123e+03',
                '#.4r': '0.1235e+03',
                '#!1r': '0.1e+03',
                '#!2r': '0.12e+03',
                '#!3r': '0.123e+03',
                '#!4r': '0.1235e+03',
                '#!5r': '0.12346e+03',
                '#!6r': '0.123456e+03',
                '#!7r': '0.1234560e+03'
            },
            1234.56: {
                '#r': '1.23456e+03',
                '#.-3r': '0e+03',  # TODO: What actually is expected here?
                '#.-2r': '0e+03',  # TODO: What actually is expected here?
                '#.-1r': '0e+03',  # TODO: What actually is expected here?
                '#.0r': '1e+03',
                '#.1r': '1.2e+03',
                '#.2r': '1.23e+03',
                '#.3r': '1.235e+03',
                '#.4r': '1.2346e+03',
                '#.5r': '1.23456e+03',
                '#!1r': '1e+03',
                '#!2r': '1.2e+03',
                '#!3r': '1.23e+03',
                '#!4r': '1.235e+03',
                '#!5r': '1.2346e+03',
                '#!6r': '1.23456e+03',
                '#!7r': '1.234560e+03'
            },
            12345.6: {
                '#r': '12.3456e+03',
                '#.-3r': '0e+03',  # TODO: What actually is expected here?
                '#.-2r': '0e+03',  # TODO: What actually is expected here?
                '#.-1r': '10e+03',  # TODO: What actually is expected here?
                '#.0r': '12e+03',
                '#.1r': '12.3e+03',
                '#.2r': '12.35e+03',
                '#.3r': '12.346e+03',
                '#.4r': '12.3456e+03',
                '#.5r': '12.34560e+03',
                '#!1r': '10e+03',
                '#!2r': '12e+03',
                '#!3r': '12.3e+03',
                '#!4r': '12.35e+03',
                '#!5r': '12.346e+03',
                '#!6r': '12.3456e+03',
                '#!7r': '12.34560e+03'
            }
        }
        for num, fmt_dict in cases.items():
            for format_spec, expected_num_str in fmt_dict.items():
                snum = sfloat(num)
                snum_str = f'{snum:{format_spec}}'
                with self.subTest(num=num, format_spec=format_spec,
                                  expected_num_str=expected_num_str,
                                  actual_num_str=snum_str):
                    self.assertEqual(snum_str, expected_num_str)

    def test_separators(self):
        cases: dict[float, dict[str, str]] = {
            123456.654321: {
                '': '123456.654321',
                ',': '123,456.654321',
                ',.s': '123,456.654 321',
                ',._': '123,456.654_321',
                '_._': '123_456.654_321',
                's.s': '123 456.654 321',
                'n,n': '123456,654321',
                '.,': '123.456,654321',
                '.,s': '123.456,654 321',
                '.,_': '123.456,654_321',
                '_,_': '123_456,654_321',
                's,s': '123 456,654 321',
            },
            12345.54321: {
                '': '12345.54321',
                ',': '12,345.54321',
                ',.s': '12,345.543 21',
                ',._': '12,345.543_21',
                '_._': '12_345.543_21',
                's.s': '12 345.543 21',
                'n,n': '12345,54321',
                '.,': '12.345,54321',
                '.,s': '12.345,543 21',
                '.,_': '12.345,543_21',
                '_,_': '12_345,543_21',
                's,s': '12 345,543 21',
            }
        }
        for num, fmt_dict in cases.items():
            for format_spec, expected_num_str in fmt_dict.items():
                snum = sfloat(num)
                snum_str = f'{snum:{format_spec}}'
                with self.subTest(num=num, format_spec=format_spec,
                                  expected_num_str=expected_num_str,
                                  actual_num_str=snum_str):
                    self.assertEqual(snum_str, expected_num_str)

    def test_format(self):
        for num, fmt_dict in fmtcases.items():
            for format_spec, expected_num_str in fmt_dict.items():
                snum = sfloat(num)
                snum_str = f'{snum:{format_spec}}'

                with self.subTest(num=num, format_spec=format_spec,
                                  expected_num_str=expected_num_str,
                                  actual_num_str=snum_str):
                    self.assertEqual(snum_str, expected_num_str)


if __name__ == '__main__':
    unittest.main()
