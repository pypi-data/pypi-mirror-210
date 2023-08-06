import os

# String holders for code
activation_function = """
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
class PerceptronPlotter:
    def __init__(self, random_seed=42):
        self.random_seed = random_seed
        self.X_train = None
        self.y_train = None
        self.clf = None

    def generate_data(self):
        np.random.seed(self.random_seed)
        self.X_train, self.y_train = make_classification(n_samples=100, n_features=2, n_informative=2, n_redundant=0, n_clusters_per_class=1)

    def train_classifier(self):
        self.clf = Perceptron().fit(self.X_train, self.y_train)

    def plot_decision_regions(self):
        xx, yy = np.meshgrid(np.arange(self.X_train[:, 0].min() - 1, self.X_train[:, 0].max() + 1, 0.02),
                             np.arange(self.X_train[:, 1].min() - 1, self.X_train[:, 1].max() + 1, 0.02))
        Z = self.clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

        plt.figure(figsize=(8, 6))
        plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.Paired)
        plt.scatter(self.X_train[:, 0], self.X_train[:, 1], c=self.y_train, cmap=plt.cm.Paired)
        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        plt.title('Perceptron Decision Regions')
        plt.show()

    def run(self):
        self.generate_data()
        self.train_classifier()
        self.plot_decision_regions()

plotter = PerceptronPlotter(random_seed=44)
plotter.run()
"""

recognize_5x3_matrix = """ 
class PerceptronNN:
    def __init__(self, nn=10):
        self.nn = nn
        self.clf = MLPClassifier(hidden_layer_sizes=(self.nn,), random_state=42)
        self.train_data = {
            0: [[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]],
            1: [[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
            2: [[1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1]],
            3: [[1, 1, 1], [0, 0, 1], [0, 1, 1], [0, 0, 1], [1, 1, 1]],
            4: [[1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]],
            5: [[1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1]],
            6: [[1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 1], [1, 1, 1]],
            7: [[1, 1, 1], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 0]],
            8: [[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 1, 1]],
            9: [[1, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]]
        }

    def train(self):
        # Create the training set
        training_data = self.train_data
        X_train = []
        y_train = []
        for digit, data in training_data.items():
            X_train.append(np.array(data).flatten())
            y_train.append(digit)

        # Convert training data to NumPy arrays
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        # print(X_train, y_train)

        # Train the MLP classifier
        self.clf.fit(X_train, y_train)

    def recognize(self, test_data):
        # Convert test data to NumPy array
        X_test = np.array(test_data)
        predictions = self.clf.predict(X_test)
        majority_vote = np.argmax(np.bincount(predictions))
        return majority_vote

recognizer = PerceptronNN(16)
recognizer.train()
test_data = np.array([test_data]).flatten()
print(predictions)
"""

ann_forward_backward = """ 
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Initialize weights and biases
        self.W1 = np.random.randn(self.input_size, self.hidden_size)
        self.b1 = np.zeros((1, self.hidden_size))
        self.W2 = np.random.randn(self.hidden_size, self.output_size)
        self.b2 = np.zeros((1, self.output_size))
        
    def forward_propagation(self, X):
        # Forward propagation through the network
        
        # Layer 1 (input to hidden)
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        
        # Layer 2 (hidden to output)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        
        return self.a2
    
    def backward_propagation(self, X, y, learning_rate):
        # Backpropagation to update weights and biases
        
        # Calculate gradients
        self.dz2 = self.a2 - y
        self.dW2 = np.dot(self.a1.T, self.dz2)
        self.db2 = np.sum(self.dz2, axis=0, keepdims=True)
        self.dz1 = np.dot(self.dz2, self.W2.T) * self.sigmoid_derivative(self.a1)
        self.dW1 = np.dot(X.T, self.dz1)
        self.db1 = np.sum(self.dz1, axis=0, keepdims=True)
        
        # Update weights and biases
        self.W2 -= learning_rate * self.dW2
        self.b2 -= learning_rate * self.db2
        self.W1 -= learning_rate * self.dW1
        self.b1 -= learning_rate * self.db1
    
    def train(self, X, y, epochs, learning_rate):
        # Training the neural network
        
        for epoch in range(epochs):
            # Forward propagation
            output = self.forward_propagation(X)
            
            # Backpropagation
            self.backward_propagation(X, y, learning_rate)
            
            # Print loss for every 100 epochs
            if epoch % 100 == 0:
                loss = self.calculate_loss(y, output)
                print(f"Epoch {epoch}: Loss = {loss:.4f}")
    
    def predict(self, X):
        # Make predictions using the trained network
        
        output = self.forward_propagation(X)
        predictions = np.argmax(output, axis=1)
        return predictions
    
    def sigmoid(self, x):
        # Sigmoid activation function
        
        return 1 / (1 + np.exp(-x))
    
    def sigmoid_derivative(self, x):
        # Derivative of the sigmoid function
        
        return x * (1 - x)
    
    def calculate_loss(self, y_true, y_pred):
        # Calculate the mean squared loss
        
        return np.mean(np.square(y_true - y_pred))

nn = NeuralNetwork(input_size=2, hidden_size=4, output_size=1)

# Define the training data (X) and target labels (y)
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

# Train the neural network for 1000 epochs with a learning rate of 0.1
epochs = 1000
learning_rate = 0.1

for epoch in range(epochs):
    # Forward propagation
    output = nn.forward_propagation(X)

    # Backpropagation
    nn.backward_propagation(X, y, learning_rate)

    # Print loss for every 100 epochs
    if epoch % 100 == 0:
        loss = nn.calculate_loss(y, output)
        print(f"Epoch {epoch}: Loss = {loss:.4f}")

# Make predictions on new data
new_data = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
predictions = nn.predict(new_data)

print(predictions)
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

        
(X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()

# Split the data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, 
                                                  test_size=0.2, random_state=42)

# Normalize pixel values
X_train = X_train / 255.0
X_val = X_val / 255.0
X_test = X_test / 255.0

# Create and train the model
cnn = ConvNetImageClassification(num_classes=10)
cnn.run(X_train, y_train, 
        X_val, y_val, 
        X_test, y_test, 
        epochs=20, batch_size=128)
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
class CNNModel:
    def __init__(self, num_classes):
        self.num_classes = num_classes
        self.model = self.build_model()

    def build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(self.num_classes, activation='softmax')
        ])
        return model

    def train(self, X_train, y_train, epochs=10, batch_size=128):
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)

    def evaluate(self, X_test, y_test):
        loss, accuracy = self.model.evaluate(X_test, y_test)
        print("Test Loss:", loss)
        print("Test Accuracy:", accuracy)

    def predict(self, X):
        return self.model.predict(X)

(X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()

X_train = X_train / 255.0
X_test = X_test / 255.0

num_classes = 10
cnn_model = CNNModel(num_classes)
cnn_model.train(X_train, y_train, epochs=10, batch_size=32)
cnn_model.evaluate(X_test, y_test)
predictions = cnn_model.predict(X_test)
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

masterDict = {
    'activation_function' : activation_function,
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