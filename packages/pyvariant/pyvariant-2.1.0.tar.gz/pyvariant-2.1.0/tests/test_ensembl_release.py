import pandas as pd
from constants import (
    CACHE_DIR,
    TEST_ENS100_CANONICAL_TRANSCRIPT,
    TEST_ENS100_CONTIG_ALIAS,
    TEST_ENS100_EXON_ALIAS,
    TEST_ENS100_GENE_ALIAS,
    TEST_ENS100_PROTEIN_ALIAS,
    TEST_ENS100_TRANSCRIPT_ALIAS,
)

from pyvariant.ensembl_release import EnsemblRelease
from pyvariant.sequence import PyfaidxFasta


def test_init():
    obj = EnsemblRelease(
        species="homo_sapiens",
        release=100,
        cache_dir=CACHE_DIR,
        canonical_transcript=TEST_ENS100_CANONICAL_TRANSCRIPT,
        contig_alias=TEST_ENS100_CONTIG_ALIAS,
        exon_alias=TEST_ENS100_EXON_ALIAS,
        gene_alias=TEST_ENS100_GENE_ALIAS,
        protein_alias=TEST_ENS100_PROTEIN_ALIAS,
        transcript_alias=TEST_ENS100_TRANSCRIPT_ALIAS,
    )
    assert isinstance(obj.df, pd.DataFrame)
    assert isinstance(obj.cds_fasta, list)
    assert not obj.cds_fasta
    assert isinstance(obj.dna_fasta, list)
    assert isinstance(obj.dna_fasta[0], PyfaidxFasta)
    assert isinstance(obj.protein_fasta, list)
    assert isinstance(obj.protein_fasta[0], PyfaidxFasta)
    assert isinstance(obj.rna_fasta, list)
    assert isinstance(obj.rna_fasta[0], PyfaidxFasta)
    assert isinstance(obj._canonical_transcript, list)
    assert isinstance(obj._contig_alias, dict)
    assert isinstance(obj._exon_alias, dict)
    assert isinstance(obj._gene_alias, dict)
    assert isinstance(obj._protein_alias, dict)
    assert isinstance(obj._transcript_alias, dict)
