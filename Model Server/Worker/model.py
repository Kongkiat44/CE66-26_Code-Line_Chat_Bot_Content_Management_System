import cv2
import face_recognition
import dlib
import math
import os
import numpy as np
from sklearn.cluster import DBSCAN
from pymongo_database import getAllClusterData
import networkx as nx

# Load face predictor model
predictor_path = "Worker/shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)

# Load environment variables
preprocess_width = int(os.getenv('PREPROCESS_SIZE', 600))
face_dir = os.getenv('FACE_DIRECTORY')
dbscan_eps = float(os.getenv('DBSCAN_EPS', 0.282))
if dbscan_eps <= 0:
    dbscan_eps = 0.1
max_graph_layer = int(os.getenv('MAX_GRAPH_LAYER', 4))
if max_graph_layer <= 0:
    max_graph_layer = 1

# Preprocess image
def preprocess(img, mode):
    # Check preprocess_width
    if preprocess_width > 0:
        # Resize image
        ratio = float(preprocess_width) / img.shape[1]
        target_height = int(img.shape[0] * ratio)
        resized_image = cv2.resize(img, (preprocess_width, target_height), interpolation=cv2.INTER_LINEAR)

        # Normalize brightness
        if mode == True:
            # Convert the image to the LAB color space
            lab_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2LAB)

            # Separate the LAB channels
            l_channel, a_channel, b_channel = cv2.split(lab_image)

            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l_channel_normalized = clahe.apply(l_channel)

            # Merge the LAB channels back together
            normalized_lab_image = cv2.merge([l_channel_normalized, a_channel, b_channel])

            # Convert the normalized LAB image back to BGR
            normalized_image = cv2.cvtColor(normalized_lab_image, cv2.COLOR_LAB2BGR)

            return normalized_image
        return resized_image
    return img

# Find face locations in image
def faceLocation(img):
    return face_recognition.face_locations(img, 1, 'cnn')

# Align and crop face image
def faceAlignment(face_list, img, resized_img):
    aligned_faces = []
    for face_location in face_list:
        # Get each border side of face
        top, right, bottom, left = face_location

        # # Copy image for save
        # cp_img = img.copy()

        # Convert face region to grayscale for facial landmark detection
        face_gray = cv2.cvtColor(img[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
        
        # Detect facial landmarks
        landmarks = predictor(face_gray, dlib.rectangle(0, 0, face_gray.shape[1], face_gray.shape[0]))

        # # Draw circle around landmarks
        # for i in range(0, 68):  # 68 landmarks for the face
        #     x, y = landmarks.part(i).x, landmarks.part(i).y
        #     if i in [30, 36, 45]:
        #         cv2.circle(cp_img, (x + left, y + top), 3, (255, 0, 0), -1)  # Draw a red circle at each landmark point
        #     else:
        #         cv2.circle(cp_img, (x + left, y + top), 3, (0, 0, 255), -1)  # Draw a red circle at each landmark point

        # # Draw bounding box around the face
        # cv2.rectangle(cp_img, (left, top), (right, bottom), (0, 255, 0), 2)

        # # Save face with landmarks
        # cv2.imwrite('face_landmarks.jpg', cp_img)

        # Extract the coordinates of specific facial landmarks (for example, eyes and nose)
        left_eye_x = landmarks.part(36).x
        left_eye_y = landmarks.part(36).y
        right_eye_x = landmarks.part(45).x
        right_eye_y = landmarks.part(45).y
        nose_x = landmarks.part(30).x
        nose_y = landmarks.part(30).y

        # Calculate the angle between the eyes
        angle_rad = math.atan2(right_eye_y - left_eye_y, right_eye_x - left_eye_x)
        angle_deg = math.degrees(angle_rad)

        # Perform the rotation to align the eyes horizontally
        rotation_matrix = cv2.getRotationMatrix2D((nose_x, nose_y), angle_deg, 1.0)

        # Get the size of the original face
        face_width = right - left
        face_height = bottom - top

        # Calculate the coordinates of the rotated face corners
        rotated_corners = cv2.transform(np.array([[[left, top], [left + face_width, top], [left, top + face_height], [right, bottom]]]), rotation_matrix)[0]

        # Find the new bounding box of the rotated face
        min_x = int(np.min(rotated_corners[:, 0]))
        max_x = int(np.max(rotated_corners[:, 0]))
        min_y = int(np.min(rotated_corners[:, 1]))
        max_y = int(np.max(rotated_corners[:, 1]))

        # Calculate the size of the resulting image
        result_width = max_x - min_x
        result_height = max_y - min_y

        # Perform rotation on the original image
        rotated_face = cv2.warpAffine(resized_img, rotation_matrix, (resized_img.shape[1], resized_img.shape[0]), flags=cv2.INTER_LINEAR)

        # Crop the rotated face to remove black borders
        cropped_face = rotated_face[min_y:min_y + result_height, min_x:min_x + result_width]

        # Add the resized face to the list
        aligned_faces.append(cropped_face)
    return aligned_faces

# Encoding faces in image
def encodeFace(face_list, img):
    return face_recognition.face_encodings(img, face_list)

# Clustering encoded face, delete old cluster and insert new cluster in database, then map new cluster id to generated cluster id
def clustering(encoded_list, group_id, db):
    # Create DBSCAN model
    model = DBSCAN(eps=dbscan_eps, min_samples=2)

    # Clustering encoded face (-1 is noise and others are cluster_id)
    predicted_cluster = model.fit_predict(encoded_list)

    # Delete all old cluster in group
    filter_to_delete = {'group_id': group_id}
    db['Clusters'].delete_many(filter_to_delete)

    # Find max cluster id
    max_cluster_id = max(predicted_cluster)

    inserted_cluster_id = []
    # if there are any cluster
    if max_cluster_id >= 0:
        # Prepare all cluster data to be inserted
        cluster_data = []
        for _ in range(max_cluster_id+1):
            data = {'group_id': group_id}
            cluster_data.append(data)

        # Insert all data to Clusters
        responese = db['Clusters'].insert_many(cluster_data)

        # Get all ids of inserted data
        inserted_cluster_id = responese.inserted_ids

        # Change inserted id to dict
        cluster_id = {}
        for index, value in enumerate(inserted_cluster_id):
            cluster_id[index] = value

        # Mapping predicted cluster id to inserted cluster id
        predicted_cluster = [cluster_id.get(item, item) for item in predicted_cluster]
    return predicted_cluster, inserted_cluster_id

# Find relation of each image and mapping with image
def clusterRelation(inserted_cluster_id, img_face_count, predicted_cluster):
    # Define variebles
    img_clusters = {} # Map each image and cluster ex. {'img1': [0, 1, 2], 'img2': [1, 3], 'img3': []}
    relations_cluster = {} # Relation of each cluster ex.
    # {
    #   'cluster1': {
    #       'cluster2': 8
    #       'cluster3': 0
    #       'cluster4': 2
    #   }
    #   'cluster2': {
    #       'cluster1': 8
    #       'cluster3': 11
    #       'cluster4': 4
    #   }
    # }
    cluster_count = {} # Count each cluster image ex. {'cluster1': 5, 'cluster2': 8}

    # Prepare relation cluster and cluster count dict
    for cluster_id in inserted_cluster_id:
        relations_cluster[str(cluster_id)] = {}
        for relate_cluster_id in inserted_cluster_id:
            if cluster_id != relate_cluster_id:
                relations_cluster[str(cluster_id)][str(relate_cluster_id)] = 0
        cluster_count[str(cluster_id)] = 0

    # Create images cluster list and relation cluster
    count = 0 # Use to track face image
    for key, value in img_face_count.items():
        img_cluster_list = []
        for i in range(value):
            current_cluster_id = predicted_cluster[count]
            # If not a noise
            if current_cluster_id != -1:
                # If not in list
                if current_cluster_id not in img_cluster_list:
                    cluster_count[str(current_cluster_id)] += 1
                    # If list is not empty
                    if len(img_cluster_list) > 0:
                        # Count relation
                        for cluster_id in img_cluster_list:
                            relations_cluster[str(cluster_id)][str(current_cluster_id)] += 1
                            relations_cluster[str(current_cluster_id)][str(cluster_id)] += 1
                    # Add cluster id to list
                    img_cluster_list.append(current_cluster_id)
            count += 1
        img_clusters[key] = img_cluster_list
    return img_clusters, relations_cluster, cluster_count

# Create graph image
def createGraph(cluster_id, group_id, db):
    # Get all clusters data
    cluster_data = getAllClusterData(group_id, db)
    
    # Count relations
    relation_count = sum(cluster_data[cluster_id]['relations'].values())

    # If no relation
    if relation_count == 0:
        # Create single people graph
        # Define graph type False = single, True = group
        g_type = False

        # Main face image directory
        face_img_path = face_dir + cluster_data[cluster_id]['face_link']

        # Load main face image
        face_img = cv2.imread(face_img_path)

        # If can't load image
        if face_img is None:
            return None, False

        # Define output size
        output_size = 360

        # Create white image
        result = np.ones((output_size, output_size, 3), dtype=np.uint8) * 255

        # Calculate position of face image
        x_offset = (output_size - face_img.shape[0]) // 2
        y_offset = (output_size - face_img.shape[1]) // 2

        # Paste face image to white image
        result[x_offset:x_offset + face_img.shape[0], y_offset:y_offset + face_img.shape[1], :] = face_img

        # Define variables for text
        image_count = cluster_data[cluster_id]['image_count']
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_size = 1
        font_thickness = 2

        # Get text size
        text_size = cv2.getTextSize(str(image_count), font, font_size, font_thickness)[0]

        # Calculate text position
        text_position = ((output_size - text_size[0]) // 2, output_size - 20)

        # Draw text to image
        cv2.putText(result, str(image_count), text_position, font, font_size, (0, 0, 0), font_thickness, cv2.LINE_AA)

    else:
        # Define graph type False = single, True = group
        g_type = True

        # Prepare variable
        curr_list = [cluster_id]
        sum_image_count = 0
        max_weight = 0

        # Create undirected graph
        G = nx.Graph()

        # Add node and prepare edge
        for layer in range(max_graph_layer):
            next_list = []
            for id in curr_list:
                # If not have this node in graph, Add this node
                if not G.has_node(id):
                    G.add_node(id)

                # Add all node and edge that have relation
                for sub_id, weight in cluster_data[id]['relations'].items():
                    # If already add this node and edge, continue next sub_id
                    if cluster_data[sub_id]['is_used'] == True:
                        continue

                    # If not have this node in graph, Add this node
                    if not G.has_node(id):
                        G.add_node(id)
                    # Add edge
                    G.add_edge(id, sub_id)
                    max_weight = max(max_weight, weight)
                    
                    # If sub_id not in curr_list and next_list, Add sub_id to next_list
                    if sub_id not in curr_list and sub_id not in next_list:
                        next_list.append(sub_id)
                
                # Change is_used of id to True
                cluster_data[id]['is_used'] = True

                # Find max image_count for scaling
                sum_image_count += cluster_data[id]['image_count']

            # Copy next layer node id
            curr_list = next_list.copy()
            
            # If no next layer node id
            if len(curr_list) == 0:
                break

        # Define max scaled weight range
        max_scale_weight = 20.0

        # Get node positions from the layout
        pos = nx.spring_layout(G)

        # Create white canvas
        result_size = 2000
        result = np.ones((result_size, result_size, 3), dtype=np.uint8) * 255

        # Define graph size
        offset_size = 200
        graph_size = result_size - (offset_size * 2)

        # Find the minimum and maximum values for position x and y
        min_x, max_x = min(pos[node][0] for node in pos), max(pos[node][0] for node in pos)
        min_y, max_y = min(pos[node][1] for node in pos), max(pos[node][1] for node in pos)

        # Shift and scale the coordinates to be in the range [0, 1]
        pos = {node: ((pos[node][0] - min_x) / (max_x - min_x), (pos[node][1] - min_y) / (max_y - min_y)) for node in pos}

        # Shift and scale the coordinates to be in the range [200, 1800]
        pos = {node: (int(pos[node][0] * graph_size + offset_size), int(pos[node][1] * graph_size + offset_size)) for node in pos}

        # Draw edge and text on canvas
        for edge in G.edges(data=True):
            # Get node positions
            src = edge[0]
            dst = edge[1]
            x_src, y_src = pos[src]
            x_dst, y_dst = pos[dst]

            # Calculate scale of weight
            scaled_weight = cluster_data[src]['relations'][dst] / max_weight * max_scale_weight

            # Define line color
            # line_color = (120, 120, 120)
            if scaled_weight <= max_scale_weight/3:
                line_color = (255, 0, 0) # blue, cv2 use BGR
            elif scaled_weight <= max_scale_weight/3 * 2:
                line_color = (0, 255, 0) # green
            else:
                line_color = (0, 0, 255) # red

            # Draw edge line
            cv2.line(result, (x_src, y_src), (x_dst, y_dst), line_color, 2)

            # Calculate midpoint of line
            text_pos = ((x_src + x_dst) // 2, (y_src + y_dst) // 2)

            # Add text to center of edge
            text = str(cluster_data[src]['relations'][dst])
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            font_thickness = 2
            cv2.putText(result, text, text_pos, font, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)

        # Draw node image on canvas
        for node, (x, y) in pos.items():
            # Scale image_count
            scaled_image_count = cluster_data[node]['image_count'] / float(sum_image_count)

            # Calculate node size, image will be (node_size, node_size, 3)
            max_node_size = 300
            min_node_size = 50
            node_size = int(scaled_image_count * max_node_size / 2)

            # Minimize node size if it too small
            node_size = max(node_size, min_node_size)

            # Calculate bounding box of node on canvas
            x_start, x_end = max(0, x - node_size), min(result_size - 1, x + node_size)
            y_start, y_end = max(0, y - node_size), min(result_size - 1, y + node_size)

            # Concatenate node image path
            node_img_path = face_dir + cluster_data[node]['face_link']

            # Load node image
            node_img = cv2.imread(node_img_path)

            # If can't load image
            if node_img is None:
                return None, False

            # Resize node image to node_size
            node_img = cv2.resize(node_img, (x_end - x_start, y_end - y_start), interpolation=cv2.INTER_LINEAR)

            # draw node image on canvas
            result[y_start:y_end, x_start:x_end] = node_img

            # If main node, draw border
            if node == cluster_id:
                # Define border parameter
                border_color = [0, 0, 255] # red
                border_width = 5

                # Draw top border
                result[y_start - border_width:y_start, x_start - border_width:x_end + border_width] = border_color
                # Draw bottom border
                result[y_end:y_end + border_width, x_start - border_width:x_end + border_width] = border_color
                # Draw left border
                result[y_start - border_width:y_end + border_width, x_start - border_width:x_start] = border_color
                # Draw right border
                result[y_start - border_width:y_end + border_width, x_end:x_end + border_width] = border_color
    return result, g_type