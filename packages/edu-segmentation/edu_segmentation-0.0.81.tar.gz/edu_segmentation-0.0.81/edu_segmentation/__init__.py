
import os
import subprocess
import sys

if not os.path.isfile(os.path.join(os.path.dirname(__file__), f"already_run.txt")):
    # Get the path of the requirements.txt file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    req_path = os.path.join(dir_path, 'requirements.txt')

    # Install the requirements using pip
    subprocess.check_call(['pip', 'install', '-r', req_path])

    import requests

    # function is placed here because requirements.txt needs to be downloaded first to get requests
    def download_torch_models(model_folder, model_name):
        username = "patrialyx"
        repo_name = "edu-segmentation-models"
        tag = "v1.0.0"
        model_url = f"https://github.com/{username}/{repo_name}/releases/download/{tag}/{model_name}"
        model_path = os.path.join(os.path.dirname(__file__), f"{model_folder}/model_dependencies/{model_name}")

        response = requests.get(model_url)

        with open(model_path, "wb") as f:
            f.write(response.content)

    # just automatically download all models for the user
    try:
        model_name = "BERT_token_classification_final.pth"
        model_folder = "BERTTokenClassification"
        path_to_exist = os.path.join(os.path.dirname(__file__), f"{model_folder}/model_dependencies")
        if not os.path.exists(path_to_exist):
            os.makedirs(path_to_exist)
        if os.path.isfile(os.path.join(os.path.dirname(__file__), f"{model_folder}/model_dependencies/{model_name}")):
            print(f"Segbot BERT-uncased Model has already been downloaded.")
            pass
        else:
            print("Downloading Segbot BERT-uncased Model...")
            download_torch_models(model_folder, model_name)
            print("Segbot BERT-uncased Model downloaded successfully.")
    except:
        print("Failed to download BERT-uncased Segbot Model.")
    try:
        model_name = "model_segbot.torchsave"
        model_folder = "BARTTokenClassification"
        if os.path.isfile(os.path.join(os.path.dirname(__file__), f"{model_folder}/model_dependencies/{model_name}")):
            # print(f"Original Segbot Model has already been downloaded.")
            pass
        else:
            # print("Downloading Original Segbot Model...")
            download_torch_models(model_folder, model_name)
            # print("Original Segbot Model downloaded successfully.")
    except:
        print("Failed to download Original Segbot Model.")

    try:
        model_name = "model_segbot_bart.torchsave"
        model_folder = "BARTTokenClassification"
        if os.path.isfile(os.path.join(os.path.dirname(__file__), f"{model_folder}/model_dependencies/{model_name}")):
            print(f"Segbot BART Model has already been downloaded.")
        else:
            print("Downloading Segbot BART Model...")
            download_torch_models(model_folder, model_name)
            print("Segbot BART Model downloaded successfully.")
    except:
        print("Failed to download Segbot BART Model.")
        # repeat = 1
        # while repeat:
        #     print("Which model would you like to download? \n")
        #     option = int(input("(1) Input 1 for Original Segbot Model (2) Input 2 for Segbot BART Model (3) None \n"))
        #     if option == 1:
        #         model_name = "model_segbot.torchsave"
        #         if os.path.isfile(f"{model_name}"):
        #             print(f"Original Segbot Model has already been downloaded.")
        #         else:
        #             download_torch_models(model_name)
        #             print("Downloading Original Segbot Model...")
        #     elif option == 2:
        #         model_name = "model_segbot_bart.torchsave"
        #         if os.path.isfile(f"{model_name}"):
        #             print(f"Segbot BART Model has already been downloaded.")
        #         else:
        #             download_torch_models(f"{model_name}")
        #             print("Downloading Segbot BART Model...")
        #     elif option == 3:
        #         repeat = 0
        #     else:
        #         print("Input format is wrong. Only accept '1', '2', or '3'")
    with open(os.path.join(os.path.dirname(__file__), f"already_run.txt"), "w") as file:
        pass
