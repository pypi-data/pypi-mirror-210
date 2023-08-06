import sys
import torch
import requests, json, pickle
from importlib.machinery import SourceFileLoader
from termcolor import colored
import os
import rich
from tqdm import tqdm
from .utils import *
from .functional_test import CheckModel, TensorflowChecks, TorchChecks

# hide warnings from tensorflow
import warnings

warnings.filterwarnings("ignore")


class Model:
    """
    Make sure model file and weights are in current directory
    Parameters: modelname

    modelname: model file name eg: vggnet, if file name is vggnet.py

    """

    def __init__(self, modelname, token, weights=False, url=""):
        self.__modelname = ""
        self.__model_path = ""
        self.__weights_path = ""
        self.__framework = TENSORFLOW_FRAMEWORK
        self.__ext = ".py"
        self.model = None
        self.__get_paths(modelname)
        self.__token = token
        self.weights = weights
        self.__url = url + "upload/"
        self.__check_model_url = url + "check-model/"
        # self.__url = 'http://127.0.0.1:8000/upload/'
        self.__recievedModelname = self.upload()

    def __get_paths(self, path):
        """
        take path provided by user as modelname
        updates model path, weights path and model name
        """
        # check if user provided a filename
        if "/" not in path:
            path = "./" + path
        # check if user provided path with .py extension
        root, ext = os.path.splitext(path)
        if ext:
            if ext != self.__ext:
                self.__ext = ".zip"
            # assign the provided path to model's path
            self.__model_path = path
            # get weights path --> remove .py from the given path and add _weights.pkl after it
            self.__weights_path = path.rsplit(".", 1)[0] + "_weights.pkl"
            # get model name --> get model name from given path
            self.__modelname = path.rsplit(".", 1)[0].split("/")[-1]
        else:
            # get models path --> add .py at the end of given path
            if os.path.exists(path + ".zip"):
                self.__ext = ".zip"
            self.__model_path = path + self.__ext
            # get weights path --> add _weights.pkl after given path
            self.__weights_path = path + "_weights.pkl"
            # get model name --> get filename from given path
            self.__modelname = path.split("/")[-1]

    def getNewModelId(self):
        if self.__recievedModelname is not None:
            return (
                self.__recievedModelname,
                self.__modelname,
                self.__ext,
                self.__model_path,
                self.__framework,
            )

    def upload(self):
        # load model from current directory
        status = False
        message = None
        # create progress bar with total number of nested functions
        self.progress_bar = tqdm(total=8, desc="Model Upload Progress")
        try:
            # call check model class for model checks
            model_checks_generic = CheckModel(
                self.progress_bar,
                model_name=self.__modelname,
                model_path=self.__model_path,
            )
            (
                status,
                message,
                model_name,
                progress_bar,
            ) = model_checks_generic.model_func_checks()
            if not status:
                model_checks_generic.remove_tmp_file()
                text = colored(
                    message,
                    "red",
                )
                print(text, "\n")
                self.progress_bar.close()
                return None
            loaded_model = model_checks_generic.model
            self.__framework = model_checks_generic.framework
            model_check_class = TensorflowChecks
            if self.__framework == PYTORCH_FRAMEWORK:
                model_check_class = TorchChecks
            elif self.__framework == TENSORFLOW_FRAMEWORK:
                model_check_class = TensorflowChecks
            model_checks = model_check_class(
                model=loaded_model,
                model_name=model_name,
                progress_bar=self.progress_bar,
            )
            (
                status,
                message,
                model_name,
                progress_bar,
            ) = model_checks.model_func_checks()
            if not status:
                model_checks_generic.remove_tmp_file()
                text = colored(
                    message,
                    "red",
                )
                print(text, "\n")
                self.progress_bar.close()
                return None
            self.progress_bar.update(1)
            model_checks_generic.remove_tmp_file(update_progress_bar=True)
            self.model = model_checks.model
            updated_model_name = self.__upload_model()
            self.progress_bar.close()
            return updated_model_name
        except FileNotFoundError:
            text = colored(
                f"\nUpload failed. There is no model with the name '{self.__modelname}' in your folder '{os.getcwd()}'.",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            self.progress_bar.close()
            return None
        except Exception as e:
            text = colored(
                f"\nUpload failed.",
                "red",
            )
            print(text, "\n")
            if self.__url != "https://tracebloc.azurewebsites.net/":
                print(
                    f"Error in Upload is {e} at {sys.exc_info()[-1].tb_lineno} with message : {message}"
                )
            self.progress_bar.close()
            return None

    def __upload_model(self):
        model_file = open(self.__model_path, "rb")
        if self.weights:
            w = self.checkWeights()
            if not w:
                return None
            weights_file = open(self.__weights_path, "rb")
            files = {"upload_file": model_file, "upload_weights": weights_file}
            values = {
                "model_name": self.__modelname,
                "setWeights": True,
                "type": "functional_test",
            }
        else:
            files = {"upload_file": model_file}
            values = {
                "model_name": self.__modelname,
                "setWeights": False,
                "type": "functional_test",
            }
        # call check-model API to do functional test
        header = {"Authorization": f"Token {self.__token}"}
        r = requests.post(
            self.__check_model_url, headers=header, files=files, data=values
        )
        model_file.close()
        body_unicode = r.content.decode("utf-8")
        content = json.loads(body_unicode)
        text = content["text"]
        check_status = content["check_status"]
        if not check_status:
            tex = colored(
                text,
                "red",
            )
            print(tex, "\n")
            return None
        self.progress_bar.update(1)
        return content["model_name"]

    def checkWeights(self):
        # load model weights from current directory
        try:
            weights_file = open(self.__weights_path, "rb")
        except FileNotFoundError:
            text = colored(
                f"Weights Upload failed. No weights file found with the name '{self.__modelname}_weights.pkl' in path '{os.getcwd()}'.",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            return False
        # Load weights to check if it works
        try:
            we = pickle.load(weights_file)
            model = SourceFileLoader(
                self.__modelname, f"{self.__model_path}"
            ).load_module()
            model = model.MyModel()
            model.set_weights(we)
            weights_file.close()
            return True
        except ValueError:
            weights_file.close()
            text = colored(
                "Weights upload failed. Provide weights compatible with provided model.",
                "red",
            )
            print(text, "\n")
            print(
                "For more information check the docs 'https://docs.tracebloc.io/weights'"
            )
            return False
