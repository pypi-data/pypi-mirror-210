import colorsys
import os
from collections import Counter
from collections import defaultdict

import numpy as np
import pandas as pd
from PIL import Image
from keras.layers import Dense, Flatten, MaxPooling1D, Conv1D
from keras.layers import Embedding
from keras.models import Sequential
from keras.models import model_from_json
from keras.preprocessing.text import Tokenizer
from keras.utils import np_utils
# from keras.preprocessing.sequence import pad_sequences
from keras.utils import pad_sequences
# from keras.utils.vis_utils import plot_model

MAX_HEIGHT = 600
MAX_WIDTH = 600
pickle_file_name_train = 'storedDFforImagesTrains.pickle'
pickle_file_name_test = 'storedDFforImagesTest.pickle'

base_path_output = "data/"

max_file_limit = 12500
global_nature = ""
wordVocab = defaultdict()


def CNNModel():
    """
    Convolutional Neural network model.
    Input is 256 vector input dimensional array as Embedding layer.
    Additional layers: Conv1d, MaxPooling, Dense, Flatten,Dense.

    Type of class label is categorical crossentropy. Adam Optimizer is selected. Display metric is accuracy.

    :return: CNN model which is a prototype of the classification model specified in this method.
    :rtype: keras.model
    """
    model = Sequential()
    model.add(Embedding(input_dim=256, output_dim=16, input_shape=(4,), batch_size=1))
    model.add(Conv1D(16, kernel_size=2, activation='relu', strides=1))
    model.add(MaxPooling1D(3))
    model.add(Dense(512))
    model.add(Flatten())
    model.add(Dense(3, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['acc'])

    # plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)

    return model


def alter_calc(image):
    """
    EXtract pixel level information from the passed image. Retrieved (r,g,b) pixel values for every pixel of the image and convert them to hsv values,
    for easier seperation of green colored pixels.

    :param image: name of image file
    :type image: string
    :return: List of pixels scanned across the image left top right, top to bottom.
    :rtype: List of tuples
    """
    im = Image.open(os.path.join(os.path.dirname(__file__), image))
    img = im.resize((MAX_HEIGHT, MAX_WIDTH), Image.ANTIALIAS)
    pixels = list(img.getdata())
    pixels_rgb = list(map(np.array, pixels))
    pixels_hsv = list(map(lambda x: x / 255, pixels_rgb))
    pixels_hsv = list(map(lambda x: colorsys.rgb_to_hsv(x[0], x[1], x[2]), pixels_hsv))
    pixels_hsv = list(map(lambda x: (int(x[0] * 360), int(x[1] * 100), int(x[2] * 100)), pixels_hsv))
    return pixels_hsv


def kerasTokenizerUnit(topbestwords):
    """
    Convert the (h,s,v) value of every pixel to a 256 dimensional feature vector that serves as an input to the CNN EMbedding layer.

    :param topbestwords: maximum dimesion of vector, default: 256
    :type integer
    :return: 256 dimensional vector
    :rtype: np.array
    """
    tokenizer = Tokenizer(num_words=topbestwords)
    list_range = " ".join(map(str, list(range(topbestwords))))
    tokenizer.fit_on_texts([list_range])
    return tokenizer


def image_area_calculator(basepath, sample):
    """
    Process the desired image, and extract the pixel level information of every pixel in the image in (h,s,v) format.
    Utlizes alter_calc method to generate (h,s,v) values.

    :param basepath: default path of images
    :type basepath: string
    :param sample: name of image file
    :type sample: string
    :return: returns the vector embedding which will be input to CNN model.
    :rtype: list of lists
    """
    tokenizer_ = kerasTokenizerUnit(256)
    pixels_list = alter_calc(os.path.join(basepath, sample))
    size_ = len(pixels_list)

    string_list = [[" ".join(map(str, i))] for i in pixels_list]
    finalSequence_ = [j for i in string_list for j in tokenizer_.texts_to_sequences(i)]
    finalSequence_ = pad_sequences(finalSequence_, maxlen=4, padding='pre')
    return [finalSequence_, size_]


def processInputTrain():
    """
    Function that extracts all training images from default traininf images foled (test_images/) and converts them into required input vector format for CNN embedding layer.
    """
    # Read from Pickle Object
    print("Reading from Pickle Object Saved.", end="\n")
    basepath = os.path.join(os.path.dirname(__file__), 'test_images/')
    tokenizer_ = kerasTokenizerUnit(255)
    list_train_images = sorted(os.listdir(basepath))
    pixels_list = list()
    class_labels_norm = list()
    for check in list_train_images:
        pix = alter_calc(basepath + check)
        size_ = len(pix)
        pixels_list.extend(pix)
        class_labels_norm.extend(generateClassLabels(size_, check))
    string_list = [[" ".join(map(str, i))] for i in pixels_list]
    # finalSequence_ = []
    finalSequence_ = [j for i in string_list for j in tokenizer_.texts_to_sequences(i)]
    finalSequence_ = pad_sequences(finalSequence_, maxlen=4, padding='pre')
    return [string_list, class_labels_norm, finalSequence_]


def load_model():
    """
    Loads the already available model previously saved on disk.
    """
    json_file = open(os.path.join(os.path.dirname(__file__), 'model.json'), 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(os.path.join(os.path.dirname(__file__), "model.h5"))
    print("Loaded model from disk")
    loaded_model.compile(loss='categorical_crossentropy',
                         optimizer='adam',
                         metrics=['acc'])
    return loaded_model


def saveToDisk(string_list, class_labels_norm, finalSequence_):
    """
    Saves CNN model configuration and input/output pixel/class_label values to disk for later use. Utilizes pickle objects for compressed serialized storage.
    """
    pixel_label_df = []
    finalSequence_ = [i for i in finalSequence_]
    for i, j, k in zip(string_list, class_labels_norm, finalSequence_):
        pixel_label_df.append([i, j, k])
    dataframeToDisk = pd.DataFrame(pixel_label_df)
    print(dataframeToDisk.shape)
    print(dataframeToDisk.head())
    dataframeToDisk.to_pickle('savedPicklePixelLabel.pickle')
    return "Successfully Written Data to Disk (Pickle Object) !"


def readFromDisk():
    """
    Reads the previously sored pixel/class label values saved as pickled objects.
    """
    dataframeFromDisk = pd.read_pickle('savedPicklePixelLabel.pickle')
    print(dataframeFromDisk.head())
    list_ = range(0, dataframeFromDisk.shape[0])
    string_list = [dataframeFromDisk.loc[i, 0] for i in list_]
    class_labels_norm = [dataframeFromDisk.loc[i, 1] for i in list_]
    finalSequence_ = [dataframeFromDisk.loc[i, 2] for i in list_]
    print(len(string_list))
    return string_list, class_labels_norm, finalSequence_


def saveModelToDisk(model):
    """
    Saves the currenly used CNN model configuration to disk.

    :param model: current CNN model
    :type model: keras.CNN model
    """
    # serialize model to JSON
    model_json = model.to_json()
    with open(os.path.join(os.path.dirname(__file__), "model.json"), "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5

    model.save("modelIOS.h5")
    model.save_weights("model.h5")
    print("Saved model to disk")


def generateClassLabels(sample, color):
    """
    Generates class labels for all the pixels extracted from an image.
    Example: if red.png was fetched, all pixels of this image are labelled 'red'. Likewise, for all images in the default training folder (test_images/)
    In our default environment, we have green for all kinds of leaf images, red for all red squared, and any other is irrelevant to pur computations.
    """
    temp = np.zeros(sample)
    if (str(color).__contains__('green')):
        temp[temp == 0.0] = 0
    if (str(color).__contains__('red')):
        temp[temp == 0.0] = 1
    if (str(color).__contains__('envelope') or str(color).__contains__('white')):
        temp[temp == 0.0] = 2
    return temp


def regular(string_list, class_labels_norm, finalSequence_):
    """
    Trains CNN model with the passed embedding vectors of the image.
    CNN model is trained with 600*600 image dimesions, so 360000 data pointes per training image, for all images in default training images directory, for 10 iterations.
    Note: At the time of documenting, the acuarcy of model achieved was 99.5%.

    :param string_list: Dummy variable. Not used.
    :param class_labels_norm: Normalized class labels for the colors.
    :type class_labels_norm: Vector
    :param finalSequence_: Input embedding vectors for image
    :type finalSequence_: List of vectors.
    """
    print('Reading from disk....', end='\n')
    finalSequence_ = pad_sequences(finalSequence_, maxlen=4, padding='pre')
    # finalSequence_ = [np.array(x).reshape((4,1)) for x in finalSequence_]
    # Fit Model on Training Data. Comment out if model is saved to disk.
    print('Defining Model....', end='\n')
    model = CNNModel()
    print('Training Model....', end='\n')

    class_labels_norm_ = np_utils.to_categorical(class_labels_norm)

    model.fit(finalSequence_, class_labels_norm_, epochs=3, validation_split=0.1)
    saveModelToDisk(model)

    score = model.evaluate(finalSequence_, class_labels_norm_, verbose=0)
    print("The model performed with " + str(round(score[1] * 100, 2)) + " Accuracy.")
    print("The model performed with " + str(score[0]) + " Loss.")


def getPixelFromLabel(label):
    """
    Function to get the pizel from the class label. This reverse mapping is use to generate an image file fom available class labels.

    :param label: class label
    :type label: int
    :return: (r,g,b) equivalent of class label color.
    :rtype: tuple
    """
    if label == 0:
        return (0, 255, 0)
    if label == 1:
        return (255, 0, 0)
    else:
        return (255, 255, 153)


def RETRAIN_MODEL_FROM_SCRATCH():
    """
    Retrain the CNN model process entirely from scratch. This is action taken when use uses Tools->Retrain model from GUI menu.
    """
    print('Working on Training Data...', end="\n")
    string_list, class_labels_norm, finalSequence_ = processInputTrain()

    regular(string_list, class_labels_norm, finalSequence_)


def PROCESS_IMAGE(sample_name_list, path_, red_square):
    """
    Accept the image file name from LeafAreaCalculator and prcoess the passed image by cobverting it to model input vector and processing all pixels in the image.
    CNN model ouptput class color labels for every pixel. Simple math is then used to calculate leaf area(green pixels) from green:red ratio of all classified labels.

    :param sample_name_list: image file name to process
    :type sample_name_list:  string
    :param path_: default path to search for image
    :type path_: string
    :return: list of useful parameters: image_file_name, area in cm^2 and ** optional use parameters.
    :rtype: List
    """
    model = load_model()
    list_ = list()
    a = 1

    path_save = os.path.join(os.path.dirname(__file__), 'saved_images/')
    path = path_save

    howManyFiles = len(sample_name_list)
    print(str(howManyFiles) + ' Images Processing..', end='\n')
    print('PROGRESS:', end='\n\n')
    for sample_name in sample_name_list:
        finalSequence_, size = image_area_calculator(path_, sample_name)
        # y_prob = model.predict_classes(finalSequence_, verbose=0)
        y_prob = model.predict(finalSequence_)
        y_prob = np.argmax(y_prob, axis=1)

        # print('ybprob: ', y_prob)
        abc = Counter(y_prob)
        red = abc[1.0] / (size)
        if red == 0:
            continue
        green = abc[0.0] / (size)
        area = (green * red_square) / red
        list_of_pixels = list(map(lambda x: getPixelFromLabel(x), y_prob))

        im2 = Image.new("RGB", (MAX_HEIGHT, MAX_WIDTH))
        im2.putdata(list_of_pixels)
        im2.save(path + sample_name)
        a += 1
        list_ = [sample_name, area, red * size, (red * 100), green * size, [MAX_HEIGHT, MAX_WIDTH]]

    return list_
