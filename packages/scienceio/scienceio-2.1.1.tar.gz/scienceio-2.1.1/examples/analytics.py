#!/usr/bin/env python

import argparse
import pandas as pd

from convert_data_model import convert_data_model


def count_text(df) -> int:
    """len(df) = # of text spans"""
    return len(df)


def count_text_unique(df) -> int:
    """unique text spans (no correction for caps/lower/etc.)"""
    return df.text.nunique()


def count_concepts_unique(df) -> int:
    """unique biomedical concepts"""
    return df.concept_id.nunique()


def count_types_unique(df) -> int:
    """unique concept types"""
    return df.concept_type.nunique()


def quantizer(score):
    """
    Quantizes scores with desired range

    Run with:
        df[col] = df[col].apply(lambda x: quantizer(x))

    to transform column into quantized values (or set to new column)
    """
    if score >= 0.99:
        return "Very High"
    elif score >= 0.9:
        return "High"
    elif score >= 0.7:
        return "Moderate"
    elif score >= 0.5:
        return "Low"
    else:
        return "Very Low"


def quantize_scores(df):
    """Quantize the scores in the dataframe"""
    df["score_id"] = df["score_id"].apply(lambda x: quantizer(x))
    df["score_type"] = df["score_type"].apply(lambda x: quantizer(x))
    return df


def get_score_counts(df, col="score_id"):
    """Returns counts by score"""
    return (
        df.groupby(col)
        .count()["pos_start"]
        .reset_index()
        .sort_values(by="pos_start", ascending=False)
        .rename(columns={"pos_start": "mentions"})
        .reset_index(drop=True)
    )


def get_score_dict(df, col="score_id"):
    """Returns a dict of counts by score_id"""

    # get counts
    conf = get_score_counts(df, col)

    # zip two columns to create dict
    conf_dict = dict(zip(conf[col], conf["mentions"]))

    # add zero values
    for k in ["Very High", "High", "Moderate", "Low", "Very Low"]:
        if not k in conf_dict:
            conf_dict[k] = 0

    return conf_dict


def get_top(df, col="concept_name", N: int = 10):
    """get top N values by count"""
    return (
        df.groupby(col)
        .count()["pos_start"]
        .reset_index()
        .sort_values(by="pos_start", ascending=False)
        .rename(columns={"pos_start": "mentions"})
        .reset_index(drop=True)
        .head(n=N)
    )


def get_top_dict(df, col="concept_name", N: int = 10):
    """Get top values as dict with ordered lists"""
    return get_top(df, col, N).to_dict("list")


def report(df):
    """get report of basic summary stats"""
    print(
        f"Found {count_text(df)} mentions of healthcare information ({count_text_unique(df)} unique)."
    )
    print(
        f"Found {count_concepts_unique(df)} unique concepts, spanning {count_types_unique(df)} categories."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, default=None, help="File to analyze")
    args = parser.parse_args()

    # read file
    df = pd.read_csv(args.filename, sep=None, engine="python")

    # convert and quantize
    df = convert_data_model(df)
    df = quantize_scores(df)
