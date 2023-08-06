from typing import BinaryIO
from bytez.model import Model
from typing import BinaryIO, List

class HhousenDocsumModel(Model):
    def preprocess(self, input_pdf: BinaryIO):
        """
        Converts a pdf into an xml file
        Args:
        - input_pdf (BinaryIO): The binary PDF file to be summarized.
        """
        request_params = {
            "input_pdf": input_pdf,
            "preprocess": "1"
            }

        url = 'https://hhousen-docsum-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)

    def inference(
        self,
        input_pdf: BinaryIO = None,
        input_text: str = None,
        chapter_heading_font: List[int] = None,
        body_heading_font: List[int] = None,
        body_font: List[int] = None,
        model: str = 'bart',
        bart_state_dict_key: str = 'model',
        bart_fairseq: bool = False,
        beam_size: int = 5,
        min_length: int = 50,
        max_length: int = 200,
        alpha: float = 0.95,
        block_trigram: bool = True,
    ) -> bytes:
        """
        Runs text summarization on a given PDF file or input text and returns the output as a dictionary of chapter and headings to summarized text or as a summarized text string respectively.

        Args:
        - input_pdf (BinaryIO, optional): The binary PDF file to be summarized.
        - input_text (str, optional): The input text to be summarized. If provided, the `input_pdf` parameter will be ignored.
        - chapter_heading_font (List[int], optional): The font of the chapter titles. Defaults to None.
        - body_heading_font (List[int], optional): The font of headings within chapter. Defaults to None.
        - body_font (List[int], optional): The font of the body (the text you want to summarize). Defaults to None.
        - model (str, optional): The summarization model to use. Must be either 'bart' or 'presumm'. Defaults to 'bart'.
        - bart_state_dict_key (str, optional): The state_dict key to load from the pickle file specified with `bart_checkpoint`. Defaults to 'model'.
        - bart_fairseq (bool, optional): Use fairseq model from torch hub instead of huggingface transformers library models. Cannot be used if `bart_checkpoint` is supplied. Defaults to False.
        - beam_size (int, optional): Presumm only. The beam size for the summarization process. Defaults to 5.
        - min_length (int, optional): The minimum length of the summary. Defaults to 50.
        - max_length (int, optional): The maximum length of the summary. Defaults to 200.
        - alpha (float, optional): Presumm only. The alpha value for controlling length penalty in the summarization process. Defaults to 0.95.
        - block_trigram (bool, optional): Presumm only. Whether to block repeating trigrams in the summary. Defaults to True.

        Returns:
        - bytes: The output of the summarization. This is a dictionary of chapter and headings to summarized text.
        """

        request_params = {
            "input_pdf": input_pdf,
            "preprocess": "0",
            "model": model,
            "bart_state_dict_key": bart_state_dict_key,
            "bart_fairseq": bart_fairseq,
            "chapter_heading_font": chapter_heading_font,
            "body_heading_font": body_heading_font,
            "body_font": body_font,
            "input_text": input_text,
            "beam_size": beam_size,
            "min_length": min_length,
            "max_length": max_length,
            "alpha": alpha,
            "block_trigram": "1" if block_trigram else "0",
        }

        url = 'https://hhousen-docsum-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)