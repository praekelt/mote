from collections import OrderedDict

from django.test import TestCase

from mote.utils import deepmerge


class UtilsTestCase(TestCase):

    def test_deepmerge(self):
        source = {
            "one": {"aaa": 1, "bbb": 2},
            "two": [1, 2, 3],
            "three":[
                {"actor": {"name": "Tom", "surname": "Hanks"}},
                {"actor": {"name": "Denzel", "surname": "Washington"}},
            ],
            "four": [
                {"actor": {"name": "Alec", "surname": "Baldwin"}},
                {"actor": {"name": "Brad", "surname": "Pitt"}},
            ],
            "five": [
                {
                    "movie": {
                        "title": "Good Will Hunting",
                        "actors": [
                            {"actor": {"name": "Ben", "surname": "Affleck"}}
                        ]
                    }
                }
            ],
            "six":[
                {"actor": {"name": "Tom", "surname": "Hanks"}},
                {"actor": {"name": "Denzel", "surname": "Washington"}},
            ],
        }
        delta = {
            "one": {"bbb": 777, "ccc": 888},
            "two": [3, 4, 5],
            "three": {"actor": {"name": "Colin"}},
            "four": [
                {"actor": {"name": "Stephen"}},
                {"actor": {"name": "Harrison", "surname": "Ford"}},
                {"actor": {"name": "William"}}
            ],
            "five": [
                {
                    "movie": {
                        "title": "Good Will Hunting",
                        "actors": [
                            {"actor": {"name": "Matt", "surname": "Damon"}},
                            {"actor": {"name": "Casey"}}
                        ]
                    }
                }
            ],
            "six": [
                {"archetype": False, "director": {"name": "Guillermo"}},
                {"score": {"name": "Hans"}}
            ],
            "infinity": {"a": 0}
        }
        result = deepmerge(source, delta)
        self.assertEqual(
            {
            "one": {"aaa": 1, "bbb": 777, "ccc": 888},
            "two": [3, 4, 5],
            "three":[
                {"actor": {"name": "Colin", "surname": "Hanks"}}
            ],
            "four": [
                {"actor": {"name": "Stephen", "surname": "Baldwin"}},
                {"actor": {"name": "Harrison", "surname": "Ford"}},
                {"actor": {"name": "William", "surname": "Baldwin"}}
            ],
            "five": [
                {
                    "movie": {
                        "title": "Good Will Hunting",
                        "actors": [
                            {"actor": {"name": "Matt", "surname": "Damon"}},
                            {"actor": {"name": "Casey", "surname": "Affleck"}}
                        ]
                    }
                }
            ],
            "six": [
                {"archetype": False, "director": {"name": "Guillermo"}},
                {"score": {"name": "Hans"}}
            ],
            "infinity": {"a": 0}
            },
            result
        )

    def test_deepmerge_nones(self):
        # If both source and delta are None the result must be None
        source = None
        delta = None
        result = deepmerge(source, delta)
        assert(result, None)

        # If delta is None, we want to retain source
        source = {
            "one": {"aaa": 1, "bbb": 2},
            "two": [1, 2, 3],
            "three":[
                {"actor": {"name": "Tom", "surname": "Hanks"}},
                {"actor": {"name": "Denzel", "surname": "Washington"}},
            ],
            "four": [
                {"actor": {"name": "Alec", "surname": "Baldwin"}},
                {"actor": {"name": "Brad", "surname": "Pitt"}},
            ],
            "five": [
                {
                    "movie": {
                        "title": "Good Will Hunting",
                        "actors": [
                            {"actor": {"name": "Ben", "surname": "Affleck"}}
                        ]
                    }
                }
            ]
        }
        delta = None
        result = deepmerge(source, delta)
        self.assertEqual(result, source, "Result must be == source!")

        # If source is None we want to retain source
        source = None
        delta = {
            "one": {"aaa": 1, "bbb": 2},
            "two": [1, 2, 3],
            "three":[
                {"actor": {"name": "Tom", "surname": "Hanks"}},
                {"actor": {"name": "Denzel", "surname": "Washington"}},
            ],
            "four": [
                {"actor": {"name": "Alec", "surname": "Baldwin"}},
                {"actor": {"name": "Brad", "surname": "Pitt"}},
            ],
            "five": [
                {
                    "movie": {
                        "title": "Good Will Hunting",
                        "actors": [
                            {"actor": {"name": "Ben", "surname": "Affleck"}}
                        ]
                    }
                }
            ]
        }
        result = deepmerge(source, delta)
        self.assertEqual(result, source, "Result must be == None!")

    def test_list_with_nones(self):
        """`None` values are discarded from lists.
        """
        source = {
            "three": [
                {"actor": {"name": "Tom", "surname": "Hanks"}},
                {"actor": {"name": "Denzel", "surname": "Washington"}},
            ],
        }
        delta = {
            "three": [
                {"actor": {"name": "Tom", "surname": "Hanks"}},
                None,
            ],
        }
        result = deepmerge(source, delta)
        self.assertEqual(
            result,
            {"three": [{"actor": {"name": "Tom", "surname": "Hanks"}}]}
        )

    def test_arbitrary_keys(self):
        """Introduce keys that are not in source.
        """
        source = {
            "three": [
                {"actor": {"name": "Tom", "surname": "Hanks"}},
            ],
        }
        delta = {
            "three": [
                {"actor": {"name": "Tom", "surname": "Hanks", "age": 50}},
            ],
            "four": 1
        }
        result = deepmerge(source, delta)
        self.assertEqual(
            result,
            {
                "three": [{"actor": {"name": "Tom", "surname": "Hanks", "age": 50}}],
                "four": 1
            }
        )

    def test_key_order(self):
        # Delta key range does not span source key range. Source order wins.
        source = OrderedDict([
            ("one", "One"),
            ("two", "Two"),
            ("three", "Three"),
        ])
        delta = OrderedDict([
            ("three", "Three X"),
            ("two", "Two X")
        ])
        result = deepmerge(source, delta)
        self.assertEqual(["one", "two", "three"], list(result.keys()))

        # Delta key range spans source key range. Delta order wins.
        source = OrderedDict([
            ("one", "One"),
            ("two", "Two"),
            ("three", "Three"),
        ])
        delta = OrderedDict([
            ("three", "Three X"),
            ("two", "Two X"),
            ("one", "One X"),
            ("four", "Four X")
        ])
        result = deepmerge(source, delta)
        self.assertEqual(["three", "two", "one", "four"], list(result.keys()))
