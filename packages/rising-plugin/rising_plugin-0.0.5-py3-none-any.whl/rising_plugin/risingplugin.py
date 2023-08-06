import os
import json
import datetime
from typing import List, Any

from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import utils
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
import openai

import replicate
from firebase_admin import storage

from .common.utils import (
    OPENAI_API_KEY,
    FIREBASE_STORAGE_ROOT,
    COMMAND_SMS_INDEXS,
)
from image_embedding import (
    query_image_text,
    get_prompt_image_with_message,
)

def getCompletion(query, model="gpt-3.5-turbo", uuid="", image_search=True,):
    llm = ChatOpenAI(model_name=model, temperature=0, openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm, chain_type="stuff")

    with open("src/langchain/phone.json", "r") as infile:
        data = json.load(infile)
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    query_result = embeddings.embed_query(query)
    doclist = utils.maximal_marginal_relevance(query_result, data, k=1)
    loader = CSVLoader(file_path="src/langchain/phone.csv", encoding="utf8")
    csv_text = loader.load()

    docs = []

    for res in doclist:
        docs.append(
            Document(
                page_content=csv_text[res].page_content, metadata=csv_text[res].metadata
            )
        )

    chain_data = chain.run(input_documents=docs, question=query)
    try:
        result = json.loads(chain_data)
        # check image query with only its text
        if result["program"] == "image":
            if image_search:
                result["content"] = json.dumps(
                    {"image_name": query_image_text(result["content"], "", uuid)}
                )
            # else:
            #     return result
        return str(result)
    except ValueError as e:
        # Check sms query
        if doclist[0] in COMMAND_SMS_INDEXS:
            return str(json.dumps({"program": "sms", "content": chain_data}))
        return str(json.dumps({"program": "message", "content": chain_data}))


def query_image_ask(image_content, message, uuid):
    prompt_template = get_prompt_image_with_message(image_content, message)
    data = getCompletion(prompt_template, uuid, False)
    chain_data = json.loads(data.replace("'", '"'))
    if chain_data["program"] == "image":
        return True
    return False


def getTextFromImage(filename):
    # Create a reference to the image file you want to download
    bucket = storage.bucket()
    blob = bucket.blob(FIREBASE_STORAGE_ROOT.__add__(filename))
    download_url = ""

    try:
        # Download the image to a local file
        download_url = blob.generate_signed_url(
            datetime.timedelta(seconds=300), method="GET", version="v4"
        )

        output = replicate.run(
            "salesforce/blip:2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746",
            input={"image": download_url},
        )

    except Exception as e:
        output = str("Error happend while analyzing your prompt. Please ask me again :")

    return str(output)


"""chat with ai
response: 
{
 'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
 'object': 'chat.completion',
 'created': 1677649420,
 'model': 'gpt-3.5-turbo',
 'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
 'choices': [
   {
    'message': {
      'role': 'assistant',
      'content': 'The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers.'},
    'finish_reason': 'stop',
    'index': 0
   }
  ]
}
"""
def handle_chat_completion(messages: Any, model: str) -> Any:
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )
    return response
