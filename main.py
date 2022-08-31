# Reference to build API and deploy to vercel from
# https://dev.to/arctype/deploy-a-python-api-on-vercel-using-postgres-4871
# Delete the .env folder before run `vercel .` since will exceed the upload limit

import jieba
import json
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class ChineseText(BaseModel):
    text: str


def parse_chinese_text(text):
    text_jb = jieba.lcut(text)

    # Remove new line characters at beginning of array
    if text_jb[0] == "\n":
        text_jb.pop(0)

    # Make sure last element is a new line character for the loop to work properly
    if text_jb[len(text_jb) - 1] != "\n":
        text_jb.append("\n")

    # Create sub arrays for each line
    split_lines = []
    last_split = 0
    for i in range(len(text_jb)):
        if text_jb[i] == "\n":
            split_lines.append(text_jb[last_split:i])
            last_split = i + 1

    # print(split_lines)

    # Cross reference HSK vocab
    hsk_file = open('hsk.json')
    hsk_vocab = json.load(hsk_file)

    # Check to see if any HSK vocabulary in segmented text
    # If match, replace the word with hsk entry
    for sentence in split_lines:
        for i in range(len(sentence)):
            word = sentence[i]
            if word in hsk_vocab:
                sentence[i] = hsk_vocab[word]

    hsk_file.close()
    return split_lines


# API logic
app = FastAPI()

origins = [
    "https://chinese-hsk-reader.surge.sh"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)


@app.post("/segmentor")
def segment_chinese(data: ChineseText):
    print(data.text)
    json_compatible_item_data = jsonable_encoder(parse_chinese_text(data.text))
    return JSONResponse(content=json_compatible_item_data)


@app.get("/hello")
def greet():
    return JSONResponse("hi")


# @app.get("/hsk-lookup")
# def hsk_lookup(word):
#     return JSONResponse(content=word);
