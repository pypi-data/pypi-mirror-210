import csv
from pathlib import Path
from typing import Dict, Iterator, List

import pytest

from pyvariant import EnsemblRelease

TEST_CASES = Path(__file__).parent / "data" / "test_data.csv"


def load_params() -> Iterator[Dict]:
    """Load parameters used to run the tests from a file.

    Yields:
        Iterator[Dict]: Test parameters as dictionaries
    """
    with open(TEST_CASES, "r") as fh:
        for row in csv.DictReader(fh, delimiter=","):
            for key in row:
                if row[key] and key.endswith(("end", "offset", "start")):
                    row[key] = int(row[key])

            yield row


def select_params(required: List[str]) -> Iterator[Dict]:
    """Filter down the test parameters to just those with the required non-null values.

    Args:
        required (List[str]): List of keys for which the matching value(s) must be non-null

    Yields:
        Iterator[Dict]: Test parameters with the required value(s)
    """
    yield from (row for row in load_params() if all([row[key] for key in required]))


def assert_and_select_expected(output: List, expected: str):
    """Select the expected variant from a list (if it exists) for further testing."""
    # If there is no expected variant output, assert the function returned an empty list
    if not expected:
        assert not output, f"Expected no output, got: {output}"

    # Assert that the expected variant is in the list of variants returned by the function
    str_to_variant = {str(i): i for i in output}
    assert expected in str_to_variant, f"Expected {expected}, got: {list(str_to_variant)}"

    return str_to_variant[expected]


def assert_cdna_has_attributes(cdna, params: Dict):
    """Assert that a cDNA variant has all the expected attributes."""
    assert cdna.is_cdna
    assert str(cdna) == params["cdna_str"]
    assert cdna.start == params["cdna_start"]
    assert cdna.end == params["cdna_end"]
    assert cdna.start_offset == params["cdna_start_offset"]
    assert cdna.end_offset == params["cdna_end_offset"]
    assert cdna.strand == params["strand"]
    assert cdna.contig_id == params["contig_id"]
    assert cdna.gene_id == params["gene_id"]
    assert cdna.gene_name == params["gene_name"]
    assert cdna.transcript_id == params["transcript_id"]
    assert cdna.transcript_name == params["transcript_name"]
    assert cdna.protein_id == params["protein_id"]


def assert_dna_has_attributes(dna, params: Dict):
    """Assert that a DNA variant has all the expected attributes."""
    assert dna.is_dna
    assert str(dna) == params["dna_str"]
    assert dna.start == params["dna_start"]
    assert dna.end == params["dna_end"]
    assert dna.start_offset == params["dna_start_offset"]
    assert dna.end_offset == params["dna_end_offset"]
    assert dna.strand == params["strand"]
    assert dna.contig_id == params["contig_id"]


def assert_protein_has_attributes(protein, params: Dict):
    """Assert that a protein variant has all the expected attributes."""
    assert protein.is_protein
    assert str(protein) == params["protein_str"]
    assert protein.start == params["protein_start"]
    assert protein.end == params["protein_end"]
    assert protein.start_offset == params["protein_start_offset"]
    assert protein.end_offset == params["protein_end_offset"]
    assert protein.strand == params["strand"]
    assert protein.contig_id == params["contig_id"]
    assert protein.gene_id == params["gene_id"]
    assert protein.gene_name == params["gene_name"]
    assert protein.transcript_id == params["transcript_id"]
    assert protein.transcript_name == params["transcript_name"]
    assert protein.protein_id == params["protein_id"]


def assert_rna_has_attributes(rna, params: Dict):
    """Assert that an RNA variant has all the expected attributes."""
    assert rna.is_rna
    assert str(rna) == params["rna_str"]
    assert rna.start == params["rna_start"]
    assert rna.end == params["rna_end"]
    assert rna.start_offset == params["rna_start_offset"]
    assert rna.end_offset == params["rna_end_offset"]
    assert rna.strand == params["strand"]
    assert rna.contig_id == params["contig_id"]
    assert rna.gene_id == params["gene_id"]
    assert rna.gene_name == params["gene_name"]
    assert rna.transcript_id == params["transcript_id"]
    assert rna.transcript_name == params["transcript_name"]


@pytest.mark.parametrize("params", select_params(["cdna_str"]), ids=lambda x: x["cdna_str"])
def test_cdna_to_cdna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a cDNA variant can be parsed from a string and mapped to the expected cDNA variant."""
    output = ensembl100.to_cdna(params["cdna_str"])
    if select := assert_and_select_expected(output, params["cdna_str"]):
        assert_cdna_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["cdna_str"]), ids=lambda x: x["cdna_str"])
def test_cdna_to_dna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a cDNA variant can be parsed from a string and mapped to the expected DNA variant."""
    output = ensembl100.to_dna(params["cdna_str"])
    if select := assert_and_select_expected(output, params["dna_str"]):
        assert_dna_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["cdna_str"]), ids=lambda x: x["cdna_str"])
def test_cdna_to_protein_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a cDNA variant can be parsed from a string and mapped to the expected protein variant."""
    output = ensembl100.to_protein(params["cdna_str"])
    if select := assert_and_select_expected(output, params["protein_str"]):
        assert_protein_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["cdna_str"]), ids=lambda x: x["cdna_str"])
def test_cdna_to_rna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a cDNA variant can be parsed from a string and mapped to the expected RNA variant."""
    output = ensembl100.to_rna(params["cdna_str"])
    if select := assert_and_select_expected(output, params["rna_str"]):
        assert_rna_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["protein_str"]), ids=lambda x: x["protein_str"])
def test_protein_to_cdna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a protein variant can be parsed from a string and mapped to the expected cDNA variant."""
    output = ensembl100.to_cdna(params["protein_str"])
    if select := assert_and_select_expected(output, params["cdna_str"]):
        assert_cdna_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["protein_str"]), ids=lambda x: x["protein_str"])
def test_protein_to_dna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a protein variant can be parsed from a string and mapped to the expected DNA variant."""
    output = ensembl100.to_dna(params["protein_str"])
    if select := assert_and_select_expected(output, params["dna_str"]):
        assert_dna_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["protein_str"]), ids=lambda x: x["protein_str"])
def test_protein_to_protein_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a protein variant can be parsed from a string and mapped to the expected protein variant."""
    output = ensembl100.to_protein(params["protein_str"])
    if select := assert_and_select_expected(output, params["protein_str"]):
        assert_protein_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["protein_str"]), ids=lambda x: x["protein_str"])
def test_protein_to_rna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a protein variant can be parsed from a string and mapped to the expected RNA variant."""
    output = ensembl100.to_rna(params["protein_str"])
    if select := assert_and_select_expected(output, params["rna_str"]):
        assert_rna_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["rna_str"]), ids=lambda x: x["rna_str"])
def test_rna_to_cdna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a RNA variant can be parsed from a string and mapped to the expected cDNA variant."""
    output = ensembl100.to_cdna(params["rna_str"])
    if select := assert_and_select_expected(output, params["cdna_str"]):
        assert_cdna_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["rna_str"]), ids=lambda x: x["rna_str"])
def test_rna_to_dna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a RNA variant can be parsed from a string and mapped to the expected DNA variant."""
    output = ensembl100.to_dna(params["rna_str"])
    if select := assert_and_select_expected(output, params["dna_str"]):
        assert_dna_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["rna_str"]), ids=lambda x: x["rna_str"])
def test_rna_to_protein_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a RNA variant can be parsed from a string and mapped to the expected protein variant."""
    output = ensembl100.to_protein(params["rna_str"])
    if select := assert_and_select_expected(output, params["protein_str"]):
        assert_protein_has_attributes(select, params)


@pytest.mark.parametrize("params", select_params(["rna_str"]), ids=lambda x: x["rna_str"])
def test_rna_to_rna_from_str(ensembl100: EnsemblRelease, params: Dict):
    """Test that a RNA variant can be parsed from a string and mapped to the expected RNA variant."""
    output = ensembl100.to_rna(params["rna_str"])
    if select := assert_and_select_expected(output, params["rna_str"]):
        assert_rna_has_attributes(select, params)
