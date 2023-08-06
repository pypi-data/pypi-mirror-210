import inspect
import requests, json
import dill
import base64
from termcolor import colored
from tracebloc_package import check_parameters
from .utils import *
from .functional_test import CheckModel, TensorflowChecks, TorchChecks



class LinkModelDataSet:
    """
    creating a training plan and assign data set
    parameters: modelId, datasetId, token

    methods:get_parameters, get_trainingplan
    """

    def __init__(
        self,
        modelId,
        model,
        modelname,
        datasetId,
        token,
        weights,
        totalDatasetSize,
        total_images,
        num_classes,
        class_names,
        url="",
        environment="production",
        framework=TENSORFLOW_FRAMEWORK,
    ):
        self.__url = url
        # self.__url = 'http://127.0.0.1:8000/'
        self.__token = token
        self.__earlystopCallback = {}
        self.__reducelrCallback = {}
        self.__modelCheckpointCallback = {}
        self.__terminateOnNaNCallback = {}
        self.__learningRateSet = False
        self.__optimizerSet = False
        self.__callbacks = str()
        self.__message = "training"
        self.__datasetId = datasetId
        self.__epochs = 10
        self.__cycles = 1
        self.__modelId = modelId
        self.__modelName = modelname
        self.__model = model
        self.__image_shape = 224
        self.__image_type = "rgb"
        self.__optimizer = "sgd"
        self.__totalDatasetSize = totalDatasetSize
        self.__trainingDatasetSize = totalDatasetSize
        self.__trainingClasses = class_names
        self.__subdataset = {}
        self.__lossFunction = {TYPE: STANDARD, VALUE: "categorical_crossentropy"}
        self.__learningRate = {TYPE: CONSTANT, VALUE: 0.001}
        self.__seed = False
        self.__total_images = total_images
        self.__num_classes = num_classes
        self.__class_names = class_names
        self.__batchSize = self.__default_batchSize()
        self.__featurewise_center = False
        self.__samplewise_center = False
        self.__featurewise_std_normalization = False
        self.__samplewise_std_normalization = False
        self.__zca_whitening = False
        self.__rotation_range = 0
        self.__width_shift_range = 0.0
        self.__height_shift_range = 0.0
        self.__brightness_range = "None"
        self.__shear_range = 0.0
        self.__zoom_range = 0.0
        self.__channel_shift_range = 0.0
        self.__fill_mode = "nearest"
        self.__cval = 0.0
        self.__horizontal_flip = False
        self.__vertical_flip = False
        self.__rescale = "None"
        self.__validation_split = self.__default_validation_split()
        self.__shuffle = True
        self.__layers_non_trainable = ""
        self.__metrics = str(["accuracy"])
        self.__objective = ""
        self.__name = "None"
        self.__modelType = "None"
        self.__category = "Classification"
        self.__upperboundTime = 0
        self.__weights = weights
        self.__images_per_class = json.dumps(self.__class_names)
        self.__eligibility_passed = True
        self.__error_method = []
        self.__reform_model = False
        self._environment = environment
        self.__framework = framework
        self.__experiment_url = "https://ai.tracebloc.io/experiments/"
        if environment == "development" or environment == "ds":
            self.__experimenturl = "https://dev.tracebloc.io/experiments/"
        elif environment == "staging":
            self.__experimenturl = "https://stg.tracebloc.io/experiments/"

    def resetTrainingPlan(self):
        self.__earlystopCallback = {}
        self.__reducelrCallback = {}
        self.__modelCheckpointCallback = {}
        self.__terminateOnNaNCallback = {}
        self.__learningRateSet = False
        self.__optimizerSet = False
        self.__callbacks = str()
        self.__epochs = 10
        self.__cycles = 1
        self.__image_shape = 224
        self.__image_type = "rgb"
        self.__optimizer = "sgd"
        self.__trainingDatasetSize = self.__totalDatasetSize
        self.__trainingClasses = self.__class_names
        self.__lossFunction = {TYPE: STANDARD, VALUE: "categorical_crossentropy"}
        self.__learningRate = {TYPE: CONSTANT, VALUE: 0.001}
        self.__seed = False
        self.__batchSize = self.__default_batchSize()
        self.__featurewise_center = False
        self.__samplewise_center = False
        self.__featurewise_std_normalization = False
        self.__samplewise_std_normalization = False
        self.__zca_whitening = False
        self.__rotation_range = 0
        self.__width_shift_range = 0.0
        self.__height_shift_range = 0.0
        self.__brightness_range = "None"
        self.__shear_range = 0.0
        self.__zoom_range = 0.0
        self.__channel_shift_range = 0.0
        self.__fill_mode = "nearest"
        self.__cval = 0.0
        self.__horizontal_flip = False
        self.__vertical_flip = False
        self.__rescale = "None"
        self.__validation_split = self.__default_validation_split()
        self.__shuffle = True
        self.__layers_non_trainable = ""
        self.__metrics = str(["accuracy"])
        self.__objective = ""
        self.__name = "None"
        self.__modelType = "None"
        self.__category = "Classification"
        self.__upperboundTime = 0
        self.__images_per_class = json.dumps(self.__class_names)
        self.__eligibility_passed = True
        self.__reform_model = False
        print("Training Plan Parameters reset")

    def __print_error(self, error):
        self.__eligibility_passed = False
        method = inspect.currentframe().f_back.f_code.co_name
        text = colored(
            error,
            "red",
        )
        print(text, "\n")
        self.__error_method.append(method)

    def __not_supported_parameters(self, parameter):
        text = colored(
            f"The parameter {parameter} is not supported till now on pytorch",
            "red",
        )
        print(text, "\n")

    def __remove_error_method(self):
        method = inspect.currentframe().f_back.f_code.co_name
        if method in self.__error_method:
            self.__error_method.remove(method)
        if len(self.__error_method) == 0:
            self.__eligibility_passed = True

    def trainingClasses(self, training_dataset: dict):
        """
        creates sub dataset of the current dataset of the no of images per class selected by user
        Please provide number of images per class
        example: dataset: {'car': 65, 'person': 42}
        Classes in dataset car, person

        trainingObject.trainingClasses({'car': 30, 'person': 30})
        """
        checkeligible = True
        class_names = self.__class_names.keys()
        for class_name in class_names:
            num_images = int(self.__class_names[class_name])
            if class_name in training_dataset.keys():
                value = training_dataset[class_name]
                if 0 < value <= num_images:
                    pass
                else:
                    checkeligible = False
                    error_msg = f"Please provide num of images for class {class_name} greater than 0 and less than equal to {num_images}"
                    self.__print_error(error_msg)
            else:
                checkeligible = False
                error_msg = "trainingDatasetSize dictionary must contain all classes that are present in the dataset. Customisation in terms of classes is not allowed."
                self.__print_error(error_msg)
        if checkeligible:
            self.__trainingClasses = training_dataset
            self.__trainingDatasetSize = getImagesCount(training_dataset)
            self.__subdataset = json.dumps(
                {
                    "trainingDatasetSize": self.__trainingDatasetSize,
                    "trainingClasses": self.__trainingClasses,
                }
            )
            self.__remove_error_method()
            # recalculate the validation split
            header = {"Authorization": f"Token {self.__token}"}
            data = {
                "edges_involved": json.dumps(list(self.__total_images.keys())),
                "images_per_class": json.dumps(training_dataset),
                "type": "recalculate_image_count_per_edge",
                "datasetId": self.__datasetId,
            }
            re = requests.post(
                f"{self.__url}check-model/",
                headers=header,
                data=data,
            )
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            if re.status_code == 200:
                self.__total_images = content["total_images_per_edge"]
                self.__validation_split = self.__default_validation_split()
            # else:
            #     self.__print_error(content['message'])

    def __update_image_model(self):
        """
        change image type and size data as user choice in model file provided by user
        """
        header = {"Authorization": f"Token {self.__token}"}
        data = {
            "model_name": self.__modelId,
            "image_shape": self.__image_shape,
            "image_type": self.__image_type,
            "type": "reform_model",
        }
        re = requests.post(
            f"{self.__url}check-model/",
            headers=header,
            data=data,
        )
        if re.status_code == 202:
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            self.__modelId = content["model_name"]
        if re.status_code == 400:
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            error_message = f"Error Occured while setting updated image format for model as {content['message']}"
            self.__print_error(error_message)

    def imageShape(self, image_shape: int):
        """
        Set image shape
        parameters: integer. value must be between 48 and 224
        example: trainingObject.imageShape(224)
        default: 224
        maximum value : 224
        """
        if type(image_shape) is int and (48 <= image_shape <= 224):
            self.__image_shape = image_shape
            self.__update_image_model()
            self.__remove_error_method()
        else:
            error_msg = "Invalid input type or value '0' given for image shape"
            self.__print_error(error_msg)

    def imageType(self, image_type: str):
        """
        Set image type to be used for training
        parameters: string type values.
        supported type: ['rgb', 'gray']
        example: trainingObject.imageType('rgb')
        default: rgb
        """
        allowed_types = ["rgb", "grayscale"]
        try:
            if type(image_type) is str:
                allowed_types.index(image_type.lower())
                self.__image_type = image_type.lower()
                self.__update_image_model()
                self.__remove_error_method()
        except:
            error_msg = "Enter values from supported values only "
            self.__print_error(error_msg)

    def seed(self, seed: bool):
        """
        Boolean.
        Sets the global random seed when selected
        default: False
        example:trainingObject.seed(True)
        """
        if type(seed) == bool:
            self.__seed = str(seed)
            self.__remove_error_method()
        else:
            error_msg = "Invalid input type given for seed\n"
            self.__print_error(error_msg)

    def experimentName(self, name: str):
        """
        String.
        Name of the experiment
        example:trainingObject.experimentName('Classifying manufacturing defects')
        """
        self.__name = str(name)

    def objective(self, objective: str):
        """
        String.
        Objective of the experiment
        example:trainingObject.objective('Classify images using Convolutional Neural Networks (specifically, VGG16)
        pre-trained on the ImageNet dataset with Keras deep learning library.')
        """
        if type(objective) == str:
            self.__objective = objective
            self.__remove_error_method()
        else:
            error_msg = "Please enter a string in objective\n"
            self.__print_error(error_msg)

    def epochs(self, epochs: int):
        """
        Integer.
        Number of epochs to train the model.
        An epoch is an iteration over the entire data provided.
        Note that in conjunction with initial_epoch, epochs is to be understood as "final epoch".
        The model is not trained for a number of iterations given by epochs,
        but merely until the epoch of index epochs is reached.
        example: trainingObject.epochs(100)
        default: 10
        """
        if type(epochs) == int and epochs != 0:
            self.__epochs = epochs
            self.__remove_error_method()
        else:
            error_msg = "Invalid input type or value '0' given for epochs\n"
            self.__print_error(error_msg)

    def cycles(self, cycles: int):
        """
        Set number of cycles
        parameters: integer type values.
        example: trainingObject.cycles(10)
        default: 1
        """
        if type(cycles) == int and cycles != 0:
            self.__cycles = cycles
            self.__remove_error_method()
        else:
            self.__eligibility_passed = False
            error_msg = "Invalid input type or value '0' given for cycles\n"
            self.__print_error(error_msg)

    def __default_batchSize(self):
        """
        set default batch size when training object is created
        """
        # get edge with the lowest images
        edge_min = min(self.__total_images, key=self.__total_images.get)
        # get images count for selected edge
        images = int(self.__total_images[edge_min])
        batch = images // 3
        if 8 < batch < 16:
            return 8
        elif 16 < batch < 32:
            return 16
        elif 32 < batch < 64:
            return 32
        elif batch > 64:
            return 64
        else:
            return batch

    def batchSize(self, batchSize: int):
        """
        Integer or None. Number of samples per gradient update. If unspecified, batch_size will default to 32.
        example: trainingObject.batchSize(16)
        default: 32
        """
        # get edge with lowest images
        edge_min = min(self.__total_images, key=self.__total_images.get)
        # get images count for selected edge
        images = int(self.__total_images[edge_min])
        # check for no of batches
        if type(batchSize) == int:
            if images // batchSize < 3:
                error_msg = "Please choose smaller batch size as dataset selected have less images\n"
                self.__print_error(error_msg)
                return
            self.__batchSize = batchSize
            self.__remove_error_method()
        else:
            error_msg = "Invalid input type given for batchSize\n"
            self.__print_error(error_msg)

    def __default_validation_split(self):
        """
        set default validation split when training object is created
        """
        # get edge with lowest images
        edge_min = min(self.__total_images, key=self.__total_images.get)
        images = int(self.__total_images[edge_min])
        minimum = round(self.__num_classes / images, 2)
        if minimum == 0 or minimum == 1:
            self.__eligibility_passed = False
        return minimum

    def validation_split(self, validation_split: float):
        """
        Float. Fraction of images reserved for validation (strictly between 0 and 1).
        example: trainingObject.validation_split(0.2)
        default: 0.1
        """
        # calculate minimum validation split using the following equation
        # minimum = number of classes / total images
        # get edge with lowest images
        edge_min = min(self.__total_images, key=self.__total_images.get)
        images = int(self.__total_images[edge_min])
        minimum = round(self.__num_classes / images, 2)

        if type(validation_split) == float and minimum <= validation_split <= 1.0:
            self.__validation_split = validation_split
            self.__remove_error_method()
        else:
            error_msg = f"Invalid input type or set value not less than {minimum} for validation_split\n"
            self.__print_error(error_msg)

    def optimizer(self, optimizer: str):
        """
        String (name of optimizer)
        example: trainingObject.optimizer('rmsprop')
        supported optimizers: ['adam','rmsprop','sgd','adadelta', 'adagrad', 'adamax','nadam', 'ftrl']
        default: 'sgd'
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            o = ["adam", "rmsprop", "sgd", "adadelta", "adagrad", "adamax", "nadam", "ftrl"]
            optlrrateflag = True
            error = None
            optimizer = optimizer.lower()
            try:
                o.index(optimizer)
                if self.__learningRateSet:
                    optlrrateflag, error = check_parameters.get_optimizer(
                        optimizer, self.__learningRate.copy()
                    )
                if not optlrrateflag and error is not None:
                    error_msg = f"While setting optimiser error Occurred as {error}"
                    self.__print_error(error_msg)
                else:
                    self.__optimizer = optimizer
                    self.__optimizerSet = True
                    self.__remove_error_method()
            except Exception as e:
                error_msg = f"Please provide supported optimizers: {o}\n"
                self.__print_error(error_msg)
        else:
            o = ["adam", "rmsprop", "sgd", "adadelta", "adagrad", "adamax", "nadam", "ftrl"]
            try:
                o.index(optimizer)
                self.__optimizer = optimizer
                self.__remove_error_method()
            except:
                error_msg = f"Please provide supported optimizers: {o}\n"
                self.__print_error(error_msg)

    def learningRate(self, learningRate: dict):
        """
        Set learning rate by passing a dictionary
        There are three different type of learningrate : constant, adaptive, custom
        default: {'type': 'constant', 'value': 0.0001}
        Set constant type learning rate for optimization.
        parameters: value
        example: trainingObject.learningRateConstant({'type': 'constant', 'value': 0.0001})

        Adaptive learning rate as per learning rate schedulars present in tensorflow
        parameters: dictionary containing schedular Name in schedular key value and rest all neccessary parameters added in dictionary
        example: trainingObject.learningRateAdaptive({'type': 'adaptive', 'schedular': 'ExponentialDecay', 'decay_steps':1000, 'decay_rate':0.5})

        Set learning rate for as custom function.
        first write custom learning rate function as method and pass method name in learning rate
        example:
        def custom_LearningRate_schedular(epoch):
            if epoch < 5:
                return 0.01
            else:
                return 0.01 * tf.math.exp(0.1 * (10 - epoch))
        trainingObject.learningRateCustom({'type': 'constant', 'value': custom_LearningRate_schedular, 'epoch': 4})
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            optlrrateflag = True
            error = None
            if TYPE in learningRate.keys():
                if self.__optimizerSet:
                    optlrrateflag, error = check_parameters.get_optimizer(
                        self.__optimizer, learningRate.copy()
                    )
                if not optlrrateflag:
                    error_msg = f"While setting Learning Rate error Occured as {error}"
                    self.__print_error(error_msg)
                else:
                    if learningRate[TYPE] == CUSTOM and callable(learningRate[VALUE]):
                        try:
                            # Serialize the loss function
                            serialized_data = learningRate
                            # Encode the binary data as text
                            encoded_data = base64.b64encode(serialized_data).decode("utf-8")
                            self.__learningRate = {TYPE: CUSTOM, VALUE: encoded_data}
                            self.__learningRateSet = True
                            self.__remove_error_method()
                        except Exception as e:
                            error_msg = f"Error while setting custom learning rate : {e}\n"
                            self.__print_error(error_msg)
                    elif learningRate[TYPE] == CONSTANT or learningRate[TYPE] == ADAPTIVE:
                        self.__learningRate = learningRate
                        self.__learningRateSet = True
                        self.__remove_error_method()
                    else:
                        error_msg = "Input not as per given convention for learningRate\n"
                        self.__print_error(error_msg)
            else:
                error_msg = "Input not as per given convention for learningRate\n"
                self.__print_error(error_msg)
        else:
            if learningRate[TYPE] == CONSTANT:
                self.__learningRate = learningRate
                self.__remove_error_method()
            else:
                error_msg = "Adaptive and Custom learning rate"
                self.__not_supported_parameters(error_msg)

    def lossFunction(self, lossFunction: dict):
        """
        Set loss function
        parameters: string type values or custom loss function.
        default: {'type': 'standard', 'value':'categorical_crossentropy'}

        set standard loss function like this
        example: trainingObject.lossFunctionStandard({'type': 'standard', 'value':'binary_crossentropy'})
        supported loss functions: ['binary_crossentropy','categorical_crossentropy', 'mse']

        set custom loss function like this
        example:
        def custom_mse(y_true, y_pred):

            # calculating squared difference between target and predicted values
            loss = K.square(y_pred - y_true)  # (batch_size, 2)

            # multiplying the values with weights along batch dimension
            loss = loss * [0.3, 0.7]          # (batch_size, 2)

            # summing both loss values along batch dimension
            loss = K.sum(loss, axis=1)        # (batch_size,)

            return loss
        trainingObject.lossFunctionCustom({'type': 'custom', 'value':custom_mse})
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            l = ["binary_crossentropy", "categorical_crossentropy", "mse"]
            if TYPE in lossFunction.keys() and VALUE in lossFunction.keys():
                if lossFunction[TYPE] == STANDARD:
                    try:
                        l.index(lossFunction[VALUE].lower())
                        self.__lossFunction = lossFunction
                        self.__remove_error_method()
                    except:
                        error_msg = f"Please provide tensorflow supported default loss functions losses: {l}\n"
                        self.__print_error(error_msg)
                elif lossFunction[TYPE] == CUSTOM:
                    if callable(lossFunction[VALUE]):
                        try:
                            # Serialize the loss function
                            serialized_data = dill.dumps(lossFunction[VALUE])
                            # Encode the binary data as text
                            encoded_data = base64.b64encode(serialized_data).decode("utf-8")

                            try:
                                # TODO: change the check model class according to framework used
                                model_checks = TensorflowChecks(model=self.__model, model_name=self.__modelName, progress_bar=None)
                                model_checks.small_training_loop(custom_loss=lossFunction)

                                lossFunction[VALUE] = encoded_data
                                self.__lossFunction = lossFunction
                                self.__remove_error_method()
                            except Exception as e:
                                error_msg = f"custom loss provided give error as {e}\n"
                                self.__print_error(error_msg)
                                return
                        except Exception as e:
                            error_msg = (
                                f"Please provide supported loss functions or custom loss build with tensorflow "
                                f"supported default losses: {lossFunction}\n"
                            )
                            self.__print_error(error_msg)
                else:
                    error_msg = "Invalid input function given for loss function\n"
                    self.__print_error(error_msg)
            else:
                error_msg = "type missing in lossfunction"
                self.__print_error(error_msg)
        else:
            l = ["binary_crossentropy", "categorical_crossentropy", "mse"]
            if TYPE in lossFunction.keys() and VALUE in lossFunction.keys() and lossFunction[TYPE] == STANDARD:
                try:
                    l.index(lossFunction[VALUE].lower())
                    self.__lossFunction = lossFunction
                    self.__remove_error_method()
                except:
                    error_msg = f"Please provide tensorflow supported default loss functions losses: {l}\n"
                    self.__print_error(error_msg)
            else:
                error_msg = "Custom loss function"
                self.__not_supported_parameters(error_msg)

    def __getlayers(self):
        """
        load model and get all layers avaiable in model
        """
        isvalidlayers, model_layers = layer_instance_check(self.__model)
        return model_layers

    def layersFreeze(self, layersFreeze: list):
        """
        Provide name of layers in a list to be frozen before training a model.
        Get layers name in a model provided with the summary shown above.
        example: trainingObject.layersFreeze(['layer_name','layer_name', ...])
        default: None
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            all_layers = self.__getlayers()
            if type(layersFreeze) == list and all(
                isinstance(sub, str) for sub in layersFreeze
            ):
                layers_eligible = True
                for layer in layersFreeze:
                    if layer not in all_layers:
                        layers_eligible = False
                if layers_eligible:
                    layersFreeze = str(layersFreeze)
                    self.__layers_non_trainable = layersFreeze
                    self.__remove_error_method()
                else:
                    error_msg = f"Provide layers only which model contains for layersFreeze : {all_layers}\n"
                    self.__print_error(error_msg)
            else:
                error_msg = "Provide values as list of strings for layersFreeze\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("layersFreeze")

    def terminateOnNaNCallback(self):
        """
        Callback that terminates training when a NaN loss is encountered.
        example: trainingObject.terminateOnNaNCallback()
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            c = [""]
            self.__terminateOnNaNCallback["terminateOnNaN"] = c
        else:
            self.__not_supported_parameters("terminateOnNaNCallback")

    def modelCheckpointCallback(self, monitor: str, save_best_only: bool):
        """
        Callback to save the model weights. parameters: monitor: Quantity to be monitored, save_best_only:  if
        save_best_only=True, it only saves when the model is considered the "best" and the latest best model
        according to the quantity monitored will not be overwritten. example: trainingObject.modelCheckpointCallback(
        'val_loss', True)
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            f = ["accuracy", "loss", "val_loss", "val_accuracy"]
            try:
                f.index(monitor.lower())
                if type(save_best_only) == bool:
                    c = [monitor, save_best_only]
                    self.__modelCheckpointCallback["modelCheckpoint"] = c
                    self.__remove_error_method()
                else:
                    error_msg = "Invalid datatype for arguments given for save_best_only\n"
                    self.__print_error(error_msg)
            except:
                error_msg = f"Please provide supported monitor values: {f}\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("modelCheckpointCallback")

    def earlystopCallback(self, monitor: str, patience: int):
        """
        Stop training when a monitored metric has stopped improving.
        parameters: monitor: Quantity to be monitored,
                                patience: Number of epochs with no improvement after which training will be stopped.
        example: trainingObject.earlystopCallback('loss', 10)


        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            f = ["accuracy", "loss", "val_loss", "val_accuracy"]
            try:
                f.index(monitor.lower())
                if type(patience) == int:
                    c = [monitor, patience]
                    self.__earlystopCallback["earlystopping"] = c
                    self.__remove_error_method()
                else:
                    error_msg = "Invalid datatype for arguments given for patience\n"
                    self.__print_error(error_msg)
            except:
                error_msg = f"Please provide supported monitor values: {f}\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("earlystopCallback")

    def reducelrCallback(
        self, monitor: str, factor: float, patience: int, min_delta: float
    ):
        """
        Reduce learning rate when a metric has stopped improving. parameters: monitor: Quantity to be monitored,
        factor: factor by which the learning rate will be reduced. new_lr = lr * factor. patience: number of epochs
        with no improvement after which learning rate will be reduced. min_delta: threshold for measuring the new
        optimum, to only focus on significant changes.
        example: trainingObject.reducelrCallback('loss', 0.1, 10, 0.0001)
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            f = ["accuracy", "loss", "val_loss", "val_accuracy"]
            try:
                f.index(monitor.lower())
                if (
                    type(factor) == float
                    and type(patience) == int
                    and type(min_delta) == float
                ):
                    c = [monitor, factor, patience, min_delta]
                    self.__reducelrCallback["reducelr"] = c
                    self.__remove_error_method()
                else:
                    error_msg = (
                        "Invalid datatype for arguments given for reducelrCallback\n"
                    )
                    self.__print_error(error_msg)
            except:
                error_msg = f"Please provide supported monitor values: {f}\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("reducelrCallback")

    def __setCallbacks(self):
        """
        List of dictionaries.
        List of tensorflow callbacks for training.
        default: []
        """
        c = []
        if len(self.__reducelrCallback) != 0:
            c.append(self.__reducelrCallback)
        if len(self.__earlystopCallback) != 0:
            c.append(self.__earlystopCallback)
        if len(self.__modelCheckpointCallback) != 0:
            c.append(self.__modelCheckpointCallback)
        if len(self.__terminateOnNaNCallback) != 0:
            c.append(self.__terminateOnNaNCallback)

        self.__callbacks = str(c)

    def samplewise_center(self, samplewise_center: bool):
        """
        Boolean. Set each sample mean to 0.
        example: trainingObject.samplewise_center(True)
        default: False
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(samplewise_center) == bool:
                self.__samplewise_center = samplewise_center
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for samplewise_center\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("samplewise_center")

    def samplewise_std_normalization(self, samplewise_std_normalization: bool):
        """
        Boolean. Divide each input by its std.
        example: trainingObject.samplewise_std_normalization(True)
        default: False
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(samplewise_std_normalization) == bool:
                self.__samplewise_std_normalization = samplewise_std_normalization
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for samplewise_std_normalization\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("samplewise_std_normalization")

    def rotation_range(self, rotation_range: int):
        """
        Int. Degree range for random rotations.
        example: trainingObject.rotation_range(2)
        default: 0
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(rotation_range) == int:
                self.__rotation_range = rotation_range
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for rotation_range\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("rotation_range")

    def width_shift_range(self, width_shift_range):
        """
        Float or int
        float: fraction of total width, if < 1, or pixels if >= 1.
        int: integer number of pixels from interval (-width_shift_range, +width_shift_range)
        With width_shift_range=2 possible values are integers [-1, 0, +1], same as with width_shift_range=[-1, 0, +1],
        while with width_shift_range=1.0 possible values are floats in the interval [-1.0, +1.0).
        example: trainingObject.width_shift_range(0.1)
        default: 0.0
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(width_shift_range) == float or type(width_shift_range) == int:
                self.__width_shift_range = width_shift_range
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for width_shift_range\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("width_shift_range")

    def height_shift_range(self, height_shift_range):
        """
        Float or int
        float: fraction of total height, if < 1, or pixels if >= 1.
        int: integer number of pixels from interval (-height_shift_range, +height_shift_range)
        With height_shift_range=2 possible values are integers [-1, 0, +1], same as with height_shift_range=[-1, 0, +1],
        while with height_shift_range=1.0 possible values are floats in the interval [-1.0, +1.0).
        example: trainingObject.height_shift_range(0.1)
        default: 0.0
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(height_shift_range) == float or type(height_shift_range) == int:
                self.__height_shift_range = height_shift_range
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for height_shift_range\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("height_shift_range")

    def brightness_range(self, brightness_range):
        """
        Tuple or list of two floats. Range for picking a brightness shift value from.
        example: trainingObject.brightness_range((0.1,0.4))
        default: None
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if (type(brightness_range) == tuple and len(brightness_range) == 2) or (
                type(brightness_range) == list and len(brightness_range)
            ) == 2:

                if (
                    type(brightness_range[0]) == float
                    and type(brightness_range[1]) == float
                ):
                    brightness_range = str(brightness_range)
                    self.__brightness_range = brightness_range
                    self.__remove_error_method()
                else:
                    error_msg = "provide float values for brightness_range\n"
                    self.__print_error(error_msg)
            else:
                error_msg = "Please provide tuple of two floats for brightness_range\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("brightness_range")

    def shear_range(self, shear_range: float):
        """
        Float. Shear Intensity (Shear angle in counter-clockwise direction in degrees)
        example: trainingObject.shear_range(0.2)
        default: 0.0
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(shear_range) == float:
                self.__shear_range = shear_range
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for shear_range\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("shear_range")

    def zoom_range(self, zoom_range):
        """
        Float or [lower, upper]. Range for random zoom. If a float, [lower, upper] = [1-zoom_range, 1+zoom_range].
        example: trainingObject.zoom_range(0.2)
        default: 0.0
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(zoom_range) == float or type(zoom_range) == list:
                self.__zoom_range = zoom_range
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for zoom_range\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("zoom_range")

    def channel_shift_range(self, channel_shift_range: float):
        """
        Float. Range for random channel shifts.
        example: trainingObject.channel_shift_range(0.4)
        default: 0.0
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(channel_shift_range) == float:
                self.__channel_shift_range = channel_shift_range
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for channel_shift_range\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("channel_shift_range")

    def fill_mode(self, fill_mode: str):
        """
        One of {"constant", "nearest", "reflect" or "wrap"}. Default is 'nearest'.
        Points outside the boundaries of the input are filled according to the given mode:
        'constant': kkkkkkkk|abcd|kkkkkkkk (cval=k)
        'nearest': aaaaaaaa|abcd|dddddddd
        'reflect': abcddcba|abcd|dcbaabcd
        'wrap': abcdabcd|abcd|abcdabcd
        example: trainingObject.fill_mode("nearest")
        default: "nearest"
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            f = ["constant", "nearest", "reflect", "wrap"]
            try:
                f.index(fill_mode.lower())
                self.__fill_mode = fill_mode.lower()
                self.__remove_error_method()
            except:
                error_msg = f"Please provide supported fill modes: {f}\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("fill_mode")

    def cval(self, cval: float):
        """
        Float or Int. Value used for points outside the boundaries when fill_mode = "constant".
        example: trainingObject.cval(0.3)
        default: 0.0
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(cval) == float:
                self.__cval = cval
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for cval\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("cval")

    def horizontal_flip(self, horizontal_flip: bool):
        """
        Boolean. Randomly flip inputs horizontally.
        example: trainingObject.horizontal_flip(True)
        default: False
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(horizontal_flip) == bool:
                self.__horizontal_flip = horizontal_flip
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for horizontal_flip\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("horizontal_flip")

    def vertical_flip(self, vertical_flip: bool):
        """
        Boolean. Randomly flip inputs vertically.
        example: trainingObject.vertical_flip(True)
        default: False
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(vertical_flip) == bool:
                self.__vertical_flip = vertical_flip
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for vertical_flip\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("vertical_flip")

    def rescale(self, rescale: float):
        """
        rescaling factor. Defaults to None. If None, no rescaling is applied,
        otherwise we multiply the data by the value provided (after applying all other transformations).
        example: trainingObject.rescale(0.003921568627)
        default: None
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(rescale) == float:
                self.__rescale = rescale
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for rescale\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("rescale")

    def shuffle(self, shuffle: bool):
        """
        whether to shuffle the data (default: True)
        example: trainingObject.shuffle(False)
        default: True
        """
        if self.__framework == TENSORFLOW_FRAMEWORK:
            if type(shuffle) == bool:
                self.__shuffle = shuffle
                self.__remove_error_method()
            else:
                error_msg = "Invalid input type given for shuffle\n"
                self.__print_error(error_msg)
        else:
            self.__not_supported_parameters("shuffle")

    # def category(self, category: str):
    #     """
    #     String.
    #     Category of experiment, like classification
    #     example:trainingObject.category('classification')
    #     default_value: 'Classification'
    #
    #     """
    #     if type(category) == str:
    #         self.__category = category
    #     else:
    #         print("Invalid input type given for category\n\n")
    #
    # def modelType(self, modelType: str):
    #     """
    #     String.
    #     Type of model used in the experiment, like VGGNET
    #     example:trainingObject.modelType('VGGNET')
    #
    #
    #     """
    #     if type(modelType) == str:
    #         self.__modelType = modelType
    #     else:
    #         print("Invalid input type given for modelType\n\n")
    #
    # def stepsPerEpoch(self, stepsPerEpoch: int):
    #     """
    #     Integer.
    #     Total number of steps (batches of samples) before declaring
    #     one epoch finished and starting the next epoch.
    #     example: setStepsPerEpoch(5)
    #     default: None
    #     """
    #     if type(stepsPerEpoch) == int and stepsPerEpoch >= 15:
    #         self.__stepsPerEpoch = stepsPerEpoch
    #     else:
    #         print(
    #             "Invalid input type or value less than 15 given for stepsPerEpoch\n\n"
    #         )
    #
    # def initialEpoch(self, initialEpoch: int):
    #     """
    #     Integer. Epoch at which to start training
    #     (useful for resuming a previous training run).
    #     example: setInitialEpoch(2)
    #     default: 0
    #     """
    #     if type(initialEpoch) == int:
    #         self.__initialEpoch = initialEpoch
    #     else:
    #         print("Invalid input type given for initialEpoch\n\n")
    #
    # def validationSteps(self, validationSteps: int):
    #     """
    #     Integer. Total number of steps (batches of samples) to draw before stopping
    #     when performing validation at the end of every epoch.
    #     example: setValidationSteps(20)
    #     default: None
    #     """
    #     if type(validationSteps) == int and validationSteps >= 15:
    #         self.__validationSteps = validationSteps
    #     else:
    #         print(
    #             "Invalid input type or value less than 15 given for validationSteps\n\n"
    #         )
    # def featurewise_center(self, featurewise_center: bool):
    #     """
    #     Boolean. Set input mean to 0 over the dataset, feature-wise.
    #     example: trainingObject.featurewise_center(True)
    #     default: False
    #
    #
    #     """
    #     if type(featurewise_center) == bool:
    #         self.__featurewise_center = featurewise_center
    #     else:
    #         print("Invalid input type given for featurewise_center\n\n")
    #
    # def featurewise_std_normalization(self, featurewise_std_normalization: bool):
    #     """
    #     Boolean. Divide inputs by std of the dataset, feature-wise.
    #     example: trainingObject.featurewise_std_normalization(True)
    #     default: False
    #
    #
    #     """
    #     if type(featurewise_std_normalization) == bool:
    #         self.__featurewise_std_normalization = featurewise_std_normalization
    #     else:
    #         print("Invalid input type given for featurewise_std_normalization\n\n")
    #
    # def zca_whitening(self, zca_whitening: bool):
    #     """
    #     Boolean. Apply ZCA whitening.
    #     example: trainingObject.zca_whitening(True)
    #     default: False
    #
    #
    #     """
    #     if type(zca_whitening) == bool:
    #         self.__zca_whitening = zca_whitening
    #     else:
    #         print("Invalid input type given for zca_whitening\n\n")
    #
    # def data_format(self, data_format: str):
    #     """
    #     String.
    #     Image data format, either "channels_first" or "channels_last".
    #     "channels_last" mode means that the images should have shape
    #     (samples, height, width, channels),
    #     "channels_first" mode means that the images should have shape
    #     (samples, channels, height, width).
    #     example: setDataFormat("channels_first")
    #     default: None
    #     """
    #     d = ["channels_last"]
    #     try:
    #         d.index(data_format.lower())
    #         self.__data_format = data_format.lower()
    #     except:
    #         print(f"Please provide supported fill modes: {d}\n\n")
    #
    # def dtype(self, dtype: str):
    #     """
    #     String.
    #     Dtype to use for the generated arrays.
    #     example: dtype('float32')
    #     default: None
    #     """
    #     d = ["float32", "float64"]
    #     try:
    #         d.index(dtype.lower())
    #         self.__dtype = dtype.lower()
    #     except:
    #         print(f"Please provide supported fill modes: {d}\n\n")
    #
    # def metrics(self,metrics:list):
    # 	'''
    # 	List of strings.
    # 	List of metrics to be evaluated by the model
    # 	during training and testing.
    # 	example: setMetrics(['accuracy','mse'])
    # 	default: ['accuracy']
    # 	'''
    # 	if type(metrics)== list and all(isinstance(sub, str) for sub in metrics):
    # 		metrics = str(metrics)
    # 		self.__metrics = metrics
    # 	else:
    # 		print("Provide values as list of strings")
    #
    # 	def __display_time(self,seconds, granularity=5):
    # 		intervals = (
    # 		('weeks', 604800),  # 60 * 60 * 24 * 7
    # 		('days', 86400),    # 60 * 60 * 24
    # 		('hours', 3600),    # 60 * 60
    # 		('minutes', 60),
    # 		('seconds', 1),)
    # 		result = []
    #
    # 		for name, count in intervals:
    # 			value = seconds // count
    # 			if value:
    # 				seconds -= value * count
    # 				if value == 1:
    # 					name = name.rstrip('s')
    # 				result.append("{} {}".format(value, name))
    # 		return ', '.join(result[:granularity])
    #
    # 	def getEstimate(self):
    #
    # 		header = {'Authorization' : f"Token {self.__token}"}
    # 		re = requests.post(f"{self.__url}flops/",headers= header,data={'datasetId':self.__datasetId,
    # 			'batchSize':self.__batchSize,'noOfEpochs':self.__epochs,'modelName':self.__modelName})
    # # 		print(re.status_code)
    # 		if re.status_code == 200:
    #
    # 			body_unicode = re.content.decode('utf-8')
    # 			content = int(json.loads(body_unicode))
    # 			self.__upperboundTime = content
    # 			cycleTime = content * self.__cycles
    # 			display = self.__display_time(cycleTime)
    #
    # 			print(f"It will take around {display} to complete {self.__cycles} cycles for given training plan.")

    def __checkTrainingPlan(self):
        # call API to compare current training plan for duplication
        header = {"Authorization": f"Token {self.__token}"}
        data = {"parameters": json.dumps(self.__getParameters())}
        # print(data,"\n\n")
        re = requests.post(
            f"{self.__url}trainingplan/{self.__datasetId}/", headers=header, data=data
        )
        # print(re.text)
        if re.status_code == 200:
            body_unicode = re.content.decode("utf-8")
            content = json.loads(body_unicode)
            # print(content)
            if content["status"]:
                userResponse = input(
                    "You already have an experiment with current Training Plan want to proceed?\n\n"
                )
                if userResponse.lower() == "yes" or userResponse.lower() == "y":
                    return True
                elif userResponse.lower() == "no" or userResponse.lower() == "n":
                    return False
                else:
                    text = colored(f"Please Enter Valid Input", "red")
                    print(text, "\n")
            else:
                return True

    def start(self):
        if not self.__eligibility_passed:
            text = colored(f"All fields in training plan are not correct", "red")
            print(text, "\n")
            return
        # set callbacks
        self.__setCallbacks()
        # call checkTrainingPlan for duplication check
        duplication = self.__checkTrainingPlan()
        if duplication:
            # Create Experiment
            header = {"Authorization": f"Token {self.__token}"}
            re = requests.post(
                f"{self.__url}experiments/", headers=header, data=self.__getParameters()
            )
            if re.status_code == 201:
                body_unicode = re.content.decode("utf-8")
                content = json.loads(body_unicode)
                text = colored(
                    f"Experiment created with id:{content['experimentKey']}", "green"
                )
                print(text, "\n")
                explink = (
                    self.__experimenturl
                    + self.__datasetId
                    + "/"
                    + content["experimentKey"]
                    + "/"
                )
                # data = {"experiment_id": content["id"]}
                # Send training request to server
                # r = requests.post(f"{self.__url}training/", headers=header, data=data)
                # body_unicode = r.content.decode("utf-8")
                # content = json.loads(body_unicode)
                print("Training request sent....")
                print(
                    "Updated weights will be available to download once training completed"
                )
                print("\n")
                print(" Link to Experiment is : " + str(explink))
                print(" Training Plan Information for Experiment is :")
                self.getTrainingPlan()
            elif re.status_code == 403:
                body_unicode = re.content.decode("utf-8")
                content = json.loads(body_unicode)
                message = content["message"]
                text = colored(message, "red")
                print(text, "\n")
            elif re.status_code == 400:
                text = colored("Mandatory Fields Missing", "red")
                print(text, "\n")
            else:
                if self._environment != "production":
                    print(re.content, "\n")
                text = colored(
                    "Experiment creation Failed. Please ensure you have entered correct parameters.",
                    "red",
                )
                print(text, "\n")

    def __getParameters(self):
        parameters = {
            "message": "training",
            "datasetId": self.__datasetId,
            "epochs": self.__epochs,
            "cycles": self.__cycles,
            "modelName": self.__modelId,
            "optimizer": self.__optimizer,
            "lossFunction": json.dumps(self.__lossFunction),
            "learningRate": json.dumps(self.__learningRate),
            "batchSize": self.__batchSize,
            "featurewise_center": self.__featurewise_center,
            "samplewise_center": self.__samplewise_center,
            "featurewise_std_normalization": self.__featurewise_std_normalization,
            "samplewise_std_normalization": self.__samplewise_std_normalization,
            "zca_whitening": self.__zca_whitening,
            "rotation_range": self.__rotation_range,
            "width_shift_range": self.__width_shift_range,
            "height_shift_range": self.__height_shift_range,
            "brightness_range": self.__brightness_range,
            "shear_range": self.__shear_range,
            "zoom_range": self.__zoom_range,
            "channel_shift_range": self.__channel_shift_range,
            "fill_mode": self.__fill_mode,
            "cval": self.__cval,
            "horizontal_flip": self.__horizontal_flip,
            "vertical_flip": self.__vertical_flip,
            "rescale": self.__rescale,
            "validation_split": self.__validation_split,
            "shuffle": self.__shuffle,
            "layersFreeze": self.__layers_non_trainable,
            "metrics": self.__metrics,
            "objective": self.__objective,
            "name": self.__name,
            "modelType": self.__modelType,
            "category": self.__category,
            "upperboundTime": self.__upperboundTime,
            "callbacks": self.__callbacks,
            "pre_trained_weights": self.__weights,
            "subdataset": self.__subdataset,
            "images_per_class": self.__images_per_class,
            "image_shape": self.__image_shape,
            "image_type": self.__image_type,
            "framework": self.__framework,
        }

        return parameters

    def getTrainingPlan(self):
        if self.__eligibility_passed:
            print(
                f" \033[1mTraining Description\033[0m\n\n",
                f"experimentName: {self.__name}\n",
                f"modelName: {self.__modelName}\n",
                f"objective: {self.__objective}\n",
                f"\n \033[1mDataset Parameters\033[0m\n\n",
                f"datasetId: {self.__datasetId}\n",
                f"totalDatasetSize: {self.__totalDatasetSize}\n",
                f"allClasses: {self.__class_names}\n\n",
                f"trainingDatasetSize: {self.__trainingDatasetSize}\n",
                f"trainingClasses: {self.__trainingClasses}\n",
                f"imageShape: {self.__image_shape}\n",
                f"imageType: {self.__image_type}\n",
                f"seed: {self.__seed}\n",
                "\n \033[1mTraining Parameters\033[0m\n\n",
                f"epochs: {self.__epochs}\n",
                f"cycles: {self.__cycles}\n",
                f"batchSize: {self.__batchSize}\n",
                f"validation_split: {self.__validation_split}\n",
                "\n \033[1mHyperparameters\033[0m\n\n",
                f"optimizer: {self.__optimizer}\n",
                f"lossFunction: {self.__lossFunction}\n",
                f"learningRate: {self.__learningRate}\n",
                f"layersFreeze: {self.__layers_non_trainable}\n",
                f"earlystopCallback: {self.__earlystopCallback}\n",
                f"reducelrCallback: {self.__reducelrCallback}\n",
                f"modelCheckpointCallback: {self.__modelCheckpointCallback}\n",
                f"terminateOnNaNCallback: {self.__terminateOnNaNCallback}\n",
                "\n \033[1mAugmentation Parameters\033[0m\n\n",
                f"brightness_range: {self.__brightness_range}\n",
                f"channel_shift_range: {self.__channel_shift_range}\n",
                f"cval: {self.__cval}\n",
                f"fill_mode: {self.__fill_mode}\n",
                f"height_shift_range: {self.__height_shift_range}\n",
                f"horizontal_flip: {self.__horizontal_flip}\n",
                f"rescale: {self.__rescale}\n",
                f"rotation_range: {self.__rotation_range}\n",
                f"samplewise_center: {self.__samplewise_center}\n",
                f"samplewise_std_normalization: {self.__samplewise_std_normalization}\n",
                f"shear_range: {self.__shear_range}\n",
                f"shuffle: {self.__shuffle}\n",
                f"vertical_flip: {self.__vertical_flip}\n",
                f"width_shift_range: {self.__width_shift_range}\n",
                f"zoom_range: {self.__zoom_range}\n",
            )
        else:
            print("Training Parameters not set properly")
            return
