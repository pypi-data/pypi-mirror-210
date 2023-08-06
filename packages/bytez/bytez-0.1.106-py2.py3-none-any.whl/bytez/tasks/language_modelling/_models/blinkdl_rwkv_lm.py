from typing import BinaryIO
from bytez.model import Model


class BlinkdlRwkvLmModel(Model):
    def inference(self, input: str, temperature: float = 1.0, top_p: float = 0.8, top_p_newline: float = 0.9) -> bytes:
        """
        Runs inference on the given input text and returns the generated text as a string.

                    Args:
                      input (str): The input text for which new text will be generated.
                      
                      temperature (float, optional): Control the "creativity" of the generated text. Higher values generate more creative text. Defaults to 1.0.
                      
                      top_p (float, optional): Control the "safeness" of the generated text. Lower values generate safer text. Defaults to 0.8.
                      
                      top_p_newline (float, optional): Control the "safeness" of the generated text at newline characters. Lower values generate safer text. Defaults to 0.9.
            
                    Returns:
                        str: The generated text as a string.
        """

        request_params = {'input': input, 'temperature': temperature, 'top_p': top_p, 'top_p_newline': top_p_newline}

        url = 'https://blinkdl-rwkv-lm-tfhmsoxnpq-uc.a.run.app'

        return self._Model__inference(url=url, request_params=request_params)