import unittest

from src.sdif_toolkit.io import IndividualEntry, Result, Seed, create_entry
from src.sdif_toolkit.time import Time


class TestCreateEntry(unittest.TestCase):

    def test_timed_final_entry_with_result(self):
        input = {
            "ActSeed_course": "Y",
            "ActualSeed_time": 120.00,
            "Pre_course": None,
            "Pre_heat": None,
            "Pre_lane": None,
            "Pre_Time": None,
            "Fin_course": "Y",
            "Fin_heat": 1,
            "Fin_lane": 1,
            "Fin_Time": 119.00,
            "Fin_place": 1,
            "Ev_score": 20,
        }
        expected_seeds = {
            "f": Seed(
                time=Time(12000),
                course="Y",
                heat=1,
                lane=1,
            )
        }
        expected_results = {
            "f": Result(
                time=Time(11900),
                type="f",
                course="Y",
                rank=1,
                points=20
            )
        }
        expected = IndividualEntry()
        expected.seeds = expected_seeds
        expected.results = expected_results

        actual = create_entry(input, IndividualEntry)

        self.assertEqual(actual.seeds, expected.seeds)
        self.assertEqual(actual.results, expected.results)

    def test_prelim_final_entry_with_results(self):
        input = {
            "ActSeed_course": "Y",
            "ActualSeed_time": 120.00,
            "Pre_course": "Y",
            "Pre_heat": 1,
            "Pre_lane": 1,
            "Pre_Time": 119.00,
            "Pre_place": 1,
            "Fin_course": "Y",
            "Fin_heat": 2,
            "Fin_lane": 2,
            "Fin_Time": 118.00,
            "Fin_place": 1,
            "Ev_score": 20
        }
        expected_seeds = {
            "p": Seed(
                time=Time(12000),
                course="Y",
                heat=1,
                lane=1,
            ),
            "f": Seed(
                time=Time(11900),
                course="Y",
                heat=2,
                lane=2,
            )
        }
        expected_results = {
            "p": Result(
                time=Time(11900),
                type="p",
                course="Y",
                rank=1,
            ),
            "f": Result(
                time=Time(11800),
                type="f",
                course="Y",
                rank=1,
                points=20
            )
        }
        expected = IndividualEntry()
        expected.seeds = expected_seeds
        expected.results = expected_results

        actual = create_entry(input, IndividualEntry)

        self.assertEqual(actual.seeds, expected.seeds)
        self.assertEqual(actual.results, expected.results)

    def test_timed_final_entry_without_seed_time_with_result(self):
        input_none = {
            "ActSeed_course": None,
            "ActualSeed_time": None,
            "Pre_course": None,
            "Pre_heat": None,
            "Pre_lane": None,
            "Pre_Time": None,
            "Fin_course": "Y",
            "Fin_heat": 1,
            "Fin_lane": 1,
            "Fin_Time": 119.00,
            "Fin_place": 1,
            "Ev_score": 20,
        }
        input_blank_zero = {
            "ActSeed_course": "",
            "ActualSeed_time": 0.00,
            "Pre_course": None,
            "Pre_heat": None,
            "Pre_lane": None,
            "Pre_Time": None,
            "Fin_course": "Y",
            "Fin_heat": 1,
            "Fin_lane": 1,
            "Fin_Time": 119.00,
            "Fin_place": 1,
            "Ev_score": 20,
        }
        expected_seeds = {
            "f": Seed(
                time=Time(0),
                course="Y",
                heat=1,
                lane=1,
            )
        }
        expected_results = {
            "f": Result(
                time=Time(11900),
                type="f",
                course="Y",
                rank=1,
                points=20
            )
        }
        expected = IndividualEntry()
        expected.seeds = expected_seeds
        expected.results = expected_results

        actual_none = create_entry(input_none, IndividualEntry)
        actual_blank_zero = create_entry(input_blank_zero, IndividualEntry)

        self.assertEqual(actual_none.seeds, expected.seeds)
        self.assertEqual(actual_blank_zero.results, expected.results)

    def test_prelim_final_entry_without_seed_time_with_results(self):
        input_none = {
            "ActSeed_course": None,
            "ActualSeed_time": None,
            "Pre_course": "Y",
            "Pre_heat": 1,
            "Pre_lane": 1,
            "Pre_Time": 119.00,
            "Pre_place": 1,
            "Fin_course": "Y",
            "Fin_heat": 2,
            "Fin_lane": 2,
            "Fin_Time": 118.00,
            "Fin_place": 1,
            "Ev_score": 20,
        }
        input_blank_zero = {
            "ActSeed_course": "",
            "ActualSeed_time": 0.00,
            "Pre_course": "Y",
            "Pre_heat": 1,
            "Pre_lane": 1,
            "Pre_Time": 119.00,
            "Pre_place": 1,
            "Fin_course": "Y",
            "Fin_heat": 2,
            "Fin_lane": 2,
            "Fin_Time": 118.00,
            "Fin_place": 1,
            "Ev_score": 20,
        }
        expected_seeds = {
            "p": Seed(
                time=Time(0),
                heat=1,
                lane=1,
            ),
            "f": Seed(
                time=Time(11900),
                course="Y",
                heat=2,
                lane=2,
            )
        }
        expected_results = {
            "p": Result(
                time=Time(11900),
                type="p",
                course="Y",
                rank=1,
                points=20,
            ),
            "f": Result(
                time=Time(11800),
                type="f",
                course="Y",
                rank=1,
                points=20,
            )
        }
        expected = IndividualEntry()
        expected.seeds = expected_seeds
        expected.results = expected_results

        actual_none = create_entry(input_none, IndividualEntry)
        actual_blank_zero =  create_entry(input_blank_zero, IndividualEntry)

        self.assertEqual(actual_none.seeds, expected.seeds)
        self.assertEqual(actual_blank_zero.results, expected.results)

# TODO: Add testing for DQ states