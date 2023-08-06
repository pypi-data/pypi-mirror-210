from typing import BinaryIO
from bytez.model import Model


class Dmmiller612BertExtractiveSummarizerModel(Model):
    def inference(self, input: str, num_sentences: int = 5, min_length: int = 0,
                  transformers_bert_model: str = None, use_coreference: bool = False,
                  coreference_greedyness: float = None, use_sbert: bool = False,
                  ratio: float = 0.2, max_length: int = 500,
                  retrieve_embeddings: bool = False, embeddings_ratio: float = None,
                  embeddings_aggregate: str = "mean",
                  calculate_elbow: bool = False, k_max: int = 10,
                  calculate_optimal_k: bool = False) -> bytes:
        """
        Summarizes input text into a shorter version that highlights the key points.

        Args:
            input (str): The text to be summarized.
            num_sentences (int, optional): The number of sentences for the resulting summary to have. Defaults to 5.
            min_length (int, optional): The minimum length (in characters) for each sentence in the summary. Defaults to 0.
            transformers_bert_model (str, optional): The name of a transformers bert model for custom loading. Defaults to None.
            use_coreference (bool, optional): Whether to use coreference resolution for pronoun handling. Defaults to False.
            coreference_greedyness (float, optional): The greediness factor for coreference resolution. Defaults to None.
            use_sbert (bool, optional): Whether to use SBERT model for sentence embedding. Defaults to False.
            ratio (float, optional): The ratio of the input text to be included in the summary. Defaults to 0.2.
            max_length (int, optional): The maximum length (in characters) for the resulting summary. Defaults to 500.
            retrieve_embeddings (bool, optional): Whether to retrieve sentence embeddings instead of a summary. Defaults to False.
            embeddings_ratio (float, optional): The ratio of sentences to be included in the retrieved embeddings. Defaults to None.
            embeddings_aggregate (str, optional): The method for aggregating the sentence embeddings. Can be one of "mean", "median", "max", "min". Defaults to "mean".
            calculate_elbow (bool, optional): Whether to calculate the elbow curve for k-means clustering. Defaults to False.
            k_max (int, optional): The maximum number of clusters to consider for the elbow curve. Defaults to 10.
            calculate_optimal_k (bool, optional): Whether to calculate the optimal number of clusters using the silhouette score. Defaults to False.

        Returns:
            bytes: The resulting summary or embeddings as bytes.
        """

        url = 'http://localhost:8080'

        request_params = {
            'input': input,
            'num_sentences': num_sentences,
            'min_length': min_length,
            'transformers_bert_model': transformers_bert_model,
            'use_coreference': 1 if use_coreference else 0,
            'coreference_greedyness': coreference_greedyness,
            'use_sbert': 1 if use_sbert else 0,
            'ratio': ratio,
            'max_length': max_length,
            'retrieve_embeddings': 1 if retrieve_embeddings else 0,
            'embeddings_ratio': embeddings_ratio,
            'embeddings_aggregate': embeddings_aggregate,
            'calculate_elbow': 1 if calculate_elbow else 0,
            'k_max': k_max,
            'calculate_optimal_k': 1 if calculate_optimal_k else 0
        }

        url = 'https://dmmiller612-bert-extractive-summarizer-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)
