import os.path
from shutil import copy2

import pandas as pd
import pytest
from constants import (
    FTP_ENS100_CDNA_FASTA,
    FTP_ENS100_DNA_FASTA,
    FTP_ENS100_GTF,
    FTP_ENS100_NCRNA_FASTA,
    FTP_ENS100_PEP_FASTA,
    TEST_DIR,
)
from gtfparse import read_gtf

from pyvariant.ensembl_cache import (
    EnsemblCache,
    cds_offset_cdna,
    cds_offset_transcript,
    exon_offset_transcript,
    infer_cdna,
    infer_genes,
    infer_protein_id,
    infer_transcripts,
    normalize_df,
)


def assert_same_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
    assert diff.empty, "values are not equal"
    # assert df1.dtypes.to_dict() == df2.dtypes.to_dict(), "dtypes are not equal"
    assert True


@pytest.fixture
def ensembl_100_gtf():
    return read_gtf(FTP_ENS100_GTF, result_type="pandas")


@pytest.fixture
def normalize_df_output():
    path = os.path.join(TEST_DIR, "test_ensembl_cache_data", "normalize_df_output.pickle")
    return pd.read_pickle(path)


def test_normalize_df(ensembl_100_gtf, normalize_df_output):
    df = normalize_df(ensembl_100_gtf)
    assert_same_df(df, normalize_df_output)


@pytest.fixture
def infer_cdna_output():
    path = os.path.join(TEST_DIR, "test_ensembl_cache_data", "infer_cdna_output.pickle")
    return pd.read_pickle(path)


def test_infer_cdna(normalize_df_output, infer_cdna_output):
    df = infer_cdna(normalize_df_output)
    assert not df[df["feature"] == "cdna"].empty
    assert_same_df(df, infer_cdna_output)


@pytest.fixture
def infer_transcripts_output():
    path = os.path.join(TEST_DIR, "test_ensembl_cache_data", "infer_transcripts_output.pickle")
    return pd.read_pickle(path)


def test_infer_transcripts(normalize_df_output, infer_transcripts_output):
    df = infer_transcripts(normalize_df_output)
    assert not df[df["feature"] == "transcript"].empty
    assert_same_df(df, infer_transcripts_output)


@pytest.fixture
def infer_genes_output():
    path = os.path.join(TEST_DIR, "test_ensembl_cache_data", "infer_genes_output.pickle")
    return pd.read_pickle(path)


def test_infer_genes(normalize_df_output, infer_genes_output):
    df = infer_genes(normalize_df_output)
    assert not df[df["feature"] == "gene"].empty
    assert_same_df(df, infer_genes_output)


@pytest.fixture
def exon_offset_transcript_output():
    path = os.path.join(TEST_DIR, "test_ensembl_cache_data", "exon_offset_transcript_output.pickle")
    return pd.read_pickle(path)


def test_exon_offset_transcript(infer_transcripts_output, exon_offset_transcript_output):
    df = exon_offset_transcript(infer_transcripts_output)
    assert_same_df(df, exon_offset_transcript_output)


@pytest.fixture
def cds_offset_transcript_output():
    path = os.path.join(TEST_DIR, "test_ensembl_cache_data", "cds_offset_transcript_output.pickle")
    return pd.read_pickle(path)


def test_cds_offset_transcript(exon_offset_transcript_output, cds_offset_transcript_output):
    df = cds_offset_transcript(exon_offset_transcript_output)
    assert_same_df(df, cds_offset_transcript_output)


@pytest.fixture
def cds_offset_cdna_output():
    path = os.path.join(TEST_DIR, "test_ensembl_cache_data", "cds_offset_cdna_output.pickle")
    return pd.read_pickle(path)


def test_cds_offset_cdna(infer_cdna_output, cds_offset_cdna_output):
    df = cds_offset_cdna(infer_cdna_output)
    assert_same_df(df, cds_offset_cdna_output)


@pytest.fixture
def infer_protein_id_output():
    path = os.path.join(TEST_DIR, "test_ensembl_cache_data", "infer_protein_id_output.pickle")
    return pd.read_pickle(path)


def test_infer_protein_id(infer_cdna_output, infer_protein_id_output):
    df = infer_protein_id(infer_cdna_output)
    assert_same_df(df, infer_protein_id_output)


@pytest.fixture
def ensembl_cache_100(tmp_path):
    return EnsemblCache("homo_sapiens", 100, str(tmp_path))


def test_install(ensembl_cache_100, mocker):
    # Mock download logic so we don't accidently download anything from Ensembl
    def mock_download_cdna_fasta():
        copy2(FTP_ENS100_CDNA_FASTA, ensembl_cache_100.release_cache_dir)

    def mock_download_dna_fasta():
        copy2(FTP_ENS100_DNA_FASTA, ensembl_cache_100.release_cache_dir)

    def mock_download_ncrna_fasta():
        copy2(FTP_ENS100_NCRNA_FASTA, ensembl_cache_100.release_cache_dir)

    def mock_download_pep_fasta():
        copy2(FTP_ENS100_PEP_FASTA, ensembl_cache_100.release_cache_dir)

    def mock_download_gtf():
        copy2(FTP_ENS100_GTF, ensembl_cache_100.release_cache_dir)

    mocker.patch.object(ensembl_cache_100, "download_cdna_fasta", mock_download_cdna_fasta)
    mocker.patch.object(ensembl_cache_100, "download_dna_fasta", mock_download_dna_fasta)
    mocker.patch.object(ensembl_cache_100, "download_ncrna_fasta", mock_download_ncrna_fasta)
    mocker.patch.object(ensembl_cache_100, "download_pep_fasta", mock_download_pep_fasta)
    mocker.patch.object(ensembl_cache_100, "download_gtf", mock_download_gtf)

    # Build the cache
    ensembl_cache_100.install(clean=True, recache=True, redownload=True)

    # Validate that the cache files exist
    assert os.path.exists(ensembl_cache_100.local_cdna_fasta_filepath)
    assert os.path.exists(ensembl_cache_100.local_cdna_index_filepath)
    assert os.path.exists(ensembl_cache_100.local_dna_fasta_filepath)
    assert os.path.exists(ensembl_cache_100.local_dna_index_filepath)
    assert os.path.exists(ensembl_cache_100.local_ncrna_fasta_filepath)
    assert os.path.exists(ensembl_cache_100.local_ncrna_index_filepath)
    assert os.path.exists(ensembl_cache_100.local_pep_fasta_filepath)
    assert os.path.exists(ensembl_cache_100.local_pep_index_filepath)
    assert os.path.exists(ensembl_cache_100.local_gtf_cache_filepath)
    assert not os.path.exists(ensembl_cache_100.local_gtf_filepath)

    # Validate that the cache has all the required data
    df = ensembl_cache_100.load_df()
    assert not df[
        (df["transcript_id"] == "ENST00000256078")
        & (df["cdna_start"] <= 100)
        & (df["cdna_end"] >= 101)
        & (df["feature"].isin(["CDS", "stop_codon"]))
    ].empty
