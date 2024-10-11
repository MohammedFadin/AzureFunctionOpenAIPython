import os
import requests
import json
from openai import AzureOpenAI
import azure.functions as func
import logging
from dotenv import load_dotenv

load_dotenv()

app = func.FunctionApp()


@app.function_name(name="chat")  # This is your function name, could be anything
@app.route(
    route="chat", auth_level=func.AuthLevel.FUNCTION
)  # route is the endpoint of the function (e.g.https://<functionapp>.azurewebsites.net/api/chat)
def main(
    req: func.HttpRequest,
) -> (
    func.HttpResponse
):  # if you change the main function name, make sure to change the entrypoint in function.json
    logging.info("Python HTTP trigger function processed a request.")

    # OPTIONAL if you want to integrate Azure AI Search
    aisearch_endpoint = os.getenv("AISEARCH_ENDPOINT")
    aisearch_key = os.getenv("AISEARCH_KEY")
    aisearch_index = os.getenv("AISEARCH_INDEX")
    aisearch_resourcename = os.getenv("AISEARCH_RESOURCENAME")

    client = AzureOpenAI(
        azure_endpoint=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPEN_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
    )

    # Getting the parameters from the request
    user_input = req.get_body().decode("utf-8")
    logging.info("POST request payload contains:{user_input}")

    response = client.chat.completions.create(
        model="hybridcopilot",  # model = "deployment_name".
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that helps people find information.",
            },
            {
                "role": "user",
                "content": "hello",
            },
            {
                "role": "assistant",
                "content": "Hello! How can I assist you today?",
            },
            {"role": "user", "content": "why am i paying warranty deposit?"},
            {
                "role": "assistant",
                "content": "The warranty deposit is an amount you pay if you are sponsoring a dependent second degree, typically in humanitarian cases. It is important to keep the receipt showing that you paid the warranty deposit [doc1].",
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False,
        extra_body={
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": f"{aisearch_endpoint}",
                        "index_name": f"{aisearch_index}",
                        "semantic_configuration": "azureml-default",
                        "query_type": "vector_semantic_hybrid",
                        "fields_mapping": {},
                        "in_scope": True,
                        "role_information": "You are an AI assistant that helps people find information.",
                        "filter": None,
                        "strictness": 3,
                        "top_n_documents": 5,
                        "authentication": {"type": "api_key", "key": f"{aisearch_key}"},
                        "embedding_dependency": {
                            "type": "deployment_name",
                            "deployment_name": "textembeddingada",
                        },
                    },
                }
            ]
        },
    )

    model_response = response.choices[0].message.content
    logging.info(model_response)

    return func.HttpResponse(
        json.dumps(model_response), status_code=200, mimetype="application/json"
    )
