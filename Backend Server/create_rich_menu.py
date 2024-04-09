import requests, os

# line chat bot access token
bot_access_token = "LINE-BOT-ACCESS-TOKEN"

# rich menu buttons in json data
richMenuV3 = {
    "size": {
        "width": 2500,
        "height": 1686
    },
    "selected": True,
    "name": "Richmenu-v3-4Options",
    "chatBarText": "Menu",
    "areas": [
        {
            "bounds": {
                "x": 0,
                "y": 0,
                "width": 1250,
                "height": 843
            },
            "action": {
                "type": "postback",
                "label": "A_searchImage",
                "data": "action=searchImage",
                "displayText": "ค้นหาภาพด้วยใบหน้า"
            }
        },
        {
            "bounds": {
                "x": 1251,
                "y": 0,
                "width": 1250,
                "height": 843
            },
            "action": {
                "type": "postback",
                "label": "B_relationship",
                "data": "action=CreateRelaGraph",
                "displayText": "สร้างกราฟความสัมพันธ์"
            }
        },
        {
            "bounds": {
                "x": 0,
                "y": 844,
                "width": 1250,
                "height": 843
            },
            "action": {
                "type": "uri",
                "label": "C_useLiffApp",
                "uri": "https://liff.line.me/1660748214-64JZBlo0" #insert liff url here
            }
        },
        {
            "bounds": {
                "x": 1251,
                "y": 844,
                "width": 1250,
                "height": 843
            },
            "action": {
                "type": "postback",
                "label": "D_infomation",
                "data": "action=getInfo",
                "displayText": "คู่มือการใช้งาน"
            }
        }
    ]
}

# function for creating rich menu
def ex_create_rich_menu_six_button() -> dict:
    rich_menu_main = richMenuV3
    return rich_menu_main

# function for setting rich menu in Line
def ex_create_rich_menu() -> None:

    post_rich_menu_url = "https://api.line.me/v2/bot/richmenu"
    url_headers = {"Authorization":"Bearer {access_token}".format(access_token=bot_access_token),
                   "Content-Type": "application/json"}
    
    post_data = ex_create_rich_menu_six_button()

    # send rich menu to Line Messaging API server
    rich_menu_response = requests.post(url=post_rich_menu_url, headers=url_headers, json=post_data)
    response_status_code = rich_menu_response.status_code
    
    if response_status_code == 200:
        print("POST rich menu successful")

        # get rich menu id
        response_content_json = rich_menu_response.json()
        print(str(response_content_json))
        rich_menu_id = response_content_json["richMenuId"]
        print(rich_menu_id)
        
        # upload rich menu image to Line API server
        file_path = "full_path_to_rich_menu_image_file-LineCMS-RichMenuV3-4Options.png" # change this to full path
        content_type = "image/png"
        try:
            os.system("curl -v -X POST https://api-data.line.me/v2/bot/richmenu/{richMenuId}/content -H \"Authorization: Bearer {access_token}\" -H \"Content-Type: {Ctype}\" -T {filePath}".format(richMenuId=rich_menu_id, access_token=bot_access_token, Ctype=content_type, filePath=file_path))
            upload_image_status_code = 200
        except Exception as e:
            print("An exception has occured\nException message: {msg}".format(msg=e))
            
        if upload_image_status_code == 200:
            print("Set rich menu image successful")

            # set rich menu as default rich menu
            set_default_rich_menu_url = "https://api.line.me/v2/bot/user/all/richmenu/{richMenuId}".format(richMenuId=rich_menu_id)
            url_headers.pop("Content-Type")
            set_def_rich_menu_response = requests.post(url=set_default_rich_menu_url, headers=url_headers)
            def_rich_menu_status_code = set_def_rich_menu_response.status_code
            
            if def_rich_menu_status_code == 200:
                print("Set default rich menu successful")
            else:
                raise Exception("Set default rich menu failed", set_def_rich_menu_response.status_code, set_def_rich_menu_response.text)
        else:
            raise Exception("Set rich menu image failed")
    else:
        raise Exception("POST rich menu failed",rich_menu_response.status_code, rich_menu_response.text)


if __name__ == "__main__":
    ex_create_rich_menu()
