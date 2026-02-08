"""Tests for core utility functions."""

from uncluttered.core.utils import generate_slug, make_unique_slug


class TestGenerateSlug:
    def test_basic_title(self):
        assert generate_slug("Chocolate Chip Cookies") == "chocolate-chip-cookies"

    def test_apostrophes_removed(self):
        assert generate_slug("Grandma's Famous Pie") == "grandmas-famous-pie"

    def test_special_characters(self):
        assert generate_slug("Easy Mac & Cheese!") == "easy-mac-cheese"

    def test_unicode_normalized(self):
        assert generate_slug("Crème Brûlée") == "creme-brulee"

    def test_extra_whitespace(self):
        assert generate_slug("  Too   Many   Spaces  ") == "too-many-spaces"

    def test_numbers_preserved(self):
        assert generate_slug("5-Minute Oatmeal") == "5-minute-oatmeal"

    def test_empty_string(self):
        assert generate_slug("") == ""


class TestMakeUniqueSlug:
    def test_no_conflict(self):
        assert make_unique_slug("carbonara", set()) == "carbonara"

    def test_single_conflict(self):
        assert make_unique_slug("carbonara", {"carbonara"}) == "carbonara-2"

    def test_multiple_conflicts(self):
        existing = {"carbonara", "carbonara-2", "carbonara-3"}
        assert make_unique_slug("carbonara", existing) == "carbonara-4"

    def test_unrelated_slugs_ignored(self):
        existing = {"pasta", "risotto"}
        assert make_unique_slug("carbonara", existing) == "carbonara"
