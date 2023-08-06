import os

# String holders for code
activation_function = """
import numpy as np
import matplotlib.pyplot as plt

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def relu(x):
    return np.maximum(0, x)

def tanh(x):
    return np.tanh(x)

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / np.sum(e_x)

def leaky_relu(x, alpha=0.1):
    return np.where(x >= 0, x, alpha * x)

def plot_activation_function(activation_fn, name):
    x = np.linspace(-10, 10, 100)
    y = activation_fn(x)

    plt.plot(x, y)
    plt.title(name)
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.grid(True)
    plt.show()

# Plotting sigmoid function
plot_activation_function(sigmoid, 'Sigmoid')    
        
"""

mcculloh_pitt = """
def mcculloch_pitts_neuron(inputs, weights):
    activation = np.sum(inputs * weights)
    if activation >= 0:
        return 1
    else:
        return 0
def andnot(x1, x2):
    weights = np.array([2, -3])  # Weights for AND and NOT operations
    inputs = np.array([x1, x2])
    return mcculloch_pitts_neuron(inputs, weights)
    
# Testing the ANDNOT function
print(andnot(0, 0))  # Output: 0
print(andnot(0, 1))  # Output: 0
print(andnot(1, 0))  # Output: 1
print(andnot(1, 1))  # Output: 0            
"""

ascii_perceptron = """ 
# Define the training data
training_data = [
    (48, 0),  # ASCII representation of '0' is even (0)
    (49, 1),  # ASCII representation of '1' is odd (1)
    (50, 0),  # ASCII representation of '2' is even (0)
    # Add more training data for other digits here
]

# Initialize the weights and bias
weights = np.zeros(8)  # Adjusted to match the length of the binary representation
bias = 0

# Train the perceptron
for _ in range(10):
    for x, label in training_data:
        binary_rep = np.unpackbits(np.array([x], dtype=np.uint8))
        y = np.sum(binary_rep)  # Convert ASCII to binary and sum the bits
        y = 1 if y % 2 == 0 else 0  # Label 1 for even, 0 for odd
        
        # Update weights and bias based on the perceptron learning rule
        activation = np.dot(weights, binary_rep) + bias
        prediction = 1 if activation >= 0 else 0
        weights += (y - prediction) * binary_rep
        bias += (y - prediction)

# Test the perceptron
test_data = [48, 49, 50]  # ASCII representations of '0', '1', and '2'
for x in test_data:
    binary_rep = np.unpackbits(np.array([x], dtype=np.uint8))
    y = np.sum(binary_rep)  # Convert ASCII to binary and sum the bits
    y = 1 if y % 2 == 0 else 0  # Label 1 for even, 0 for odd
    
    activation = np.dot(weights, binary_rep) + bias
    prediction = 1 if activation >= 0 else 0
    
    print(f"Input: {x}, Label: {y}, Prediction: {prediction}")
"""

descision_region_perceptron = """ 
import numpy as np
import matplotlib.pyplot as plt

# Define the training data
X = np.array([
    [2, 4],
    [4, 2],
    [4, 4],
    [3, 1],
    [1, 3],
    [2, 2]
])

Y = np.array([-1, -1, -1, 1, 1, 1])

# Initialize the weights and bias
weights = np.zeros(X.shape[1])
bias = 0

# Train the perceptron
epochs = 10
for _ in range(epochs):
    for x, y in zip(X, Y):
        activation = np.dot(weights, x) + bias
        prediction = np.sign(activation)
        
        if prediction != y:
            weights += y * x
            bias += y
            
# Plot the training data and decision boundary
plt.scatter(X[:, 0], X[:, 1], c=Y, cmap='bwr', edgecolors='k')
x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx1, xx2 = np.meshgrid(np.arange(x1_min, x1_max, 0.02),
                       np.arange(x2_min, x2_max, 0.02))
Z = np.sign(np.dot(np.c_[xx1.ravel(), xx2.ravel()], weights) + bias)
Z = Z.reshape(xx1.shape)
plt.contourf(xx1, xx2, Z, alpha=0.3, cmap='bwr')
plt.xlabel('X1')
plt.ylabel('X2')
plt.title('Perceptron Decision Regions')
plt.show()            
"""

recognize_5x3_matrix = """ 
import tensorflow as tf
import numpy as np

# Define training data
train_data = {
    0: np.array([[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]]),
    1: np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]]),
    2: np.array([[1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1]]),
    3: np.array([[1, 1, 1], [0, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]]),
    4: np.array([[1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]]),
    5: np.array([[1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1]]),
    6: np.array([[1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 1], [1, 1, 1]]),
    7: np.array([[1, 1, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]]),
    8: np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 1, 1]]),
    9: np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]])
}

# Prepare training data
x_train = []
y_train = []
for digit, matrix in train_data.items():
    x_train.append(matrix.flatten())
    y_train.append(digit)

x_train = np.array(x_train)
y_train = np.array(y_train)

# Define the model architecture
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(15,)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(x_train, y_train, epochs=25)

# Test the model
test_data = {
    0: np.array([[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]]),
    1: np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]]),
    2: np.array([[1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1]]),
    3: np.array([[1, 1, 1], [0, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]]),
    4: np.array([[1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]]),
    5: np.array([[1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1]]),
    6: np.array([[1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 1], [1, 1, 1]]),
    7: np.array([[1, 1, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]]),
    8: np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 1, 1]]),
    9: np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]])
}

x_test = []
y_test = []
for digit, matrix in test_data.items():
    x_test.append(matrix.flatten())
    y_test.append(digit)

x_test = np.array(x_test)
y_test = np.array(y_test)

# Evaluate the model
loss, accuracy = model.evaluate(x_test, y_test)
print(f'Test loss: {loss}')
print(f'Test accuracy: {accuracy}')
"""

ann_forward_backward = """ 
import numpy as np

class NeuralNetwork:
    def __init__(self, layers):
        self.weights = [np.random.randn(x, y) for x, y in zip(layers[:-1], layers[1:])]
        self.biases = [np.random.randn(1, y) for y in layers[1:]]

    def forward_propagation(self, a):
        for w, b in zip(self.weights, self.biases):
            a = self.activation(np.dot(a, w) + b)
        return a

    def train(self, X, y, learning_rate, num_iterations):
        for i in range(num_iterations):
            activations = [X]
            for w, b in zip(self.weights, self.biases):
                z = np.dot(activations[-1], w) + b
                activations.append(self.activation(z))
            delta = (activations[-1] - y) * self.activation_derivative(z)
            nabla_b = [delta]
            nabla_w = [np.dot(activations[-2].T, delta)]
            for l in range(2, len(self.weights) + 1):
                delta = np.dot(delta, self.weights[-l + 1].T) * self.activation_derivative(z)
                nabla_b.append(delta)
                nabla_w.append(np.dot(activations[-l - 1].T, delta))
            self.weights = [w - learning_rate * nw for w, nw in zip(self.weights, nabla_w[::-1])]
            self.biases = [b - learning_rate * nb for b, nb in zip(self.biases, nabla_b[::-1])]
            if (i + 1) % 1000 == 0:
                cost = 0.5 * np.mean((self.forward_propagation(X) - y) ** 2)
                print(f"Cost after iteration {i + 1}: {cost}")

    def activation(self, z):
        return 1 / (1 + np.exp(-z))

    def activation_derivative(self, z):
        return self.activation(z) * (1 - self.activation(z))

# XOR dataset
X = np.array([[0, 0],
              [0, 1],
              [1, 0],
              [1, 1]])

y = np.array([[0],
              [1],
              [1],
              [0]])

# Create a neural network with 2 input neurons, 2 hidden neurons, and 1 output neuron
nn = NeuralNetwork([2, 2, 1])

# Train the neural network
nn.train(X, y, learning_rate=0.1, num_iterations=10000)

# Test the neural network
output = nn.forward_propagation(X)
print("\nOutput after training:")
print(output.round())                      
"""

xor_backprop = """ 
# Activation function - sigmoid
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Derivative of sigmoid function
def sigmoid_derivative(x):
    return x * (1 - x)

# Input dataset
X = np.array([[0, 0],
              [0, 1],
              [1, 0],
              [1, 1]])

# Output dataset
y = np.array([[0],
              [1],
              [1],
              [0]])

# Seed the random number generator
np.random.seed(1)

# Initialize weights randomly with mean 0
synaptic_weights_0 = 2 * np.random.random((2, 3)) - 1
synaptic_weights_1 = 2 * np.random.random((3, 1)) - 1


# Training loop
for iteration in range(10000):

    # Forward propagation
    layer_0 = X
    layer_1 = sigmoid(np.dot(layer_0, synaptic_weights_0))
    layer_2 = sigmoid(np.dot(layer_1, synaptic_weights_1))

    # Calculate the error
    layer_2_error = y - layer_2

    if iteration % 1000 == 0:
        print("Error after", iteration, "iterations:", np.mean(np.abs(layer_2_error)))

    # Back propagation
    layer_2_delta = layer_2_error * sigmoid_derivative(layer_2)
    layer_1_error = layer_2_delta.dot(synaptic_weights_1.T)
    layer_1_delta = layer_1_error * sigmoid_derivative(layer_1)

    # Update weights
    synaptic_weights_1 += layer_1.T.dot(layer_2_delta)
    synaptic_weights_0 += layer_0.T.dot(layer_1_delta) 

# Test the network
print("\nOutput after training:")
layer_0 = X
layer_1 = sigmoid(np.dot(layer_0, synaptic_weights_0))
layer_2 = sigmoid(np.dot(layer_1, synaptic_weights_1))
print(layer_2)                     
"""

art_network = """ 
def art1(input_pattern, vigilance):
    # Parameters
    n = len(input_pattern)
    m = 2 * n

    # Initialize weights
    weights = np.ones((m, n))

    while True:
        # Calculate activation
        activation = np.dot(weights, input_pattern)

        # Find the winning category
        winning_category = np.argmax(activation)

        # Check if the winning category meets the vigilance criterion
        match = np.dot(weights[winning_category], input_pattern) / np.sum(input_pattern)

        if match >= vigilance:
            return winning_category

        # Otherwise, create a new category
        new_category = np.random.randint(m)
        weights[new_category] = input_pattern

# Input patterns
patterns = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
]

# Test pattern
test_pattern = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Vigilance parameter
vigilance = 0.9

# Train and test the network
category = art1(test_pattern, vigilance)

# Print the result
print("Test pattern:", test_pattern)
print("Category:", category)        
"""

hopfield_network = """ 
def train_hopfield_network(patterns):
    num_patterns = len(patterns)
    num_neurons = len(patterns[0])
    
    weights = np.zeros((num_neurons, num_neurons))
    
    for pattern in patterns:
        pattern = pattern.reshape((num_neurons, 1))
        weights += pattern @ pattern.T
        
    np.fill_diagonal(weights, 0)
    
    return weights

def recall_hopfield_network(weights, initial_state, num_iterations=10):
    num_neurons = len(weights)
    state = initial_state.copy()
    
    for _ in range(num_iterations):
        for i in range(num_neurons):
            activation = weights[i] @ state
            state[i] = np.sign(activation)
    
    return state

# Define the 4 vectors to be stored
patterns = [
    np.array([1, 1, 1, -1]),
    np.array([-1, -1, -1, 1]),
    np.array([1, -1, 1, -1]),
    np.array([-1, 1, -1, 1])
]

# Train the Hopfield Network
weights = train_hopfield_network(patterns)

# Test the Hopfield Network
test_vector = np.array([1, 1, 1, 1])
retrieved_pattern = recall_hopfield_network(weights, test_vector)

print("Retrieved Pattern:")
print(retrieved_pattern)      
"""

cnn_object_detection = """ 
import torchvision
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import warnings
warnings.filterwarnings('ignore')
from torchvision import transforms as T

model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

def get_prediction(img_path, threshold):
  img = Image.open(img_path) # Load the image
  transform = T.Compose([T.ToTensor()]) # Defing PyTorch Transform
  img = transform(img) # Apply the transform to the image
  pred = model([img]) # Pass the image to the model
  pred_class = [COCO_INSTANCE_CATEGORY_NAMES[i] for i in list(pred[0]['labels'].numpy())] # Get the Prediction Score
  pred_boxes = [[(i[0], i[1]), (i[2], i[3])] for i in list(pred[0]['boxes'].detach().numpy())] # Bounding boxes
  pred_score = list(pred[0]['scores'].detach().numpy())
  pred_t = [pred_score.index(x) for x in pred_score if x > threshold][-1] # Get list of index with score greater than threshold.
  pred_boxes = pred_boxes[:pred_t+1]
  pred_class = pred_class[:pred_t+1]
  return pred_boxes, pred_class


def object_detection_api(img_path, threshold=0.5, rect_th=3, text_size=3, text_th=3):
    boxes, pred_cls = get_prediction(img_path, threshold)
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for i in range(len(boxes)):
        pt1 = (int(boxes[i][0][0]), int(boxes[i][0][1]))
        pt2 = (int(boxes[i][1][0]), int(boxes[i][1][1]))
        cv2.rectangle(img, pt1, pt2, color=(0, 255, 0), thickness=rect_th)
        cv2.putText(img, pred_cls[i], pt1, cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 255, 0), thickness=text_th)
    plt.figure(figsize=(20, 30))
    plt.imshow(img)
    plt.xticks([])
    plt.yticks([])
    plt.show()

import urllib.request

url = 'https://images.fastcompany.net/image/upload/v1526438285/fcweb/p-2-01-05-For-leading-Americans-beyond-thoughts-and-prayers-FA0618PARK001_s5koi2.jpg'
filename = 'person.jpg'

urllib.request.urlretrieve(url, filename)

object_detection_api('person.jpg', threshold=0.8)
plt.savefig('result.png')              
"""

cnn_image_classification = """ 
class CNNObjectDetection:
    def __init__(self, num_classes=10, filters=32, kernel=(3, 3), dense_nodes=64):
        self.filters = filters
        self.kernel = kernel
        self.dense_nodes = dense_nodes
        self.num_classes = num_classes
        self.model = self.create_model()

    def create_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(self.filters, self.kernel, activation='relu', input_shape=(32, 32, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(self.dense_nodes, activation='relu'),
            tf.keras.layers.Dense(self.num_classes, activation='softmax')
        ])
        return model

    def train_model(self, X_train, y_train, X_val, y_val, epochs, batch_size):
        # Compile the model
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        history = self.model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, batch_size=batch_size)

        return history

    def plot_accuracy(self, history):
        # Plot accuracy graph
        plt.plot(history.history['accuracy'])
        plt.plot(history.history['val_accuracy'])
        plt.title('Model Accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='upper left')
        plt.show()

    def plot_loss(self, history):
        # Plot loss graph
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title('Model Loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='upper right')
        plt.show()

    def evaluate_model(self, X_test, y_test):
        loss, accuracy = self.model.evaluate(X_test, y_test)
        print("Test Loss:", loss)
        print("Test Accuracy:", accuracy)

    def run(self, X_train, y_train, X_val, y_val, X_test, y_test, epochs=10, batch_size=32, plot=False):
        history = self.train_model(X_train, y_train, X_val, y_val, epochs, batch_size)

        if plot: self.plot_accuracy(history)
        if plot: self.plot_loss(history)

        self.evaluate_model(X_test, y_test)

# Load and preprocess the data
(X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()

# Split the data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, 
                                                  test_size=0.2, random_state=42)

# Normalize pixel values
X_train = X_train / 255.0
X_val = X_val / 255.0
X_test = X_test / 255.0

# Create and train the model
cnn = ConvNetImageClassification(num_classes=10, filters=32, kernel=(3, 3), dense_nodes=64)
cnn.run(X_train, y_train, 
        X_val, y_val, 
        X_test, y_test, 
        epochs=20, batch_size=128,
        plot=True)
"""

cnn_tf_implementation = """
import tensorflow as tf

# Define the CNN model
def cnn_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    return model

# Load the MNIST dataset
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

# Preprocess the data
x_train = x_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
x_test = x_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0
y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
y_test = tf.keras.utils.to_categorical(y_test, num_classes=10)

# Create an instance of the model
model = cnn_model()

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(x_train, y_train, batch_size=32, epochs=5, validation_data=(x_test, y_test))

# Evaluate the model
loss, accuracy = model.evaluate(x_test, y_test)
print(f'Test loss: {loss:.4f}')
print(f'Test accuracy: {accuracy:.4f}')    
"""

mnist_detection = """ 
import tensorflow as tf
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Load MNIST dataset from scikit-learn
mnist = fetch_openml('mnist_784', version=1)
X, y = mnist["data"], mnist["target"]

# Convert target values to integers
y = y.astype(int)

# Preprocess the data
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=14)

# Define the model architecture
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=5, batch_size=32, validation_data=(X_test, y_test))

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test, y_test)
print("Test Loss:", test_loss)
print("Test Accuracy:", test_acc)
"""
bam_net = """
import numpy as np

def create_bam():
    bam = np.zeros((4, 4))
    return bam

def train_bam(bam, X, Y):
    for i in range(len(X)):
        x = np.reshape(X[i], (1, -1))
        y = np.reshape(Y[i], (1, -1))
        bam += np.dot(x.T, y)
    
def recall_bam(bam, X):
    Y = []
    for i in range(len(X)):
        x = np.reshape(X[i], (1, -1))
        y = np.dot(x, bam)
        y[y >= 0] = 1
        y[y < 0] = -1
        Y.append(y)
    return np.array(Y)
    
# Example usage
X = np.array([[1, 1, -1, -1], [-1, -1, 1, 1]])  # Input vectors
Y = np.array([[1, -1, 1, -1], [-1, 1, -1, 1]])  # Output vectors

bam = create_bam()
train_bam(bam, X, Y)

# Test recall
test_X = np.array([[1, 1, -1, -1]])
output = recall_bam(bam, test_X)
print("Output:", output)    
"""
logistic_reg = """
import tensorflow as tf
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load the Iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split the dataset into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features using StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Define the logistic regression model
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(3, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=1)

# Evaluate the model on the test set
loss, accuracy = model.evaluate(X_test, y_test)
print("Test Loss:", loss)
print("Test Accuracy:", accuracy)
"""
masterDict = {
    'activation_function' : activation_function,
    'bam_net' : bam_net,
    'logistic_reg' : logistic_reg,
    'mcculloh_pitt': mcculloh_pitt,
    'ascii_perceptron': ascii_perceptron,
    'descision_region_perceptron': descision_region_perceptron,
    'recognize_5x3_matrix': recognize_5x3_matrix,
    'ann_forward_backward': ann_forward_backward,
    'xor_backprop': xor_backprop,
    'art_network': art_network,
    'hopfield_network':hopfield_network,
    'cnn_object_detection': cnn_object_detection,
    'cnn_image_classification': cnn_image_classification,
    'cnn_tf_implementation': cnn_tf_implementation,
    'mnist_detection': mnist_detection  
}

class Writer:
    def __init__(self, filename):
        self.filename = os.path.join(os.getcwd(), filename)
        self.masterDict = masterDict
        self.questions = list(masterDict.keys())

    def getCode(self, input_string):
        input_string = self.masterDict[input_string]
        with open(self.filename, 'w') as file:
            file.write(input_string)
        print(f'##############################################')

if __name__ == '__main__':
    write = Writer('output.txt')
    # print(write.questions)
    write.getCode('descision_region_perceptron')