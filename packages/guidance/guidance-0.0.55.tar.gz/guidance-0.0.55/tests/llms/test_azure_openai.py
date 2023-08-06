import guidance

def test_basic():
    import json
    import os

    # load azure_params.json from the same directory as this file
    path = os.path.dirname(os.path.abspath(__file__))
    with open(path + os.path.sep + "azure_params.json", "r") as f:
        params = json.load(f)
    llm = guidance.llms.AzureOpenAI('gpt2', caching=False, **params)
    with llm.session() as s:
        out = s("this is a test", max_tokens=5)
        print(out)