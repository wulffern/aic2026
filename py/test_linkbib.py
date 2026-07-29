#!/usr/bin/env python3
"""Offline tests for py/linkbib.py.

Covers everything except the two functions that actually open a socket, so
the parsing, matching and formatting can be checked without network. Run:

    python3 -m unittest discover -s py -p 'test_*.py'
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import linkbib


# Shape of a real Crossref /works record, trimmed to the fields fetch reads.
LIU2010 = {
    "type": "journal-article",
    "DOI": "10.1109/jssc.2010.2042254",
    "title": ["A 10-bit 50-MS/s SAR ADC With a Monotonic Capacitor Switching Procedure"],
    "container-title": ["IEEE Journal of Solid-State Circuits"],
    "volume": "45",
    "issue": "4",
    "page": "731-740",
    "issued": {"date-parts": [[2010, 4]]},
    "author": [
        {"given": "Chun-Cheng", "family": "Liu"},
        {"given": "Soon-Jyh", "family": "Chang"},
        {"given": "Guan-Ying", "family": "Huang"},
        {"given": "Ying-Zu", "family": "Lin"},
    ],
}

CONFERENCE = {
    "type": "proceedings-article",
    "DOI": "10.1109/example.2019.1234",
    "title": ["Ring Amplifiers for Switched Capacitor Circuits"],
    "container-title": ["2019 IEEE Custom Integrated Circuits Conference"],
    "issued": {"date-parts": [[2019]]},
    "author": [{"given": "Benjamin", "family": "Hershberg"}],
}


class TestUrls(unittest.TestCase):

    def test_arnumber_from_document_url(self):
        self.assertEqual(
            linkbib.arnumber("https://ieeexplore.ieee.org/document/5437496"),
            "5437496")

    def test_arnumber_from_stamp_url(self):
        self.assertEqual(
            linkbib.arnumber(
                "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4381437"),
            "4381437")

    def test_both_spellings_are_one_paper(self):
        a = linkbib.normalize("https://ieeexplore.ieee.org/document/4381437")
        b = linkbib.normalize(
            "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4381437")
        self.assertEqual(a, b)

    def test_citable_hosts(self):
        self.assertTrue(linkbib.citable("https://ieeexplore.ieee.org/document/90025"))
        self.assertTrue(linkbib.citable(
            "https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/2778127"))
        self.assertFalse(linkbib.citable("https://en.wikipedia.org/wiki/Diode"))
        self.assertFalse(linkbib.citable("https://github.com/wulffern/sun_pll_sky130nm"))

    def test_ieee_non_article_urls_are_not_citable(self):
        for url in ("https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=LVDS",
                    "https://ieeexplore.ieee.org/book/5273726",
                    "https://ieeexplore.ieee.org/mediastore_new/IEEE/content/x-large.gif"):
            self.assertFalse(linkbib.citable(url), url)

    def test_figure_on_a_citable_host_is_not_a_reference(self):
        self.assertFalse(linkbib.citable(
            "https://www.researchgate.net/profile/X/publication/1/figure/fig1/AS:7.jpg"))

    def test_doi_from_url(self):
        self.assertEqual(
            linkbib.doi_from_url("https://link.springer.com/article/10.1007/s10470-010-9576-3"),
            "10.1007/s10470-010-9576-3")
        self.assertEqual(
            linkbib.doi_from_url("https://doi.org/10.1017/9781108626200"),
            "10.1017/9781108626200")
        self.assertIsNone(
            linkbib.doi_from_url("https://ieeexplore.ieee.org/document/5437496"))


class TestAuthors(unittest.TestCase):

    def test_initials_of_hyphenated_given_name(self):
        self.assertEqual(linkbib.initials("Chun-Cheng"), "C.-C.")

    def test_initials_of_simple_name(self):
        self.assertEqual(linkbib.initials("Carsten"), "C.")

    def test_initials_of_two_given_names(self):
        self.assertEqual(linkbib.initials("John Paul"), "J. P.")

    def test_author_list_matches_house_style(self):
        self.assertEqual(
            linkbib.format_author(LIU2010["author"]),
            "C.-C. Liu and S.-J. Chang and G.-Y. Huang and Y.-Z. Lin")


class TestKeys(unittest.TestCase):

    def test_key_is_lastname_and_two_digit_year(self):
        self.assertEqual(linkbib.make_key("C.-C. Liu and S.-J. Chang", "2010", set()),
                         "liu10")

    def test_collision_gets_a_suffix(self):
        taken = {"liu10"}
        self.assertEqual(linkbib.make_key("C.-C. Liu", "2010", taken), "liu10a")
        taken.add("liu10a")
        self.assertEqual(linkbib.make_key("C.-C. Liu", "2010", taken), "liu10b")

    def test_key_never_collides_with_the_existing_bibliography(self):
        keys, _ = linkbib.read_bib_keys("pdf/aic.bib")
        self.assertIn("cjm11", keys)
        self.assertNotIn(linkbib.make_key("P. Harpe", "2012", keys), keys)


class TestFields(unittest.TestCase):

    def test_journal_article(self):
        f = linkbib.fields_from_work(LIU2010)
        self.assertEqual(f["journal"], "IEEE Journal of Solid-State Circuits")
        self.assertEqual(f["volume"], "45")
        self.assertEqual(f["number"], "4")
        self.assertEqual(f["pages"], "731-740")
        self.assertEqual(f["year"], "2010")
        self.assertEqual(f["doi"], "10.1109/jssc.2010.2042254")
        self.assertNotIn("booktitle", f)

    def test_conference_paper_uses_booktitle(self):
        f = linkbib.fields_from_work(CONFERENCE)
        self.assertEqual(linkbib.entry_type(CONFERENCE), "inproceedings")
        self.assertIn("booktitle", f)
        self.assertNotIn("journal", f)

    def test_missing_fields_are_simply_absent(self):
        f = linkbib.fields_from_work({"type": "journal-article", "title": ["T"]})
        self.assertEqual(f["title"], "T")
        self.assertNotIn("volume", f)
        self.assertNotIn("year", f)


class TestBibtex(unittest.TestCase):

    def setUp(self):
        fields = linkbib.fields_from_work(LIU2010)
        self.text = linkbib.to_bibtex("liu10", "article", fields)

    def test_no_stray_semicolon(self):
        # 443 entries in aic.bib close with '};'. New entries must not.
        self.assertTrue(self.text.rstrip().endswith("}"))
        self.assertNotIn("};", self.text)

    def test_author_comes_first_and_doi_is_present(self):
        lines = self.text.strip().split("\n")
        self.assertEqual(lines[0], "@article{liu10,")
        self.assertTrue(lines[1].startswith("author="))
        self.assertIn('doi= "10.1109/jssc.2010.2042254"', self.text)

    def test_last_field_has_no_trailing_comma(self):
        lines = self.text.strip().split("\n")
        self.assertFalse(lines[-2].endswith(","))

    def test_round_trips_through_the_reader(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".bib", delete=False) as fo:
            fo.write(self.text)
            name = fo.name
        try:
            keys, dois = linkbib.read_bib_keys(name)
            titles = linkbib.read_bib_titles(name)
            self.assertEqual(keys, {"liu10"})
            self.assertEqual(dois, {"10.1109/jssc.2010.2042254"})
            self.assertIn(linkbib.squash(LIU2010["title"][0]), titles)
        finally:
            os.unlink(name)


class TestTitleMatching(unittest.TestCase):

    def test_identical_titles_score_one(self):
        self.assertEqual(linkbib.similarity("A Ring Amplifier", "a ring amplifier!"), 1.0)

    def test_a_different_paper_falls_below_threshold(self):
        score = linkbib.similarity(
            "A 10-bit 50-MS/s SAR ADC With a Monotonic Capacitor Switching Procedure",
            "A 12-Bit 1.25-GS/s DAC in 90 nm CMOS With >70 dB SFDR up to 500 MHz")
        self.assertLess(score, linkbib.TITLE_THRESHOLD)

    def test_punctuation_drift_still_matches(self):
        score = linkbib.similarity(
            "A CMOS Temperature Sensor With a Voltage-Calibrated Inaccuracy of "
            "± 0.15 C (3sigma) From -55 Cto 125 C",
            "A CMOS Temperature Sensor With a Voltage-Calibrated Inaccuracy of "
            "±0.15°C (3σ) From −55°C to 125°C")
        self.assertGreater(score, 0.80)


class TestScan(unittest.TestCase):
    """The scan runs against the real lectures, so it notices drift."""

    def test_finds_candidates_in_the_course(self):
        links = linkbib.scan_lectures("lectures/*.md")
        self.assertGreater(len(links), 50)

    def test_every_candidate_is_on_a_paper_host(self):
        for link in linkbib.scan_lectures("lectures/*.md"):
            self.assertTrue(linkbib.citable(link.url), link.url)

    def test_repeated_papers_collapse(self):
        papers = linkbib.group(linkbib.scan_lectures("lectures/*.md"))
        self.assertLess(len(papers), len(linkbib.scan_lectures("lectures/*.md")))
        # The compiled SAR ADC is linked from several lectures.
        self.assertIn("ieee:7906479", papers)
        self.assertGreater(len(papers["ieee:7906479"]), 1)


class TestTitleGuard(unittest.TestCase):

    def test_a_real_title_passes(self):
        self.assertTrue(linkbib.looks_like_a_title(
            "A 10-bit 50-MS/s SAR ADC With a Monotonic Capacitor Switching Procedure"))

    def test_one_word_of_prose_does_not(self):
        self.assertFalse(linkbib.looks_like_a_title("diffusion"))

    def test_link_text_that_is_just_the_url_does_not(self):
        self.assertFalse(linkbib.looks_like_a_title(
            "https://ieeexplore.ieee.org/document/1477063"))


class TestNearMissTitles(unittest.TestCase):
    """The failure that matters: a different paper whose title contains ours.

    l03_refbias links "A CMOS bandgap reference circuit with sub-1-V
    operation" (Banba, JSSC 1999). Crossref returns Navarro's ISCAS 2011
    "A simple CMOS bandgap reference circuit with sub-1-V operation".
    """

    BANBA = "A CMOS bandgap reference circuit with sub-1-V operation"
    NAVARRO = "A simple CMOS bandgap reference circuit with sub-1-V operation"

    def test_the_threshold_cannot_separate_them(self):
        # Documents why an exact-match flag is needed rather than a higher bar.
        self.assertGreater(linkbib.similarity(self.BANBA, self.NAVARRO),
                           linkbib.TITLE_THRESHOLD)

    def test_but_they_are_not_an_exact_match(self):
        self.assertNotEqual(linkbib.squash(self.BANBA), linkbib.squash(self.NAVARRO))

    def test_punctuation_drift_still_counts_as_exact(self):
        self.assertEqual(linkbib.squash("A sub-1-V 15-ppm/°C CMOS bandgap"),
                         linkbib.squash("A sub 1 V 15 ppm/C CMOS bandgap"))


if __name__ == "__main__":
    unittest.main()
