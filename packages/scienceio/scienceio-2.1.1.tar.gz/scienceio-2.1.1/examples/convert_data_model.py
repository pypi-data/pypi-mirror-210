#!/usr/bin/env python

import argparse
import pandas as pd


def beta_mapper():
    """For converting previous data models to beta model"""
    return {
        "text": "text",
        "start": "pos_start",
        "end": "pos_end",
        "text_norm": "concept_id",
        "entity": "concept_id",
        "canonical_name": "concept_name",
        "entity_p": "score_id",
        "tag": "concept_type",
        "entity_type": "concept_type",
        "entity_type_p": "score_type",
        "entity_subtype": "concept_subtype",
    }


def remap_concept_types(df):
    """Convert legacy concept types to beta types"""
    type_mapper = {
        "Activity": "Context",
        "Anatomy": "Anatomy & Physiology",
        "Boolean": "Context",
        "Cardinal": "Context",
        "Cell": "Cell Biology",
        "Cell Component": "Cell Biology",
        "CellLine": "Cell Biology",
        "Chemical": "Chemicals & Drugs",
        "Concept": "Context",
        "Device": "Medical Devices",
        "Disease": "Medical Conditions",
        "Gene": "Genetics",
        "Geography": "Context",
        "Group": "Context",
        "Mutation": "Genetics",
        "None": "None",
        "Nucleic Acid, Nucleoside, or Nucleotide": "Genetics",
        "Object": "Context",
        "Occupation": "Context",
        "Organization": "Context",
        "Phenomenon": "Anatomy & Physiology",
        "Physiology": "Anatomy & Physiology",
        "Procedure": "Medical Procedures",
        "Species": "Species & Viruses",
    }
    if "concept_type" in df.columns:
        return df.replace({"concept_type": type_mapper})
    else:
        return df.replace({"entity_type": type_mapper})


def convert_data_model(df):
    """Remap column names and change types"""
    df = df.rename(columns=beta_mapper())
    df = remap_concept_types(df)
    return df


def save_dataframe(df, filename: str = "input.tsv", sep: str = "\t"):
    """Save locally"""
    if "." in filename:
        filename = filename.split(".")[0] + "_REMAPPED.tsv"
    df.to_csv(filename, sep=sep, index=False)


def main(filename):
    """Convert file to proper data model"""
    print(f"Reading: {filename}")
    df = pd.read_csv(filename, sep=None, engine="python")
    df_remapped = convert_data_model(df)
    save_dataframe(df_remapped, filename)
    print(f"Saved to: {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename", type=str, default=None, help="File to have data model remapped"
    )
    args = parser.parse_args()

    main(filename=args.filename)
