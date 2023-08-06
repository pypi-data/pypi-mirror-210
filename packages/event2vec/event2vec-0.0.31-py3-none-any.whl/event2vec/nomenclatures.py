import os
from multiprocessing.sharedctypes import Value
from typing import List

import pandas as pd

from event2vec.config import DIR2RESOURCES


def add_ATC2concepts(
    path2concepts: str, path2irpha: str
) -> pd.DataFrame:  # pragma: no cover
    """
    Description: Add ATC07 and ATC03 codes and labels to an omop concept table
    """
    concepts = pd.read_csv(path2concepts)
    irPha = pd.read_csv(
        path2irpha,
        dtype={
            "PHA_PRS_C13": "int",
            "PHA_ATC_C07": "str",
            "PHA_ATC_C03": "str",
        },
        sep=";",
    )
    concepts_drugs_as_ATC7 = (
        irPha.loc[:, ["PHA_ATC_C07", "PHA_ATC_L07"]]
        .rename(
            columns={
                "PHA_ATC_C07": "concept_code",
                "PHA_ATC_L07": "concept_name",
            }
        )
        .drop_duplicates()
    )
    concepts_drugs_as_ATC3 = (
        irPha.loc[:, ["PHA_ATC_C03", "PHA_ATC_L03"]]
        .rename(
            columns={
                "PHA_ATC_C03": "concept_code",
                "PHA_ATC_L03": "concept_name",
            }
        )
        .drop_duplicates()
    )
    for col in [
        "concept_id",
        "domain_id",
        "vocabulary_id",
        "concept_class_id",
        "standard_concept",
        "valid_start_date",
        "valid_end_date",
        "invalid_reason",
        "m_language_id",
        "m_project_id",
    ]:
        if col == "vocabulary_id":
            concepts_drugs_as_ATC7.loc[:, col] = "SNDS - ATC7"
            concepts_drugs_as_ATC3.loc[:, col] = "SNDS - ATC3"
        elif col == "domain_id":
            concepts_drugs_as_ATC7.loc[:, col] = "drug"
            concepts_drugs_as_ATC3.loc[:, col] = "drug"
        else:
            concepts_drugs_as_ATC7.loc[:, col] = 0
            concepts_drugs_as_ATC3.loc[:, col] = 0
    all_concepts = pd.concat(
        (concepts, concepts_drugs_as_ATC3, concepts_drugs_as_ATC7), sort=False
    )
    # enforce types
    all_concepts.loc[:, "concept_name"] = all_concepts.loc[
        :, "concept_name"
    ].apply(lambda x: str(x))
    all_concepts.loc[:, "concept_code"] = all_concepts.loc[
        :, "concept_code"
    ].apply(lambda x: str(x))

    return all_concepts


def get_concepts_labels(
    study_codes: List,
    path2concept_trees: str = DIR2RESOURCES,
    verbose: int = 1,
    atc_level: int = 5,
) -> pd.DataFrame:  # pragma: no cover
    """
    From our csv describing terminologies trees, build a df of concept code/concept_name/vocabulary
    :param atc_level: atc level (between 1 and 5),
        - 1 is anatomical (14 letters) eg. C Cardiovascular system
        - 2 is therapeutic (two digits for 94 codes) eg. C03 Diuretics
        - 3 is pharmacological (one letter for 267 groups) eg. C03C High-ceiling diuretics
        - 4 is chemical subgroup (one letter for 887 codes) eg. C03CA Sulfonamides
        - 5 is chemical susbtance (two digits for 4949 codes) eg. C03CA01 furosemide
    :param  path2concept_trees:
    :param study_codes:
    :param verbose:
    :return: a Dataframe with all study concept codes and their corresponding vocabulary and concept name
    """
    # check the type to avoid overflow
    if not isinstance(study_codes, list):
        raise ValueError("Expected type is a list for study_codes")
    if atc_level not in [
        1,
        2,
        3,
        4,
        5,
    ]:
        raise ValueError("Expected atc_level is between 1 and 5")
    # Load vocabularies from resources
    available_vocabularies = {
        "ngap": "ngap_tree.csv",
        "atc7": "atc_tree.csv",
        "ccam": "ccam_tree.csv",
        "cim10": "icd10_tree.csv",
        "nabm": "nabm_tree.csv",
    }
    if verbose:
        print(
            "available terminology trees are : {}".format(
                available_vocabularies.keys()
            )
        )
    terminologies = {}
    for vocab_name, file_name in available_vocabularies.items():
        terminologies[vocab_name] = pd.read_csv(
            os.path.join(path2concept_trees, file_name)
        )
        if vocab_name == "nabm":
            terminologies[vocab_name].loc[:, "concept_code"] = (
                terminologies[vocab_name]
                .loc[:, "concept_code"]
                .map(lambda x: str(x))
            )
        # load only specific atc level
        if vocab_name == "atc7":
            atc_levels = [
                "ATC 1st",
                "ATC 2nd",
                "ATC 3rd",
                "ATC 4th",
                "ATC 5th",
            ]
            terminologies[vocab_name] = terminologies[vocab_name].loc[
                terminologies[vocab_name]["concept_class_id"]
                == atc_levels[atc_level - 1],
                :,
            ]

    label_unfound = []
    label_doublons = []
    code2label = {}
    code2terminology = {}
    study_code_df = pd.DataFrame({"concept_code": study_codes})
    for vocab_name, vocab_tree in terminologies.items():
        study_concepts = study_code_df.merge(
            vocab_tree.loc[:, ["concept_code", "concept_name"]],
            on="concept_code",
            how="left",
        ).dropna()
        for c, l in zip(
            study_concepts["concept_code"], study_concepts["concept_name"]
        ):
            if c in code2label.keys():
                label_doublons.append(c)
            code2label[c] = l
            code2terminology[c] = vocab_name

    for c in study_codes:
        if c not in code2label.keys():
            code2label[c] = c
            code2terminology[c] = "unknown"
            label_unfound.append(c)
    concepts_df = pd.DataFrame([code2label, code2terminology]).transpose()
    concepts_df.reset_index(inplace=True)
    concepts_df.columns = [
        "concept_code",
        "concept_name",
        "concept_terminology",
    ]
    print(concepts_df.shape)
    if verbose:
        print(
            "{} concept codes are not found in terminology trees.".format(
                len(label_unfound)
            )
        )
        print(
            "{} concepts are found in more than one terminology.".format(
                len(label_doublons)
            )
        )
        print(
            "Please rerun this function with verbose >=2 to get back unfound and doublons as second and third results."
        )
    if verbose >= 2:
        return concepts_df, label_unfound, label_doublons
    else:
        return concepts_df
