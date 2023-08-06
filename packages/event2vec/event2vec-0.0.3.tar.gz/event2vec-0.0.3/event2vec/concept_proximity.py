from typing import Dict

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def get_closest_nn(
    source_concept_code: str,
    embedding_dict: Dict[str, np.matrix],
    concept_labels: pd.DataFrame,
    k: int = 10,
):  # pragma: no cover
    """
    Get the k closest neighbors of a source embedding in a matrix of embeddings
    """

    source_concept_id = concept_labels[
        concept_labels["concept_code"] == source_concept_code
    ]["concept_id"].values[0]
    source_embedding = [embedding_dict[source_concept_id]]
    distances = cosine_similarity(
        source_embedding, np.matrix(list(embedding_dict.values()))
    )[0]
    closest_indices = np.argsort(distances)[-k:]
    closest_similarities = distances[closest_indices]
    top_k_concept_ids = np.array(list(embedding_dict.keys()))[closest_indices]
    top_k_concepts = concept_labels.merge(
        pd.DataFrame(
            {
                "concept_id": top_k_concept_ids,
                "similarity": closest_similarities,
            }
        )
    ).sort_values("similarity", ascending=False)

    return top_k_concepts
