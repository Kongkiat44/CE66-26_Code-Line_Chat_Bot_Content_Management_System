from flask import Flask, request, abort, jsonify
import json, os, requests, time, hashlib
import random, string
from datetime import datetime

# from created module for MongoDB connection
import linecms_database

# import classes related to MongoDB
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from pymongo.mongo_client import MongoClient

# import classes from Line Bot SDK
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, ImageMessage, PushMessageRequest,
)
from linebot.v3.webhooks import (MessageEvent, TextMessageContent, ImageMessageContent,
    JoinEvent, LeaveEvent, MemberJoinedEvent, MemberLeftEvent, UnsendEvent, FollowEvent, 
    UnfollowEvent, PostbackEvent, FileMessageContent, 
)

# create flask app variable
app = Flask(__name__)

# get string variables from docker compose file (environment section) and stored as constant
BOT_ACCESS_TOKEN = os.getenv("BOT_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
SAVE_GROUPPROFILE_PATH = os.getenv("SAVE_GROUPPROFILE_PATH")
SAVE_GRAPH_PATH = os.getenv("SAVE_GRAPH_PATH")
SAVE_FACE_PATH = os.getenv("SAVE_FACE_PATH")
SAVE_IMAGE_PATH = os.getenv("SAVE_IMAGE_PATH")
SAVE_FILE_PATH = os.getenv("SAVE_FILE_PATH")
MODEL_SERVER_IMAGE_LINK = os.getenv("MODEL_SERVER_IMAGE_LINK")
MODEL_SERVER_OTHER_LINK = os.getenv("MODEL_SERVER_OTHER_LINK")
MODEL_SERVER_GRAPH_LINK = os.getenv("MODEL_SERVER_GRAPH_LINK")
SERVER_URL = os.getenv("SERVER_URL")
LIFF_URL = os.getenv("LIFF_URL")

# set line bot config with access token and webhook handler with channel secret id
# both access token and channel secret id can be found on Line Developer on Chat bot info
configuration = Configuration(access_token=BOT_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# set messaging api variable for interaction with line chat bot
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

# default states for checking database connection
save_data_on_db = True
is_mongoDB_connect = False
db_client = None

# variables about database name and collections
DATABASE_NAME = os.getenv("DATABASE_NAME")
database = None
col_groups = None
col_images = None
col_users = None
col_faces = None
col_graphs = None
col_clusters = None
col_logs = None
col_files = None
col_imgreq = None

# ---- Defined Function Section ----

# function for creating bubble menu for user to download select file
def pushFileBubbleMenu(groupName: str, fileName: str, fileUrl: str):
    bubbleMenu = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": fileName,
                    "weight": "bold",
                    "size": "xl",
                    "align": "start",
                    "wrap": True,
                    "scaling": True,
                    "style": "normal"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "กลุ่ม",
                                    "color": "#aaaaaa",
                                    "size": "md",
                                    "flex": 1,
                                    "weight": "regular"
                                },
                                {
                                    "type": "text",
                                    "text": groupName,
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "md",
                                    "flex": 5
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "ดาวน์โหลดไฟล์",
                        "uri": fileUrl
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
            ],
            "flex": 0
        }
    }
    bubble_menu_dict = {
        "type": "flex",
        "altText": "LineCMS ได้ส่งไฟล์",
        "contents": {
            "type": "carousel",
            "contents": [bubbleMenu]
        }
    } 
    return bubble_menu_dict

# function for creating bubble menu for user to click to get more images
def moreImageBubbleMenu(requestImgId: str):
    bubbleMenu = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "กดปุ่มเพื่อดูรูปภาพเพิ่มเติม",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center",
                    "wrap": True,
                    "scaling": False,
                    "style": "normal"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "ดูรูปภาพเพิ่มเติม",
                        "data": "imgreq="+requestImgId
                    },
                    "color": "#00ad74",
                    "style": "primary"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
            ],
            "flex": 0
        }
    }
    bubble_menu_dict = {
        "type": "flex",
        "altText": "กดเพื่อดูรูปเพิ่ม",
        "contents": {
            "type": "carousel",
            "contents": [bubbleMenu]
        }
    } 
    return bubble_menu_dict

# function for creating a bubble menu of face
def create_bubble_menu_face(faceUrl: str, clusterId: str, groupId: str, action: str):
    # return false if function doesn't get all 4 parameters
    if faceUrl is None or clusterId is None or groupId is None or action is None:
        return False
    
    # create bubble menu with given parameter
    bubble_menu_dict = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": SERVER_URL+"/linecms/face/"+faceUrl,
            "size": "240px",
            "animated": False,
            "aspectMode": "cover",
            "aspectRatio": "1:1",
            "align": "center"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "เลือกใบหน้านี้",
                        "data": "selectFace=1&clusterId="+clusterId+"&groupId="+groupId+"&type="+action
                    },
                    "style": "primary",
                    "position": "relative",
                    "height": "sm"
                }
            ],
            "spacing": "lg",
            "position": "relative",
            "maxHeight": "75px",
            "height": "115px"
        }
    }
    return bubble_menu_dict

# function for creating a bubble menu of group
def create_bubble_menu_group(picUrl: str, groupName: str, groupId: str, buttonLabel: str, action: str):
    # return false if function doesn't get all 5 parameters
    if picUrl is None or groupName is None or groupId is None or buttonLabel is None or action is None:
        return False
    
    # create bubble menu with given parameter
    bubble_menu_dict = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": picUrl,
            "size": "full",
            "animated": False,
            "aspectMode": "cover",
            "aspectRatio": "17:15",
            "align": "center"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": groupName,
                    "size": "xl",
                    "align": "center",
                    "weight": "regular",
                    "style": "normal",
                    "wrap": False
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": buttonLabel,
                        "data": "selectGroup=1&groupId="+groupId+"&type="+action
                    },
                    "style": "primary",
                    "position": "relative",
                    "height": "sm"
                }
            ],
            "spacing": "lg",
            "position": "relative",
            "maxHeight": "130px",
            "height": "115px"
        }
    }
    return bubble_menu_dict

# function for creating a carousel menu for select group
def create_carousel_menus_group(groupList: list, actType: str):
    bubbles_object_list = []

    # create bubble menus from given list of groups
    for group in groupList:
        if ("groupId" not in group) or ("groupName" not in group) or ("profileLink" not in group):
            return False
        else:
            bubble_menu_dict = create_bubble_menu_group(picUrl=group["profileLink"], groupName=group["groupName"], groupId=group["groupId"], buttonLabel="เลือกกลุ่มนี้", action=actType)
            if bubble_menu_dict is False:
                return False
            else:
                bubbles_object_list.append(bubble_menu_dict)

    carousel_menus_dict = {
        "type": "flex",
        "altText": "LineCMS ได้ส่งเมนูเลือกกลุ่มไลน์",
        "contents": {
            "type": "carousel",
            "contents": bubbles_object_list
        }
    }        
    return carousel_menus_dict

# function for creating a carousel menu for select face
def create_carousel_menus_face(faceList: list, actType: str):
    bubbles_object_list = []

    # create bubble menus from given list of faces
    for face in faceList:
        if ("clusterId" not in face) or ("faceFile" not in face) or ("groupId" not in face):
            return False
        else:
            bubble_menu_dict = create_bubble_menu_face(faceUrl=face["faceFile"], clusterId=face["clusterId"], groupId=face["groupId"], action=actType)
            if bubble_menu_dict is False:
                return False
            else:
                bubbles_object_list.append(bubble_menu_dict)

    carousel_menus_dict = {
        "type": "flex",
        "altText": "LineCMS ได้ส่งเมนูเลือกใบหน้า",
        "contents": {
            "type": "carousel",
            "contents": bubbles_object_list
        }
    }        
    return carousel_menus_dict

# function for creating a document of group data to save in database collection named 'Groups'
def create_group_col_data(line_bot_api: MessagingApi, group_id: str) -> dict:
    # get group information and user ids of that group from line messaging api
    api_response = line_bot_api.get_group_summary(group_id)
    group_summary = json.loads(api_response.to_json())
    api_response = line_bot_api.get_group_members_ids(group_id)
    group_member_ids = json.loads(api_response.to_json())

    total_ids = []
    total_ids.extend(group_member_ids["memberIds"])

    # get next group of user ids with next token if there is property 'next' in api response
    while "next" in group_member_ids:
        next_token = group_member_ids["next"]
        api_response = line_bot_api.get_group_members_ids(group_id,start=next_token)
        group_member_ids = json.loads(api_response.to_json())
        total_ids.extend(group_member_ids["memberIds"])
    
    # if api response does not contain property 'pictureUrl' then the group profile link is blank
    if "pictureUrl" not in group_summary:
        group_image_link = ""
    else:
        group_image_link = group_summary["pictureUrl"]

    # create a document of group data
    group_col_data = {
        "_id": group_id,
        "group_name": group_summary["groupName"],
        "group_image_link": group_image_link,
        "member_ids": total_ids,
        "status": "Active",
        "image_count": 0,
        "file_count": 0,
        "last_used": datetime.now()
    }

    return group_col_data

# function for creating a document of image data to save in database collection named 'Images'
def create_image_col_data(imageName: str, groupId: str, messageId: str, senderId:str) -> dict:
    image_col_data = {
        "_id": imageName,
        "group_id": groupId,
        "cluster_ids": [],
        "message_id": messageId,
        "sender_id": senderId,
        "saved_time": datetime.now(),
        "updated_time": datetime.now()
    }
    return image_col_data

# function for creating a document of file data to save in database collection named 'Files'
def create_file_col_data(localFileName: str, groupId: str, lineFileName: str, messageId: str, senderId: str) -> dict:
    file_col_data = {
        "_id": localFileName,
        "group_id": groupId,
        "file_name": lineFileName,
        "message_id": messageId,
        "sender_id": senderId,
        "saved_time": datetime.now(),
    }
    return file_col_data

# function for creating a document of user data to save in database collection named 'Users'
def create_user_col_data(userId: str) -> dict:
    user_col_data = {
        "_id": userId,
        "status": "Active",
        "added_time": datetime.now(),
        "last_used": datetime.now()
    }
    return user_col_data

# function for creating a document of log data to save in database collection named 'Logs'
def create_log_col_data(type: str, relatedTo: str, message: str, savedTime: datetime) -> dict:
    log_data = {
        "type": type,
        "related_to": relatedTo,
        "content": message,
        "saved_time": savedTime,
    }
    return log_data

# function for creating a document of image request data to save in database collection named 'ImageRequests'
def create_imgreq_col_data(userId: str, clusterId: ObjectId, imgLink: list) -> dict:
    imgreq_col_data = {
        "user_id":userId,
        "cluster_id":clusterId,
        "img_link_list":imgLink
    }
    return imgreq_col_data

# function for set select database name and collections
def set_db_variables(dbClient : MongoClient, dbName: str = None):
    try:
        dbClient.admin.command("ping")
    except Exception as e:
        return False, str(e)

    global database, col_users, col_groups, col_images, col_logs, col_clusters, col_faces, col_graphs, col_files, col_imgreq
    if dbName == None:
        database = dbClient[DATABASE_NAME]
    else:
        database = dbClient[dbName]

    # set variables corresponding to each database collections
    col_users = database.Users
    col_groups = database.Groups
    col_images = database.Images
    col_logs = database.Logs
    col_clusters = database.Clusters
    col_faces = database.Faces
    col_graphs = database.Graphs
    col_files = database.Files
    col_imgreq = database.ImageRequests
    return True, ""



# function for responding to user select option 'Search Image by Face' or 'Create Relationship Graph' from rich menu or start-up menu
def action_img_graph(action: str, userId: str) -> None:
    if action == "searchImage":
        log_message = "User tapped \"Search Image by Face\" menu on LineCMS official"
        action_msg = "ค้นหารูปภาพด้วยใบหน้า"
        action_type = "image"
    elif action == "createRelaGraph":
        log_message = "User tapped \"Create Relationship Graph\" menu on LineCMS official"
        action_msg = "สร้างกราฟความสัมพันธ์"
        action_type = "graph"
    else:
        raise Exception("Incorrect action argument. arg:",action)

    # log user activity to database
    log_data = create_log_col_data("Official", userId, log_message, datetime.now())
    col_logs.insert_one(log_data)

    # find groups that both user and line chat bot are member of group
    group_list = []
    for group in col_groups.find({"status":"Active"}):
        if userId in group["member_ids"]:
            group_data = {
                "groupId":group["_id"],
                "groupName":group["group_name"],
                "profileLink":group["group_image_link"]
            }
            group_list.append(group_data)
    
    # Response to user
    
    # send response message and/or 'select group' menus to user
    if len(group_list) > 12: # 
        # send message to tell user to select a group on LIFF website
        th_text = """โปรดกรุณาเข้าเว็บไซต์ LIFF จากลิงค์นี้เพื่อทำขั้นตอนเลือกกลุ่มไลน์ที่ต้องการ{actmsg}ต่อไป\n* เว็บไซต์สามารถใช้งานได้บนแอพไลน์ของอุปกรณ์ Andriod และ iOS เท่านั้น""".format(actmsg=action_msg)
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text)]
            )
        )
        # send user a LIFF website message
        liffAppLink = LIFF_URL
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=liffAppLink)]
            )
        )
    elif len(group_list) > 0:
        th_text = "โปรดกรุณาเลือกกลุ่มไลน์ที่ต้องการ{actmsg}จากเมนูต่อไปนี้".format(actmsg=action_msg)
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text)]
            )
        )

        # create carousel menus and send to user
        group_carousel_menus = create_carousel_menus_group(groupList=group_list, actType=action_type)
        if group_carousel_menus is False:
            raise Exception("While processing Post Event {actmsg}, the issue was occured at creating carousel menu for group".format(actmsg=action_msg))
        else:
            url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN), "Content-Type":"application/json"}
            carousel_menu_post_data = {
                "to": userId,
                "messages": [group_carousel_menus]
            }
            post_menu_response = requests.post(url="https://api.line.me/v2/bot/message/push", headers=url_headers, json=carousel_menu_post_data)
            if post_menu_response.status_code != 200:
                raise Exception("There was an issue occured at sending carousel menu for selecting group", post_menu_response.status_code, post_menu_response.text)
    else:
        th_text = "ขณะนี้เราไม่พบกลุ่มไลน์ที่สามารถทำรายการดังกล่าวได้ โปรดตรวจสอบให้แน่ใจว่าในกลุ่มไลน์ที่คุณต้องการทำรายการมีแชทบอท CMS Official อยู่ภายในกลุ่ม หรือหากยังไม่มีแชทบอทอยู่ภายในกลุ่มคุณสามารถเชิญ CMS Official เข้าไปในกลุ่มเพื่อให้สามารถทำรายการต่อไปได้"
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text)]
            )
        )

# function for responding to user when select a group from 'select group' menus
def res_sel_group(action_type: str, userId: str, groupId: str) -> None:
    cluster_list = []
    if action_type == "image":
        action_msg = "ค้นหารูปภาพด้วยใบหน้า"
    elif action_type == "graph":
        action_msg = "สร้างกราฟความสัมพันธ์"
    else:
        raise Exception("Incorrect action type argument. arg:",action_type)
    
    # log user activity to database
    log_message = "User chose group id {groupId} from carousel menu on LineCMS official".format(groupId=groupId)
    log_data = create_log_col_data("Official", userId, log_message, datetime.now())
    col_logs.insert_one(log_data)

    # check the condition of selected group (both user and line chat bot are still member of group)
    selGroup = col_groups.find_one({"_id":groupId})
    if (selGroup is None) or (selGroup["status"] == "Deleted") or not (userId in selGroup["member_ids"]):
        th_text = "ขณะนี้กลุ่มไลน์ที่คุณเลือกไม่สามารถทำรายการ{actmsg}ได้ โปรดตรวจสอบให้แน่ใจว่ากลุ่มไลน์ที่คุณเลือกมีแชทบอท CMS Official และคุณเป็นสมาชิกภายในกลุ่ม".format(actmsg=action_msg)
        
        # send message to user when condition is not met and exit function
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text)]
            )
        )
        return None

    # get cluster data with selected group id from database
    for cluster in col_clusters.find({"group_id":groupId}):
        if "face_link" in cluster:
            cluster_data = {
                "clusterId":str(cluster["_id"]),
                "faceFile":cluster["face_link"],
                "groupId":groupId
            }
            cluster_list.append(cluster_data)

    # Response to user
    
    # send response message and/or 'select face' menus to user
    if len(cluster_list) > 12:
        # send message to tell user to select a face on LIFF website
        th_text2 = """เนื่องจากมีใบหน้าที่ให้เลือกได้มากกว่าที่จะแสดงในห้องแชทนี้ได้ โปรดกรุณาเข้าเว็บไซต์ LIFF จากลิงค์นี้เพื่อทำการ{actmsg}บนเว็บไซต์แทน\n* เว็บไซต์สามารถใช้งานได้บนแอพไลน์ของอุปกรณ์ Andriod และ iOS เท่านั้น""".format(actmsg=action_msg)
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text2)]
            )
        )
        # send user a LIFF website message
        liffAppLink = LIFF_URL
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=liffAppLink)]
            )
        )
    elif len(cluster_list) > 0:
        # create carousel menus and send to user with message
        group_carousel_menus = create_carousel_menus_face(faceList=cluster_list, actType=action_type)
        th_text = "โปรดกรุณาเลือกใบหน้าที่ต้องการ{actmsg}จากเมนูต่อไปนี้".format(actmsg=action_msg)
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text)]
            )
        )
        
        if group_carousel_menus is False:
            raise Exception("While processing Post Event {actmsg}, the issue was occured at creating carousel menu for face".format(actmsg=action_msg))
        else:
            url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN), "Content-Type":"application/json"}
            carousel_menu_post_data = {
                "to": userId,
                "messages": [group_carousel_menus]
            }
            post_menu_response = requests.post(url="https://api.line.me/v2/bot/message/push", headers=url_headers, json=carousel_menu_post_data)
            if post_menu_response.status_code != 200:
                raise Exception("There was an issue occured at sending carousel menu for selecting face", post_menu_response.status_code, post_menu_response.text)
    else:
        th_text1 = """ขณะนี้ระบบไม่พบรูปภาพที่นำมาใช้ได้ หากในกลุ่มไลน์ยังไม่มีการส่งรูปภาพที่มีใบหน้าของคนอยู่ในภาพ กรุณาส่งรูปภาพลงในกลุ่ม รอประมวลผลสัก 5-10 นาทีและกลับมาทำรายการนี้อีกครั้ง"""
        th_text2 = """กรณีมีการส่งรูปภาพจำนวนมากลงในกลุ่ม ตัวระบบกำลังประมวลผลรูปภาพที่ได้รับในกลุ่ม โปรดรออย่างน้อย 10 นาทีและกลับมาทำรายการซ้ำอีกครั้ง"""
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text1)]
            )
        )
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text2)]
            )
        )

# function for responding to user when select a face from 'select face' menus
def res_sel_face(action_type: str, userId: str, groupId: str, clusterId: str) -> None:
    if action_type == "image":
        action_msg = "ค้นหารูปภาพด้วยใบหน้า"
    elif action_type == "graph":
        action_msg = "สร้างกราฟความสัมพันธ์"
    else:
        raise Exception("Incorrect action type argument. arg:",action_type)
    
    # log user activity to database
    log_message = "User chose face from cluster id {clusterId} from carousel menu on LineCMS official".format(clusterId=clusterId)
    log_data = create_log_col_data("Official", userId, log_message, datetime.now())
    col_logs.insert_one(log_data)

    # check the condition of selected group (both user and line chat bot are still member of group)
    selGroup = col_groups.find_one({"_id":groupId})
    if (selGroup is None) or (selGroup["status"] == "Deleted") or not (userId in selGroup["member_ids"]):
        # send message to user when condition is not met and exit function
        th_text = "ขณะนี้กลุ่มไลน์ที่คุณเลือกไม่สามารถทำรายการ{actmsg}ได้ โปรดตรวจสอบให้แน่ใจว่ากลุ่มไลน์ที่คุณเลือกมีแชทบอท CMS Official และคุณเป็นสมาชิกภายในกลุ่ม".format(actmsg=action_msg)
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text)]
            )
        )
        return None

    # if act type is 'image' then send images to user
    # if act type is 'graph' then send POST request to model server and response to user with message
    if action_type == "image":
        reqImgLinkList = []
        
        if not ObjectId.is_valid(clusterId):
            raise Exception("in res_sel_face, action_type=image, cannot create ObjectId from given cluster id "+clusterId)
        
        # query image collection to select image with match group id and has cluster id in cluster_ids array
        # and then add image url link to list
        for image in col_images.find({"group_id":groupId, "cluster_ids":ObjectId(clusterId)}):
            imgUrl = SERVER_URL+"/linecms/image/"+str(image["_id"])
            reqImgLinkList.append(imgUrl)
        
        # check if image links are more than 20 links
        # if true then create image request collection, store in db and send the first 20 images to user
        # if false then send all images to user without creating image request collection
        if len(reqImgLinkList) > 20:
            for i in range(20):
                imglink = reqImgLinkList.pop()
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=userId,
                        messages=[ImageMessage(originalContentUrl=imglink, previewImageUrl=imglink)]
                    )
                )
            
            # create and store image request data to db collection and delete the previous one if exist
            prevReq = col_imgreq.find_one({"user_id": userId, "cluster_id": ObjectId(clusterId)})
            if prevReq is not None:
                delResult = col_imgreq.delete_one({"_id":prevReq["_id"]})
                if delResult.deleted_count == 0:
                    raise Exception("Cannot delete the previous document in ImageRequests collection")

            imgreq_data = create_imgreq_col_data(userId, ObjectId(clusterId), reqImgLinkList)
            insertResult = col_imgreq.insert_one(imgreq_data)
            reqimgId = str(insertResult.inserted_id)
            
            # send message to user
            th_text = """ในปัจจุบันยังเหลือรูปภาพ {imgcount} รูปให้คุณสามารถดูเพิ่มได้ หากต้องการดูรูปภาพเพิ่มเติมให้คุณกดปุ่ม \"ดูรูปภาพเพิ่มเติม\" ถัดจากข้อความนี้""".format(imgcount=len(reqImgLinkList))
            line_bot_api.push_message(
                PushMessageRequest(
                    to=userId,
                    messages=[TextMessage(text=th_text)]
                )
            )

            # create send bubble menu 'click to see more images' to user
            moreImageBtn = moreImageBubbleMenu(reqimgId)
            url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN), "Content-Type":"application/json"}
            bubble_menu_post_data = {
                "to": userId,
                "messages": [moreImageBtn]
            }
            post_menu_response = requests.post(url="https://api.line.me/v2/bot/message/push", headers=url_headers, json=bubble_menu_post_data)
            if post_menu_response.status_code != 200:
                raise Exception("There was an issue occured at sending bubble menu for \'click for more image\'", post_menu_response.status_code, post_menu_response.text)
        else:
            while len(reqImgLinkList) > 0:
                imglink = reqImgLinkList.pop()
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=userId,
                        messages=[ImageMessage(originalContentUrl=imglink, previewImageUrl=imglink)]
                    )
                )
    elif action_type == "graph":
        # send cluster id and user id to model server
        isPostGraph, postGraphMsg = post_relationshipGraph(clusterId, userId)
        if not isPostGraph:
            raise Exception("Fail to post relationship graph. {msg}".format(msg=postGraphMsg))
        
        #send message to user
        th_text = "เราได้รับคำขอสร้างกราฟจากคุณแล้ว เราจะทำการส่งผลลัพธ์การสร้างกราฟความสัมพันธ์มาให้ในช่องทางนี้เมื่อดำเนินการเสร็จเรียบร้อยแล้ว โปรดกลับมาตรวจสอบผลลัพธ์ในภายหลัง"
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=th_text)]
            )
        )
    else:
        raise Exception("Incorrect action type argument")

# function for responding to postback event from 'click to see more images' bubble menu
def postMoreImage(reqId: str, reqUserId: str):
    if not ObjectId.is_valid(reqId):
        raise Exception("in postMoreImage function it cannot create ObjectId from given string ObjectId "+reqId)
    
    # query db collection with request id
    reqImgDoc = col_imgreq.find_one({"_id":ObjectId(reqId)})

    # send message to user if there is no more images left to see more (query collection return None)
    # and exit the function
    if reqImgDoc is None:
        th_text = """คุณได้กดดูรูปภาพครบทั้งหมดแล้ว ระบบจึงไม่สามารถส่งรูปภาพได้อีก กรุณากดเมนู ค้นหารูปภาพด้วยใบหน้า เพื่อทำรายการใหม่อีกครั้ง"""
        line_bot_api.push_message(
            PushMessageRequest(
                to=reqUserId,
                messages=[TextMessage(text=th_text)]
            )
        )
        return None

    # get image link list
    reqImgLinkList = reqImgDoc["img_link_list"]

    # if image links are more than 20 link then send the first 20 images link to user and send bubble menu 'click to see more images' to user
    # if not more than 20 links then send all image links to user
    if len(reqImgLinkList) > 20:
        for i in range(20):
            imglink = reqImgLinkList.pop()
            line_bot_api.push_message(
                PushMessageRequest(
                    to=reqUserId,
                    messages=[ImageMessage(originalContentUrl=imglink, previewImageUrl=imglink)]
                )
            )
        
        # update image request document in ImageRequests collection
        updateReq = col_imgreq.find_one_and_update(filter={"_id":ObjectId(reqId)},update={"$set":{"img_link_list":reqImgLinkList}},
                                        return_document=ReturnDocument.AFTER)
        
        # check if it updates the existed one and not from new document
        if reqImgDoc["_id"] != updateReq["_id"]:
            raise Exception("""in postMoreImage function, updated ObjectId is not the same with before update
                            before update:{idbefore}\nafter update:{idafter}""".format(idbefore=str(reqImgDoc["_id"]), idafter=str(updateReq["_id"])))
        
        # send message to user
        th_text = """ในปัจจุบันยังเหลือรูปภาพ {imgcount} รูปให้คุณสามารถดูเพิ่มได้ หากต้องการดูรูปภาพเพิ่มเติมให้คุณกดปุ่ม \"ดูรูปภาพเพิ่มเติม\" ถัดจากข้อความนี้""".format(imgcount=len(reqImgLinkList))
        line_bot_api.push_message(
            PushMessageRequest(
                to=reqUserId,
                messages=[TextMessage(text=th_text)]
            )
        )

        # send bubble menu 'click to see more images'
        moreImageBtn = moreImageBubbleMenu(reqId)
        url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN), "Content-Type":"application/json"}
        bubble_menu_post_data = {
            "to": reqUserId,
            "messages": [moreImageBtn]
        }
        post_menu_response = requests.post(url="https://api.line.me/v2/bot/message/push", headers=url_headers, json=bubble_menu_post_data)
        if post_menu_response.status_code != 200:
            raise Exception("There was an issue occured at sending bubble menu for \'click for more image\'", post_menu_response.status_code, post_menu_response.text)
    else:
        while len(reqImgLinkList) > 0:
            imglink = reqImgLinkList.pop()
            line_bot_api.push_message(
                PushMessageRequest(
                    to=reqUserId,
                    messages=[ImageMessage(originalContentUrl=imglink, previewImageUrl=imglink)]
                )
            )
        
        # delete image request document from collection
        delResult = col_imgreq.delete_one({"_id":ObjectId(reqId)})
        if delResult.deleted_count == 0:
            raise Exception("in postMoreImage function, cannot delete document after sent all leftover image. Doc id:"+reqId)

# function for sending POST request to model server to create relationship graph
def post_relationshipGraph(clusterId: str, userId: str):
    model_api_data = {
        "user_id":userId,
        "cluster_id":clusterId
    }
    model_api_url = MODEL_SERVER_GRAPH_LINK
    max_retry = 3
    retry_count = 0
    while retry_count < max_retry:
        response = requests.post(model_api_url,json=model_api_data)
        if response.status_code == 200:
            return True, "Request sent successful"
        elif response.status_code == 500:
            time.sleep(1)
            retry_count += 1
        else:
            return False, "Post returned unexpected status.\nres_status_code={code}\nres_text={text}".format(code=response.status_code, text=response.text)
    else:
        return False, "Retry post model api reach maximum value"

# function for create start-up carousel menu (for device that does not support line rich menu)
def createStartUpCarouselMenu():
    stringMsgSet = [
        {
            "icon":"cms-searchimage.png",
            "title":"ค้นหาภาพด้วยใบหน้า",
            "reqData":"searchImg"
        },
        {
            "icon":"cms-graph.png",
            "title":"สร้างกราฟความสัมพันธ์",
            "reqData":"createGraph"
        },
        {
            "icon":"cms-liff.png",
            "title":"ใช้งานบนเว็บไซต์",
            "reqData":"useLIFF",
            "uri":LIFF_URL
        },
        {
            "icon":"cms-infoguide.png",
            "title":"คู่มือการใช้งาน",
            "reqData":"getInfo"
        },
    ]

    carouselMenuList = []

    for menu in stringMsgSet:
        if menu["reqData"] == "useLIFF":
            bubble_menu_dict = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": SERVER_URL+"/linecms/icon/{iconName}".format(iconName=menu["icon"]),
                    "size": "50%",
                    "animated": False,
                    "aspectMode": "fit",
                    "aspectRatio": "1:1",
                    "align": "center",
                    "offsetTop": "15px",
                    "offsetBottom": "15px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": menu["title"],
                            "size": "xl",
                            "align": "center",
                            "weight": "regular",
                            "style": "normal",
                            "wrap": True
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "เลือกเมนูนี้",
                                "uri": menu["uri"] #insert liff url here
                            },
                            "style": "primary",
                            "position": "relative",
                            "height": "sm"
                        }
                    ],
                    "spacing": "lg",
                    "position": "relative",
                    "maxHeight": "160px",
                    "height": "135px"
                }
            }
        else:    
            bubble_menu_dict = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": SERVER_URL+"/linecms/icon/{iconName}".format(iconName=menu["icon"]),
                    "size": "50%",
                    "animated": False,
                    "aspectMode": "fit",
                    "aspectRatio": "1:1",
                    "align": "center",
                    "offsetTop": "15px",
                    "offsetBottom": "15px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": menu["title"],
                            "size": "xl",
                            "align": "center",
                            "weight": "regular",
                            "style": "normal",
                            "wrap": True
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "postback",
                                "label": "เลือกเมนูนี้",
                                "data": "request={req}".format(req=menu["reqData"])
                            },
                            "style": "primary",
                            "position": "relative",
                            "height": "sm"
                        }
                    ],
                    "spacing": "lg",
                    "position": "relative",
                    "maxHeight": "160px",
                    "height": "135px"
                }
            }
        carouselMenuList.append(bubble_menu_dict)
    
    return carouselMenuList

# function for sending start-up message to user when user add or unblock LineCMS OA
def sendStartUpMessage(userId: str):
    getStartedMessage = {
        "greet": """ยินดีต้อนรับสู่ระบบ LineCMS ระบบแชทบอทที่จะเก็บรูปภาพและไฟล์เอกสารในกลุ่มไลน์ให้อัตโนมัติ และให้คุณสามารถเข้าถึงและจัดการไฟล์ที่ถูกเก็บไว้ในภายหลังได้ในเวลาที่ต้องการ""",
        "guideMenu": """ระบบของเรามีให้คุณสามารถค้นหารูปภาพจากใบหน้าคนที่คุณสนใจ ดูกราฟความสัมพันธ์ระหว่างบุคคล จัดการไฟล์เอกสารรูปภาพของตัวเองและคลังเก็บไฟล์ในแต่ละกลุ่มไลน์ให้คุณสามารถเข้าไปดาวน์โหลดได้ โดยในปัจจุบันคุณสามารถค้นหารูปภาพจากใบหน้าและดูกราฟความสัมพันธ์ได้ผ่านช่องแชทนี้ ส่วนการจัดการไฟล์และอื่นๆสามารถทำได้ผ่านเว็บไซต์ LIFF ของระบบเรา คุณสามารถเลือกเมนูที่ต้องการทำได้ผ่าน Rich menu ที่แสดงอยู่ด้านล่างในช่องแชทนี้ หรือสามารถกดเลือกได้ผ่านเมนูเลื่อนต่อไปนี้""",
        "limits":"""** เว็บไซต์ LIFF สามารถใช้งานได้ผ่านแอพไลน์บนอุปกรณ์ Andriod และ iOS เท่านั้น"""
    }
    line_bot_api.push_message(
        PushMessageRequest(
            to=userId,
            messages=[TextMessage(text=getStartedMessage["greet"])]
        )
    )
    line_bot_api.push_message(
        PushMessageRequest(
            to=userId,
            messages=[TextMessage(text=getStartedMessage["guideMenu"])]
        )
    )
    line_bot_api.push_message(
        PushMessageRequest(
            to=userId,
            messages=[TextMessage(text=getStartedMessage["limits"])]
        )
    )

    # create start-up carousel menu
    carouselMenu = createStartUpCarouselMenu()
    carousel_menus_dict = {
        "type": "flex",
        "altText": "LineCMS ได้ส่งเมนูเลื่อนรายการบริการ",
        "contents": {
            "type": "carousel",
            "contents": carouselMenu
        }
    }

    # send menu to user
    url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN), "Content-Type":"application/json"}
    carousel_menu_post_data = {
        "to": userId,
        "messages": [carousel_menus_dict]
    }
    post_menu_response = requests.post(url="https://api.line.me/v2/bot/message/push", headers=url_headers, json=carousel_menu_post_data)
    if post_menu_response.status_code != 200:
        raise Exception("There was an issue occured at sending carousel menu for start up message", post_menu_response.status_code, post_menu_response.text)

# [v1]function for sending guides to user, v1: send instruction as text only
def sendInfoGuide(userId: str):
    th_text = """คุณได้เลือก คู่มือการใช้งาน\nคุณสามารถอ่านรายละเอียดและวิธีการใช้งานระบบของเราได้ตามข้อความต่อไปนี้"""
    line_bot_api.push_message(
        PushMessageRequest(
            to=userId,
            messages=[TextMessage(text=th_text)]
        )
    )

    # send message sets to user
    infoMsgSet = [
        {
            "about":"chatmenu", # use only to review the code and text
            "msg":"""ในหน้าแชทที่คุณอยู่จะมีเมนูให้สามารถเลือกได้ 3 เมนู ได้แก่\n1.ค้นหาภาพด้วยใบหน้า\n2.สร้างกราฟความสัมพันธ์\n3.ใช้งานบนเว็บไซต์\nโดยแต่ละเมนูมีรายละเอียดและขั้นตอนการใช้งานดังต่อไปนี้"""
        },
        {
            "about": "findimage1",
            "msg":"""* ค้นหาภาพด้วยใบหน้า *\nมีขั้นตอนการใช้งานดังนี้\n1.กดเมนู ค้นหาภาพด้วยใบหน้า\n2.เลือกกลุ่มไลน์ที่ต้องการค้นหาจากเมนูเลื่อนเลือกกลุ่มไลน์\n3.เลือกใบหน้าที่ต้องการอยู่ในรูปภาพจากเมนูเลื่อนเลือกใบหน้า\n\nจากนั้นแชทบอทจะทำการส่งรูปภาพผลลัพธ์มายังหน้าแชท CMS Official"""
        },
        {
            "about": "findimage2",
            "msg":"""ข้อมูลเพิ่มเติม: ในขั้นตอนที่ 2 และ 3 หากใบจำนวนเมนูให้เลือกมากกว่า 12 เมนู ระบบจะส่งข้อความพร้อมลิงค์เว็บไซต์ของระบบให้ผู้ใช้งานทำต่อในหน้าเว็บไซต์ LIFF App แทนเพื่อให้ผู้ใช้งานสามารถเลือกเมนูจากจำนวนเมนูทั้งหมดที่มีได้\n\nข้อมูลเพิ่มเติมที่ 2: หากจำนวนรูปภาพผลลัพธ์ทั้งหมดมีมากกว่า 20 รูป ระบบจะทำการส่งเพียง 20 รูปแรกพร้อมบอกจำนวนรูปภาพที่เหลือและปุ่มเมนูให้ส่งรูปภาพต่อหากผู้ใช้ต้องการได้รูปภาพที่เหลืออยู่เพิ่ม โดยระบบจะทำการส่งรูปภาพสูงสุดครั้งละ 20 รูปในครั้งถัดๆ ไปพร้อมปุ่มเมนูให้แสดงรูปภาพชุดถัดไป"""
        },
        {
            "about": "creategraph1",
            "msg":"""* สร้างกราฟความสัมพันธ์ *\nมีขั้นตอนการใช้งานดังนี้\n1.กดเมนู สร้างกราฟความสัมพันธ์\n2.เลือกกลุ่มไลน์ที่ต้องการสร้างกราฟจากเมนูเลื่อนเลือกกลุ่มไลน์\n3.เลือกใบหน้าที่ต้องการให้เป็นใบหน้าหลักที่สนใจจากเมนูเลื่อนเลือกใบหน้า\n\nจากนั้นแชทบอทจะทำการส่งรูปภาพผลลัพธ์กราฟพร้อมข้อความอธิบายกราฟมายังหน้าแชท CMS Official เมื่อทำการประมวลผลกราฟเรียบร้อยแล้ว"""
        },
        {
            "about": "creategraph2",
            "msg":"""ข้อมูลเพิ่มเติม: ในขั้นตอนที่ 2 และ 3 หากใบจำนวนเมนูให้เลือกมากกว่า 12 เมนู ระบบจะส่งข้อความพร้อมลิงค์เว็บไซต์ของระบบให้ผู้ใช้งานทำขั้นตอนต่อในหน้าเว็บไซต์ LIFF App แทนเพื่อให้ผู้ใช้งานสามารถเลือกเมนูจากจำนวนเมนูทั้งหมดที่มีได้"""
        },
        {
            "about": "liffapp1",
            "msg":"""* ใช้งานบนเว็บไซต์ *\nเป็นเมนูให้ผู้ใช้สามารถทำรายการเมนูต่างๆ ของระบบผ่านหน้าเว็บไซต์แทนหน้าช่องแชทเพื่อเพิ่มความสะดวกแก่ผู้ใช้ โดยเริ่มต้นการใช้งานเว็บไซต์จะมีขั้นตอนดังนี้\n1.กดเมนู ใช้งานบนเว็บไซต์\n2.กดอนุญาตให้สิทธิ์ในการเข้าถึงข้อมูลกับ LIFF App ของระบบ\n3.เลือกกลุ่มไลน์ที่ต้องการทำรายการเมนูต่างๆ จากหน้าเลือกกลุ่มไลน์\n\nหลังทำขั้นตอนที่ 3 ผู้ใช้จะเข้าสู่หน้าตัวเลือกเมนูที่ผู้ใช้สามารถใช้งานได้ในกลุ่มไลน์ที่เลือก โดยจะมีเมนูให้เลือกอยู่ 4 เมนูได้แก่\n1.ค้นหารูปด้วยใบหน้า\n2.สร้างกราฟความสัมพันธ์\n3.แกลเลอรี่\n4.จัดการไฟล์ส่วนตัว\n\nโดยในแต่ละเมนูจะมีรายละเอียดและการใช้งานดังต่อไปนี้"""
        },
        {
            "about": "liffapp2",
            "msg":"""* เมนูค้นหารูปด้วยใบหน้า *\nเป็นเมนูให้ผู้ใช้ค้นหารูปภาพที่มีใบหน้าของบุคคลที่ต้องการอยู่ภายในรูป คล้ายกับเมนูค้นหาภาพด้วยใบหน้าในช่องแชท\n\nเมื่อกดเมนูนี้แล้วผู้ใช้จะเข้าสู่หน้าเลือกใบหน้าที่ต้องการค้นหารูปภาพ และเมื่อผู้ใช้เลือกใบหน้าแล้วหน้าเว็บไซต์จะแสดงชุดรูปภาพผลลัพธ์ที่ได้ให้ผู้ใช้สามารถดูและส่งรูปภาพไปยังหน้าแชท CMS Official ให้ผู้ใช้สามารถกลับไปบันทึกรูปลงเครื่องได้"""
        },
        {
            "about": "liffapp3",
            "msg":"""* เมนูสร้างกราฟความสัมพันธ์ *\nเป็นเมนูให้ผู้ใช้ขอสร้างกราฟความสัมพันธ์ของบุคคลที่พบเจอภายในรูปภาพที่มีอยู่ในกลุ่มไลน์ที่เลือก คล้ายกับเมนูสร้างกราฟความสัมพันธ์ในช่องแชท\n\nเมื่อกดเมนูนี้แล้วผู้ใช้จะเข้าสู่หน้าเลือกใบหน้าที่ต้องการเป็นใบหน้าหลักที่สนใจของกราฟ และเมื่อผู้ใช้เลือกใบหน้าแล้วหน้าเว็บไซต์จะแสดงผลการทำรายการ โดยหากทำรายการสำเร็จจะแสดงผลลัพธ์ทำรายการสำเร็จและจะส่งผลลัพธ์กราฟและคำอธิบายกราฟไปให้ที่หน้าแชท CMS Official แต่หากทำรายไม่สำเร็จจะแสดงผลลัพธ์ทำรายการไม่สำเร็จและให้ผู้ใช้ทำรายการใหม่อีกครั้ง"""
        },
        {
            "about": "liffapp4",
            "msg":"""* เมนูแกลเลอรี่ *\nเป็นเมนูแสดงข้อมูลสมาชิก รูปภาพและไฟล์เอกสารของกลุ่มไลน์ที่ผู้ใช้เลือก\n\nเมื่อกดเมนูนี้แล้วผู้ใช้จะเข้าสู่หน้าแรกของแกลเลอรี่ซึ่งจะแสดงรายชื่อสมาชิกของกลุ่ม จำนวนรูปภาพและไฟล์เอกสารที่แต่ละสมาชิกส่งลงในกลุ่ม และจำนวนรูปภาพและไฟล์เอกสารทั้งหมดที่มีอยู่ภายในระบบปัจจุบันตั้งแต่ที่แชทบอทเข้าร่วมกลุ่ม โดยช่องแสดงจำนวนรูปภาพและไฟล์เอกสารทั้งหมดนั้นผู้ใช้สามารถกดเพื่อดูรายการรูปภาพหรือไฟล์เอกสารเพิ่มเติมได้ โดยจะแสดงเป็นรายการรูปภาพหรือไฟล์เอกสารตามที่ผู้ใช้กด ซึ่งผู้ใช้สามารถดูรายละเอียดของรูปภาพหรือไฟล์เอกสารและส่งรูปภาพหรือไฟล์นั้นไปยังหน้าแชท CMS Official ให้ผู้ใช้สามารถกลับไปบันทึกลงเครื่องได้"""
        },
        {
            "about": "liffapp5",
            "msg":"""* เมนูจัดการไฟล์ส่วนตัว *\nเป็นเมนูให้ผู้ใช้สามารถจัดการแก้ไขหรือลบรูปภาพและไฟล์เอกสารที่ผู้ใช้ส่งลงในกลุ่มไลน์ที่มีอยู่ในระบบได้ ซึ่งจะมีลักษณะการทำงานคล้ายคลึงกับเมนูแกลเลอรี่แต่จะแสดงข้อมูลของรูปภาพและไฟล์เอกสารที่ผู้ใช้เป็นผู้ส่งเท่านั้น\n\nเมื่อผู้ใช้กดเมนูนี้แล้วผู้ใช้จะเข้าสู่หน้าแสดงรายการรูปภาพ โดยมีช่องแสดงจำนวนรูปภาพและไฟล์เอกสารทั้งหมดที่ผู้ใช้เป็นผู้ส่งอยู่ภายในระบบปัจจุบัน ซึ่งเมื่อกดช่องแสดงรูปภาพหรือไฟล์เอกสารเว็บไซต์จะแสดงหน้ารายการรูปภาพหรือไฟล์เอกสารตามที่ผู้ใช้กด และผู้ใช้สามารถดูรายละเอียด ส่งไปยังหน้าแชท และสามารถลบรูปภาพหรือไฟล์เอกสารที่เลือกออกจากระบบได้"""
        }
    ]
    for text in infoMsgSet:
        line_bot_api.push_message(
            PushMessageRequest(
                to=userId,
                messages=[TextMessage(text=text["msg"])]
            )
        )

#  ---- End Defined Function Section ----


# create directories in docker environment (the current path is in ./app so add ".." to start at root path)
docker_saved_file_paths = [SAVE_IMAGE_PATH, SAVE_FACE_PATH, SAVE_GRAPH_PATH, SAVE_FILE_PATH, SAVE_GROUPPROFILE_PATH]
for saved_path in docker_saved_file_paths:
    os.makedirs(".."+saved_path, exist_ok=True)

# copy icon images to docker icon directory
MSG_ICON_PATH = os.getenv("MSG_ICON_PATH")
os.makedirs(".."+MSG_ICON_PATH, exist_ok=True)
os.system("cp ./icon/* {iconPath}".format(iconPath=MSG_ICON_PATH))

# connect to MongoDB database
failDBCon_count = 0
dbMsg = ""
while failDBCon_count < 10:
    isConnect, dbMsg = set_db_variables(dbClient=linecms_database.getdbclient())
    if isConnect:
        break
    else:
        failDBCon_count += 1
else:
    raise Exception("Failed to connect to MongoDB. ErrorMessage:",dbMsg)



# flask app root path (for testing flask is running)
@app.route("/")
def testroot():
    return "This is CMS root path", 200

# api route for receive liff backend (nestjs) request when user press 'send to chat' button in LIFF website
@app.route("/cms/api/liff/fetch_file", methods=["POST"])
def response_fetchFile():
    # retrieve data
    body_json = request.get_json()
    fileType = body_json["fileType"]
    fileId = body_json["fileId"]
    reqUserId = body_json["reqUserId"]

    if not ((fileType == "image") or (fileType == "doc")):
        raise Exception("Incorrect file type data:", fileType)
    
    try:
        if fileType == "image":
            # send image to chat of LineCMS Official
            fileUrl = SERVER_URL+"/linecms/image/"+fileId
            line_bot_api.push_message(
                PushMessageRequest(
                    to=reqUserId,
                    messages=[ImageMessage(originalContentUrl=fileUrl, previewImageUrl=fileUrl)]
                )
            )
        else:
            # get file url link from database
            queryFile = col_files.find_one({"_id":fileId})
            if queryFile is None:
                raise Exception("Cannot find file in database with id:"+fileId)
            fileName = queryFile["file_name"]
            groupId = queryFile["group_id"]

            queryGroup = col_groups.find_one({"_id":groupId})
            if queryGroup is None:
                raise Exception("Cannot find group in database with id:"+groupId)
            groupName = queryGroup["group_name"]

            fileUrl = SERVER_URL+"/linecms/file/"+fileId

            # create and send 'download file' bubble menu to user
            pushFileMenu = pushFileBubbleMenu(groupName, fileName, fileUrl)
            url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN), "Content-Type":"application/json"}
            bubble_menu_post_data = {
                "to": reqUserId,
                "messages": [pushFileMenu]
            }
            post_menu_response = requests.post(url="https://api.line.me/v2/bot/message/push", headers=url_headers, json=bubble_menu_post_data)
            if post_menu_response.status_code != 200:
                raise Exception("There was an issue occured at sending bubble menu for \'Download file\'", post_menu_response.status_code, post_menu_response.text)
            
            # send message to tell user about downloading file
            th_text = """เนื่องจากไลน์ไม่อนุญาตให้ผู้ใช้ดาวน์โหลดไฟล์ภายใน LIFF App ของไลน์ได้ เมื่อผู้ใช้กดปุ่มดาวน์โหลดไฟล์แล้วขึ้นหน้าว่างเปล่า ให้ทำการกดปุ่มจุด 3 จุดที่อยู่มุมล่างขวาและเลือก \"เปิดด้วยเบราว์เซอร์เริ่มต้น\" เพื่อให้เริ่มการดาวน์โหลดไฟล์"""
            line_bot_api.push_message(
                PushMessageRequest(
                    to=reqUserId,
                    messages=[TextMessage(text=th_text)]
                )
            )
    except Exception as e:
        statusDict = {
            "sendSuccess": False,
            "errorMessage": str(e)
        }
        return statusDict, 200
    else:
        statusDict = {
            "sendSuccess": True
        }
    return statusDict, 200

# api route for receive liff backend (nestjs) request when user press 'delete file/image' button on LIFF website
@app.route("/cms/api/liff/delete_file", methods=["POST"])
def response_deleteFile():
    # retrieve data
    body_json = request.get_json()
    delFileType = body_json["fileType"]
    delFileId = body_json["fileId"]
    reqUserId = body_json["reqUserId"]

    if not ((delFileType == "image") or (delFileType == "doc")):
        raise Exception("Incorrect file type data:", delFileType)
    
    try:
        if delFileType == "image":
            # delete image data from database collection
            selImage = col_images.find_one(filter={"_id":delFileId})
            imgGroupId = selImage["group_id"]
            delResult = col_images.delete_one(filter={"_id":delFileId})
            if delResult.deleted_count == 0:
                raise Exception("Cannot delete image data in database, image id: "+delFileId)
            
            # sent delete command to model api when user delete image (to update cluster data)
            model_api_data = {
                "image_name":delFileId,
                "group_id":imgGroupId,
                "command": "delete"
            }
            model_api_url = MODEL_SERVER_OTHER_LINK
            max_retry = 3
            retry_count = 0
            while retry_count < max_retry:
                response = requests.post(model_api_url,json=model_api_data)
                if response.status_code == 200:
                    break
                elif response.status_code == 500:
                    time.sleep(1)
                    retry_count += 1
                else:
                    print(response.status_code, response.text)
                    break
            else:
                print("Retry post model api reach maximum value")

            # delete image file from server
            os.remove(path=SAVE_IMAGE_PATH+delFileId)

            # delete face data and face file on database collection if it is created from deleted image
            if col_faces.find_one(filter={"image_link":delFileId}) is not None:
                unsend_face = col_faces.find_one_and_delete(filter={"image_link":delFileId})
                face_name = unsend_face["_id"]
                os.remove(path=SAVE_FACE_PATH+face_name)
            
            # update group image count in database
            col_groups.find_one_and_update(filter={"_id":imgGroupId}, update={"$inc":{"image_count":-1}})

            #Log user delete image
            log_message = "User id {userId} has delete image id {imgId} in LIFF".format(userId=reqUserId, imgId=delFileId)
            log_data = create_log_col_data("LIFF", imgGroupId, log_message, datetime.now())
            col_logs.insert_one(log_data)
        else:
            # delete file data from database collection
            selFile = col_files.find_one(filter={"_id": delFileId})
            fileGroupId = selFile["group_id"]
            deleteResult = col_files.delete_one(filter={"_id": delFileId})
            if deleteResult.deleted_count == 0:
                raise Exception("Cannot delete file data from database, file id: "+delFileId)
            
            # delete file from server
            os.remove(path=SAVE_FILE_PATH+delFileId)

            # update file count in group data
            col_groups.find_one_and_update(filter={"_id":fileGroupId}, update={"$inc":{"file_count":-1}})

            # log user delete file
            log_message = "User id {userId} has delete file id {fileId} in LIFF".format(userId=reqUserId, fileId=delFileId)
            log_data = create_log_col_data("LIFF", fileGroupId, log_message, datetime.now())
            col_logs.insert_one(log_data)
    except Exception as e :
        statusDict = {
            "isDeleteComplete": False,
            "errorMessage": str(e)
        }
        return statusDict, 200
    else:
        statusDict = {
            "isDeleteComplete": True
        }
    return statusDict, 200

# api route for receive liff backend (nestjs) request when frontend need to render 'Gallery' page
@app.route("/cms/api/liff/member_profile", methods=["POST"])
def response_memInfo():
    # retrieve data
    body_json = request.get_json()
    reqGroupId = body_json["groupId"]
    reqUserIdList = body_json["userIdList"]

    # get username and profile link from line messaging api
    url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN)}

    memberProfileList = []

    for user in reqUserIdList:
        memberProfile_url = "https://api.line.me/v2/bot/group/{groupId}/member/{userId}".format(groupId=reqGroupId, userId=user)
        response = requests.get(url=memberProfile_url, headers=url_headers)
        if response.status_code != 200:
            raise Exception("Cannot request member profile to line api, response message:",response.status_code,response.text)
        jsonResponse = response.json()
        memberProfileList.append({
            "userId":user,
            "userName": jsonResponse["displayName"],
            "userProfileLink": jsonResponse["pictureUrl"]
        })
    
    # response json data
    returnDataDict = {
        "responseData": memberProfileList
    }
    return returnDataDict, 200

# api route for receive liff backend (nestjs) request when frontend need total file size of group chat
@app.route("/cms/api/liff/total_file_size", methods=["POST"])
def response_fileSize():
    # retrieve data
    body_json = request.get_json()
    fileType = body_json["fileType"]
    groupId = body_json["groupId"]

    totalSize = 0

    # calculate total file size of that group in server
    if fileType == "image":
        for image in col_images.find({"group_id":groupId}):
            fileName = image["_id"]
            totalSize += os.path.getsize(SAVE_IMAGE_PATH+fileName)
    elif fileType == "doc":
        for doc in col_files.find({"group_id":groupId}):
            fileName = doc["_id"]
            totalSize += os.path.getsize(SAVE_FILE_PATH+fileName)
    else:
        raise Exception("Incorrect fileType data:", fileType)
    returnData = {
        "fileTotalSize":totalSize
    }
    return returnData, 200

# api route for receive liff backend (nestjs) request when user select face to create relationship graph on LIFF website
@app.route("/cms/api/liff/create_graph", methods=["POST"])
def response_createGraph():
    # retrieve data
    body_json = request.get_json()
    userid = body_json["userId"]
    clusterid = body_json["clusterId"]
    
    # send cluster id and user id to model server api to create relationship graph
    isPostGraph, postGraphMsg = post_relationshipGraph(clusterid, userid)
    if not isPostGraph:
        returnData = {
            "isPostComplete": False,
            "errorMessage": postGraphMsg
        }
    else:
        th_text = "เราได้รับคำขอสร้างกราฟผ่านเว็บไซต์ LIFF จากคุณแล้ว เราจะทำการส่งผลลัพธ์การสร้างกราฟความสัมพันธ์มาให้ในช่องทางนี้เมื่อดำเนินการเสร็จเรียบร้อยแล้ว โปรดกลับมาตรวจสอบผลลัพธ์ในภายหลัง"
        line_bot_api.push_message(
            PushMessageRequest(
                to=userid,
                messages=[TextMessage(text=th_text)]
            )
        )

        # log user activity to database
        log_message = "User chose face from cluster id {clusterId} from LIFF Website to create relationship graph".format(clusterId=clusterid)
        log_data = create_log_col_data("LIFF", userid, log_message, datetime.now())
        col_logs.insert_one(log_data)

        returnData = {
            "isPostComplete": True
        }
    return returnData, 200

# api route for receive model server data when it finish creating relationship graph
@app.route("/cms/api/model", methods=["POST"])
def response_model():
    body_json = request.get_json()
    if body_json["title"] == "graph":
        isComplete = bool(body_json["is_complete"])

        # if model server create graph successfully then send graph image and description message to user who request it
        if isComplete:
            # retrieve data
            userId = body_json["user_id"]
            graphId = body_json["graph_id"]
            isGroupGraph = bool(body_json["is_group"]) # boolean: true=group type graph, false=single type graph
            graphImageUrl = SERVER_URL+"/linecms/graph/"+graphId
            selGraph = col_graphs.find_one({"_id":graphId})
            selGroup = col_groups.find_one({"_id":selGraph["group_id"]})

            # check if received graph data is exist in database
            if selGraph is None:
                raise Exception("While retrieving data from model, Database cannot find data from graph id {graphid}".format(graphid=graphId))
            
            # send message to user
            th_text = "ผลลัพธ์จากคำขอสร้างกราฟความสัมพันธ์ของกลุ่ม {groupName} ที่คุณได้ทำรายการไว้เป็นดังต่อไปนี้".format(groupName=selGroup["group_name"])
            line_bot_api.push_message(
                PushMessageRequest(
                    to=userId,
                    messages=[TextMessage(text=th_text)]
                )
            )

            # send graph result to user's LineCMS Official chat
            line_bot_api.push_message(
                PushMessageRequest(
                    to=userId,
                    messages=[ImageMessage(originalContentUrl=graphImageUrl, previewImageUrl=graphImageUrl)]
                )
            )
            if isGroupGraph:
                th_text = """คำอธิบายเพิ่มเติมเกี่ยวกับตัวกราฟความสัมพันธ์\n\n• รูปภาพใบหน้าที่มีกรอบเส้นสีแดงคือภาพใบหน้าคนหลักที่คุณได้เลือกไว้ตอนส่งคำขอสร้างกราฟความสัมพันธ์
                \n• รูปภาพใบหน้าขนาดเล็กที่อยู่รอบใบหน้าหลักคือใบหน้าคนที่ปรากฏอยู่ในภาพเดียวกันกับภาพที่มีใบหน้าคนหลัก
                \n• เส้นเชื่อมโยงระหว่างใบหน้าหลักและตัวเลขประกอบเส้นเชื่อมบ่งบอกถึงจำนวนรูปภาพที่มีใบหน้าของคนหลักและใบหน้าของคนคนนั้นปรากฏอยู่ในภาพเดียวกัน
                \n• ข้อมูลจากกราฟเป็นการแสดงให้เห็นถึงความถี่ที่มีคนหลักและคนอื่นๆ ปรากฏอยู่ในภาพเดียวกันแบบเบื้องต้น เพื่อให้ผู้ใช้งานสามารถมองเห็นความสัมพันธ์ระหว่างคน 2 คนจากรูปภาพที่มีในกลุ่มไลน์นั้นได้สะดวกขึ้น
                """
            else:
                th_text = "คำอธิบายเพิ่มเติมเกี่ยวกับตัวกราฟความสัมพันธ์\n• ตัวเลขด้านล่างรูปใบหน้าคนแสดงถึงจำนวนรูปภาพที่มีใบหน้าของคนที่คุณเลือกภายในกลุ่มไลน์นั้น"
            line_bot_api.push_message(
                PushMessageRequest(
                    to=userId,
                    messages=[TextMessage(text=th_text)]
                )
            )
        # [Not used yet] there is error while creating graph
        else: 
            errorMsg = ""
    #  [Not used yet] handle other title if it is not about graph
    elif body_json["title"] == "something else":
        dosomething = ""
    return "OK", 200

# api route for receive line chat bot webhook data
@app.route("/cms/api/linewh", methods=["POST"])
def linewebhook():

    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)

    # check if webhook body is valid
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return "OK"



# line webhook event handler when user send text to LineCMS Official or in group chat
@handler.add(event=MessageEvent, message=TextMessageContent)
def handle_textmessage(event):
    global api_client, line_bot_api

    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    event_type = event_data_dict["source"]["type"]

    # response to user who send text message to LineCMS Official chat room
    if event_type == "user":
        th_text = "เราเห็นข้อความที่คุณส่งมาแล้ว!"
        line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(text=th_text)]
            )
        )

# line webhook event handler when user send image to group chat
# save image to server
@handler.add(event=MessageEvent, message=ImageMessageContent)
def save_imagemessage(event):
    # retrieve data from webhook body
    message_id = event.message.id
    event_data_dict = json.loads(event.to_json())
    group_id = event_data_dict["source"]["groupId"]
    user_id = event_data_dict["source"]["userId"]
    event_timestamp = str(event_data_dict["timestamp"])
    
    # create image file name
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    image_filename = hashlib.sha1(bytes(random_str+event_timestamp,encoding="utf-8")).hexdigest()
    
    # get image from Line API
    content_url = "https://api-data.line.me/v2/bot/message/{messageId}/content"
    url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN)}
    image_data = requests.get(url=content_url.format(messageId = str(message_id)),headers=url_headers)
    
    # save image to server
    with open(file=SAVE_IMAGE_PATH+image_filename+".jpg", mode="wb") as imagefile:
        for chunk in image_data.iter_content():
            imagefile.write(chunk)
        imagefile.close()
    
    # insert new image data to database
    new_image_data = create_image_col_data(imageName=image_filename+".jpg", groupId=group_id, messageId=message_id, senderId=user_id)
    col_images.insert_one(new_image_data)

    # log user activity
    log_message = "User id {userId} sent an image id {msgId} to group chat".format(userId=user_id, msgId=message_id)
    log_data = create_log_col_data("Group", group_id, log_message, datetime.now())
    col_logs.insert_one(log_data)

    # update image count in group data
    return_data = col_groups.find_one_and_update(filter={"_id":group_id}, update={"$inc":{"image_count":1}, "$set":{"last_used":datetime.now()}})
    if return_data is None:
        raise Exception("While updating image count, database cannot find the data from group id")

    # sent POST request to model server for face detection
    model_api_data = {
        "image_name":image_filename+".jpg",
        "group_id":group_id
    }
    model_api_url = MODEL_SERVER_IMAGE_LINK
    max_retry = 3
    retry_count = 0
    while retry_count < max_retry:
        response = requests.post(model_api_url,json=model_api_data)
        if response.status_code == 200:
            break
        elif response.status_code == 500:
            time.sleep(1)
            retry_count += 1
        else:
            print(response.status_code, response.text)
            break
    else:
        print("Retry post model api reach maximum value")

# line webhook event handler when user send file to group chat
# save file to server
@handler.add(event=MessageEvent, message=FileMessageContent)
def handle_fileMessage(event):
    # retrieve data from webhook body
    messageId = event.message.id
    eventDataDict = json.loads(event.to_json())
    groupId = eventDataDict["source"]["groupId"]
    userId = eventDataDict["source"]["userId"]
    eventTimestamp = str(eventDataDict["timestamp"])
    fileName = eventDataDict["message"]["fileName"]
    fileExt = str(fileName).split(".").pop()

    # create file name
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    localFileName = hashlib.sha1(bytes(random_str+eventTimestamp,encoding="utf-8")).hexdigest()

    # get file from Line API
    content_url = "https://api-data.line.me/v2/bot/message/{messageId}/content"
    url_headers = {"Authorization":"Bearer {access_token}".format(access_token=BOT_ACCESS_TOKEN)}
    fileData = requests.get(url=content_url.format(messageId = str(messageId)),headers=url_headers)    

    # save file to server
    with open(file=SAVE_FILE_PATH+localFileName+"."+fileExt, mode="wb") as docfile:
        for chunk in fileData.iter_content():
            docfile.write(chunk)
        docfile.close()

    # insert new file data to database
    newFileData = create_file_col_data(localFileName+"."+fileExt, groupId, fileName, messageId, userId)
    col_files.insert_one(newFileData)

    # log user activity to database
    log_message = "User id {userId} sent file id {msgId} to group chat".format(userId=userId, msgId=messageId)
    log_data = create_log_col_data("Group", groupId, log_message, datetime.now())
    col_logs.insert_one(log_data)

    # update file count in group data
    return_data = col_groups.find_one_and_update(filter={"_id":groupId}, update={"$inc":{"file_count":1}, "$set":{"last_used":datetime.now()}})
    if return_data is None:
        raise Exception("While updating image count, database cannot find the data from group id")

# line webhook event handler when chat bot join group
@handler.add(event=JoinEvent)
def create_data_group(event):
    global api_client, line_bot_api
    
    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    group_id = event_data_dict["source"]["groupId"]

    # insert new group data to database
    # if not then update status to 'Active' if chat bot has joined group within 3 days since day that chat bot left
    if col_groups.find_one({"_id":group_id}) is None:
        new_group_data = create_group_col_data(line_bot_api,group_id)
        col_groups.insert_one(new_group_data)

        # log chat bot join new group chat
        log_message = "Chat bot has joined new group chat"
        log_data = create_log_col_data("Group", group_id, log_message, datetime.now())
    else:
        join_group_data = col_groups.find_one(filter={"_id":group_id})
        if join_group_data["status"] == "Deleted":
            col_groups.find_one_and_update(filter={"_id":group_id}, update={"$set":{"status":"Active", "last_used":datetime.now()}})
        
        # send current information in the system message to group chat
        th_text = """เนื่องจากแชทบอทเรายังไม่ได้ออกจากกลุ่มเกิน 3 วันตั้งแต่วันที่แชทบอทออกจากกลุ่ม ทำให้รูปภาพและไฟล์ของกลุ่มไลน์นี้ยังไม่ถูกลบออกจากระบบ
        \nข้อมูลเพิ่มเติม:\n• จำนวนรูปภาพที่ถูกเก็บ = {imgCount} รูป\n• จำนวนไฟล์ที่ถูกเก็บ = {fileCount} ไฟล์""".format(imgCount=str(join_group_data["image_count"]), fileCount=str(join_group_data["file_count"]))
        line_bot_api.push_message(
            PushMessageRequest(
                to=group_id,
                messages=[TextMessage(text=th_text)]
            )
        )

        # log chat bot rejoin group chat within 3 days
        log_message = "Chat bot has rejoined group chat"
        log_data = create_log_col_data("Group", group_id, log_message, datetime.now())
    # insert log to database
    col_logs.insert_one(log_data)

    # send initial information and brief usage to group chat
    th_text = """สวัสดีครับ/ค่ะ\nแชทบอท CMS Official จากระบบ LineCMS ให้บริการเก็บรูปภาพและไฟล์เอกสารภายในกลุ่มไลน์อัตโนมัติ โดยแชทบอทจะเริ่มเก็บตั้งแต่ตอนนี้เป็นต้นไป\n\nสมาชิกทุกคนในกลุ่มสามารถเข้าถึงรูปภาพและไฟล์เอกสารและบริการของเรา เช่น ค้นหาภาพด้วยใบหน้า สร้างกราฟความสัมพันธ์ และอื่นๆ ได้โดยการเพิ่มเพื่อนบัญชีทางการ CMS Official จากการกดรูปโปรไฟล์แชทบอทนี้และเข้าไปที่หน้าแชทบัญชีเพื่อใช้บริการของเรา"""
    line_bot_api.push_message(
        PushMessageRequest(
            to=group_id,
            messages=[TextMessage(text=th_text)]
        )
    )

    # send data gathering details to group chat
    th_text = """** รายละเอียดการเก็บข้อมูลและการใช้งานข้อมูลภายในระบบ LineCMS **\n\nเมื่อแชทบอท LineCMS (CMS Official) เข้าร่วมอยู่ภายในไลน์กลุ่มตัวแชทบอทจะทำการเก็บรวบรวมข้อมูลต่อไปนี้
    1. รูปโปรไฟล์ของสมาชิกภายในกลุ่ม
    2. ชื่อที่แสดงของสมาชิกภายในกลุ่ม
    3. ไฟล์รูปภาพที่สมาชิกส่งลงในกลุ่ม รวมถึงชื่อผู้ส่งและวันเวลาที่ส่ง โดยเริ่มเก็บตั้งแต่วันที่แชทบอทเข้าร่วมกลุ่ม (ยกเว้นรูปภาพจากอัลบั้มรูปภาพ)
    4. ไฟล์เอกสารที่สมาชิกส่งลงในกลุ่ม รวมถึงชื่อผู้ส่งและวันเวลาที่ส่ง โดยเริ่มเก็บตั้งแต่วันที่แชทบอทเข้าร่วมกลุ่ม
    โดยระบบ LineCMS จะนำข้อมูลเหล่านี้ไปใช้ในการให้บริการต่างๆ ภายในช่องแชท CMS Official และเว็บไซต์ LIFF App ของระบบ ซึ่งมีได้แก่ ค้นหาภาพด้วยใบหน้า, สร้างกราฟความสัมพันธ์, แกลเลอรี่ และการจัดการไฟล์ส่วนตัว โดยมีเพียงบุคคลที่เป็นสมาชิกของกลุ่มเท่านั้นที่สามารถมองเห็นและดาวน์โหลดไฟล์ภายในกลุ่มไลน์ที่มีแชทบอทนี้ได้
    ข้อมูลเหล่านี้จะถูกเก็บอยู่ภายในระบบตั้งแต่วันที่แชทบอทเข้าร่วมกลุ่มไลน์ และจะถูกลบออกจากระบบเมื่อแชทบอทออกจากกลุ่มไลน์นี้เป็นเวลาเกิน 3 วันนับตั้งแต่วันที่ออกจากกลุ่ม"""
    line_bot_api.push_message(
        PushMessageRequest(
            to=group_id,
            messages=[TextMessage(text=th_text)]
        )
    )

# line webhook event handler when chat bot left group (user in group kick chat bot out)
@handler.add(event=LeaveEvent)
def handle_leavegroup(event):
    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    group_id = event_data_dict["source"]["groupId"]

    # update group status to 'Deleted' and time of left group on database
    if col_groups.find_one(filter={"_id":group_id}) is None:
        raise Exception("while processing chat bot leave group event, database cannot find group data from group id")
    else:
        col_groups.find_one_and_update(filter={"_id":group_id}, update={"$set":{"status":"Deleted", "last_used": datetime.now()}})

        # log chat bot left group chat
        log_message = "Chat bot has left group chat"
        log_data = create_log_col_data("Group", group_id, log_message, datetime.now())
        col_logs.insert_one(log_data)

# line webhook event handler when user joined group which has chat bot in it
@handler.add(event=MemberJoinedEvent)
def handle_user_join_group(event):
    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    group_id = event_data_dict["source"]["groupId"]
    join_member_list = event_data_dict["joined"]["members"]

    join_member_id_list = []
    
    # get all user ids
    for member in join_member_list:
        join_member_id_list.append(member["userId"])
    
    # update member ids of group data on database with new user id(s)
    if col_groups.find_one(filter={"_id":group_id}) is None:
        raise Exception("while processing member joined event, database cannot find group data from group id")
    else:
        group_data = col_groups.find_one(filter={"_id":group_id})
        group_member_ids = group_data["member_ids"]
        group_member_ids.extend(join_member_id_list)
        col_groups.find_one_and_update(filter={"_id":group_id}, update={"$set":{"member_ids":group_member_ids}})

        # log user(s) joined group chat
        if len(join_member_id_list) > 1:
            uidStr = ""
            for uid in join_member_id_list:
                uidStr = uidStr + uid
                if uid != join_member_id_list[-1]:
                    uidStr = uidStr + ", "
            log_message = "There are {userCount} users joined group chat. User ids = [{idStr}]".format(userCount=len(join_member_id_list), idStr=uidStr)
        else:
            log_message = "There is {userCount} user joined group chat. User id = {uid}".format(userCount=len(join_member_id_list), uid=join_member_id_list[0])
        log_data = create_log_col_data("Group", group_id, log_message, datetime.now())
        col_logs.insert_one(log_data)

# line webhook event handler when user left group which has chat bot in it
@handler.add(event=MemberLeftEvent)
def handle_user_leave_group(event):
    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    group_id = event_data_dict["source"]["groupId"]
    left_member_list = event_data_dict["left"]["members"]
    left_member_id_list = []

    # get all left user ids
    for member in left_member_list:
        left_member_id_list.append(member["userId"])
    
    # update group member ids on database
    if col_groups.find_one(filter={"_id":group_id}) is None:
        raise Exception("while processing member left event, database cannot find group data from group id")
    else:
        group_data = col_groups.find_one(filter={"_id":group_id})
        group_member_ids = group_data["member_ids"]

        # remove left user id from member ids
        for userId in left_member_id_list:
            group_member_ids.remove(userId)
        
        # update group data on database
        col_groups.find_one_and_update(filter={"_id":group_id}, update={"$set":{"member_ids":group_member_ids}})

        # log user(s) left group chat
        if len(left_member_id_list) > 1:
            uidStr = ""
            for uid in left_member_id_list:
                uidStr = uidStr + uid
                if uid != left_member_id_list[-1]:
                    uidStr = uidStr + ", "
            log_message = "There are {userCount} users left group chat. User ids = [{idStr}]".format(userCount=len(left_member_id_list), idStr=uidStr)
        else:
            log_message = "There is {userCount} user left group chat. User id = {uid}".format(userCount=len(left_member_id_list), uid=left_member_id_list[0])
        log_data = create_log_col_data("Group", group_id, log_message, datetime.now())
        col_logs.insert_one(log_data)

# line webhook event handler when user add or unblock LineCMS Official
@handler.add(event=FollowEvent)
def handle_follow_unblock_official(event):
    global api_client, line_bot_api

    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    user_id = event_data_dict["source"]["userId"]

    if col_users.find_one(filter={"_id":user_id}) is None:
        # insert new user data to database when user add as a friend for the first time
        new_user_data = {
            "_id": user_id,
            "status": "Active",
            "added_time": datetime.now(),
            "last_used": datetime.now()
        }
        col_users.insert_one(new_user_data)

        # log new user add official as a friend
        log_message = "New user added LineCMS official as a friend"
        log_data = create_log_col_data("Official", user_id, log_message, datetime.now())
    else:
        # update user status to 'Active' on database
        col_users.find_one_and_update(filter={"_id":user_id}, update={"$set":{"status":"Active", "last_used":datetime.now()}})

        th_text = "ยินดีต้อนรับกลับมานะครับ/คะ"
        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=th_text)]
            )
        )

        # log user unblock official
        log_message = "User unblocked LineCMS official"
        log_data = create_log_col_data("Official", user_id, log_message, datetime.now())
    # insert log data to database
    col_logs.insert_one(log_data)

    # send start-up message to user
    sendStartUpMessage(user_id)

# line webhook event handler when user block LineCMS Official
@handler.add(event=UnfollowEvent)
def handle_unfollow_official(event):
    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    user_id = event_data_dict["source"]["userId"]

    # update user status to 'Blocked' on database
    return_data = col_users.find_one_and_update(filter={"_id":user_id}, update={"$set":{"status":"Blocked"}})

    # raise error if database cannot find user data match with user id
    if return_data is None:
        raise Exception("While processing unfollow event, database cannot find the data from user id")
    
    # log user block official
    log_message = "User blocked LineCMS official"
    log_data = create_log_col_data("Official", user_id, log_message, datetime.now())
    col_logs.insert_one(log_data)

# line webhook event handler when user unsend image or file in group chat
@handler.add(event=UnsendEvent)
def handle_unsend_message(event):
    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    message_id = event_data_dict["unsend"]["messageId"]
    source_type = event_data_dict["source"]["type"]
    group_id = event_data_dict["source"]["groupId"]
    user_id = event_data_dict["source"]["userId"]

    # delete file or image (and face) data on database if user unsend in group chat
    if source_type == "group":
        # query image and file data on database
        imageResult = col_images.find_one(filter={"group_id":group_id, "message_id":message_id})
        fileResult = col_files.find_one(filter={"group_id":group_id, "message_id":message_id})
        if (imageResult is None) and (fileResult is None):
            raise Exception("While processing unsend image/file, database cannot find the image/file data from group id and message id")
        else:
            try:
                if imageResult is not None:
                    # delete image data on database
                    image_name = imageResult["_id"]
                    deleteResult = col_images.delete_one(filter={"group_id":group_id, "message_id":message_id})
                    if deleteResult.deleted_count == 0:
                        raise Exception("Cannot delete image data from database, image id: "+image_name)
                    
                    # sent delete command to model server to update cluster data
                    model_api_data = {
                        "image_name":image_name,
                        "group_id":group_id,
                        "command": "delete"
                    }
                    model_api_url = MODEL_SERVER_OTHER_LINK
                    max_retry = 3
                    retry_count = 0
                    while retry_count < max_retry:
                        response = requests.post(model_api_url,json=model_api_data)
                        if response.status_code == 200:
                            break
                        elif response.status_code == 500:
                            time.sleep(1)
                            retry_count += 1
                        else:
                            print(response.status_code, response.text)
                            break
                    else:
                        print("Retry post model api reach maximum value")

                    # delete image file from server
                    os.remove(path=SAVE_IMAGE_PATH+image_name)

                    # delete face data on database and face file if created from original image
                    if col_faces.find_one(filter={"image_link":image_name}) is not None:
                        unsend_face = col_faces.find_one_and_delete(filter={"image_link":image_name})
                        face_name = unsend_face["_id"]
                        os.remove(path=SAVE_FACE_PATH+face_name)
                    
                    # update image count in group data
                    col_groups.find_one_and_update(filter={"_id":group_id}, update={"$inc":{"image_count":-1}})

                    # log user unsend image in group chat
                    log_message = "User id {userId} has unsended image id {msgId} in group chat".format(userId=user_id, msgId=message_id)
                    log_data = create_log_col_data("Group", group_id, log_message, datetime.now())
                    col_logs.insert_one(log_data)
                else:
                    # delete file data on database
                    deleteResult = col_files.delete_one(filter={"group_id":group_id, "message_id":message_id})
                    if deleteResult.deleted_count == 0:
                        raise Exception("Cannot delete file data from database, file id: "+fileResult["_id"])
                    
                    # delete file from server
                    os.remove(path=SAVE_FILE_PATH+fileResult["_id"])

                    # update file count in group data
                    col_groups.find_one_and_update(filter={"_id":group_id}, update={"$inc":{"file_count":-1}})

                    # log user unsend file in group chat
                    log_message = "User id {userId} has unsended file id {msgId} in group chat".format(userId=user_id, msgId=message_id)
                    log_data = create_log_col_data("Group", group_id, log_message, datetime.now())
                    col_logs.insert_one(log_data)
            except Exception as e :
                raise Exception("Cannot delete file/image from unsend event, error message: "+str(e))

# line webhook event handler when user tap menu from rich menu or carousel menu in LineCMS Official
@handler.add(event=PostbackEvent)
def handle_postback_event(event):
    global api_client, line_bot_api

    # retrieve data from webhook body
    event_data_dict = json.loads(event.to_json())
    user_id = event_data_dict["source"]["userId"]
    postback_data = event_data_dict["postback"]["data"]
    
    # call function according to received postback data
    if (postback_data == "action=searchImage") or (postback_data == "request=searchImg"):
        action_img_graph(action="searchImage", userId=user_id)
    elif (postback_data == "action=CreateRelaGraph") or (postback_data == "request=createGraph"):
        action_img_graph(action="createRelaGraph", userId=user_id)
    elif (postback_data == "action=getInfo") or (postback_data == "request=getInfo"):
        sendInfoGuide(user_id)
    elif "selectGroup=1" in postback_data: # when user select group from carousel menu
        data_list = postback_data.split(sep="&")
        act_type = data_list.pop().replace("type=","")
        group_id = data_list.pop().replace("groupId=","")
        res_sel_group(action_type=act_type, userId=user_id, groupId=group_id)
    elif "selectFace=1" in postback_data: # when user select face from carousel menu
        data_list = postback_data.split(sep="&")
        act_type = data_list.pop().replace("type=","")
        group_id = data_list.pop().replace("groupId=","")
        cluster_id_str = data_list.pop().replace("clusterId=","")
        res_sel_face(action_type=act_type, userId=user_id, groupId=group_id, clusterId=cluster_id_str)
    elif "imgreq=" in postback_data: # when user tap 'click to see more images' bubble menu
        reqImgId = postback_data.replace("imgreq=","")
        postMoreImage(reqImgId, user_id)
