import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Get database client
def getDatabase():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    url = os.getenv('MONGO_DB_URL')
 
    # Raise error if no MONGO_DB_URL
    if url is None:
        raise ValueError('No MONGO_DB_URL')

    # Create a connection using MongoClient
    client = MongoClient(url)

    # Create the database
    return client['LineCMS']

# Get encoded face from database
def getEncodedFace(group_id, db):
    # Get wanted data from database
    result = db['Images'].aggregate([
        {
            '$match': {'group_id': group_id}
        },
        {
            '$lookup': {
                'from': 'Faces',
                'localField': '_id',
                'foreignField': 'image_link',
                'as' : 'face_data'
            }
        },
        {
            '$project': {
                '_id': 1,
                'face': {
                    '$map': {
                        'input': '$face_data',
                        'in': {
                            '_id': '$$this._id',
                            'encoded' : '$$this.encoded'
                        }
                    }
                }
            }
        }
    ])

    # Formatting data
    img_face_count = {} # Count each image face ex. {'img1': 2, 'img2': 1}
    face_name_list = [] # List of face name(_id)
    encoded_list = [] # List of encoded face (for DBSCAN)
    for record in result:
        img_face_count[record['_id']] = len(record['face'])
        for face in record['face']:
            face_name_list.append(face['_id'])
            encoded_list.append(face['encoded'])
    return img_face_count, face_name_list, encoded_list

# Insert log of model server to database
def insertLog(content, db):
    # Insert content to database
    log_data = {
        'type': 'Others',
        'related_to': 'Model',
        'content': content,
        'saved_time': datetime.now()
    }

    return db['Logs'].insert_one(log_data)

# Get cluster data from database
def getClusterData(cluster_id, db):
    # Change (str)id to ObjectID
    doc_id = ObjectId(cluster_id)

    # Get cluster data
    result = db['Clusters'].find_one({'_id': doc_id})

    # If can't find data
    if result is None:
        return None, None, None, None
    return result['group_id'], result['face_link'], result['image_count'], result['relations']

# Get all cluster data from database
def getAllClusterData(group_id, db):
    # Prepare query data
    query = {'group_id': group_id}

    # Get all cluster data
    result = db['Clusters'].find(query)

    # Format cluster data
    formatted_result = {}
    for data in result:
        _id = str(data['_id'])
        formatted_result[_id] = {
            'face_link': data['face_link'],
            'image_count': data['image_count'],
            'relations': {key: value for key, value in data['relations'].items() if value > 0}, # Filter keys with values greater than 0
            'is_used': False
        }
    return formatted_result