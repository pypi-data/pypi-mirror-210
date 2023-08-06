from typing import BinaryIO
from bytez.model import Model


class HazyresearchH3Model(Model):
    def inference(self, input:str, genlen:int = 128, top_p:float = 0.9, top_k:int = 50) -> bytes:
        """
        Runs text generation on the given input string and returns the generated text as a string.

    Args:
      input (str): Input string for the model.
      genlen (int, optional): The length of the output string. Defaults to 128.
      top_p (float, optional): Top-p sampling value. Defaults to 0.9.
      top_k (int, optional): Top-k sampling value. Defaults to 50.

    Returns:
        str: The generated text.
        """

        request_params = {
    "input": input,
    "genlen": genlen,
    "top_p": top_p,
    "top_k": top_k
}

        url = 'https://hazyresearch-h3-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)