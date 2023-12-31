# Functionality: Plots the images produced in the output as a matplotlib figure
import matplotlib.pyplot as plt
import numpy
import torch

from database_connection import connect_to_mongo

client = connect_to_mongo()
db = client.cse515_project_phase1
collection = db.features
rep_collection = db.phase2_representative_images


def output_plotter(feature_name, input_image, feature_vals, feature_val_keys, k):
    # Create a figure where the images can be plotted
    fig = plt.figure(figsize=(10, 7))
    fig.add_subplot(2, 6, 1)

    fig.suptitle(feature_name + ' query top 10 outputs for input image ID ' +
                 str(input_image["image_id"]), fontsize=16)

    # Plotting the input image in the figure
    plt.imshow((numpy.squeeze(torch.tensor(
        numpy.array(input_image["image"])).permute(1, 2, 0))))
    plt.title("Query Image ID: " + str(input_image["image_id"]))

    print("Results for " + feature_name + ":")

    # Plotting the images produced by the query result
    for i in range(k):
        print(feature_vals[feature_val_keys[i]])
        image = collection.find_one(
            {"image_id": feature_vals[feature_val_keys[i]]})
        img = torch.tensor(numpy.array(image["image"]))

        fig.add_subplot(2, 6, i + 1)
        plt.imshow((numpy.squeeze(img.permute(1, 2, 0))))
        plt.axis('off')
        plt.title("Result ID: " + str(image["image_id"] +
                  "\nDistance: " + str(round(feature_val_keys[i], 4))))

    plt.show()


def task_2_output_plotter(feature_name, label, feature_vals, feature_val_keys, k):
    # Create a figure where the images can be plotted
    fig = plt.figure(figsize=(10, 7))
    fig.add_subplot(2, 6, 1)

    fig.suptitle(feature_name + ' query top 10 outputs for input label ' +
                 str(label), fontsize=16)

    im = collection.find_one({"target": label})
    # Plotting the input image in the figure
    plt.imshow((numpy.squeeze(torch.tensor(
        numpy.array(im["image"])).permute(1, 2, 0))))
    plt.title("Query Image label: " + str(label))

    print("Results for " + feature_name + ":")

    # Plotting the images produced by the query result
    for i in range(k):
        print(feature_vals[feature_val_keys[i]])
        image = collection.find_one(
            {"image_id": feature_vals[feature_val_keys[i]]})
        img = torch.tensor(numpy.array(image["image"]))

        fig.add_subplot(2, 6, i + 1)
        plt.imshow((numpy.squeeze(img.permute(1, 2, 0))))
        plt.axis('off')
        plt.title("Result ID: " + str(image["image_id"] +
                  "\nDistance: " + str(round(feature_val_keys[i], 4))))

    plt.show()


def task_7_output_plotter(sim_measures, sim_measure_keys, k, query_image):
    fig = plt.figure(figsize=(10, 7))
    fig.add_subplot(2, 6, 1)

    fig.suptitle('query top 10 outputs for input image ID ' +
                 str(query_image), fontsize=16)

    im = collection.find_one({"image_id": query_image})
    # Plotting the input image in the figure
    plt.imshow((numpy.squeeze(torch.tensor(
        numpy.array(im["image"])).permute(1, 2, 0))))
    plt.title("Query Image ID: " + str(query_image))

    print("Results" + ":")
    # Plotting the images produced by the query result
    for i in range(1, k):
        print(sim_measures[sim_measure_keys[i]])
        image = collection.find_one(
            {"image_id": sim_measures[sim_measure_keys[i]]})
        img = torch.tensor(numpy.array(image["image"]))

        fig.add_subplot(2, 6, i + 1)
        plt.imshow((numpy.squeeze(img.permute(1, 2, 0))))
        plt.axis('off')
        plt.title("Result ID: " + str(image["image_id"] +
                  "\nDistance: " + str(round(sim_measure_keys[i], 4))))

    plt.show()


def task_10_output_plotter(res, query_image):
    fig = plt.figure(figsize=(10, 7))
    fig.add_subplot(2, 6, 1)

    fig.suptitle(
        f'Query top {len(res)} outputs for input image label {query_image}', fontsize=16)

    im = rep_collection.find_one({"target": query_image})
    im = collection.find_one({"image_id": im['image_id']})
    # Plotting the input image in the figure
    plt.imshow((numpy.squeeze(torch.tensor(
        numpy.array(im["image"])).permute(1, 2, 0))))
    plt.title("Query Image ID: " + str(query_image))

    print("Results" + ":")
    # Plotting the images produced by the query result
    for i in range(1, len(res)):
        print(res[i][0])
        image = collection.find_one(
            {"image_id": str(res[i][0])})
        img = torch.tensor(numpy.array(image["image"]))

        fig.add_subplot(2, 6, i + 1)
        plt.imshow((numpy.squeeze(img.permute(1, 2, 0))))
        plt.axis('off')
        plt.title("Result ID: " + str(image["image_id"] +
                  "\nDistance: " + str(round(res[i][1], 4))))

    plt.show()


def output_plotter_task_11(dataset, label, feature_descriptor, input_image_id_list):
    def closest_factors(n):
        factor = int(n ** 0.5)

        while n % factor != 0:
            factor -= 1

        return factor, n // factor

    no_of_images = len(input_image_id_list)
    rows, columns = closest_factors(no_of_images)
    for i, image_id in enumerate(input_image_id_list):
        image, label = dataset[int(image_id)]
        image = image.numpy().transpose((1, 2, 0))
        mean = [0.485, 0.456, 0.406]
        std = [0.229, 0.224, 0.225]
        image = image * std + mean
        image = image.clip(0, 1)

        plt.subplot(rows, columns, i+1)
        plt.imshow(image)
        plt.title(f"Label: {label}")

    plt.suptitle(
        f'These are the images for label: {label} and feature descriptor: {feature_descriptor}')
    plt.tight_layout()
    plt.show()
