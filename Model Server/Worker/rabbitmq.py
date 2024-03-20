import os
import pika
import time
import json
import cv2
import hashlib
import numpy as np
from model import preprocess, faceLocation, faceAlignment, encodeFace, clustering, clusterRelation, createGraph
from pymongo_database import getEncodedFace, insertLog, getClusterData
from datetime import datetime
import requests

# Get environment variables
img_dir = os.getenv('IMAGE_DIRECTORY')
face_dir = os.getenv('FACE_DIRECTORY')
graph_dir = os.getenv('GRAPH_DIRECTORY')
backend_url = os.getenv('BACKEND_SERVER_URL', 'http://backend_linecms:80/api/model')
face_img_size = int(os.getenv('FACE_IMAGE_SIZE', 240))

# Create connection to RabbitMQ server
def createRabbitmqConnection():
    max_retries = 30  # Maximum number of connection retries
    retry_delay = 6  # Delay between retry attempts in seconds

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat=600))
            return connection
        except Exception as e:
            print(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)

    # If all retries fail, raise an exception
    raise Exception("Failed to establish a connection to RabbitMQ after multiple retries")

# Consume low_priority queue 
def consumeLow(channel:pika.BlockingConnection, db):
    # Get request from low_priority queue
    method_frame, header_frame, body = channel.basic_get(queue='low_priority', auto_ack=False)

    if method_frame:
        # Get delivery tag
        delivery_tag = method_frame.delivery_tag

        # Load data from message
        data = json.loads(body)
        image_name = data['image_name']
        group_id = data['group_id']
        img_path = img_dir + image_name

        # Log message to database
        insertLog(f'Processing {image_name}', db)

        # Load image
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)

        # if can't read image
        if img is None:
            # Log message to database
            insertLog(f'Failed to read {image_name}', db)

            # Acknowledge message
            channel.basic_ack(delivery_tag=delivery_tag)
            return False
        
        resized_img = preprocess(img, False)
        img = preprocess(img, True)

        # Get list of face locations in image
        face_list = faceLocation(img)

        # If face_list is not empty
        if face_list:
            # Align and crop face image
            aligned_faces = faceAlignment(face_list, img, resized_img)

            # Encode every face in image to 128 dimensional array
            encoded_faces = encodeFace(face_list, img)

            # Get others encoded face from database
            img_face_count, face_name_list, encoded_list = getEncodedFace(group_id, db)

            # Modify data for new image
            # Remove img_face_count key of new image if exist
            if image_name in img_face_count:
                del img_face_count[image_name]

            # Add data of new image
            img_face_count[image_name] = len(encoded_faces)
            for encoded in encoded_faces:
                encoded_list.append(encoded)

            # Naming face image, save to server and database
            face_data_list = []
            saved_time = datetime.now()
            for index, face_img in enumerate(aligned_faces):
                # Hash image name
                face_img_filename = hashlib.sha1(bytes(image_name + str(index), encoding='utf-8')).hexdigest() + '.jpg'
                face_img_path = face_dir + face_img_filename

                # Add new face image name to face_name_list
                face_name_list.append(face_img_filename)

                # Resize face image
                resized_face = cv2.resize(face_img, (face_img_size, face_img_size), interpolation=cv2.INTER_CUBIC)

                # Save face image to server
                cv2.imwrite(face_img_path, resized_face)

                # Prepare data for inserted
                face_data = {
                    '_id': face_img_filename,
                    'image_link': image_name,
                    'encoded': encoded_faces[index].tolist(),
                    'cluster_id': '-',
                    'saved_time': saved_time,
                    'updated_time': saved_time
                }
                face_data_list.append(face_data)
            db['Faces'].insert_many(face_data_list)

            # Clustering and insert new cluster to database
            predicted_cluster, inserted_cluster_id = clustering(encoded_list, group_id, db)

            # Find relation of each cluster
            img_clusters, relations_cluster, cluster_count = clusterRelation(inserted_cluster_id, img_face_count, predicted_cluster)
            
            # Update each cluster to database
            saved_time = datetime.now()
            for cluster_id in inserted_cluster_id:
                face_img_index = predicted_cluster.index(cluster_id)
                filter = {'_id': cluster_id}
                cluster_data = {
                    '$set': {
                        'face_link': face_name_list[face_img_index],
                        'relations': relations_cluster[str(cluster_id)],
                        'image_count': cluster_count[str(cluster_id)],
                        'saved_time': saved_time
                    }
                }
                db['Clusters'].update_one(filter, cluster_data)

            # Update each face to database
            updated_time = datetime.now()
            for _id, cluster_id in zip(face_name_list, predicted_cluster):
                filter = {'_id': _id}
                if cluster_id == -1:
                    cluster_id = '-'
                face_data = {
                    '$set': {
                        'cluster_id': cluster_id,
                        'updated_time': updated_time
                    }
                }
                db['Faces'].update_one(filter, face_data, upsert=True)

            # Update each image to database
            updated_time = datetime.now()
            for _id in img_face_count.keys():
                filter = {'_id': _id}
                image_data = {
                    '$set': {
                        'cluster_ids': img_clusters[_id],
                        'updated_time': updated_time
                    }
                }
                db['Images'].update_one(filter, image_data, upsert=True)

        # Log message
        insertLog(f'Finished processing {image_name}', db)

        # Acknowledge message
        channel.basic_ack(delivery_tag=delivery_tag)

# Consume medium_priority queue
def consumeMedium(channel:pika.BlockingConnection, db):
    # Get request from medium_priority queue
    method_frame, header_frame, body = channel.basic_get(queue='medium_priority', auto_ack=False)

    if method_frame:
        # Get delivery tag
        delivery_tag = method_frame.delivery_tag

        # Load data from message
        data = json.loads(body)
        user_id = data['user_id']
        cluster_id = data['cluster_id']

        # Log message to database
        insertLog(f'Creating graph of {cluster_id} by {user_id}', db)

        # Prepare retring parameter for API
        max_retries = 3  # Maximum number of connection retries
        retry_delay = 5  # Delay between retry attempts in seconds

        # Get group_id from cluster
        group_id, _, _, _ = getClusterData(cluster_id, db)

        # If can't find cluster data
        if group_id is None:
            # Log message to database
            insertLog(f'Failed to find cluster data of {cluster_id}', db)

            # Prepare error message for backend
            data = {
                'title': 'graph',
                'is_complete': False,
                'user_id': user_id,
                'graph_id': '',
                'is_group': False
            }

            # Check response
            for i in range(max_retries):
                # Sent error message to backend
                response = requests.post(backend_url, json=data)
                if response.status_code == 200:
                    # Request success
                    # Acknowledge message
                    channel.basic_ack(delivery_tag=delivery_tag)
                    return True
                else:
                    time.sleep(retry_delay)

                # If all retries fail, raise an exception
                raise Exception(f'Failed to send message to backend before created graph {response.status_code}, {response.text}')
            return False
        
        # Create relationship graph image
        result, g_type = createGraph(cluster_id, group_id, db)

        # If no result
        if result is None:
            # Log message to database
            insertLog(f'Failed to find some relation of {cluster_id}', db)

            # Prepare error message for backend
            data = {
                'title': 'graph',
                'is_complete': False,
                'user_id': user_id,
                'graph_id': '',
                'is_group': False
            }

            # Check response
            for _ in range(max_retries):
                # Sent error message to backend
                response = requests.post(backend_url, json=data)
                if response.status_code == 200:
                    # Request success
                    # Acknowledge message
                    channel.basic_ack(delivery_tag=delivery_tag)
                    return True
                else:
                    time.sleep(retry_delay)

                # If all retries fail, raise an exception
                raise Exception(f'Failed to send message to backend before created graph {response.status_code}, {response.text}')
            return False

        # Hash graph image name
        graph_img_filename = hashlib.sha1(bytes(cluster_id + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), encoding='utf-8')).hexdigest() + '.jpg'
        graph_img_path = graph_dir + graph_img_filename

        # Save graph image to server
        cv2.imwrite(graph_img_path, result)

        # Prepare data for inserted
        graph_data = {
            '_id': graph_img_filename,
            'group_id': group_id,
            'cluster_id': cluster_id,
            'saved_time': datetime.now()
        }

        # insert graph data to database
        db['Graphs'].insert_one(graph_data)

        # Log message to database
        insertLog(f'Finished creating graph of {cluster_id}', db)

        # Prepare complete message for backend
        data = {
                'title': 'graph',
                'is_complete': True,
                'user_id': user_id,
                'graph_id': graph_img_filename,
                'is_group': g_type
        }

        # Check response
        for i in range(max_retries):
            # Sent error message to backend
            response = requests.post(backend_url, json=data)
            if response.status_code == 200:
                # Request success
                # Acknowledge message
                channel.basic_ack(delivery_tag=delivery_tag)
                return True
            else:
                time.sleep(retry_delay)

            # If all retries fail, raise an exception
            raise Exception(f'Failed to send message to backend after created graph {response.status_code}, {response.text}')
        return False
        
# Consume high_priority queue
def consumeHigh(channel:pika.BlockingConnection, db):
    while True:
        # Get request from high_priority queue
        method_frame, header_frame, body = channel.basic_get(queue='high_priority', auto_ack=False)

        if method_frame:
            # Get delivery tag
            delivery_tag = method_frame.delivery_tag

            # Load data from message
            data = json.loads(body)
            image_name = data['image_name']
            group_id = data['group_id']
            command = data['command']

            # If command = delete (unsend image)
            if command == 'delete':
                # Log message to database
                insertLog(f'Delete {image_name} and reclustering {group_id}', db)

                # Delete image if exist in database
                filter_to_delete = {'_id': image_name}
                db['Images'].delete_one(filter_to_delete)

                # Delete faces from that image if exist in database
                filter_to_delete = {'image_link': image_name}
                db['Faces'].delete_many(filter_to_delete)

                # Get all encoded face from database
                img_face_count, face_name_list, encoded_list = getEncodedFace(group_id, db)

                # Clustering and insert new cluster to database
                predicted_cluster, inserted_cluster_id = clustering(encoded_list, group_id, db)

                # Find relation of each cluster
                img_clusters, relations_cluster, cluster_count = clusterRelation(inserted_cluster_id, img_face_count, predicted_cluster)
                
                # Update each cluster to database
                saved_time = datetime.now()
                for cluster_id in inserted_cluster_id:
                    face_img_index = predicted_cluster.index(cluster_id)
                    filter = {'_id': cluster_id}
                    cluster_data = {
                        '$set': {
                            'face_link': face_name_list[face_img_index],
                            'relations': relations_cluster[str(cluster_id)],
                            'image_count': cluster_count[str(cluster_id)],
                            'saved_time': saved_time
                        }
                    }
                    db['Clusters'].update_one(filter, cluster_data)

                # Update each face to database
                updated_time = datetime.now()
                for _id, cluster_id in zip(face_name_list, predicted_cluster):
                    filter = {'_id': _id}
                    if cluster_id == -1:
                        cluster_id = '-'
                    face_data = {
                        '$set': {
                            'cluster_id': cluster_id,
                            'updated_time': updated_time
                        }
                    }
                    db['Faces'].update_one(filter, face_data, upsert=True)

                # Update each image to database
                updated_time = datetime.now()
                for _id in img_face_count.keys():
                    filter = {'_id': _id}
                    image_data = {
                        '$set': {
                            'cluster_ids': img_clusters[_id],
                            'updated_time': updated_time
                        }
                    }
                    db['Images'].update_one(filter, image_data, upsert=True)
                
                # Log message to database
                insertLog(f'Finished reclustering {group_id}', db)

            # Acknowledge message
            channel.basic_ack(delivery_tag=delivery_tag)

        else:
            break

    