import os
import json
import yaml
import uuid
import re
import hashlib
import tiktoken
import pandas as pd
import psycopg2
from typing import Union
from datetime import datetime, timezone
from fastapi import APIRouter, status, Depends, Request,Request, UploadFile, Request,Form
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from Engine.request import requestAPI, requestAPIStream
from Engine.generate_log import logger
from Engine.schema_classes import ChatDetails,cmdb_graph_schema
from Engine.jwt_auth import JWTBearer
from Engine.api_response import APIResponse
from Engine.get_ai_details import AI_Details
from psycopg2.extras import Json
 
config_path = os.getcwd()
config = yaml.safe_load(open(config_path + "/Engine/config.yaml"))
 
ai_config = yaml.safe_load(open(config_path + "/Azure_OpenAI_Connector/config.yaml"))
 
azure_open_ai_api_url = config["azure_open_ai_api_url"]
azure_open_ai_stream_api_url = config["azure_open_ai_stream_api_url"]
 
 
Ai_config_key=config["ai_config_key"]
STATUS_FAILURE = config["STATUS_FAILURE"]
STATUS_SUCCESS = config["STATUS_SUCCESS"]
 
 
 
LOCAL_FOLDER_PATH=config["cmdb_file_path"]
 
 
response_from_cmdb_data_url=config["response_from_cmdb_data_url"]
chat_with_cmdb_prompt=config["chat_with_cmdb_prompt"]
insert_cmdb_data_url=config["insert_cmdb_data_url"]
generate_cmdb_graph_api=config["generate_cmdb_graph_api"]
db_api_base_url=config["db_api_base_url"]
db_postgress_api=config["db_postgress_api"]
get_conversation_query=config["get_conversation_query"]
insert_conversation_query=config["insert_conversation_query"]
update_conversation_query=config["update_conversation_query"]
 
chat_history={}
 
router = APIRouter(prefix="/api/chat", tags=["/api/chat"])
 
 
def create_uuid_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))
 
 
def calculate_token(input_text: Union[str, list]) -> int:
    try:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding("cl100k_base")
        total_token = 0
        if type(input_text) == str:
            total_token = len(encoding.encode(input_text))
        else:
            for item in input_text:
                num_tokens = 0
                num_tokens = len(encoding.encode(item["content"]))
                total_token += num_tokens
        return total_token
    except Exception as e:
        logger.excepition("calculate_token -" + str(e))
        total_token = 0
        return total_token
 
@router.post("/upload_cmdb",dependencies=[Depends(JWTBearer())])
def upload_file_cmdb(request: Request,file: UploadFile,user_id:str=Form(...)):
    try:
        logger.info("inside upload functionality")
        token=request.headers.get("authorization")
        filename=file.filename
        filename_without_extension = os.path.splitext(filename)[0]
 
        file_ext = os.path.splitext(filename)[1].lower()
        datetime_string = datetime.utcnow().isoformat("#", "microseconds")
        sanitized_datetime_string = re.sub(r'\W', '_', datetime_string)
        file_id="Project"+ "_"+str(filename_without_extension)+ "_"+ str(sanitized_datetime_string)
        logger.info("file id is--------------->"+str(file_id))
       
        sanitized_file_id = re.sub(r'\W', '_', file_id)
        logger.info("file id is--------------->" + str(sanitized_file_id))
       
       
        db_url = str(db_api_base_url + db_postgress_api)
        insert_query = insert_conversation_query
       
        parameters=[user_id,str(sanitized_file_id)]
        req_data={
            "query":insert_query,
            "type": "INSERT",
            "params": parameters
        }
       
       
        db_response=requestAPI(db_url,"POST",req_data,token)
        if db_response.status_code==200:
            db_response_json=json.loads(db_response.content.decode("utf-8"))
            logger.info("db response is------------------->"+str(db_response_json))
            if db_response_json["status"]==STATUS_SUCCESS:                                        
                 
                file_content = file.file.read()
 
                if file_ext in ['.xlx', '.xlsx']:
                    # Convert to .csv
                    df = pd.read_excel(pd.io.common.BytesIO(file_content))
                    csv_filename = os.path.splitext(filename)[0] + '.csv'
                    file_path = os.path.join(f"{config_path}/{LOCAL_FOLDER_PATH}/{sanitized_file_id}", csv_filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    df.to_csv(file_path, index=False)
                    logger.info(f"File converted to CSV and saved at {file_path}--------------->")
                elif file_ext == '.csv':
                    # Save CSV file as it is
                    file_path = os.path.join(f"{config_path}/{LOCAL_FOLDER_PATH}/{sanitized_file_id}", filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as buffer:
                        buffer.write(file.file.read())
                    logger.info(f"CSV file saved at {file_path}")
                else:
                    logger.error("Unsupported file type")
                    raise ValueError("Unsupported file type. Only .csv, .xlx, and .xlsx files are allowed.")
                   
                logger.info("sending the file path to cmdb module------------->")
               
                data={
                    "file_path":file_path,
                    "project_name":str(sanitized_file_id)
                }
               
                response=requestAPI(insert_cmdb_data_url,"POST",data,token)
               
                if response.status_code==200:
                    logger.info("200 response from cmdb inser api------------>")
                    response_json=json.loads(response.content.decode("utf-8"))
                    if response_json["status"]=="success":
                        logger.info("succesfully insertes in neo4J----------->"+str(response_json))
                        api_response=APIResponse(
                            status=STATUS_SUCCESS,
                            message="Successfully inserted data in neo4J",
                            data=sanitized_file_id
                        )
                        return JSONResponse(status_code=200,content=api_response.__dict__)
                    else:
                        logger.info("Could not insert in neo4J")
                        api_response=APIResponse(
                            status=STATUS_FAILURE,
                            message=response_json["message"],
                            data=[]
                        )
                        return JSONResponse(status_code=status.HTTP_400,content=api_response.__dict__)
                else:
                    logger.info("Error in the api------------------->")
                    api_response=APIResponse(
                        status=STATUS_FAILURE,
                        message=response.text,
                        data=[]
                    )
                    return JSONResponse(status_code=response.status_code,content=api_response.__dict__)
            else:
                logger.info("Error inserting new conversation----------------------------------------")
                api_response=APIResponse(
                    status=STATUS_FAILURE,
                    message="error occurred while inserting in conversation table",
                    data=[]
                )
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content=api_response.__dict__)
        else:
            logger.info("error occurred connecting to db when uploading cmbd data and inserting new conversation")
            api_response=APIResponse(
                status=STATUS_FAILURE,
                message=db_response.text,
                data=[]
            )
            return JSONResponse(status_code=db_response.status_code,content=api_response.__dict__)        
    except Exception as e:
        logger.info("error occurred while uploading excel files")
        api_response=APIResponse(
            status=STATUS_FAILURE,
            message=str(e),
            data=[]
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content=api_response.__dict__)
     
@router.post("/cmdb_graph",dependencies=[Depends(JWTBearer())])
def generate_cmdb_graph(request:Request,details:cmdb_graph_schema):
    try:
        logger.info("Started generating graph for the file uploaded--------------->")
        token=request.headers.get("authorization")
        cmdb_file_id=details.file_id
        data={
            "project_name":cmdb_file_id
        }
       
        response=requestAPI(generate_cmdb_graph_api,"POST",data,token)
        if response.status_code==200:
            response_json=json.loads(response.content.decode("utf-8"))
            if response_json["status"]=="success":
                logger.info("succesfully created graph for the file"+str(response_json))
                api_response=APIResponse(
                    status=STATUS_SUCCESS,
                    message="succesfully created graph for the file",
                    data=response_json["data"]
                )
                return JSONResponse(status_code=200,content=api_response.__dict__)
            else:
                logger.info("Error occurred while creating graph"+str(response_json))
                api_response=APIResponse(
                    status=STATUS_SUCCESS,
                    message="Error occurred while creating graph",
                    data=[]
                )
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content=api_response.__dict__)
        else:
            logger.info("error occurred while connecting to cmdb module while generating graph")
            api_response=APIResponse(
                status=STATUS_FAILURE,
                message=response.text,
                data=[]
            )
            return JSONResponse(status_code=response.status_code,content=api_response.__dict__)
    except Exception as e:
        logger.info("")
        logger.info("error occurred while generating graph from engine")
        api_response=APIResponse(
            status=STATUS_FAILURE,
            message=str(e),
            data=[]
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content=api_response.__dict__)
       
# @router.post("/generate_ai_response", description="To conversate with ai and get response",dependencies=[Depends(JWTBearer())])
def generate_ai_response(Chat_Details, request):
    try:  
        azure_open_ai_config = AI_Details(ai_config=Ai_config_key)
        auth_token = request.headers.get("authorization")
        user_id = Chat_Details.user_id
        file_id=Chat_Details.file_id
        prompt_text = Chat_Details.prompt_text
        logger.info("file id is--------------->" + str(prompt_text))
        # logger.info("chat history is-------------------->"+str(chat_history))
        db_url = str(db_api_base_url + db_postgress_api)
        select_query = get_conversation_query
       
        parameters=[str(file_id)]
        req_data={
            "query":select_query,
            "type": "SELECT",
            "params": parameters
        }
        db_response=requestAPI(db_url,"POST",req_data,auth_token)
        if db_response.status_code==200:
            db_response_json=json.loads(db_response.content.decode("utf-8"))
            logger.info("db response is------------------->"+str(db_response_json))
            if db_response_json["status"]==STATUS_SUCCESS:
                if len(db_response_json["data"])!=0:
                    logger.info("12334----------")
                    if len(db_response_json["data"][0]["messages"])!=0:
                        Msg_List=db_response_json["data"][0]["messages"][0]
                        logger.info("message list from db is------------->"+str(Msg_List))
                        logger.info("12454555--------------------")
                    else:
                        Msg_List=db_response_json["data"][0]["messages"]
                else:
                    Msg_List=db_response_json["data"]
                   
                logger.info("message list is------------->"+str(Msg_List))                    
               
                Current_Usr_Msg = {'role': 'user', 'content': prompt_text}
                Msg_List.append(Current_Usr_Msg)
                data={
                   
                    "messages":Msg_List,
                    "project_name":file_id
                }
                cmdb_response=requestAPI(response_from_cmdb_data_url,"POST",data,auth_token)                
                if cmdb_response.status_code==200:
                    cmdb_response_json=json.loads(cmdb_response.content.decode("utf-8"))
                    logger.info("cmdb response is-------->"+str(cmdb_response_json))
                    if cmdb_response_json["status"]=="success":
                        logger.info("successfully retreived response from neo4j--------------->")
                       
                        chat_with_cmdb_prompt_new=chat_with_cmdb_prompt.format(content=cmdb_response_json["data"])
                        chat_prompt = {                  
                       
                            'role': 'system',
                            'content': chat_with_cmdb_prompt_new,
                        }                    
                        Msg_List.append(chat_prompt)
                        logger.info("chat with file msg list--- " + str(Msg_List))
                        data = {
                            "prompt": Msg_List,
                            "config": azure_open_ai_config.ai_details,
                        }              
                    else:
                        logger.info("could not fetch response from neo4j")
                        chat_with_cmdb_prompt_new=chat_with_cmdb_prompt.format(content=cmdb_response_json["data"])
                        chat_prompt = {                  
                       
                            'role': 'system',
                            'content': chat_with_cmdb_prompt_new,
                        }
       
                        Msg_List.append(chat_prompt)
                        logger.info("chat with file msg list--- " + str(Msg_List))
                        data = {
                            "prompt": Msg_List,
                            "config": azure_open_ai_config.ai_details,
                        }      
                elif cmdb_response.status_code==404:
                    logger.info("No response from cmdb")
                    cmdb_response_json=json.loads(cmdb_response.content.decode("utf-8"))
                    logger.info("cmdb response when status code is-------->"+str(cmdb_response_json))
                    chat_with_cmdb_prompt_new=chat_with_cmdb_prompt.format(content=cmdb_response_json["data"])
                    chat_prompt = {                  
                   
                        'role': 'system',
                        'content': chat_with_cmdb_prompt_new,
                    }
                    Msg_List.append(chat_prompt)
                    logger.info("chat with file msg list--- " + str(Msg_List))
                    data = {
                        "prompt": Msg_List,
                        "config": azure_open_ai_config.ai_details,
                    }
                else:
                    logger.info("error connecting to cmdb module------------->")
                    cmdb_response_json=json.loads(cmdb_response.content.decode("utf-8"))
                    logger.info("cmdb response when status is not 200 is-------->"+str(cmdb_response_json))
                    chat_with_cmdb_prompt_new=chat_with_cmdb_prompt.format(content=cmdb_response_json["data"])
                    chat_prompt = {                  
                   
                        'role': 'system',
                        'content': chat_with_cmdb_prompt_new,
                    }
                    Msg_List.append(chat_prompt)
                    logger.info("chat with file msg list--- " + str(Msg_List))
                    data = {
                        "prompt": Msg_List,
                        "config": azure_open_ai_config.ai_details,
                    }
                db_url = str(db_api_base_url + db_postgress_api)
                logger.info("123")
                serialize_message_list=[json.dumps(obj) for obj in Msg_List]
                parameters_1=[serialize_message_list,str(file_id)]
                update_query = update_conversation_query
                logger.info("update query is---------->"+str(update_query))
                req_data={
                    "query":update_query,
                    "type": "UPDATE",
                    "params": parameters_1
                }  
                update_response=requestAPI(db_url,"POST",req_data,auth_token)
                if update_response.status_code==200:
                    logger.info("successfully connected to db for updating conversation--->")
                    update_response_json=json.loads(update_response.content.decode("utf-8"))
                    if update_response_json["status"]=="success":
                        logger.info("successfully updated tyhe message list------>"+str(update_response_json))
                    else:
                        logger.info("failed to update conversation list----->")
                        api_response=APIResponse(status=STATUS_FAILURE,message="error updating conversation",data=[])
                        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content=api_response.__dict__)
                else:
                    logger.info("")
                    api_response=APIResponse(status=STATUS_FAILURE,message=update_response.text,data=[])
                    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content=api_response.__dict__)      
           
            else:
              logger.info("")
        else:
            logger.info("")
                   
        stream_status: bool=False
       
        AI_resp = requestAPIStream(
            azure_open_ai_stream_api_url, "POST", data, auth_token
        )
        logger.info("AI resp is---------->"+str(AI_resp))
        for chunk in AI_resp:
            stream_Data = json.loads(chunk)
            if stream_Data["status"] == STATUS_SUCCESS:
                logger.info("streaming in progress-------------->")
                if stream_Data["message"] == "Streaming-In-progress":
                    out_data = {
                        "ai_response": stream_Data["data"][0][
                            "genai_response"
                        ]
                    }
                    response = APIResponse(
                        status=STATUS_SUCCESS,
                        message="Response Stream In-progress",
                        data=out_data,
                    )
                    response.status_code = 206
                    yield json.dumps(response.__dict__) + str("\n")
                elif stream_Data["message"] == "Streaming-Completed":
                    stream_status = True
                    AI_resp = stream_Data
                    break
                else:
                    break
            else:
                break                
    except Exception as e:
        logger.exception("Exception occured in Generate AI Response API : " + str(e))
        response = APIResponse(
            status=STATUS_FAILURE,
            message="generate_ai_response api call failed - " + str(e),
            data=[],
        )
        response.status_code = 500
        yield json.dumps(response.__dict__) + str("\n")
@router.post(
    "/generate_ai_response",
    description="To conversate with ai and get response",
    dependencies=[Depends(JWTBearer())],
)
def get_ai_response(Chat_Details: ChatDetails, request: Request):
    try:
        logger.info("----------------starting generate_ai_response------------ ")
 
        return StreamingResponse(
            generate_ai_response(Chat_Details, request),
            media_type="application/x-ndjson",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.exception("Exception occured in generate AI response API : " + str(e))
        response = APIResponse(
            status=STATUS_FAILURE,
            message="generate_ai_response api call failed - " + str(e),
            data=[],
        )
        response.status_code = 500
        return StreamingResponse(
            iter(json.dumps(response.__dict__)),
            media_type="application/x-ndjson",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )