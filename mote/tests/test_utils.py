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
            ]
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
