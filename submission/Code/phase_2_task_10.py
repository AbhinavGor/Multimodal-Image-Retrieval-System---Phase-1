# Task 10: Implement a program which, given (a) a label l, (b) a user selected latent semantics, and (c) positive integer k,
# identifies and lists k most relevant images, along with their scores, under the selected latent space.
import time
import numpy as np
import cv2
from scipy import datasets
from sklearn.cluster import KMeans
import torch
import pandas as pd
import torchvision
from torchvision.transforms import transforms
from scipy.spatial import distance
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
from database_connection import connect_to_mongo

def output_plotter(dataset, input_image_id_list, print_text):

    def closest_factors(n):
        # Start from the integer value closest to the square root
        factor = int(n ** 0.5)
        
        # Find the largest factor of n which is less than or equal to the square root of n
        while n % factor != 0:
            factor -= 1
            
        return factor, n // factor
    
    no_of_images=len(input_image_id_list)
    rows,columns=closest_factors(no_of_images)
    plt.suptitle(print_text)
    for i,image_id in enumerate(input_image_id_list):        
        image, label = dataset[int(image_id)]  # Python indexing is 0-based

        # Convert the PyTorch tensor to a numpy array and transpose the dimensions for visualization
        image = image.numpy().transpose((1, 2, 0))

        # Since we normalized the data during

        mean = [0.485, 0.456, 0.406]
        std = [0.229, 0.224, 0.225]
        image = image * std + mean
        image = image.clip(0, 1)  # Ensure the image data is between 0 and 1

        # Display the image using matplotlib
        plt.subplot(rows, columns, i+1)
        plt.imshow(image)
        
    plt.tight_layout()
    plt.show()

query_label = str(input("Enter the query label:"))
print("1. SVD.\n2. NNMF.\n3.LDA.\n4.K Means\n", end="")
ls = int(input("Select one of the above: "))

k_val = int(input("Enter how many output images are required:"))
print("1.LS1 \n2.LS2 \n3.LS3 \n4.LS4")
ls_k = str(input("Enter the latent sematic:"))
feature_names = ["color_moment", "hog", "layer3", "avgpool", "fc"]
print("1. Color Moment\n2. HoG.\n3. Layer 3.\n4. AvgPool.\n5. FC.")
feature = int(input("Select one of the feature space from above:"))
k = str(input("Enter k value:"))

client = connect_to_mongo()
db = client.cse515_project_phase1
collection = db.phase2_ls1
collection = db.phase2_features

distances = {}
# Assuming latent_space is a list of feature vectors
latent_space = []
image_id = []

# Collect features for images with the target label
for image_ls in collection.find({"target": int(query_label)}):
    latent_space.append(image_ls[feature_names[feature - 1]])
    image_id.append(image_ls["image_id"])

transform = transforms.Compose([
transforms.ToTensor(),
transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load the Caltech 101 dataset
dataset = torchvision.datasets.Caltech101(root='./data', download=True, transform=transform)

# Assuming latent_space is not empty
if len(latent_space) > 0:
    # Convert the list of feature vectors to a numpy array
    latent_space = np.array(latent_space)

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=1, random_state=42)
    kmeans.fit(latent_space)

    representative_image_in_latent_space = kmeans.cluster_centers_

    # Get the cluster centroids (representative datapoints)
    representative_image_index = np.argmin(np.sum((latent_space - kmeans.cluster_centers_)**2, axis=1))
    representative_image_id = int(image_id[int(representative_image_index)])

    print("Representative Image ID:", image_id[int(representative_image_index)])

    match int(ls_k):
        case 4:
            similarity_matrix = np.loadtxt(f"latentsemantics_task6_{k}_{feature}.csv", delimiter=",")
            image_weight_pairs = np.loadtxt(f"imageweightpairs_task6_{ls}_{feature_names[feature-1]}_{k}.csv", delimiter=",")

            weight_of_the_representative_image = image_weight_pairs[representative_image_id, 1]

            similarity_values = similarity_matrix[representative_image_id, :]

            sorted_indices = np.argsort(similarity_values)
            sorted_array = similarity_values[sorted_indices]

            # Calculate absolute differences between weights
            differences = image_weight_pairs[:, 1] - weight_of_the_representative_image

            # Get the indices of the k smallest differences
            closest_indices = np.argsort(differences)

            # Get the k closest image ids and weights
            closest_image_ids = image_weight_pairs[closest_indices, 0]
            closest_weights = image_weight_pairs[closest_indices, 1]
            closest_image_ids_list = image_weight_pairs[closest_indices, 0].astype(int).astype(str).tolist()
            print_text = f"\n\nThe requested {k_val} images for {feature_names[feature - 1]} in latent space LS {ls_k} for query label {query_label} are:"
            print(print_text)
            image_ids_result = []
            image_count = 0
            similarity_indexes_iterated = 0
            while image_count < k_val:
                similarity_indexes_iterated += 1
                if sorted_array[similarity_indexes_iterated] != 0.0:
                    print("Image ID:", {sorted_indices[similarity_indexes_iterated]}, " Similarity Score:", {sorted_array[similarity_indexes_iterated]})
                    image_ids_result.append(sorted_indices[similarity_indexes_iterated])
                    image_count += 1

            # print("\nWeight of the representative image is", weight_of_the_representative_image)
            # index_iterated = 0
            # images_listed = 0
            # image_ids_result = []
            # for index_iterated in range(len(closest_image_ids)):
            #     if images_listed == k_val:
            #         break
            #     current_image_id = closest_image_ids_list[index_iterated]
            #     if current_image_id in image_id:
            #         print("Image ID:", {closest_image_ids[index_iterated]}, " Weight:", {closest_weights[index_iterated]})
            #         image_ids_result.append(closest_image_ids[index_iterated])
            #         images_listed += 1

            output_plotter(dataset, image_ids_result, print_text)

else:
    print("No images with the target label.")