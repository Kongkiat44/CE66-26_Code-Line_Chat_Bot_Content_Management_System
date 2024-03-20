from datetime import datetime
from pymongo.errors import ConnectionFailure
from pymongo.mongo_client import MongoClient
import os

# get string variables from shell script environment and stored as constant
SAVE_FACE_PATH = os.getenv("SAVE_FACE_PATH2")
SAVE_IMAGE_PATH = os.getenv("SAVE_IMAGE_PATH2")
SAVE_FILE_PATH = os.getenv("SAVE_FILE_PATH2")
SAVE_GRAPH_PATH = os.getenv("SAVE_GRAPH_PATH2")
DATABASE_NAME = os.environ.get("DATABASE_NAME2")
MONGOSTR = os.getenv("MONGOSTR")

# function for connecting to MongoDB database
def get_database() -> MongoClient:
    try:
        mongocli = MongoClient(MONGOSTR)
    except ConnectionFailure as e:
        raise Exception("Failed to connect to database from schedule_leftgroup.py, Error Message:\n", str(e))
    return mongocli

# function for group status and graph date
def checkStatus_GroupGraph() -> None:
    # variable of current time when run this code
    current_time = datetime.now()

    # connect to database and set variables corresponding to each database collections
    db_client = get_database()
    database = db_client[DATABASE_NAME]
    col_groups = database.Groups
    col_images = database.Images
    col_faces = database.Faces
    col_clusters = database.Clusters
    col_graphs = database.Graphs
    col_logs = database.Logs
    col_files = database.Files

    deleteGids = []
    deleteGraphs = []

    # check days since chat bot left group in group data with 'Deleted' status
    for group in col_groups.find({"status":"Deleted"}):
        image_counts = group["image_count"]
        try:
            # compare chat bot left group time with current time
            left_time = group["last_used"]
            difference_time = current_time - left_time
        except Exception as e:
            # log exception to database
            log_data = {
                "type": "Others",
                "related_to": str(group["_id"]),
                "content": "Error:Cannot compare time from group last_used property, error:{err},code executed from schedule_leftgroup.py".format(err=str(e)),
                "saved_time": datetime.now(),
            }
            col_logs.insert_one(log_data)

        # delete all files associate with that group and also data on database if compared time is >= 3 days
        if difference_time.days >= 3:
            
            for image in col_images.find({"group_id":group["_id"]}):
                image_name = image["_id"]

                # delete face file from server and face data on database
                if col_faces.find_one(filter={"image_link":image_name}) is not None:
                    face = col_faces.find_one_and_delete(filter={"image_link":image_name})
                    face_name = face["_id"]
                    os.remove(path=SAVE_FACE_PATH+face_name)
                
                # delete image from server and image data on database
                col_images.delete_one(filter={"_id":image_name})
                os.remove(path=SAVE_IMAGE_PATH+image_name)
                image_counts -= 1
            
            # delete file from server and file data on database
            for file in col_files.find({"group_id":group["_id"]}):
                fileName = file["_id"]
                os.remove(path=SAVE_FILE_PATH+fileName)
            col_files.delete_many(filter={"group_id":group["_id"]})

            # delete graph from server and graph data on database
            for graph in col_graphs.find({"group_id":group["_id"]}):
                graphName = graph["_id"]
                os.remove(path=SAVE_GRAPH_PATH+graphName)
            col_graphs.delete_many(filter={"group_id":group["_id"]})

            # delete cluster data from database
            col_clusters.delete_many(filter={"group_id":group["_id"]})

            # delete group data on database
            deleteResult = col_groups.delete_one(filter={"_id":group["_id"]})

            if deleteResult.deleted_count == 0:
                # log error when cannot delete group data on database
                log_data = {
                    "type": "Group",
                    "related_to": str(group["_id"]),
                    "content": "Error:Cannot delete group data from database, gid: {gid}, code executed from schedule_leftgroup.py".format(gid=str(group["_id"])),
                    "saved_time": datetime.now(),
                }
                col_logs.insert_one(log_data)
            else:
                deleteGids.append(str(group["_id"]))
                
    
    # check graph saved_time (created time) and if it is >= 3 days then delete that graph from server and database
    for graph in col_graphs.find():
        try:
            # compare graph created time with current time
            saveTime = graph["saved_time"]
            difference_time = current_time - saveTime

            if difference_time.days >= 3:
                # delete graph data on database
                deleteResult = col_graphs.delete_one({"_id":graph["_id"]})
                if deleteResult.deleted_count == 0:
                    # log error when cannot delete graph data on database
                    log_data = {
                        "type": "Others",
                        "related_to": str(graph["_id"]),
                        "content": "Error:Cannot delete graph data from database, id: {id}, code executed from schedule_leftgroup.py".format(id=str(graph["_id"])),
                        "saved_time": datetime.now(),
                    }
                    col_logs.insert_one(log_data)
                else:
                    deleteGraphs.append(str(graph["_id"]))
                
                # delete graph file from server
                fileName = str(graph["_id"])
                os.remove(path=SAVE_GRAPH_PATH+fileName)
        except Exception as e:
            log_data = {
                "type": "Others",
                "related_to": str(graph["_id"]),
                "content": "Error:Exception occured while deleting graph, msg: {errmsg}, code executed from schedule_leftgroup.py".format(errmsg=str(e)),
                "saved_time": datetime.now(),
            }
            col_logs.insert_one(log_data)
    
    # log details of deleted group and graph
    if len(deleteGids) > 0:
        log_data = {
            "type": "Group",
            "related_to": deleteGids,
            "content": "Delete {gcount} group data from database successful".format(gcount=len(deleteGids)),
            "saved_time": datetime.now(),
        }
        col_logs.insert_one(log_data)
    
    if len(deleteGraphs) > 0:
        log_data = {
            "type": "Others",
            "related_to": deleteGraphs,
            "content": "Delete {gcount} graph data from database successful".format(gcount=len(deleteGraphs)),
            "saved_time": datetime.now(),
        }
        col_logs.insert_one(log_data)


# starting point when run this file
if __name__ == "__main__":
    checkStatus_GroupGraph()