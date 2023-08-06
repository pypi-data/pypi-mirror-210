s1 = '''
import numpy as np
import pandas as pd

column_names = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO', 'B', 'LSTAT', 'MEDV']
boston = pd.read_csv('./housing.csv', header=None, delimiter=r"\s+", names=column_names)

data = pd.DataFrame(boston.data)

"""### First look at the dataset"""

data.head()

data.columns = boston.feature_names

data['PRICE'] = boston.target

data.head()

print(data.shape)

data.isnull().sum()

"""No null values in the dataset, no missing value treatement needed"""

data.describe()

"""This is sometimes very useful, for example if you look at the CRIM the max is 88.97 and 75% of the value is below 3.677083 and mean is 3.613524 so it means the max values is actually an outlier or there are outliers present in the column"""

data.info()

"""<a id = 'visual'></a>
# Visualisation
"""

import seaborn as sns
sns.distplot(data.PRICE)

"""The distribution seems normal, has not be the data normal we would have perform log transformation or took to square root of the data to make the data normal. Normal distribution is need for the machine learning for better predictiblity of the model"""

sns.boxplot(data.PRICE)

"""<a id = 'corr'></a>
### Checking the correlation of the independent feature with the dependent feature

Correlation is a statistical technique that can show whether and how strongly pairs of variables are related.An intelligent correlation analysis can lead to a greater understanding of your data
"""

correlation = data.corr()
correlation.loc['PRICE']

import matplotlib.pyplot as plt
fig,axes = plt.subplots(figsize=(15,12))
sns.heatmap(correlation,square = True,annot = True)

"""By looking at the correlation plot LSAT is negatively correlated with -0.75 and RM is positively correlated to the price and PTRATIO is correlated negatively with -0.51"""

plt.figure(figsize = (20,5))
features = ['LSTAT','RM','PTRATIO']
for i, col in enumerate(features):
    plt.subplot(1, len(features) , i+1)
    x = data[col]
    y = data.PRICE
    plt.scatter(x, y, marker='o')
    plt.title("Variation in House prices")
    plt.xlabel(col)
    plt.ylabel('"House prices in $1000"')

"""<a id = 'split'></a>
### Splitting the dependent feature and independent feature 
"""

X = data.iloc[:,:-1]
y= data.PRICE

"""<a id = 'valid'></a>
### Splitting the data for Model Validation 
"""

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2, random_state = 4)

"""<a id  = 'NN'></a>
## Neural Networks
"""

from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

"""* We are using Keras for developing the neural network.
* Models in Keras are defined as a sequence of layers
* We create a Sequential model and add layers one at a time with activation function
* Activation function decides, whether a neuron should be activated or not by calculating weighted sum and further adding bias with it. The purpose of the activation function is to introduce non-linearity into the output of a neuron.The activation we are using is relu
* As this is a regression problem, the output layer has no activation function
* Elements of neural network has input layer, hidden layer and output layer
* input layer:- This layer accepts input features. It provides information from the outside world to the network, no computation is performed at this layer, nodes here just pass on the information(features) to the hidden layer.
* Hidden layer:-  Nodes of this layer are not exposed to the outer world, they are the part of the abstraction provided by any neural network. Hidden layer performs all sort of computation on the features entered through the input layer and transfer the result to the output layer.
* Output layer:- This layer bring up the information learned by the network to the outer world.
* Model Compilation:- The compilation is the final step in creating a model. Once the compilation is done, we can move on to training phase.
* Optimizer : - The optimizer we are using is adam. Adam is an optimization algorithm that can be used instead of the classical stochastic gradient descent procedure to update network weights iterative based in training data.
* Loss - mean square error
"""

import keras
from keras.layers import Dense, Activation,Dropout
from keras.models import Sequential

model = Sequential()

model.add(Dense(128,activation  = 'relu',input_dim =13))
model.add(Dense(64,activation  = 'relu'))
model.add(Dense(32,activation  = 'relu'))
model.add(Dense(16,activation  = 'relu'))
model.add(Dense(1))
model.compile(optimizer = 'adam',loss = 'mean_squared_error')

model.fit(X_train, y_train, epochs = 100)

"""<a id = 'eval'></a>
### Evaluation of the model
"""

y_pred = model.predict(X_test)

from sklearn.metrics import r2_score
r2 = r2_score(y_test, y_pred)
print(r2)

# Predicting RMSE the Test set results
from sklearn.metrics import mean_squared_error
rmse = (np.sqrt(mean_squared_error(y_test, y_pred)))
print(rmse)
'''

s2 = '''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sklearn import model_selection
from sklearn.preprocessing import StandardScaler,LabelEncoder, OneHotEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# from sklearn import preprocessing
# from yellowbrick.classifier import ConfusionMatrix

from google.colab import drive
drive.mount('/content/drive')

df = pd.read_csv("/content/drive/MyDrive/College/DL/Assignment2/letter-recognition.data", sep = ",", header=None)

df.head(10)

names = ['letter_Class',
         'x-box',
         'y-box',
         'width',
         'high',
         'onpix',
         'x-bar',
         'y-bar',
         'x2bar',
         'y2bar',
         'xybar',
         'x2ybr',
         'xy2br',
         'x-ege',
         'xegvy',
         'y-ege',
         'yegvx']

df.columns = names

df.head(10)

# X = df.iloc[:, 1 : 17]
# Y = df.select_dtypes(include = [object])
X = df.iloc[:, 1:].values
y = df.iloc[:, 0].values

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

y

onehot_encoder = OneHotEncoder(categories='auto')
y = onehot_encoder.fit_transform(y.reshape(-1, 1)).toarray()

y

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Sequential()
model.add(Dense(64, input_shape=(16,), activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(26, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test))

score = model.evaluate(X_test, y_test)
print(f'Test loss: {score[0]}')
print(f'Test accuracy: {score[1]}')

# print(confusion_matrix(Y_test, predictions))
y_pred = model.predict(X_test)
y_pred = np.argmax(y_pred, axis=1)
y_true = np.argmax(y_test, axis=1)
cm = confusion_matrix(y_true, y_pred)
print(cm)

target_names = label_encoder.inverse_transform(np.arange(26))
print(classification_report(y_true, y_pred, target_names=target_names))

# create a new input with 16 feature values
new_input = [[4,2,5,4,4,8,7,6,6,7,6,6,2,8,7,10]]

# standardize the input using the scaler object
new_input = scaler.transform(new_input)

# make a prediction
prediction = model.predict(new_input)

# print the predicted letter
val=np.argmax(prediction)

print(chr(ord('A')+val))

# create a new input with 16 feature values
new_input = [[5,12,3,7,2,10,5,5,4,13,3,9,2,8,4,10]]

# standardize the input using the scaler object
new_input = scaler.transform(new_input)

# make a prediction
prediction = model.predict(new_input)

# print the predicted letter
val=np.argmax(prediction)

print(chr(ord('A')+val))
'''

s3 = '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sbn
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Dense, Flatten
#from keras.optimizers import Adam
from tensorflow.keras.optimizers import Adam
from keras.callbacks import TensorBoard
from tensorflow.keras.utils import to_categorical

fashion_train_df = pd.read_csv('fashion-mnist_train.csv', sep=',')
fashion_test_df = pd.read_csv('fashion-mnist_test.csv', sep=',')

fashion_train_df.shape   # Shape of the dataset

fashion_train_df.columns   # Name of the columns of the DataSet.

"""So we can see that the 1st column is the label or target value for each row.

Now Lets find out how many distinct lables we have.
"""

print(set(fashion_train_df['label']))

"""So we have 10 different lables. from 0 to 9. 

Now lets find out what is the min and max of values of in the other columns.
"""

print([fashion_train_df.drop(labels='label', axis=1).min(axis=1).min(), 
      fashion_train_df.drop(labels='label', axis=1).max(axis=1).max()])

"""So we have 0 to 255 which is the color values for grayscale. 0 being white and 255 being black.

Now lets check some of the rows in tabular format
"""

fashion_train_df.head()

"""So evry other things of the test dataset are going to be the same as the train dataset except the shape."""

fashion_test_df.shape

"""So here we have 10000 images instead of 60000 as in the train dataset.

Lets check first few rows.
"""

fashion_test_df.head()

training = np.asarray(fashion_train_df, dtype='float32')

height = 10
width = 10

fig, axes = plt.subplots(nrows=width, ncols=height, figsize=(17,17))
axes = axes.ravel()  # this flattens the 15x15 matrix into 225
n_train = len(training)

for i in range(0, height*width):
    index = np.random.randint(0, n_train)
    axes[i].imshow(training[index, 1:].reshape(28,28))
    axes[i].set_title(int(training[index, 0]), fontsize=8)
    axes[i].axis('off')
    
plt.subplots_adjust(hspace=0.5)

training = np.asarray(fashion_train_df, dtype='float32')
X_train = training[:, 1:].reshape([-1,28,28,1])
X_train = X_train/255   
y_train = training[:, 0]

testing = np.asarray(fashion_test_df, dtype='float32')
X_test = testing[:, 1:].reshape([-1,28,28,1])
X_test = X_test/255    
y_test = testing[:, 0]

X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=12345)    # TODO : change the random state to 5

print(X_train.shape, X_val.shape, X_test.shape)
print(y_train.shape, y_val.shape, y_test.shape)

cnn_model = Sequential()
cnn_model.add(Conv2D(filters=64, kernel_size=(3,3), input_shape=(28,28,1), activation='relu'))
cnn_model.add(MaxPooling2D(pool_size = (2,2)))
cnn_model.add(Dropout(rate=0.3))
cnn_model.add(Flatten())
cnn_model.add(Dense(units=32, activation='relu'))
cnn_model.add(Dense(units=10, activation='sigmoid'))

"""**compile the model**"""

cnn_model.compile(optimizer=Adam(lr=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
cnn_model.summary()

"""**Train the model**"""

cnn_model.fit(x=X_train, y=y_train, batch_size=256, epochs=4, validation_data=(X_val, y_val))

eval_result = cnn_model.evaluate(X_test, y_test)
print("Accuracy : {:.3f}".format(eval_result[1]))

y_pred = cnn_model.predict(x=X_test)

print(y_pred[0])

height = 10
width = 10

fig, axes = plt.subplots(nrows=width, ncols=height, figsize=(20,20))
axes = axes.ravel()
for i in range(0, height*width):
    index = np.random.randint(len(y_pred))
    axes[i].imshow(X_test[index].reshape((28,28)))
    #axes[i].set_title("True Class : {:0.0f}\nPrediction : {:d}".format(y_test[index],y_pred[index]))
    axes[i].axis('off')
plt.subplots_adjust(hspace=0.9, wspace=0.5)
'''

s4 = '''

### **Goals of the project -** 
* To understand the basic implemetation of the RNN and LSTM
* To build the RNN layer by layer and understanding the significance of LSTM and the arguments used
* Understanding the importance of Normalization in RNN
* To understand the concept of time steps
* Creating training and testing set from the same data by using the concept of time steps
* Comparing the forecast of the actual and predicted stock prices
* Understanding the significance of RNN in terms of forecasting and its limitations
* Evaluating the RNN by RMSE value taken as a percentage of the orignal value

## **Step 1** : Pre-processing
"""

import numpy as np
import pandas as pd
import warnings  
warnings.filterwarnings('ignore') # to ignore the warnings

training = pd.read_csv("./Google_Stock_Price_Train.csv")
training.head()

"""**Things to consider -**
* For this project sake we will be considering only the "Open" value of the stock as we are building the RNN
* This is done because in RNN, one value at a time `t` is given as an input in a module and that in return gives the next predicted value at time `t+1`
"""

real_stock_price_train = training.iloc[:, 1:2].values     # creates a 2D array having observation and feature

"""**Step - 1.1 :** Feature Scaling"""

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler()
training2 = sc.fit_transform(real_stock_price_train)

"""**Note -**
* We prefer `Normalization` over `Standardization` here coz the sigmoid function takes values betn 0 and 1, 
* Hence it would be better to scale our values betn 0 and 1, thus its better to do use `MinMaxScaler`

**Step - 1.2 :** Checking the shape
"""

training2.shape

"""**Step 1.3 :** Getting the input and output values

**Note -**
* The input values must be the stock prices at time `t` and the output values should be the stock prices at time `t+1`
"""

# hence in the input we take
X_train = training2[0:1257]  # all but last observation as we don't have the output value for it
y_train = training2[1:1258]  # values shifted by 1

"""**Step 1.4 :** Reshaping
* We need to convert this 2D (observation and feature)array into a 3D array because it is a time series problem
* So we need to add a *time step* of 1 because our input is stock price at time `t` and output is stock price at time `t+1` and `(t+1) - t = 1`, hence `1` is the time step
"""

X_train = np.reshape(X_train, (1257, 1, 1))
# (1257, 1, 1) the 2nd argument is no. of features and 3rd argument is the time step

"""## **Step - 2 :** Building the RNN"""

# importing libraries
from keras.models import Sequential  # initialize NN as a sequnce of layers
from keras.layers import Dense  # to add fully connected layers
from keras.layers import LSTM

"""**Step 2.1 :** Initializing the RNN"""

rnn_regressor = Sequential()

"""**Step 2.2 :** Adding input layer and LSTM layer
* In the add method, we use the class corresponding to the layer we want to add
* In this case we are adding the LSTM layer thus replacing the input layer (Dense class) by the LSTM class
"""

rnn_regressor.add(LSTM(units=4, activation='sigmoid', input_shape=(1, 1)))

"""**Arguments used -**
* `units` = no. of memory units
* `input_shape=(1, 1)` means the 1st element is the time step and the 2nd element is no. of features

**Step 2.3 :** Adding the output layer
"""

rnn_regressor.add(Dense(units=1))

"""**Arguments used -**
* `units` = no. of neurons in output layer, here it is a regressor hence 1

**Step 2.4 :** Compiling the RNN
"""

rnn_regressor.compile(optimizer='adam', loss='mean_squared_error')

"""**Step 2.5 :** Fitting the RNN to training set"""

rnn_regressor.fit(X_train, y_train, batch_size=32, epochs=200)

"""**Step 2.6 :** Predicting and Visualizing the training results"""

# predicting the training results
predicted_stock_price_train = rnn_regressor.predict(X_train)
predicted_stock_price_train = sc.inverse_transform(predicted_stock_price_train)

# visualizing the training results
import matplotlib.pyplot as plt
plt.figure(figsize=(20,10))
plt.plot(real_stock_price_train, color = 'red', label='Real Google Stock Price')
plt.plot(predicted_stock_price_train, color = 'blue', label='Predicted Google Stock Price')
plt.title('Google Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Stock Price')
plt.legend()
plt.show()

"""## **Step - 3 :** Making predictions and visualizing results for testing set"""

testing = pd.read_csv("./Google_Stock_Price_Test.csv")
testing.head()

"""**Step 3.1 :** Performing similar pre-prcoessing as performed on training set"""

# taking the column of "open" value of stock price
real_stock_price_test = testing.iloc[:, 1:2].values

# feature Scaling
inputs = sc.transform(real_stock_price_test)

"""**Note -** We do only ".transform" and not "fit.transform" and we use the same scaler 'sc' we used while standardzing the training data because the scaling should be done with respect to the training data and not the testing set because the minimum and maximum of the training and testing sets may vary"""

# reshaping
inputs = np.reshape(inputs, (20, 1, 1))     # only 20 observations in testing set

# predicting the stock price (for the year 2017)
predicted_stock_price_test = rnn_regressor.predict(inputs)     # but these are the scaled values

"""**Step 3.2 :** Performing inverse scaling"""

predicted_stock_price_test = sc.inverse_transform(predicted_stock_price_test)

# visualizing the results for testing
plt.figure(figsize=(20,10))
plt.plot(real_stock_price_test, color = 'red', label='Real Google Stock Price')
plt.plot(predicted_stock_price_test, color = 'blue', label='Predicted Google Stock Price')
plt.title('Google Stock Price Prediction (Test Set)')
plt.xlabel('Time')
plt.ylabel('Stock Price')
plt.legend()
plt.show()

"""## **Conclusions**
* As there is 1 time step between the input and the output, that makes it one time step prediction
* It is seen that the predictions are actually following the real google stock prices
* If we imagine today is the 1st day of 2017 and we want to predict stock price for the next 60 days, we won't get these accurate results as our model was trained for 1 time step prediction
* As amazing as that sounds it would be hard to get such close predictions because in finance, the future variations may not always be dependent on the past, hence its nearly impossible to make long term predictions of stock price

## **Step - 4 :** Evaluating the RNN

### **Interpretation of RMSE value :**
* It is a way of figuring out how much a model disagrees with the actual data
"""

from sklearn.metrics import mean_squared_error
rmse = np.sqrt(mean_squared_error(real_stock_price_test, predicted_stock_price_test))
print('The RMSE value is', rmse)

"""* We need to express this as percentage of the orignal value coz it may tell there is a prediction error of 7, but that error won't mean the same thing whether the orignal stock price was betn 1 and 10 or betn 1000 and 10000
* Generally a good rmse expressed in terms of percentage is around or less than 1%
"""

print('RMSE in terms of % of the orignal value is', round((rmse/real_stock_price_test.mean()*100), 2) , '%')   
# we take the avg because it would be a true representative of the real stock values
'''

s5 = '''
#include <bits/stdc++.h>

using namespace std;

// Function to perform Parallel BFS
void parallelBFS(vector<vector<int>>& adj_list, int source, vector<bool>& visited, vector<int>& bfs_order) {
    queue<int> q;
    q.push(source);

    // Parallel loop over the queue
    #pragma omp parallel
    {
        while (!q.empty()) {
            // Get the next vertex from the queue
            #pragma omp for
            for (int i = 0; i < q.size(); i++) {
                int curr = q.front();
                q.pop();

                // If the current vertex has not been visited, mark it as visited
                // and explore all its neighbors
                if (!visited[curr]) {
                    #pragma omp critical
                    {
                        visited[curr] = true;
                        bfs_order.push_back(curr); // add the visited node to the bfs_order vector
                    }
                    for (int j = 0; j < adj_list[curr].size(); j++) {
                        int neighbor = adj_list[curr][j];

                        // Add the neighbor to the queue if it has not been visited
                        if (!visited[neighbor]) {
                            q.push(neighbor);
                        }
                    }
                }
            }
        }
    }
}

// Function to perform Parallel DFS
void parallelDFS(vector<vector<int>>& adj_list, int source, vector<bool>& visited, vector<int>& dfs_order) {
    stack<int> s;
    s.push(source);

    // Parallel loop over the stack
    #pragma omp parallel
    {
        while (!s.empty()) {
            // Get the next vertex from the stack
            #pragma omp for
            for (int i = 0; i < s.size(); i++) {
                int curr = s.top();
                s.pop();

                // If the current vertex has not been visited, mark it as visited
                // and explore all its neighbors
                if (!visited[curr]) {
                    #pragma omp critical
                    {
                        visited[curr] = true;
                        dfs_order.push_back(curr); // add the visited node to the dfs_order vector
                    }
                    for (int j = 0; j < adj_list[curr].size(); j++) {
                        int neighbor = adj_list[curr][j];

                        // Add the neighbor to the stack if it has not been visited
                        if (!visited[neighbor]) {
                            s.push(neighbor);
                        }
                    }
                }
            }
        }
    }
}

int main() {
    // Construct the adjacency list
    vector<vector<int>> adj_list = {
        {1, 2},
        {0, 3, 4},
        {0, 5, 6},
        {1},
        {1},
        {2},
        {2}
    };

    // Perform Parallel BFS from node 0
    int source = 0;
    int n = adj_list.size();
    vector<bool> visited(n, false);
    vector<int> bfs_order;
    parallelBFS(adj_list, source, visited, bfs_order);

    // Print the visited nodes and the BFS order
    cout << "BFS order: ";
    for (int i = 0; i < bfs_order.size(); i++) {
        cout << bfs_order[i] << " ";
    }
    cout << endl;

    for (int i = 0; i < n; i++) {
        if (visited[i]) {
            cout << "Node " << i << " has been visited" << endl;
        }
    }

    // Perform Parallel DFS from
// reset the visited vector
fill(visited.begin(), visited.end(), false);
vector<int> dfs_order;
parallelDFS(adj_list, source, visited, dfs_order);

// Print the visited nodes and the DFS order
cout << "DFS order: ";
for (int i = 0; i < dfs_order.size(); i++) {
    cout << dfs_order[i] << " ";
}
cout << endl;

for (int i = 0; i < n; i++) {
    if (visited[i]) {
        cout << "Node " << i << " has been visited" << endl;
    }
}

return 0;
}
'''

s6 = '''
#include <iostream>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <omp.h>

using namespace std;
void parallel_bubble_sort_odd_even(int arr[], int n) {
    int phase, i, temp;
    for (phase = 0; phase < n; phase++) {
        if (phase % 2 == 0) {  // Even phase
            #pragma omp parallel for private(i, temp)
            for (i = 2; i < n; i += 2) {
                if (arr[i - 1] > arr[i]) {
                    temp = arr[i - 1];
                    arr[i - 1] = arr[i];
                    arr[i] = temp;
                }
            }
        } else {  // Odd phase
            #pragma omp parallel for private(i, temp)
            for (i = 1; i < n; i += 2) {
                if (arr[i - 1] > arr[i]) {
                    temp = arr[i - 1];
                    arr[i - 1] = arr[i];
                    arr[i] = temp;
                }
            }
        }
    }
}


void bubble_sort(int arr[], int n) {
    int i, j;
    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        }
    }
}

void merge(int arr[], int l, int m, int r) {
    int n1 = m - l + 1;
    int n2 = r - m;

    int L[n1], R[n2];
    int i, j, k;

    for (i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[m + 1 + j];

    i = 0;
    j = 0;
    k = l;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        }
        else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }

    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

void merge_sort(int arr[], int l, int r) {
    if (l < r) {
        int m = l + (r - l) / 2;

        #pragma omp parallel sections
        {
            #pragma omp section
            {
                merge_sort(arr, l, m);
            }

            #pragma omp section
            {
                merge_sort(arr, m + 1, r);
            }
        }

        merge(arr, l, m, r);
    }
}

void print_array(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;
}

int main() {
    srand(time(NULL));

    int n = 10000;
    int arr[n];

    for (int i = 0; i < n; i++) {
        arr[i] = rand() % 10000;
    }

    double start_time, end_time;

    cout << "Sequential Bubble Sort" << endl;
    start_time = omp_get_wtime();
    bubble_sort(arr, n);
    end_time = omp_get_wtime();
    cout << "Time taken: " << end_time - start_time << " seconds" << endl;

    for (int i = 0; i < n; i++) {
        arr[i] = rand() % 10000;
    }

    cout << "Parallel Bubble Sort" << endl;
    start_time = omp_get_wtime();
    #pragma omp parallel
    {
        parallel_bubble_sort_odd_even(arr, n);
    }
    end_time = omp_get_wtime();
    cout << "Time taken: " << end_time - start_time << " seconds" << endl;

    for (int i = 0; i < n; i++) {
       arr[i] = rand() % 10000;
}

cout << "Sequential Merge Sort" << endl;
start_time = omp_get_wtime();
merge_sort(arr, 0, n - 1);
end_time = omp_get_wtime();
cout << "Time taken: " << end_time - start_time << " seconds" << endl;

for (int i = 0; i < n; i++) {
    arr[i] = rand() % 10000;
}

cout << "Parallel Merge Sort" << endl;
start_time = omp_get_wtime();
#pragma omp parallel
{
    #pragma omp single nowait
    {
        merge_sort(arr, 0, n - 1);
    }
}
end_time = omp_get_wtime();
cout << "Time taken: " << end_time - start_time<<setprecision(20) <<" seconds" << endl;

return 0;
}
'''

s7 = '''
#include <bits/stdc++.h>
#include <ctime>
#include <omp.h>

using namespace std;

// Parallel reduction to find min value
template<typename T> T parallel_min(const vector<T>& data)
{
    T min_value = data[0];
    #pragma omp parallel for reduction(min:min_value)
    for (int i = 1; i < data.size(); ++i)
        if (data[i] < min_value)
            min_value = data[i];

    return min_value;
}

// Parallel reduction to find max value
template<typename T> T parallel_max(const vector<T>& data)
{
    T max_value = data[0];
    #pragma omp parallel for reduction(max:max_value)
    for (int i = 1; i < data.size(); ++i)
        if (data[i] > max_value)
            max_value = data[i];
    return max_value;
}

// Parallel reduction to find sum
template<typename T> T parallel_sum(const vector<T>& data)
{
    T sum = 0;
    #pragma omp parallel for reduction(+:sum)
    for (int i = 0; i < data.size(); ++i)
        sum += data[i];

    return sum;
}

// Parallel reduction to find average
template<typename T> double parallel_average(const vector<T>& data)
{
    T sum = parallel_sum(data);
    double average = static_cast<double>(sum) / data.size();
    return average;
}

int main() {
    // Ask user for the size of the vector
    int size;
    cout << "Enter the size of the vector: ";
    cin >> size;

    // Ask user for the values of the vector
    vector<int> data(size);
    cout << "Enter the values of the vector:" << endl;
    for (int i = 0; i < size; ++i) {
        cin >> data[i];
    }

    // Find min, max, sum and average using parallel reduction
    auto start_time = chrono::steady_clock::now();

    int min_value = parallel_min(data);
    int max_value = parallel_max(data);
    int sum = parallel_sum(data);
    double average = parallel_average(data);

    auto end_time = chrono::steady_clock::now();

    // Print results and timing information
    cout << "Min value: " << min_value << endl;
    cout << "Max value: " << max_value << endl;
    cout << "Sum: " << sum << endl;
    cout << "Average: " << average << endl;
    auto duration_ms = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
    cout << "Time taken: " << duration_ms.count() << "ms" << endl;

    return 0;
}
'''

s8 = '''
#include <iostream>
#include <cstdlib>
#include <cstdio>
#include <ctime>

#define TILE_WIDTH 32

__global__ void matrixMult(int *a, int *b, int *c, int n)
{
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < n && col < n) {
        int sum = 0;
        for (int i = 0; i < n; ++i) {
            sum += a[row * n + i] * b[i * n + col];
        }
        c[row * n + col] = sum;
    }
}

int main()
{
    int n;
    n=4;

    // allocate memory for matrices on host
    int *a = new int[n * n];
    int *b = new int[n * n];
    int *c = new int[n * n];

    // initialize matrices with random values
    std::srand(std::time(0));
    for (int i = 0; i < n * n; ++i) {
        a[i] = std::rand() % 10;
        b[i] = std::rand() % 10;
    }

    // allocate memory for matrices on device
    int *dev_a, *dev_b, *dev_c;
    cudaMalloc(&dev_a, n * n * sizeof(int));
    cudaMalloc(&dev_b, n * n * sizeof(int));
    cudaMalloc(&dev_c, n * n * sizeof(int));

    // copy matrices from host to device
    cudaMemcpy(dev_a, a, n * n * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(dev_b, b, n * n * sizeof(int), cudaMemcpyHostToDevice);

    // launch kernel
    dim3 dimGrid((n - 1) / TILE_WIDTH + 1, (n - 1) / TILE_WIDTH + 1, 1);
    dim3 dimBlock(TILE_WIDTH, TILE_WIDTH, 1);
    matrixMult<<<dimGrid, dimBlock>>>(dev_a, dev_b, dev_c, n);

    // copy result matrix from device to host
    cudaMemcpy(c, dev_c, n * n * sizeof(int), cudaMemcpyDeviceToHost);

    // print result matrix
 std::cout << "Result matrix:\n";
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            std::cout << a[i * n + j] << " ";
        }
        std::cout << "\n";
    }
 std::cout << "Result matrix:\n";
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            std::cout << b[i * n + j] << " ";
        }
        std::cout << "\n";
    }
    std::cout << "Result matrix:\n";
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            std::cout << c[i * n + j] << " ";
        }
        std::cout << "\n";
    }

    // free memory on device
    cudaFree(dev_a);
    cudaFree(dev_b);
    cudaFree(dev_c);

    // free memory on host
    delete[] a;
    delete[] b;
    delete[] c;

    return 0;
}
'''

s9 = '''
#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>

using namespace std;

__global__ void vector_add(int *a, int *b, int *c, int n) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    if (i < n) {
        c[i] = a[i] + b[i];
    }
}

int main() {
    const int n = 100;  // Length of vectors
    std::vector<int> a(n), b(n), c(n);

    // Initialize vectors with random values
    std::srand(std::time(nullptr));
    for (int i = 0; i < n; ++i) {
        a[i] = std::rand() % 100;
        b[i] = std::rand() % 100;
    }

    // Allocate memory on device
    int *d_a, *d_b, *d_c;
    cudaMalloc(&d_a, n * sizeof(int));
    cudaMalloc(&d_b, n * sizeof(int));
    cudaMalloc(&d_c, n * sizeof(int));

    // Copy input data from host to device
    cudaMemcpy(d_a, a.data(), n * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, b.data(), n * sizeof(int), cudaMemcpyHostToDevice);

    // Launch kernel
    const int block_size = 256;
    const int num_blocks = (n + block_size - 1) / block_size;
    vector_add<<<num_blocks, block_size>>>(d_a, d_b, d_c, n);

    // Copy output data from device to host
    cudaMemcpy(c.data(), d_c, n * sizeof(int), cudaMemcpyDeviceToHost);

    // Free memory on device
    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);

    // Print results
    std::cout << "Vector a: ";
    for (int i = 0; i < n; ++i) {
        std::cout << a[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Vector b: ";
    for (int i = 0; i < n; ++i) {
        std::cout << b[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Vector c: ";
    for (int i = 0; i < n; ++i) {
        std::cout << c[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
'''

s10 = '''
#include<bits/stdc++.h>
#include<omp.h>
using namespace std;

int N = 5;

double linear_reg(const double x[], const double y[]) {
	double x_mean = 0, y_mean= 0;

	#pragma omp parallel for reduction(+: x_mean, y_mean)
	for(int i = 0; i < N; i++) {
		x_mean += x[i];
		y_mean += y[i];	
	}
	
	double n = N;
	x_mean /= n;
	y_mean /= n;

	double num = 0, den = 0;
	

	#pragma omp parallel for reduction(+: num, den)
	for( int i = 0; i < N; i++) {
		num += (x[i] - x_mean) * (y[i] - y_mean);
		den += (x[i] - x_mean) * (x[i] - x_mean);
	}

	return num / den;
}

int main() {
	double x[N], y[N];
	cout << "Enter co-ordinates(x, y) of " << N <<" points" <<endl;
	for(int i = 0 ; i < N; i ++) {
		cin >> x[i] >> y[i];	
	}

	cout << "Linear Regression line has slope : " << linear_reg(x, y) <<endl;

	return 0;
}
'''

s11 = '''
from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import pandas as pd

data_url = "http://lib.stat.cmu.edu/datasets/boston"
raw_df = pd.read_csv(data_url, sep="\s+", skiprows=22, header=None)
data = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
target = raw_df.values[1::2, 2]

raw_df

# from sklearn.datasets import load_boston
# boston = load_boston()

data = pd.DataFrame(data)

data.head()

data.columns = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO', 'B', 'LSTAT']

data['PRICE'] = target

data.head()

print(data.shape)

data.isnull().sum()

"""No null values in the dataset, no missing value treatement needed"""

data.describe()

"""This is sometimes very useful, for example if you look at the CRIM the max is 88.97 and 75% of the value is below 3.677083 and mean is 3.613524 so it means the max values is actually an outlier or there are outliers present in the column"""

data.info()

"""<a id = 'visual'></a>
# Visualisation
"""

import seaborn as sns
sns.distplot(data.PRICE)

"""The distribution seems normal, has not be the data normal we would have perform log transformation or took to square root of the data to make the data normal. Normal distribution is need for the machine learning for better predictiblity of the model"""

sns.boxplot(data.PRICE)

"""<a id = 'corr'></a>
### Checking the correlation of the independent feature with the dependent feature

Correlation is a statistical technique that can show whether and how strongly pairs of variables are related.An intelligent correlation analysis can lead to a greater understanding of your data
"""

correlation = data.corr()
correlation.loc['PRICE']

import matplotlib.pyplot as plt
fig,axes = plt.subplots(figsize=(15,12))
sns.heatmap(correlation,square = True,annot = True)

"""By looking at the correlation plot LSAT is negatively correlated with -0.75 and RM is positively correlated to the price and PTRATIO is correlated negatively with -0.51"""

plt.figure(figsize = (20,5))
features = ['LSTAT','RM','PTRATIO']
for i, col in enumerate(features):
    plt.subplot(1, len(features) , i+1)
    x = data[col]
    y = data.PRICE
    plt.scatter(x, y, marker='o')
    plt.title("Variation in House prices")
    plt.xlabel(col)
    plt.ylabel('"House prices in $1000"')

"""<a id = 'split'></a>
### Splitting the dependent feature and independent feature 
"""

X = data.iloc[:,:-1]
y= data.PRICE

!pip install mord

import numpy as np
# from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.cross_decomposition import PLSRegression
from mord import OrdinalRidge
from tabulate import tabulate



X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Polynomial Regression
poly_reg = make_pipeline(PolynomialFeatures(degree=2), StandardScaler(), LinearRegression())
poly_reg.fit(X_train, y_train)
y_pred_poly = poly_reg.predict(X_test)
poly_mse = mean_squared_error(y_test, y_pred_poly)
poly_r2 = r2_score(y_test, y_pred_poly)

# Lasso Regression
lasso_reg = make_pipeline(StandardScaler(), Lasso(alpha=0.1))
lasso_reg.fit(X_train, y_train)
y_pred_lasso = lasso_reg.predict(X_test)
lasso_mse = mean_squared_error(y_test, y_pred_lasso)
lasso_r2 = r2_score(y_test, y_pred_lasso)

# Partial Least Squares Regression
pls_reg = make_pipeline(StandardScaler(), PLSRegression(n_components=5))
pls_reg.fit(X_train, y_train)
y_pred_pls = pls_reg.predict(X_test)
pls_mse = mean_squared_error(y_test, y_pred_pls)
pls_r2 = r2_score(y_test, y_pred_pls)

# Ordinal Regression
ordinal_reg = OrdinalRidge(alpha=0.1)
ordinal_reg.fit(X_train, y_train)
y_pred_ordinal = ordinal_reg.predict(X_test)
ordinal_mse = mean_squared_error(y_test, y_pred_ordinal)
ordinal_r2 = r2_score(y_test, y_pred_ordinal)

# Linear Regression
linear_reg = LinearRegression()
linear_reg.fit(X_train, y_train)
y_pred_linear = linear_reg.predict(X_test)
linear_mse = mean_squared_error(y_test, y_pred_linear)
linear_r2 = r2_score(y_test, y_pred_linear)


table = [
    ["Polynomial Regression", poly_mse, poly_r2],
    ["Lasso Regression", lasso_mse, lasso_r2],
    ["Partial Least Squares Regression", pls_mse, pls_r2],
    ["Ordinal Regression", ordinal_mse, ordinal_r2],
    ["Linear Regression", linear_mse, linear_r2]
]


headers = ["Model", "Mean Squared Error", "R2 Score"]
print(tabulate(table, headers, tablefmt="grid"))

"""<a id  = 'NN'></a>
## Neural Networks
"""

from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

import keras
from keras.layers import Dense, Activation,Dropout
from keras.models import Sequential

model = Sequential()

model.add(Dense(128,activation  = 'relu',input_dim =13))
model.add(Dense(64,activation  = 'relu'))
model.add(Dense(32,activation  = 'relu'))
model.add(Dense(16,activation  = 'relu'))
model.add(Dense(1))
model.compile(optimizer = 'adam',loss = 'mean_squared_error')

model.fit(X_train, y_train, epochs = 100)

"""<a id = 'eval'></a>
### Evaluation of the model
"""

y_pred_nn = model.predict(X_test)
nn_mse = mean_squared_error(y_test, y_pred_nn)

from sklearn.metrics import r2_score
nn_r2 = r2_score(y_test, y_pred_nn)
print(nn_r2)

table = [
    ["Polynomial Regression", poly_mse, poly_r2],
    ["Lasso Regression", lasso_mse, lasso_r2],
    ["Partial Least Squares Regression", pls_mse, pls_r2],
    ["Ordinal Regression", ordinal_mse, ordinal_r2],
    ["Linear Regression", linear_mse, linear_r2],
    ["Neural Network Regression Model",nn_mse,nn_r2 ]
]


headers = ["Model", "Mean Squared Error", "R2 Score"]
print(tabulate(table, headers, tablefmt="markdown"))

"""# Result comparison
 Model                            |   Mean Squared Error |   R2 Score |
-------------------------------- | -------------------- | ----------
 Polynomial Regression            |              14.2573 |   0.805583 |
 Lasso Regression                 |              25.6567 |   0.650138 |
 Partial Least Squares Regression |              24.9245 |   0.660122 |
 Ordinal Regression               |              22.8918 |   0.687841 |
 Linear Regression                |              24.2911 |   0.668759 |
 Neural Network Regression Model  |              10.677  |   0.854406 |

"""
'''

s12 = '''
# OCR
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.preprocessing import StandardScaler

# Load the dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/letter-recognition/letter-recognition.data"
df = pd.read_csv(url, header=None)

# Split features and target
X = df.iloc[:, 1:].values.astype(float)
y = df.iloc[:, 0].values.astype(str)

# Encode the target variable
le = LabelEncoder()
y = le.fit_transform(y)

# One-hot encode the target variable
y = to_categorical(y)

df.head()

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(26, activation='softmax')
])

model.summary()

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit(X_train_scaled, y_train, epochs=100, validation_split=0.2)

loss, accuracy = model.evaluate(X_test_scaled, y_test)
print('Test loss:', loss)
print('Test accuracy:', accuracy)
'''

s13 = '''
# IMDB
import pandas as pd
import numpy as np
import re

import string
from string import digits

import numpy as np

import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical


from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import matplotlib.pyplot as plt
import nltk
nltk.download('stopwords')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

df = pd.read_csv("./IMDB Dataset.csv")
df.head()

from sklearn import preprocessing
le =  preprocessing.LabelEncoder()
df["sentiment"] = le.fit_transform(df['sentiment'])

df.head

df.isnull().sum()

X = df["review"]
y = df["sentiment"]

def stringprocess(text):
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " is", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r"\'scuse", " excuse ", text)
    text = re.sub('\W', ' ', text)
    text = re.sub('\s+', ' ', text)
    text = text.strip(' ')
    
    return text

def  textpreprocess(text):
    
    text = map(lambda x: x.lower(), text) 
    text = map(lambda x: re.sub(r"https?://\S+|www\.\S+", "", x), text) 
    text = map(lambda x: re.sub(re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});"),"", x), text) 
    text = map(lambda x: re.sub(r'[^\x00-\x7f]',r' ', x), text) 

    emoji_pattern = re.compile(
            '['
            u'\U0001F600-\U0001F64F'  
            u'\U0001F300-\U0001F5FF'  
            u'\U0001F680-\U0001F6FF'  
            u'\U0001F1E0-\U0001F1FF'  
            u'\U00002702-\U000027B0'
            u'\U000024C2-\U0001F251'
            ']+',
            flags=re.UNICODE)

    text = map(lambda x: emoji_pattern.sub(r'', x), text) 
    text = map(lambda x: x.translate(str.maketrans('', '', string.punctuation)), text) # Remove punctuations
    
    
    remove_digits = str.maketrans('', '', digits)
    text = [i.translate(remove_digits) for i in text]
    text = [w for w in text if not w in stop_words]
    text = ' '.join([lemmatizer.lemmatize(w) for w in text])
    text = text.strip()
    return text

!unzip /usr/share/nltk_data/corpora/wordnet.zip -d /usr/share/nltk_data/corpora/

import nltk
nltk.download('punkt')
import nltk
nltk.download('wordnet')

X = X.apply(lambda x: stringprocess(x))
word_tokens = X.apply(lambda x: word_tokenize(x))

preprocess_text = word_tokens.apply(lambda x: textpreprocess(x))
preprocess_text[0]

training_portion = 0.8
train_size = int(len(preprocess_text) * training_portion)

train_data = preprocess_text[0: train_size]
train_labels = np.array(y[0: train_size])

validation_data = preprocess_text[train_size:]
validation_labels = np.array(y[train_size:])


print(len(train_data))
print(len(train_labels))
print(len(validation_data))
print(len(validation_labels))

vocab_size = 500
oov_tok = '<OOV>'

tokenizer = Tokenizer(num_words = vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(train_data)
word_index = tokenizer.word_index
dict(list(word_index.items())[0:10])

train_sequences = tokenizer.texts_to_sequences(train_data)
print(train_sequences[10])

embedding_dim = 50
max_length = 70
trunc_type = 'post'  
padding_type = 'post'

train_padded = pad_sequences(train_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)
print(len(train_sequences[0]))
print(len(train_padded[0]))

train_padded[0]

validation_sequences = tokenizer.texts_to_sequences(validation_data)
validation_padded = pad_sequences(validation_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)

print(len(validation_sequences))
print(validation_padded.shape)

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

def decode_data(text):
    return ' '.join([reverse_word_index.get(i, '?') for i in text])
print(decode_data(train_padded[10]))
print('---')
print(train_data[10])

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim),
    tf.keras.layers.LSTM(64,activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.summary()

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

num_epochs = 5
history = model.fit(train_padded, train_labels, epochs=num_epochs, validation_data=(validation_padded, validation_labels), verbose=2)

def plot_graphs(history, string):
    plt.plot(history.history[string])
    plt.plot(history.history['val_'+string])
    plt.xlabel("Epochs")
    plt.ylabel(string)
    plt.legend([string, 'val_'+string])
    plt.show()

plot_graphs(history, "accuracy")
plot_graphs(history, "loss")

seed_text = "wonderful little production br br filming technique unassuming old time bbc fashion give comforting sometimes discomforting sense realism entire piece br br actor extremely well chosen michael sheen got polari voice pat truly see seamless editing guided reference williams diary entry well worth watching terrificly written performed piece masterful production one great master comedy life br br realism really come home little thing fantasy guard rather use traditional would ream technique remains solid disappears play knowledge sens particularly scene concerning orton halliwell set particularly flat halliwell mural decorating every surface terribly well done"
token_list = tokenizer.texts_to_sequences([seed_text])[0]
token_list = pad_sequences([token_list], maxlen=max_length-1, padding=padding_type, truncating=trunc_type)
predicted = (model.predict(token_list, verbose=0) > 0.5).astype("int32")

if predicted[0][0] == 0:
    print("Negative")
else:
    print("Positive")

preprocess_text[1]
'''

s14 = '''
#Ass3
from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sbn
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Dense, Flatten
from keras.optimizers import Adam
from keras.callbacks import TensorBoard
from keras.utils import to_categorical

fashion_train_df = pd.read_csv('./fashion-mnist_train.csv', sep=',')
fashion_test_df = pd.read_csv('./fashion-mnist_test.csv', sep=',')

fashion_train_df.shape   # Shape of the dataset

fashion_train_df.columns   # Name of the columns of the DataSet.

print(set(fashion_train_df['label']))

"""So we have 10 different lables. from 0 to 9. 

Now lets find out what is the min and max of values of in the other columns.
"""

print([fashion_train_df.drop(labels='label', axis=1).min(axis=1).min(), 
      fashion_train_df.drop(labels='label', axis=1).max(axis=1).max()])

"""So we have 0 to 255 which is the color values for grayscale. 0 being white and 255 being black.

Now lets check some of the rows in tabular format
"""

fashion_train_df.head()

"""So evry other things of the test dataset are going to be the same as the train dataset except the shape."""

fashion_test_df.shape

"""So here we have 10000 images instead of 60000 as in the train dataset.

Lets check first few rows.
"""

fashion_test_df.head()

training = np.asarray(fashion_train_df, dtype='float32')

height = 10
width = 10

fig, axes = plt.subplots(nrows=width, ncols=height, figsize=(17,17))
axes = axes.ravel()  # this flattens the 15x15 matrix into 225
n_train = len(training)

for i in range(0, height*width):
    index = np.random.randint(0, n_train)
    axes[i].imshow(training[index, 1:].reshape(28,28))
   # axes[i].set_title(int(training[index, 0]), fontsize=8)
    #axes[i].axis('off')
    
#plt.subplots_adjust(hspace=1)

training = np.asarray(fashion_train_df, dtype='float32')
X_train = training[:, 1:].reshape([-1,28,28,1])
X_train = X_train/255   
y_train = training[:, 0]

testing = np.asarray(fashion_test_df, dtype='float32')
X_test = testing[:, 1:].reshape([-1,28,28,1])
X_test = X_test/255    
y_test = testing[:, 0]

X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=5)    # TODO : change the random state to 5

print(X_train.shape, X_val.shape, X_test.shape)
print(y_train.shape, y_val.shape, y_test.shape)

cnn_model = Sequential()
cnn_model.add(Conv2D(filters=64, kernel_size=(3,3), input_shape=(28,28,1), activation='relu'))
cnn_model.add(MaxPooling2D(pool_size = (2,2)))
cnn_model.add(Dropout(rate=0.3))
cnn_model.add(Flatten())
cnn_model.add(Dense(units=32, activation='relu'))
cnn_model.add(Dense(units=10, activation='sigmoid'))

"""**compile the model**"""

cnn_model.compile(optimizer=Adam(lr=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
cnn_model.summary()

"""**Train the model**"""

cnn_model.fit(x=X_train, y=y_train, batch_size=512, epochs=50, validation_data=(X_val, y_val))

eval_result = cnn_model.evaluate(X_test, y_test)
print("Accuracy : {:.3f}".format(eval_result[1]))

y_pred = (cnn_model.predict(X_test) > 0.5).astype("int32")

height = 10
width = 10

fig, axes = plt.subplots(nrows=width, ncols=height, figsize=(20,20))
axes = axes.ravel()
for i in range(0, height*width):
    index = np.random.randint(len(y_pred))
    axes[i].imshow(X_test[index].reshape((28,28)))
    #axes[i].set_title("True Class : {:0.0f}\nPrediction : {:d}".format(y_test[index],y_pred[index]))
    #axes[i].axis('off')
#plt.subplots_adjust(hspace=0.9, wspace=0.5)

"""**Plot Confusin Matrix**"""

# from sklearn.metrics import confusion_matrix
# cm = confusion_matrix(y_test, y_pred)
# plt.figure(figsize=(10,5))
# sbn.heatmap(cm, annot=True)

"""**Classification Report**"""

# num_classes = 10
# class_names = ["class {}".format(i) for i in range(num_classes)]
# cr = classification_report(y_test, y_pred, target_names=class_names)
# print(cr)
'''

s15 = '''
RNN
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import os
for dirname, _, filenames in os.walk("/content/drive/MyDrive/DL assignment/5) Recurrent Neural Network"):
    for filename in filenames:
        print(os.path.join(dirname, filename))

from google.colab import drive
drive.mount('/content/drive')

base = "/content/drive/MyDrive/DL assignment/5) Recurrent Neural Network"

train_data = pd.read_csv(base+"/Stock_Price_Train.csv")

train_data.head()

train = train_data.loc[:,['Open']].values

train

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range = (0,1))
train_scaled = scaler.fit_transform(train)
train_scaled

plt.plot(train_scaled)

X_train = []
y_train = []
timesteps = 50
for i in range(timesteps, 1258):
    X_train.append(train_scaled[i-timesteps:i, 0])
    y_train.append(train_scaled[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)

X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_train

y_train

"""## Create the RNN Model"""

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import SimpleRNN
from keras.layers import Dropout

regressor = Sequential()

regressor.add(SimpleRNN(units = 50,activation='tanh', return_sequences = True, input_shape = (X_train.shape[1], 1)))
regressor.add(Dropout(0.2))

regressor.add(SimpleRNN(units = 50,activation='tanh', return_sequences = True))
regressor.add(Dropout(0.2))

regressor.add(SimpleRNN(units = 50,activation='tanh', return_sequences = True))
regressor.add(Dropout(0.2))

regressor.add(SimpleRNN(units = 50))
regressor.add(Dropout(0.2))

regressor.add(Dense(units = 1))

regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

regressor.fit(X_train, y_train, epochs = 100, batch_size = 32)

test_data = pd.read_csv(base+'/Stock_Price_Test.csv')

test_data.head()

real_stock_price = test_data.loc[:,['Open']].values

real_stock_price

total_data = pd.concat((train_data['Open'],test_data['Open']),axis=0)
inputs = total_data[len(total_data)-len(test_data)-timesteps:].values.reshape(-1,1)
inputs = scaler.transform(inputs) #min max scaler

inputs

X_test = []
for i in range(timesteps, 70):
    X_test.append(inputs[i-timesteps:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
predicted_stock_price = regressor.predict(X_test)
predicted_stock_price = scaler.inverse_transform(predicted_stock_price)

"""## Visualization"""

plt.plot(real_stock_price,color='red',label='Real Google Stock Price')
plt.plot(predicted_stock_price,color='blue',label='Predicted Google Stock Price')
plt.title('Google Stoc Price Prediction')
plt.xlabel('Time')
plt.ylabel('Google Stock Price')
plt.legend()
plt.show()
'''

s16 = '''
#GenderAndAge
import cv2
import math
import argparse

def highlightFace(net, frame, conf_threshold=0.7):
    frameOpencvDnn=frame.copy()
    frameHeight=frameOpencvDnn.shape[0]
    frameWidth=frameOpencvDnn.shape[1]
    blob=cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections=net.forward()
    faceBoxes=[]
    for i in range(detections.shape[2]):
        confidence=detections[0,0,i,2]
        if confidence>conf_threshold:
            x1=int(detections[0,0,i,3]*frameWidth)
            y1=int(detections[0,0,i,4]*frameHeight)
            x2=int(detections[0,0,i,5]*frameWidth)
            y2=int(detections[0,0,i,6]*frameHeight)
            faceBoxes.append([x1,y1,x2,y2])
            cv2.rectangle(frameOpencvDnn, (x1,y1), (x2,y2), (0,255,0), int(round(frameHeight/150)), 8)
    return frameOpencvDnn,faceBoxes


parser=argparse.ArgumentParser()
parser.add_argument('--image')

args=parser.parse_args()

faceProto="opencv_face_detector.pbtxt"
faceModel="opencv_face_detector_uint8.pb"
ageProto="age_deploy.prototxt"
ageModel="age_net.caffemodel"
genderProto="gender_deploy.prototxt"
genderModel="gender_net.caffemodel"

MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList=['Female',"Male"]

faceNet=cv2.dnn.readNet(faceModel,faceProto)
ageNet=cv2.dnn.readNet(ageModel,ageProto)
genderNet=cv2.dnn.readNet(genderModel,genderProto)

video=cv2.VideoCapture(args.image if args.image else 0)
padding=20
while cv2.waitKey(1)<0 :
    hasFrame,frame=video.read()
    if not hasFrame:
        cv2.waitKey()
        break
    
    resultImg,faceBoxes=highlightFace(faceNet,frame)
    if not faceBoxes:
        print("No face detected")

    for faceBox in faceBoxes:
        face=frame[max(0,faceBox[1]-padding):
                   min(faceBox[3]+padding,frame.shape[0]-1),max(0,faceBox[0]-padding)
                   :min(faceBox[2]+padding, frame.shape[1]-1)]

        blob=cv2.dnn.blobFromImage(face, 1.0, (227,227), MODEL_MEAN_VALUES, swapRB=False)
        genderNet.setInput(blob)
        genderPreds=genderNet.forward()
        gender=genderList[genderPreds[0].argmax()]
        print(f'Gender: {gender}')

        ageNet.setInput(blob)
        agePreds=ageNet.forward()
        age=ageList[agePreds[0].argmax()]
        print(f'Age: {age[1:-1]} years')

        cv2.putText(resultImg, f'{gender}, {age}', (faceBox[0], faceBox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2, cv2.LINE_AA)
        cv2.imshow("Detecting age and gender", resultImg)
'''

a = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16]

def plot(number):
    if number < 1 or number > 16:
        return "Laude 1 se 10 tak ke hi codes hai isme"
    return a[number - 1]
