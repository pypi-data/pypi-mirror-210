from pathlib import Path
from torch import no_grad as __torch_no_grad__
from transformers import AutoTokenizer, AutoModel

__path__ = Path(__file__).parent.joinpath("resources").joinpath("model")

tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=__path__)
model = AutoModel.from_pretrained(pretrained_model_name_or_path=__path__)

def get_embeddings(contents: list[str]):
    encoded = tokenizer(contents, padding=True, truncation=True, return_tensors="pt")
    with __torch_no_grad__():
        model_output = model(**encoded)
        embeddings = model_output.last_hidden_state[:, 0, :]
    return embeddings
