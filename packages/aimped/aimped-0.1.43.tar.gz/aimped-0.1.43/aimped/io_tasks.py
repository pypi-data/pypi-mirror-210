# Author Aimped
# Date: 2023-May-25
# Description: This file contains standart input and output (sio) keys for each task

from enum import Enum
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field

data_types = [
    'data_json',
    'data_pdf',
    'data_image',
    'data_svg',
    'data_audio',
    'data_csv',
    'data_txt',
    'data_excel',
    'data_docx',
    'data_xml',
    'data_video',
    'data_zip',
    'data_char',
    'data_file',
    'raw_output'
]


################ Task: Text Classification ################

class TextClassificationInput(BaseModel):
    text: List[str] = Field(..., description="List of texts", example=["This is an example text for classification.",
                                                                       "This is another example text for classification."])

class TextClassificationOutput(BaseModel):
    status: bool = True
    data_type: List[str] = Field(default=["data_json"], description="List of data types", enum=data_types)
    output: Dict[str, Any] = Field(
        default={"data_json": {"result": None}},
        description="data_json output dictionary",
        keys={"enum": data_types},
        example={
            'data_json': {
                'result': [
                    {
                        'category': [str],
                        'classes': [{'label': str, 'score': float},
                                    {'label': str, 'score': float}]
                    }
                ]
            }
        }
    )

    def __init__(self, model_prediction: Any, **data: Any):
        super().__init__(**data)
        self.output['data_json']['result'] = model_prediction


################ Task: Name Entity Recognition ################

class NameEntityRecognitionInput(BaseModel):
    text: List[str] = Field(..., description="List of texts", example=["This is an example text for NER."])


class NameEntityRecognitionOutput(BaseModel):
    status: bool = True
    data_type: List[str] = Field(default=["data_json"], description="List of data types", enum=data_types)
    output: Dict[str, Any] = Field(
        default={"data_json": {"result": None}},
        description="Output dictionary",
        keys={"enum": data_types},
        example={
            'data_json': {
                'result': [
                    [{
                        'entity': str,
                        'confidence': float,
                        'chunk': str,
                        'begin': int,
                        'end': int
                    }]
                ]
            }
        }
    )

    def __init__(self, model_prediction: Any, **data: Any):
        super().__init__(**data)
        self.output['data_json']['result'] = model_prediction


######################### Task: Deidentification #########################

class DeidentificationInput(BaseModel):
    text: List[str] = Field(..., description="List of texts", example=["This is an example text for deidentification."])


class DeidentificationOutput(BaseModel):
    status: bool = True
    data_type: List[str] = Field(default=["data_json"], description="List of data types", enum=data_types)
    output: Dict[str, Any] = Field(
                                    default={"data_json": {"result": None}},
                                    description="Output dictionary",
                                    keys={"enum": data_types},
                                    example={
                                        'data_json': {'result': [
                                            {'entities': [
                                                {
                                                    'entity': str,
                                                    'confidence': float,
                                                    'chunk': str,
                                                    'begin': int,
                                                    'end': int,
                                                    'faked_chunk': str
                                                }],
                                                'masked_text': str,
                                                'faked_text': str
                                            }]
                                        }}
                                )

    def __init__(self, model_prediction: Any, **data: Any):
        super().__init__(**data)
        self.output['data_json']['result'] = model_prediction


####################### Task: Chatbot ###################### TODO: Still in development

class ChatbotInput(BaseModel):
    messages: List[Dict[str, str]] = Field(..., description="List of messages",
                                           example=[{"role": "user", "content": "Who are you?"},
                                                    {"role": "assistant", "content": "I am Chat Bot. Who are you?"},
                                                    {"role": "user", "content": "I am Joseph."}
                                                    ])
    stream: bool = False
    max_tokens: int = 256
    temperature: float = 0.7

# TODO: Add post_init function to check if messages are in correct format
class ChatbotOutput(BaseModel):
    status: bool = True
    data_type: List[str] = Field(default=["data_json", "data_audio"],
                                 description="List of data types",
                                 enum=data_types)
    data_json: Dict[str, Any] = Field(default=None, description="Text API Output in dictionary", repr=False)
    data_audio: str = Field(default=None, description="Audio API Output in base64 format", repr=False,
                            example="data:audio/mp3;base64,//tQxA-audio-base64-format-string", )
    raw_output: Dict[str, Any] = Field(default=None, description="Raw API Output in dictionary", repr=False,
                                       exclude=True)
    output: Dict[str, Any] = Field(
        default={"data_json": {"text": None}, "data_audio": None, "raw_output": None},
        description="Output dictionary",
        keys={"enum": data_types},
        example={
            "data_json": {"text": "Well…   good luck…"},
            "raw_output": {'choices': [{'message': {'content': 'Well… good luck…', 'role': 'assistant',
                                                    'finish_reason': 'stop', 'index': 0, }}],
                           'created': 1683618639,
                           'id': 'chaxxpl-7EXXXXXwQNqPmXXXXXaYWkMtKNVjg',
                           'model': 'gpt-3.5-turbo-0301',
                           'object': 'chat.completion',
                           'usage': {'completion_tokens': 27,
                                     'prompt_tokens': 186,
                                     'total_tokens': 213}},
            "data_audio": "data:audio/mp3;base64,//tQxA-audio-base64-format-audio-file...==="},
    )


######################## Task: OCR ######################## TODO: Still in development

class OcrInput(BaseModel):
    text: str
    file_type: str
    file: str


class OcrOutput(BaseModel):
    status: bool
    data_type: List[str] = Field(default=["data_image"], description="List of data types", enum=data_types)
    output: Dict[str, Any] = Field(
        default={"data_image": None},
        description="Output dictionary",
        keys={"enum": data_types}
    )


if __name__ == "__main__":
    from pprint import pprint

    # Creating an instance of TextClassificationInput
    input_data = TextClassificationInput(
        text=["This is an example text for classification.", 
              "This is another example text for classification."])

    # Printing the input data
    print("\nText Classification Input:")
    pprint(input_data)
    pprint(input_data.text)

    # Creating an instance of TextClassificationOutput
    cls_result = [
        {
            'category': ["X"],
            'classes': [
                {'label': "X", 'score': 0.9}, {'label': "Y", 'score': 0.1}]
        }]
    output_data = TextClassificationOutput(model_prediction=cls_result)

    # Printing the output data
    print("\nText Classification Output:")
    pprint(output_data.dict())
    # print(output_data.json(indent=2))
