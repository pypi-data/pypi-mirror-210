import sys
from silence_tensorflow import silence_tensorflow

silence_tensorflow()
import os
import dis
import re
import shutil
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.nn as nn
import torchvision.datasets as datasets
from inspect import getmembers, isfunction
from .utils import *


# base class for checks on model file
class CheckModel:
    MAX_MODEL_NAME_LENGTH = 64
    message = ""
    model = None
    tmp_file_path = ""
    file_name = "model.py"
    tmp_file = ""
    method_name = ""
    class_name = ""
    input_shape = ""
    output_classes = ""
    framework = ""
    notallowed = ["__MACOSX", "__pycache__"]
    input_shape_patt = re.compile("(^input_shape\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    out_classes_patt = re.compile("(^output_classes\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    main_method_patt = re.compile("(^main_method\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    main_class_patt = re.compile("(^main_class\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    framework_patt = re.compile("(^framework\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")


    def __init__(
        self, progress_bar, model_name=None, model_path=None
    ):  # pragma: no cover
        self.model_name = model_name
        self.model_path = model_path
        self.progress_bar = progress_bar

    def prepare_file(self, temp_file):
        try:
            main_file, remove_lines, filelines = self.get_variables(temp_file)
            if main_file and self.framework == TENSORFLOW_FRAMEWORK:
                self.tmp_file = os.path.join(self.tmp_file_path, self.file_name)
                if self.method_name == "":
                    self.load_model(temp_file)
                    self.add_method(temp_file, remove_lines)
                else:
                    self.edit_file(temp_file, filelines, remove_lines)
            elif self.framework == PYTORCH_FRAMEWORK:
                self.tmp_file = os.path.join(self.tmp_file_path, self.file_name)
                self.edit_file(temp_file, filelines, remove_lines)
            else:
                raise Exception("Framework argument missing in file")
        except Exception as e:
            raise e

    def get_variables(self, temp_file):
        main_file = False
        remove_lines = []
        with open(temp_file, "r") as tmp_fp:
            filedata = tmp_fp.read()
        filelines = filedata.split("\n")
        for linenum, fileline in enumerate(filelines):
            if self.framework_patt.match(fileline):
                self.framework = re.sub(
                    "(framework\s{0,}[=]\s{0,})",
                    "",
                    fileline.replace("'", "").replace('"', ""),
                )
                remove_lines.append(linenum)
                if not main_file:
                    self.file_name = os.path.split(temp_file)[1]
                    main_file = True
            if self.framework == TENSORFLOW_FRAMEWORK:
                if (
                    self.input_shape_patt.match(fileline)
                    or self.out_classes_patt.match(fileline)
                    or self.main_method_patt.match(fileline)
                ):
                    if self.input_shape_patt.match(fileline):
                        self.input_shape = re.sub(
                            "(input_shape\s{0,}[=]\s{0,})",
                            "",
                            fileline.replace("'", "").replace('"', ""),
                        )
                    elif self.out_classes_patt.match(fileline):
                        self.output_classes = re.sub(
                            "(output_classes\s{0,}[=]\s{0,})",
                            "",
                            fileline.replace("'", "").replace('"', ""),
                        )
                    elif self.main_method_patt.match(fileline):
                        self.method_name = re.sub(
                            "(main_method\s{0,}[=]\s{0,})",
                            "",
                            fileline.replace("'", "").replace('"', ""),
                        )
                    remove_lines.append(linenum)
                    if not main_file:
                        self.file_name = os.path.split(temp_file)[1]
                        main_file = True
            elif self.framework == PYTORCH_FRAMEWORK:
                if self.main_class_patt.match(fileline):
                    self.class_name = re.sub(
                        "(main_class\s{0,}[=]\s{0,})",
                        "",
                        fileline.replace("'", "").replace('"', ""),
                    )
                    remove_lines.append(linenum)
                    if not main_file:
                        self.file_name = os.path.split(temp_file)[1]
                        main_file = True
        if self.framework == "":
            print("Framework parameter missing from file")
            return False, [], []
        tmp_fp.close()
        return main_file, remove_lines, filelines

    def replace_vars(self, code):
        if re.search(
            f"[^a-zA-Z_\-0-9]{self.input_shape}[^a-zA-Z_\-0-9]", code
        ) or re.search(f"{self.input_shape}[^a-zA-Z_\-0-9]", code):
            allresultsi = re.findall(
                f"[^a-zA-Z_\-0-9]{self.input_shape}[^a-zA-Z_\-0-9]", code
            )
            if allresultsi == []:
                allresultsi = re.findall(f"{self.input_shape}[^a-zA-Z_\-0-9]", code)
            for found in allresultsi:
                replace_text = found.replace(self.input_shape, "input_shape")
                code = code.replace(found, replace_text)
        if re.search(
            f"[^a-zA-Z_\-0-9]{self.output_classes}[^a-zA-Z_\-0-9]", code
        ) or re.search(f"{self.output_classes}[^a-zA-Z_\-0-9]", code):
            allresultso = re.findall(
                f"[^a-zA-Z_\-0-9]{self.output_classes}[^a-zA-Z_\-0-9]", code
            )
            if allresultso == []:
                allresultso = re.findall(f"{self.output_classes}[^a-zA-Z_\-0-9]", code)
            for found in allresultso:
                replace_text = found.replace(self.output_classes, "output_classes")
                code = code.replace(found, replace_text)
        return code

    def edit_file(self, temp_file, filelines, remove_lines=[]):
        edited_data = []
        with open(temp_file, "w") as tmp_fp:
            for linenum, fileline in enumerate(filelines):
                if linenum in remove_lines:
                    continue
                else:
                    if self.framework == TENSORFLOW_FRAMEWORK:
                        if re.search(f"def {self.method_name}\(.*\)", fileline):
                            fileline = fileline.replace(str(self.method_name), "MyModel")
                        fileline = self.replace_vars(fileline)
                    elif self.framework == PYTORCH_FRAMEWORK:
                        if re.search(f"class {self.class_name}\(.*\)", fileline):
                            fileline = fileline.replace(str(self.class_name), "MyModel")
                    edited_data.append(fileline)
            tmp_fp.writelines("\n".join(edited_data))
        tmp_fp.close()

    def get_imports(self, codelines):
        instructions = dis.get_instructions(codelines)
        instructions = [__ for __ in instructions]
        line = 0
        import_line_num = []
        for inst in instructions:
            if inst.starts_line is not None:
                line = inst.starts_line
            if "IMPORT" in inst.opname:
                if line not in import_line_num:
                    import_line_num.append(line)
        return import_line_num

    def get_parameters(self, codelines, remove_lines=[]):
        import_lines = []
        myMethod = []
        input_shape = ""
        output_classes = ""
        return_obj = ""
        all_members = getmembers(self.model)
        for member_name, member_type in all_members:
            if isinstance(member_type, tf.keras.Sequential):
                return_obj = member_name

        import_line_nums = self.get_imports(codelines)
        codelines = codelines.split("\n")
        for linenum, code in enumerate(codelines):
            if (
                re.search("(.*\s{0,}=\s{0,}[tf.]{0,}[keras.]{0,}Model\(.*\))", code)
                and return_obj == ""
            ):
                return_obj = re.sub(
                    "(\s{0,}=\s{0,}[tf.]{0,}[keras.]{0,}Model\(.*\))", "", code
                )
            code = self.replace_vars(code)
            if code == "":
                continue
            elif (linenum) in remove_lines:
                continue
            elif (linenum + 1) in import_line_nums:
                import_lines.append(code.strip())
            elif re.search("(input_shape\s{0,}[=]\s{0,}\([0-9\, ]{7,}\))", code):
                input_shape = re.sub("(input_shape\s{0,}[=]\s{0,})", "", code)
            elif re.search("(output_classes\s{0,}[=]\s{0,})", code):
                output_classes = re.sub("(output_classes\s{0,}[=]\s{0,})", "", code)
            else:
                code = code.replace("    ", "\t")
                myMethod.append(code)
        return import_lines, input_shape, output_classes, myMethod, return_obj

    def prepare_wrapper_code(self, codelines, remove_lines=[]):
        codeparts = self.get_parameters(codelines, remove_lines)
        updated_code = "\n".join(codeparts[0])
        updated_code = "\n".join(
            [
                updated_code,
                f"\ndef MyModel(input_shape={codeparts[1]}, output_classes={codeparts[2]}):",
            ]
        )
        updated_code = "\n\t".join([updated_code, "\n\t".join(codeparts[3])])
        updated_code = "\n\t".join([updated_code, f"return {codeparts[4]}"])
        return updated_code

    def add_method(self, file="", remove_lines=[]):
        try:
            if file == "":
                file = self.tmp_file
            file_obj = open(f"{file}", "r")
            codelines = file_obj.read()
            updated_code = self.prepare_wrapper_code(codelines, remove_lines)
            file_obj.close()
            file_obj = open(f"{file}", "w")
            file_obj.write(updated_code)
            file_obj.close()
        except:
            self.message = "Model file not provided as per docs"
            raise

    def check_MyModel(self):
        """
        Check if model is MyModel is present in model file
        """
        try:
            getmembers(self.model.MyModel, isfunction)
            self.progress_bar.update(1)
        except Exception:  # pragma: no cover
            self.message = "Please upload file as per docs"
            raise

    def load_model(self, filename, update_progress_bar=False):
        try:
            sys.path.append(self.tmp_file_path)
            self.model = SourceFileLoader(
                f"{filename}", f"{self.tmp_file}"
            ).load_module()
            if self.framework == PYTORCH_FRAMEWORK:
                class_ = getattr(self.model, self.class_name)
                self.model = class_()
            if update_progress_bar:
                self.progress_bar.update(1)
        except Exception as e:
            if self.message == "":
                self.message = f"Error loading the model file, {str(e)}"
            raise

    def extract_multiple_file(self):
        import zipfile

        with open(self.model_path, "rb") as file:
            with zipfile.ZipFile(file, "r") as zip_ref:
                zip_ref.extractall(self.tmp_file_path)
        return False

    def load_model_file(self):
        self.tmp_file_path = os.path.join(
            self.model_path.rsplit("/", 1)[0],
            f"tmpmodel_{self.model_name[: self.MAX_MODEL_NAME_LENGTH]}",
        )
        if not os.path.isdir(self.tmp_file_path):
            os.mkdir(self.tmp_file_path)
        # check if file contains the MyModel function
        try:
            file = self.model_path.rsplit("/", 1)[1]
            if os.path.splitext(str(file))[1] == ".zip":
                self.extract_multiple_file()
            else:
                self.tmp_file = os.path.join(self.tmp_file_path, str(file))
                self.file_name = str(file)
                shutil.copy2(self.model_path, self.tmp_file_path)
            for tmp_f in os.listdir(self.tmp_file_path):
                if not (os.path.isdir(tmp_f) or tmp_f in self.notallowed):
                    self.prepare_file(os.path.join(self.tmp_file_path, tmp_f))
            self.load_model(self.file_name, update_progress_bar=True)
            if self.framework == TENSORFLOW_FRAMEWORK:
                self.check_MyModel()
                self.check_model_arguments()
            else:
                self.progress_bar.update(2)
        except Exception as e:  # pragma: no cover
            if os.path.exists(self.tmp_file_path):
                shutil.rmtree(self.tmp_file_path)
            if self.message == "":
                self.message = f"\nError loading the model file"
            raise

    def check_model_arguments(self):
        """
        Check if MyModel contains:
            - input_shape
            - classes
        """
        try:
            self.model = self.model.MyModel(input_shape=(256, 256, 3), output_classes=1)
            self.progress_bar.update(1)
        except Exception:  # pragma: no cover
            self.message = "\nModel file not provided as per docs: MyModel function receives no arguments"
            raise

    def remove_tmp_file(self, update_progress_bar=False):
        """
        remove temporary model file
        """
        if os.path.exists(self.tmp_file_path):  # pragma: no cover
            shutil.rmtree(self.tmp_file_path)
        if update_progress_bar:
            self.progress_bar.update(1)

    def model_func_checks(self):
        # check if model is eligible
        try:
            self.load_model_file()
            self.message = "all check passed"
            eligible = True
        except Exception as e:  # pragma: no cover
            if self.message == "":
                self.message = f"Model checks failed with error as {e}"
            eligible = False
        if not eligible:
            return eligible, self.message, None, self.progress_bar  # pragma: no cover
        return True, self.message, self.model_name, self.progress_bar

class TensorflowChecks:
    def __init__(self, model, model_name, progress_bar):
        self.message = None
        self.model = model
        self.model_name = model_name
        self.progress_bar = progress_bar

    def progress_bar_update(self):
        if self.progress_bar is not None:
            self.progress_bar.update(1)

    def is_model_supported(self):
        """
        Check if model contains:
            - input_shape
            - classes
        """
        tensorflow_supported_apis = (tf.keras.models.Sequential, tf.keras.Model)
        model = self.model
        supported = isinstance(model, tensorflow_supported_apis)
        if supported:  # pragma: no cover
            # check if it is of model subclassing api
            if not hasattr(model, "input_shape"):
                self.message = "\nModel file not provided as per docs: unsupported API used for Model"  # pragma: no cover
                raise Exception("input shape missing")  # pragma: no cover
        self.progress_bar_update()

    def layer_instance_check(self):
        """
        If model layers are of type keras layers
        """
        for layer in self.model.layers:
            if not isinstance(layer, tf.keras.layers.Layer):
                self.message = "\nLayers in Model are not supported by Tensorflow"  # pragma: no cover
                raise Exception("invalid layer")  # pragma: no cover
        self.progress_bar_update()

    def small_training_loop(self, custom_loss=None):
        try:
            # mock dataset for small training
            classes = 1  # get output classes from model
            training_dataset = mock_dataset(classes)
            if custom_loss:
                # check for custom loss
                loss = custom_loss["value"]

            else:
                loss = tf.keras.losses.CategoricalCrossentropy()
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(),
                loss=loss,
            )
            self.model.fit(training_dataset, epochs=1, verbose=0)
            self.progress_bar_update()
        except Exception as e:  # pragma: no cover
            self.message = (
                "\nModel not support training on image classification dataset."
            )
            raise

    def check_original_model_channels(self):
        """
        check for model channels to be 3
        """
        model_channel = self.model
        if model_channel.input_shape[3] != 3:
            self.message = (
                "\nPlease provide model input shape with 3 channels"  # pragma: no cover
            )
            raise Exception("invalid input shape")  # pragma: no cover
        self.progress_bar_update()

    def is_model_eligible(self):
        try:
            self.is_model_supported()
            self.check_original_model_channels()
            self.layer_instance_check()
            self.small_training_loop()
            self.message = "all check passed"
        except Exception as e:  # pragma: no cover
            if self.message == "":
                self.message = f"Model checks failed with error as {e}"
            return False, self.message
        return True, self.message

    def model_func_checks(self):
        # check if model is eligible
        eligible, message = self.is_model_eligible()
        if not eligible:
            return eligible, message, None, self.progress_bar  # pragma: no cover
        return True, self.message, self.model_name, self.progress_bar


class TorchChecks:
    def __init__(self, model, model_name, progress_bar):
        self.message = None
        self.model = model
        self.model_name = model_name
        self.progress_bar = progress_bar

    def is_model_supported(self):
        """
        Check if model contains:
            - forward function
        """
        model = self.model
        if not hasattr(model, "forward"):
            self.message = "\nModel file not provided as per docs: forward function not found in  Model"
            raise Exception("forward func missing")
        self.progress_bar.update(1)

    def small_training_loop(self, custom_loss=None):
        try:
            # Define the number of fake images and other properties
            num_images = 100
            image_size = 32
            num_channels = 3
            num_classes = 10
            # Create fake image data
            train_dataset = datasets.FakeData(
                size=num_images,
                image_size=(num_channels, image_size, image_size),
                num_classes=num_classes,
                transform=transforms.ToTensor(),
            )

            train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

            # train_loader, classes = mock_torch_data(self.tmp_path)
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)
            for epoch in range(1):  # loop over the dataset multiple times

                running_loss = 0.0
                for i, data in enumerate(train_loader, 0):
                    # get the inputs; data is a list of [inputs, labels]
                    inputs, labels = data
                    labels = torch.tensor(labels, dtype=torch.long)
                    # zero the parameter gradients
                    optimizer.zero_grad()

                    # forward + backward + optimize
                    outputs = self.model(inputs)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

                    # print statistics
                    running_loss += loss.item()
            self.progress_bar.update(1)
        except Exception as e:  # pragma: no cover
            self.message = (
                "\nModel not support training on image classification dataset."
            )
            raise

    def model_func_checks(self):
        # check if model is eligible
        try:
            self.is_model_supported()
            self.progress_bar.update(2)
            self.small_training_loop()
            self.message = "all check passed"
            eligible = True
        except Exception as e:  # pragma: no cover
            if self.message == "":
                self.message = f"Model checks failed with error as {e}"
            eligible = False
        if not eligible:
            return eligible, self.message, None, self.progress_bar  # pragma: no cover
        return eligible, self.message, self.model_name, self.progress_bar
