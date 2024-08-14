import os
import requests
import json
import openai
import azure.functions as func
import logging
from dotenv import load_dotenv

app = func.FunctionApp()


@app.function_name(name="yourfunction_trigger_name")
@app.route(route="yourfunction_trigger_name", auth_level=func.AuthLevel.FUNCTION)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    load_dotenv()
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_type = "azure"
    openai.api_version = "2023-05-15"
    deployment_name = "gpt3-deployment"

    # getting the parameters from the request
    text_input = req.get_body().decode("utf-8")
    print("Printing out the text from RSS feed")
    print(text_input)
    # Send a completion call to generate an answer
    print("Sending a test completion job")

    # few shots example
    role_system = """
        Act as an experienced chatbot.....
    """
    few_shots_user_content = """
        {
            "message":"what do you think of blockchain?"
        }
    """
    few_shots_assistant_response = """"
        {
            "response":"I think blockchain is a revolutionary technology that has the potential to change the way we do business. It's a decentralized, secure, and transparent way to store and transfer data. What do you think about it?"
        }
    """
    response = openai.ChatCompletion.create(
        engine=deployment_name,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": role_system},
            {
                "role": "user",
                "content": few_shots_user_content,
            },
            {
                "role": "assistant",
                "content": few_shots_assistant_response,
            },
            {"role": "user", "content": text_input},
        ],
    )
    post_json_body = response["choices"][0]["message"]["content"]
    print(post_json_body)

    return func.HttpResponse(
        json.dumps(post_json_body), status_code=200, mimetype="application/json"
    )
