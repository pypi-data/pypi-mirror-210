from collections import Counter
  
def count_in_list(l, word):
  c = Counter(l)
  return c[word]

def h1():
  s="\'import pandas as pd\n\'+\
\'import numpy as np\n\'+\
\'df = pd.read_csv(\'HousingData.csv\')\n\'+\
\'df = df.fillna(df.mean())\n\'+\
\'from sklearn.model_selection import train_test_split\n\'+\
\'\n\'+\
\'X = df.loc[:, df.columns != \'MEDV\']\n\'+\
\'y = df.loc[:, df.columns == \'MEDV\']\n\'+\
\'X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=123)\n\'+\
\'from sklearn.preprocessing import MinMaxScaler\n\'+\
\'mns = MinMaxScaler()\n\'+\
\'mns.fit(X_train)\n\'+\
\'X_train = mns.transform(X_train)\n\'+\
\'X_test = mns.transform(X_test)\n\'+\
\'pip install mord\n\'+\
\'import numpy as np\n\'+\
\'# from sklearn.datasets import load_boston\n\'+\
\'from sklearn.model_selection import train_test_split\n\'+\
\'from sklearn.linear_model import LinearRegression, Lasso\n\'+\
\'from sklearn.preprocessing import PolynomialFeatures, StandardScaler\n\'+\
\'from sklearn.pipeline import make_pipeline\n\'+\
\'from sklearn.metrics import mean_squared_error, r2_score\n\'+\
\'from sklearn.cross_decomposition import PLSRegression\n\'+\
\'from mord import OrdinalRidge\n\'+\
\'from tabulate import tabulate\n\'+\
\'\n\'+\
\'\n\'+\
\'\n\'+\
\'X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\'+\
\'\n\'+\
\'# Polynomial Regression\n\'+\
\'poly_reg = make_pipeline(PolynomialFeatures(degree=2), StandardScaler(), LinearRegression())\n\'+\
\'poly_reg.fit(X_train, y_train)\n\'+\
\'y_pred_poly = poly_reg.predict(X_test)\n\'+\
\'poly_mse = mean_squared_error(y_test, y_pred_poly)\n\'+\
\'poly_r2 = r2_score(y_test, y_pred_poly)\n\'+\
\'\n\'+\
\'# Lasso Regression\n\'+\
\'lasso_reg = make_pipeline(StandardScaler(), Lasso(alpha=0.1))\n\'+\
\'lasso_reg.fit(X_train, y_train)\n\'+\
\'y_pred_lasso = lasso_reg.predict(X_test)\n\'+\
\'lasso_mse = mean_squared_error(y_test, y_pred_lasso)\n\'+\
\'lasso_r2 = r2_score(y_test, y_pred_lasso)\n\'+\
\'\n\'+\
\'# Partial Least Squares Regression\n\'+\
\'pls_reg = make_pipeline(StandardScaler(), PLSRegression(n_components=5))\n\'+\
\'pls_reg.fit(X_train, y_train)\n\'+\
\'y_pred_pls = pls_reg.predict(X_test)\n\'+\
\'pls_mse = mean_squared_error(y_test, y_pred_pls)\n\'+\
\'pls_r2 = r2_score(y_test, y_pred_pls)\n\'+\
\'\n\'+\
\'# Ordinal Regression\n\'+\
\'ordinal_reg = OrdinalRidge(alpha=0.1)\n\'+\
\'ordinal_reg.fit(X_train, y_train)\n\'+\
\'y_pred_ordinal = ordinal_reg.predict(X_test)\n\'+\
\'ordinal_mse = mean_squared_error(y_test, y_pred_ordinal)\n\'+\
\'ordinal_r2 = r2_score(y_test, y_pred_ordinal)\n\'+\
\'\n\'+\
\'# Linear Regression\n\'+\
\'linear_reg = LinearRegression()\n\'+\
\'linear_reg.fit(X_train, y_train)\n\'+\
\'y_pred_linear = linear_reg.predict(X_test)\n\'+\
\'linear_mse = mean_squared_error(y_test, y_pred_linear)\n\'+\
\'linear_r2 = r2_score(y_test, y_pred_linear)\n\'+\
\'\n\'+\
\'\n\'+\
\'table = [\n\'+\
\'    [\"Polynomial Regression\", poly_mse, poly_r2],\n\'+\
\'    [\"Lasso Regression\", lasso_mse, lasso_r2],\n\'+\
\'    [\"Partial Least Squares Regression\", pls_mse, pls_r2],\n\'+\
\'    [\"Ordinal Regression\", ordinal_mse, ordinal_r2],\n\'+\
\'    [\"Linear Regression\", linear_mse, linear_r2]\n\'+\
\']\n\'+\
\'\n\'+\
\'\n\'+\
\'headers = [\"Model\", \"Mean Squared Error\", \"R2 Score\"]\n\'+\
\'print(tabulate(table, headers, tablefmt=\"grid\"))\n\'+\
\'\n\'+\
\'from keras.models import Sequential\n\'+\
\'from keras.layers import Dense\n\'+\
\'model = Sequential()\n\'+\
\'\n\'+\
\'model.add(Dense(128, input_shape=(13, ), activation=\'relu\', name=\'dense_1\'))\n\'+\
\'model.add(Dense(64,activation = \'relu\',name = \'dense_2\'))\n\'+\
\'model.add(Dense(1,activation = \'linear\',name = \'dense_output\'))\n\'+\
\'\n\'+\
\'model.compile(optimizer = \'adam\',loss = \'mse\',metrics = [\'mae\'])\n\'+\
\'model.summary()\n\'+\
\'history = model.fit(X_train,y_train,epochs = 100,validation_split = 0.05,verbose = 1)\n\'+\
\'mse_nn, mae_nn = model.evaluate(X_test, y_test)\n\'+\
\'\n\'+\
\'print(\'Mean squared error on test data: \', mse_nn)\n\'+\
\'print(\'Mean absolute error on test data: \', mae_nn)\n\'+\
\'import matplotlib.pyplot as plt\n\'+\
\'lossv = []\n\'+\
\'\n\'+\
\'for epoch in range(100):\n\'+\
\'    history =  model.fit(X_train,y_train,epochs = 10,validation_split = 0.05,verbose = 1)\n\'+\
\'    lossv += history.history[\'loss\']\n\'+\
\'plt.plot(lossv)\';+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h1()
def  h2():
  s="import numpy as np\
from keras import models, layers, optimizers\
from keras.preprocessing.text import Tokenizer\
from keras.utils import pad_sequences\
from tensorflow.keras.utils import to_categorical\
import pandas as pd\
from sklearn import preprocessing\
# Load the data\
df=pd.read_csv(\"IMDB Dataset.csv\")\
train_df = df.sample(frac=0.8, random_state=25)\
test_df = df.drop(train_df.index)\
print(train_df)\
print(test_df)\
# Tokenize the text data\
tokenizer = Tokenizer(num_words=10000)\
tokenizer.fit_on_texts(train_df[\'review\'].tolist())\
# Convert the text data to sequences of integers\
train_sequences = tokenizer.texts_to_sequences(train_df[\'review\'].tolist())\
test_sequences = tokenizer.texts_to_sequences(test_df[\'review\'].tolist())\
# Pad the sequences to a fixed length\
max_length = 100\
train_data = pad_sequences(train_sequences, maxlen=max_length)\
test_data = pad_sequences(test_sequences, maxlen=max_length)\
# Convert the labels to categorical\
label_encoder = preprocessing.LabelEncoder()\
train_labels= label_encoder.fit_transform(train_df[\'sentiment\'])\
#train_labels = to_categorical(train_df[\'sentiment\'])\
model = models.Sequential()\
model.add(layers.Embedding(10000, 64, input_length=max_length))\
model.add(layers.Flatten())\
model.add(layers.Dense(32, activation=\'relu\'))\
model.add(layers.Dropout(0.5))\
model.add(layers.Dense(1, activation=\'sigmoid\'))\
model.compile(optimizer=\'adam\', loss=\'binary_crossentropy\', metrics=[\'accuracy\'])\
history = model.fit(train_data, train_labels, epochs=10, batch_size=32, validation_split=0.2)\
test_labels= label_encoder.fit_transform(test_df[\'sentiment\'])\
print(test_labels[2])\
#test_labels = to_categorical(test_df[\'sentiment\'])\
test_loss, test_acc = model.evaluate(test_data, test_labels)\
print(\'Test accuracy:\', test_acc)\
import matplotlib.pyplot as plt\
plt.plot(history.history[\'loss\'], label=\'Training Loss\')\
plt.plot(history.history[\'val_loss\'], label=\'Validation Loss\')\
plt.xlabel(\'Epoch\')\
plt.ylabel(\'Loss\')\
plt.legend()\
plt.show()\
plt.plot(history.history[\'accuracy\'], label=\'Training Accuracy\')\
plt.plot(history.history[\'val_accuracy\'], label=\'Validation Accuracy\')\
plt.xlabel(\'Epoch\')\
plt.ylabel(\'Accuracy\')\
plt.legend()\
plt.show()\
predictions = model.predict(test_data)\
text = tokenizer.sequences_to_texts(test_data)\
pred = np.zeros(len(predictions))\
for i, score in enumerate(predictions):\
    pred[i] = np.round(score)\
predicted_sentiments = [\'positive\' if label == 1 else \'negative\' for label in pred]    \
print(f\"Review text: {text[4]}\n\")\
print(f\"Review : {predicted_sentiments[4]}\")\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h2()
def  h3():
  s="import pandas as pd\
import numpy as np\
fashion_train_df = pd.read_csv(\'fashion_minst/fashion-mnist_train.csv\', sep=\',\')\
fashion_test_df = pd.read_csv(\'fashion_minst/fashion-mnist_test.csv\', sep=\',\')\
import matplotlib.pyplot as plt\
import seaborn as sbn\
training = np.asarray(fashion_train_df, dtype=\'float32\')\
height = 10\
width = 10\
fig, axes = plt.subplots(nrows=width, ncols=height, figsize=(17,17))\
axes = axes.ravel()  # this flattens the 15x15 matrix into 225\
n_train = len(training)\
for i in range(0, height*width):\
    index = np.random.randint(0, n_train)\
    axes[i].imshow(training[index, 1:].reshape(28,28))\
    axes[i].set_title(int(training[index, 0]), fontsize=8)\
    axes[i].axis(\'off\')\
plt.subplots_adjust(hspace=0.5)\
from sklearn.model_selection import train_test_split\
training = np.asarray(fashion_train_df, dtype=\'float32\')\
X_train = training[:, 1:].reshape([-1,28,28,1])\
X_train = X_train/255   \
y_train = training[:, 0]\
testing = np.asarray(fashion_test_df, dtype=\'float32\')\
X_test = testing[:, 1:].reshape([-1,28,28,1])\
X_test = X_test/255    \
y_test = testing[:, 0]\
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=5) \
from sklearn.metrics import confusion_matrix, classification_report\
from keras.models import Sequential\
from keras.layers import Conv2D, MaxPooling2D, Dropout, Dense, Flatten\
from keras.optimizers import Adam\
from keras.callbacks import TensorBoard\
from keras.utils import to_categorical\
cnn_model = Sequential()\
cnn_model.add(Conv2D(filters=64, kernel_size=(3,3), input_shape=(28,28,1), activation=\'relu\'))\
cnn_model.add(MaxPooling2D(pool_size = (2,2)))\
cnn_model.add(Dropout(rate=0.3))\
cnn_model.add(Flatten())\
cnn_model.add(Dense(units=32, activation=\'relu\'))\
cnn_model.add(Dense(units=10, activation=\'sigmoid\'))\
cnn_model.compile(optimizer=Adam(lr=0.001), loss=\'sparse_categorical_crossentropy\', metrics=[\'accuracy\'])\
cnn_model.summary()\
cnn_model.fit(x=X_train, y=y_train, batch_size=512, epochs=100, validation_data=(X_val, y_val))\
eval_result = cnn_model.evaluate(X_test, y_test)\
print(\"Accuracy :\",(eval_result[1]))\
y_pred = cnn_model.predict(x=X_test)\
y_pred[2].argmax()\
y_pred = [pred.argmax() for pred in y_pred]\
height = 10\
width = 10\
fig, axes = plt.subplots(nrows=width, ncols=height, figsize=(20,20))\
axes = axes.ravel()\
for i in range(0, height*width):\
    index = np.random.randint(len(y_pred))\
    axes[i].imshow(X_test[index].reshape((28,28)))\
    axes[i].set_title(\"True Class : {:0.0f}\nPrediction : {:d}\".format(y_test[index],y_pred[index]))\
    axes[i].axis(\'off\')\
plt.subplots_adjust(hspace=0.9, wspace=0.5)\
cm = confusion_matrix(y_test, y_pred)\
plt.figure(figsize=(10,5))\
sbn.heatmap(cm, annot=True)\
# Classification Report \
num_classes = 10\
class_names = [\"class {}\".format(i) for i in range(num_classes)]\
cr = classification_report(y_test, y_pred, target_names=class_names)\
print(cr)\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h3()
def  h4():
  s="from google.colab import drive\
drive.mount(\'/content/drive\')\
DATA_PATH=\"/content/drive/MyDrive/dataset/PlantVillage\"\
import pandas as pd\
import numpy as np\
import matplotlib.pyplot as plt\
import cv2\
import os\
import seaborn as sns\
import tensorflow as tf\
from tensorflow.keras.models import *\
from tensorflow.keras.layers import *\
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array\
for cat in os.listdir(DATA_PATH):\
    path = os.path.join(DATA_PATH, cat)\
    for img in os.listdir(path):\
        image = cv2.imread(os.path.join(path, img), cv2.IMREAD_UNCHANGED)\
        plt.imshow(image)\
        plt.title(f\'{cat}\')\
        plt.show()\
        break\
IMG_SHAPE = (224, 224)\
INPUT_SHAPE = [224, 224, 3]\
EPOCHS = 10\
BS = 32\
img_data_gen = ImageDataGenerator(rescale=1./255, rotation_range=0.2, horizontal_flip=True, vertical_flip=True,\
                                 shear_range=0.2, validation_split=0.25)\
train_data_gen = img_data_gen.flow_from_directory(DATA_PATH, batch_size=BS, subset=\'training\', \
                                                  class_mode=\'categorical\', shuffle=True) \
val_data_gen = img_data_gen.flow_from_directory(DATA_PATH, batch_size=BS, subset=\'validation\', \
                                                  class_mode=\'categorical\', shuffle=True) \
label = train_data_gen.class_indices\
label\
img = train_data_gen.__getitem__(11)[0]\
plt.imshow(img[0])\
#plt.title(label[11])\
plt.figure(figsize=(16,10))\
for i in range(15):\
    plt.subplot(5, 3, i+1)\
    img = train_data_gen.__getitem__(i)[0]\
    plt.imshow(img[0])\
    plt.xticks()\
    plt.show()\
def model_building(model_name, INPUT_SHAPE=INPUT_SHAPE):\
    print(\'Model Initialization started\')\
    base_model = model_name(include_top=False, weights=\'imagenet\', input_shape=INPUT_SHAPE)\
    for layers in base_model.layers:\
        layers.trainable = False\
    print(\'Model Initialization finished\')\
    #model creation\
    print(\'Model creation started\')\
    inp_model = base_model.output\
    x = GlobalAveragePooling2D()(inp_model)\
    x = Dense(128, activation = \'relu\')(x)\
    x = Dense(15, activation = \'sigmoid\')(x)\
    model = Model(inputs = base_model.input, outputs = x)\
    #model summary\
    print(\'Model summary\')\
    #model.summary()\
    #model compilation\
    model.compile(optimizer = \'adam\', metrics=[\'accuracy\'], loss = \'categorical_crossentropy\')\
    history = model.fit(train_data_gen, validation_data=val_data_gen, \
                       validation_steps=len(val_data_gen)//BS,\
                        steps_per_epoch=len(train_data_gen)//BS,\
                       batch_size=BS, \
                       epochs=EPOCHS)\
    print(\'Model Building Finished\')\
    !mkdir -p saved_model\
    model.save(f\'saved_model/{model_name}_1.h5\')\
    print(\'Model was saved\')\
    return history\
def evaluation_plot(model):\
    sns.set_style(\'whitegrid\')\
    plt.figure(figsize=(10, 8))\
    plt.plot(model[\'loss\'], label = \'loss\')\
    plt.plot(model[\'accuracy\'], label = \'accuracy\')\
    plt.plot(model[\'val_loss\'], label = \'val_loss\')\
    plt.plot(model[\'val_accuracy\'], label = \'val_accuracy\')\
    plt.legend()\
    plt.title(\'Model Evaluation\')\
    plt.show()\
from tensorflow.keras.applications.vgg16 import VGG16\
vgg16_hist = model_building(VGG16)\
evaluation_plot(vgg16_hist.history)\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h4()
def  h5():
  s="import pandas as pd\
import numpy as np\
base = \"Recurrent Neural Network\"\
train_data = pd.read_csv(base+\"/Stock_Price_Train.csv\")\
train_data.head()\
train = train_data.loc[:,[\'Open\']].values\
train\
from sklearn.preprocessing import MinMaxScaler\
scaler = MinMaxScaler(feature_range = (0,1))\
train_scaled = scaler.fit_transform(train)\
train_scaled\
X_train = []\
y_train = []\
timesteps = 50\
for i in range(timesteps, 1258):\
    X_train.append(train_scaled[i-timesteps:i, 0])\
    y_train.append(train_scaled[i, 0])\
X_train, y_train = np.array(X_train), np.array(y_train)\
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))\
from keras.models import Sequential\
from keras.layers import Dense\
from keras.layers import SimpleRNN\
from keras.layers import Dropout\
regressor = Sequential()\
regressor.add(SimpleRNN(units = 50,activation=\'tanh\', return_sequences = True, input_shape = (X_train.shape[1], 1)))\
regressor.add(Dropout(0.2))\
regressor.add(SimpleRNN(units = 50,activation=\'tanh\', return_sequences = True))\
regressor.add(Dropout(0.2))\
regressor.add(SimpleRNN(units = 50,activation=\'tanh\', return_sequences = True))\
regressor.add(Dropout(0.2))\
regressor.add(SimpleRNN(units = 50))\
regressor.add(Dropout(0.2))\
regressor.add(Dense(units = 1))\
regressor.compile(optimizer = \'adam\', loss = \'mean_squared_error\')\
regressor.fit(X_train, y_train, epochs = 100, batch_size = 32)\
test_data = pd.read_csv(base+\'/Stock_Price_Test.csv\')\
test_data.head()\
real_stock_price = test_data.loc[:,[\'Open\']].values\
real_stock_price\
total_data = pd.concat((train_data[\'Open\'],test_data[\'Open\']),axis=0)\
inputs = total_data[len(total_data)-len(test_data)-timesteps:].values.reshape(-1,1)\
inputs = scaler.transform(inputs) #min max scaler\
X_test = []\
for i in range(timesteps, 70):\
    X_test.append(inputs[i-timesteps:i, 0])\
X_test = np.array(X_test)\
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))\
predicted_stock_price = regressor.predict(X_test)\
predicted_stock_price = scaler.inverse_transform(predicted_stock_price)\
plt.plot(real_stock_price,color=\'red\',label=\'Real Google Stock Price\')\
plt.plot(predicted_stock_price,color=\'blue\',label=\'Predicted Google Stock Price\')\
plt.title(\'Google Stoc Price Prediction\')\
plt.xlabel(\'Time\')\
plt.ylabel(\'Google Stock Price\')\
plt.legend()\
plt.show()\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h5()
def  h6():
  s="import pandas as pd\
import numpy as np\
df = pd.read_csv(\"letter-recognition.csv\", sep = \",\")\
df=df.iloc[:,1:]\
from sklearn.model_selection import train_test_split\
X = df.iloc[:, 1 : 17]\
y = df.select_dtypes(include = [object])\
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=10)\
from sklearn.preprocessing import StandardScaler\
scaler = StandardScaler()\
scaler.fit(X_train)\
X_train = scaler.transform(X_train)\
X_test = scaler.transform(X_test)\
!pip install yellowbrick\
#!pip install yellowbrick\
from sklearn.neural_network import MLPClassifier\
from sklearn.metrics import accuracy_score\
from yellowbrick.classifier import ConfusionMatrix\
mlp = MLPClassifier(hidden_layer_sizes = (250, 300), max_iter = 1000000, activation = \'logistic\')\
cm = ConfusionMatrix(mlp, classes=\"A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z\".split(\',\'))\
cm.fit(X_train, y_train.values.ravel())\
cm.score(X_test, y_test)\
predictions = cm.predict(X_test)\
print(predictions)\
print(\"Accuracy: \", accuracy_score(y_test, predictions))\
from sklearn.metrics import classification_report\
print(classification_report(y_test, predictions, digits=5))\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h6()
def  h7():
  s="// design and implement parallel breath first search and depth first search based on existing algorithm using openMP use Tree or an undirected graph for bfs and dfs\
#include <bits/stdc++.h>\
#include <omp.h>\
#include <chrono>\
using namespace std::chrono;\
using namespace std;\
int N;\
vector<int> graph [100000];\
void bfs(int start) {\
	vector<bool> vis(N);\
	queue<int> q;\
	q.push(start);\
	while(!q.empty()) {\
		int cur = q.front();\
		q.pop();\
		if(!vis[cur]) {\
			vis[cur] = 1; cout << cur <<\" \";\
			#pragma omp parallel for\
			for (int next: graph[cur]) {\
				if(!vis[next]) q.push(next);			\
			}		\
		}	\
	}\
}\
void sbfs(int start) {\
	vector<bool> vis(N);\
	queue<int> q;\
	q.push(start);\
	while(!q.empty()) {\
		int cur = q.front();\
		q.pop();\
		if(!vis[cur]) {\
			vis[cur] = 1; cout << cur <<\" \";\
			for (int next: graph[cur]) {\
				if(!vis[next]) q.push(next);			\
			}		\
		}	\
	}\
}\
int main(){\
	int n;cin>>N>>n;\
	for(int i=0;i<n;i++){\
		int a,b;\
		cin>>a>>b;\
		graph[a].push_back(b);\
		graph[b].push_back(a);\
	}\
	int startn;cin>>startn;\
	auto start = high_resolution_clock::now();\
	sbfs(startn);\
	auto stop = high_resolution_clock::now();\
   	auto duration = duration_cast<microseconds>(stop - start);\
	cout<<\" time taken by seq bfs: \"<<duration.count()<<endl;\
	start = high_resolution_clock::now();\
	bfs(startn);\
	stop = high_resolution_clock::now();\
   	duration = duration_cast<microseconds>(stop - start);\
	cout<<\" time taken by parallel bfs: \"<<duration.count()<<endl;	\
	return 0;\
}\
/*\
9 10\
1 2\
2 3\
2 4\
3 5\
5 7\
6 1\
8 3\
3 5\
6 8\
9 1\
1\
*/\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h7()
def  h8():
  s="#include<bits/stdc++.h>\
#include<omp.h>\
using namespace std;\
void serial_bubble_sort(vector<int> &arr, int n)\
{\
	int i, j;\
    	for (i = 0; i < n - 1; i++) {\
        	for (j = 0; j < n - i - 1; j++) {\
            		if (arr[j] > arr[j + 1]) \
                		swap(arr[j], arr[j + 1]);\
       		}\
    	}\
}\
void parallel_bubble_sort(vector<int> &arr, int n)\
{\
	int phase, i;\
    	for (phase = 0; phase < n; phase++) {\
        	if (phase % 2 == 0) {  \
            		#pragma omp parallel for private(i)\
            		for (i = 2; i < n; i += 2) {\
                		if (arr[i - 1] > arr[i]) \
		            		swap(arr[i-1], arr[i]);\
                	}\
            	}\
        	else {  \
            		#pragma omp parallel for private(i)\
            		for (i = 1; i < n; i += 2) {\
                		if (arr[i - 1] > arr[i]) \
		            		swap(arr[i-1], arr[i]);\
                	}\
            	}\
        }\
}\
void merge(vector<int> &arr, int l, int m, int r) \
{\
	int n1 = m - l + 1;\
	int n2 = r - m;\
	int L[n1], R[n2];\
	int i, j, k;\
	for (i = 0; i < n1; i++)\
		L[i] = arr[l + i];\
	for (j = 0; j < n2; j++)\
		R[j] = arr[m + 1 + j];\
	i = 0;\
	j = 0;\
	k = l;\
	while (i < n1 && j < n2) {\
		if (L[i] <= R[j]) {\
	    		arr[k] = L[i];\
	    		i++;\
		}\
		else {\
	    		arr[k] = R[j];\
	    		j++;\
		}\
		k++;\
	}\
	while (i < n1) {\
		arr[k] = L[i];\
		i++;\
		k++;\
	}\
	while (j < n2) {\
		arr[k] = R[j];\
		j++;\
		k++;\
	}\
}\
void serial_merge_sort(vector<int> &arr, int l, int r)\
{\
	if (l < r) \
	{\
        	int m = l + (r - l) / 2;\
		serial_merge_sort(arr, l, m);\
		serial_merge_sort(arr, m + 1, r);\
        	merge(arr, l, m, r);\
    	}\
}\
void parallel_merge_sort(vector<int> &arr, int l, int r)\
{\
	if (l < r) \
	{\
        	int m = l + (r - l) / 2;\
        	#pragma omp parallel sections\
        	{\
            		#pragma omp section\
            		{\
                		parallel_merge_sort(arr, l, m);\
            		}\
            		#pragma omp section\
            		{\
                		parallel_merge_sort(arr, m + 1, r);\
            		}\
        	}\
        	merge(arr, l, m, r);\
    	}\
}\
int main()\
{\
	int n; \
	cout<<\"\n Enter the size of the array : \";\
	cin>>n;\
	vector<int> arr, arr1, arr2, arr3, arr4;\
	for(int i=0; i<n; i++)\
		arr.push_back(rand()%500);\
	cout<<endl;\
	double start, end;\
	cout<<\"\n**************** SERIAL BUBBLE SORT *****************\n\";\
	arr1 = arr;\
	start = omp_get_wtime();\
	serial_bubble_sort(arr1, n);\
	end = omp_get_wtime();\
	cout<<\"\n Time taken = \"<<end-start<<\" seconds.\n\";\
	cout<<\"\n**************** PARALLEL BUBBLE SORT *****************\n\";\
	arr2 = arr;\
	start = omp_get_wtime();\
	parallel_bubble_sort(arr2, n);\
	end = omp_get_wtime();\
	cout<<\"\n Time taken = \"<<end-start<<\" seconds.\n\";\
	cout<<\"\n**************** SERIAL MERGE SORT *****************\n\";\
	arr3 = arr;\
	start = omp_get_wtime();\
	serial_merge_sort(arr3, 0, n);\
	end = omp_get_wtime();\
	cout<<\"\n Time taken = \"<<end-start<<\" seconds.\n\";\
	cout<<\"\n**************** PARALLEL MERGE SORT *****************\n\";\
	arr4 = arr;\
	start = omp_get_wtime();\
	parallel_merge_sort(arr4, 0, n);\
	end = omp_get_wtime();\
	cout<<\"\n Time taken = \"<<end-start<<\" seconds.\n\";\
	return 0;\
}\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h8()
def  h9():
  s="#include <bits/stdc++.h>\
#include <omp.h>\
using namespace std;\
int arr[]={2 ,1 ,5 ,7 ,6 ,3};\
int n=6;\
void max_reduction(){\
	int maximum=arr[0];\
	#pragma omp parallel for reduction(max:maximum)\
	for(int i=0;i<n;i++){\
		if(arr[i]>maximum){\
			maximum=arr[i];		\
		}	\
	}\
	cout<<\"maximum element is: \"<<maximum<<endl;\
}\
void min_reduction(){\
	int minimum=arr[0];\
	#pragma omp parallel for reduction(min:minimum)\
	for(int i=0;i<n;i++){\
		if(arr[i]<minimum){\
			minimum=arr[i];		\
		}	\
	}\
	cout<<\"minimum element is: \"<<minimum<<endl;\
}\
void sum_reduction(){\
	int total=0;\
	#pragma omp parallel for reduction(+:total)\
	for(int i=0;i<n;i++){\
		total=total+arr[i]\
	}\
	cout<<\"sum of element is: \"<<total<<endl;\
}\
void avg_reduction(){\
	int total=0;\
	#pragma omp parallel for reduction(+:total)\
	for(int i=0;i<n;i++){\
		total=total+arr[i]\
	}\
	cout<<\"avg of element is: \"<<(total/(double)n)<<endl;\
}\
int main(){\
	min_reduction();\
	max_reduction();\
	sum_reduction();\
	avg_reduction();\
	return 0;\
}\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h9()
def  h10():
  s="#include <iostream>\
#include <vector>\
#include <cstdlib>\
#include <ctime>\
using namespace std;\
__global__ void vector_add(int *a, int *b, int *c, int n) {\
    int i = threadIdx.x + blockIdx.x * blockDim.x;\
    if (i < n) {\
        c[i] = a[i] + b[i];\
    }\
}\
int main() {\
    const int n = 100;  // Length of vectors\
    std::vector<int> a(n), b(n), c(n);\
    // Initialize vectors with random values\
    std::srand(std::time(nullptr));\
    for (int i = 0; i < n; ++i) {\
        a[i] = std::rand() % 100;\
        b[i] = std::rand() % 100;\
    }\
    // Allocate memory on device\
    int *d_a, *d_b, *d_c;\
    cudaMalloc(&d_a, n * sizeof(int));\
    cudaMalloc(&d_b, n * sizeof(int));\
    cudaMalloc(&d_c, n * sizeof(int));\
    // Copy input data from host to device\
    cudaMemcpy(d_a, a.data(), n * sizeof(int), cudaMemcpyHostToDevice);\
    cudaMemcpy(d_b, b.data(), n * sizeof(int), cudaMemcpyHostToDevice);\
    // Launch kernel\
    const int block_size = 256;\
    const int num_blocks = (n + block_size - 1) / block_size;\
    vector_add<<<num_blocks, block_size>>>(d_a, d_b, d_c, n);\
    // Copy output data from device to host\
    cudaMemcpy(c.data(), d_c, n * sizeof(int), cudaMemcpyDeviceToHost);\
    // Free memory on device\
    cudaFree(d_a);\
    cudaFree(d_b);\
    cudaFree(d_c);\
    // Print results\
    std::cout << \"Vector a: \";\
    for (int i = 0; i < n; ++i) {\
        std::cout << a[i] << \" \";\
    }\
    std::cout << std::endl;\
    std::cout << \"Vector b: \";\
    for (int i = 0; i < n; ++i) {\
        std::cout << b[i] << \" \";\
    }\
    std::cout << std::endl;\
    std::cout << \"Vector c: \";\
    for (int i = 0; i < n; ++i) {\
        std::cout << c[i] << \" \";\
    }\
    std::cout << std::endl;\
    return 0;\
}\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h10()
def  h11():
  s="#include <iostream>\
#include <cstdlib>\
#include <cstdio>\
#include <ctime>\
#define TILE_WIDTH 32\
__global__ void matrixMult(int *a, int *b, int *c, int n)\
{\
    int row = blockIdx.y * blockDim.y + threadIdx.y;\
    int col = blockIdx.x * blockDim.x + threadIdx.x;\
    if (row < n && col < n) {\
        int sum = 0;\
        for (int i = 0; i < n; ++i) {\
            sum += a[row * n + i] * b[i * n + col];\
        }\
        c[row * n + col] = sum;\
    }\
}\
int main()\
{\
    int n;\
    n=4;\
    // allocate memory for matrices on host\
    int *a = new int[n * n];\
    int *b = new int[n * n];\
    int *c = new int[n * n];\
    // initialize matrices with random values\
    std::srand(std::time(0));\
    for (int i = 0; i < n * n; ++i) {\
        a[i] = std::rand() % 10;\
        b[i] = std::rand() % 10;\
    }\
    // allocate memory for matrices on device\
    int *dev_a, *dev_b, *dev_c;\
    cudaMalloc(&dev_a, n * n * sizeof(int));\
    cudaMalloc(&dev_b, n * n * sizeof(int));\
    cudaMalloc(&dev_c, n * n * sizeof(int));\
    // copy matrices from host to device\
    cudaMemcpy(dev_a, a, n * n * sizeof(int), cudaMemcpyHostToDevice);\
    cudaMemcpy(dev_b, b, n * n * sizeof(int), cudaMemcpyHostToDevice);\
    // launch kernel\
    dim3 dimGrid((n - 1) / TILE_WIDTH + 1, (n - 1) / TILE_WIDTH + 1, 1);\
    dim3 dimBlock(TILE_WIDTH, TILE_WIDTH, 1);\
    matrixMult<<<dimGrid, dimBlock>>>(dev_a, dev_b, dev_c, n);\
    // copy result matrix from device to host\
    cudaMemcpy(c, dev_c, n * n * sizeof(int), cudaMemcpyDeviceToHost);\
    // print result matrix\
 std::cout << \"Result matrix:\n\";\
    for (int i = 0; i < n; ++i) {\
        for (int j = 0; j < n; ++j) {\
            std::cout << a[i * n + j] << \" \";\
        }\
        std::cout << \"\n\";\
    }\
 std::cout << \"Result matrix:\n\";\
    for (int i = 0; i < n; ++i) {\
        for (int j = 0; j < n; ++j) {\
            std::cout << b[i * n + j] << \" \";\
        }\
        std::cout << \"\n\";\
    }\
    std::cout << \"Result matrix:\n\";\
    for (int i = 0; i < n; ++i) {\
        for (int j = 0; j < n; ++j) {\
            std::cout << c[i * n + j] << \" \";\
        }\
        std::cout << \"\n\";\
    }\
    // free memory on device\
    cudaFree(dev_a);\
    cudaFree(dev_b);\
    cudaFree(dev_c);\
    // free memory on host\
    delete[] a;\
    delete[] b;\
    delete[] c;\
    return 0;\
}\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h11()
def  h12():
  s="#include <bits/stdc++.h>\
#include <omp.h>\
using namespace std;\
// Function to generate a random dataset\
void generate_dataset(vector<double>& x, vector<double>& y, int n) {\
    srand(time(nullptr));\
    for (int i = 0; i < n; i++) {\
        double xi = rand() / (double)RAND_MAX;\
        double yi = 2 * xi + 1 + rand() / (double)RAND_MAX;\
        x.push_back(xi);\
        y.push_back(yi);\
    }\
}\
// Function to perform normal linear regression\
void normal_linear_regression(vector<double>& x, vector<double>& y, double& slope, double& intercept) {\
    double sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;\
    int n = x.size();\
    for (int i = 0; i < n; i++) {\
        sum_x += x[i];\
        sum_y += y[i];\
        sum_xy += x[i] * y[i];\
        sum_x2 += x[i] * x[i];\
    }\
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);\
    intercept = (sum_y - slope * sum_x) / n;\
}\
// Function to perform parallel linear regression using OpenMP\
void parallel_linear_regression(vector<double>& x, vector<double>& y, double& slope, double& intercept) {\
    double sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;\
    int n = x.size();\
    #pragma omp parallel for reduction(+:sum_x,sum_y,sum_xy,sum_x2)\
    for (int i = 0; i < n; i++) {\
        sum_x += x[i];\
        sum_y += y[i];\
        sum_xy += x[i] * y[i];\
        sum_x2 += x[i] * x[i];\
    }\
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);\
    intercept = (sum_y - slope * sum_x) / n;\
}\
int main() {\
    // Generate a random dataset\
    vector<double> x, y;\
    int n = 10000000;\
    generate_dataset(x, y, n);\
    // Perform normal linear regression and measure the time it takes\
    double slope, intercept;\
    auto start = chrono::high_resolution_clock::now();\
    normal_linear_regression(x, y, slope, intercept);\
    auto stop = chrono::high_resolution_clock::now();\
    auto duration = chrono::duration_cast<chrono::microseconds>(stop - start);\
    cout << \"Normal linear regression took \" << duration.count() << \" microseconds.\" << endl;\
    // Perform parallel linear regression using OpenMP and measure the time it takes\
    start = chrono::high_resolution_clock::now();\
    parallel_linear_regression(x, y, slope, intercept);\
    stop = chrono::high_resolution_clock::now();\
    duration = chrono::duration_cast<chrono::microseconds>(stop - start);\
    cout << \"Parallel linear regression using OpenMP took \" << duration.count() << \" microseconds.\" << endl;\
    return 0;\
}\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h12()
def  h13():
  s="//Submitted by Navneet Das 3433 COMP A \
#include <bits/stdc++.h>\
#include <omp.h>\
using namespace std;\
struct Point{\
	int val;	 \
	double x, y;	 \
	double distance; \
};\
bool comparison(Point a, Point b){\
	return (a.distance < b.distance);\
}\
int classifyAPoint(Point arr[], int n, int k, Point p){\
	for (int i = 0; i < n; i++){\
		arr[i].distance = sqrt((arr[i].x - p.x) * (arr[i].x - p.x) + (arr[i].y - p.y) * (arr[i].y - p.y));\
	}\
	sort(arr, arr+n, comparison);\
	int freq1 = 0;	 \
	int freq2 = 0;	\
	for (int i = 0; i < k; i++){\
		if (arr[i].val == 0){\
			freq1++;\
		}\
		else if (arr[i].val == 1){\
			freq2++;\
		}\
	}\
	return (freq1 > freq2 ? 0 : 1);\
}\
int classifyAPointParallel(Point arr[], int n, int k, Point p){\
	#pragma omp parallel\
	for (int i = 0; i < n; i++){\
		arr[i].distance = sqrt((arr[i].x - p.x) * (arr[i].x - p.x) + (arr[i].y - p.y) * (arr[i].y - p.y));\
	}\
	sort(arr, arr+n, comparison);\
	int freq1 = 0;	 \
	int freq2 = 0;	\
	for (int i = 0; i < k; i++){\
		if (arr[i].val == 0){\
		#pragma omp critical\
			freq1++;\
		}\
		else if (arr[i].val == 1){\
		#pragma omp critical\
			freq2++;\
		}\
	}\
	return (freq1 > freq2 ? 0 : 1);\
}\
int main(){\
	cout << \"Enter number of points: \";\
	int n;\
	cin >> n; \
	Point arr[n];\
	for(int i=0;i<n;i++){\
		cin >> arr[i].x;\
		cin >> arr[i].y;\
		cin >> arr[i].val; \
	}\
	Point p;\
	cout << \"Enter x and y co-ordinate of point P: \";\
	cin >> p.x >> p.y;\
	int k;\
	cout << \"Enter value of k: \";\
	cin >> k;\
	double start=0, end =0, dur = 0;\
	cout << \"For serial KNN: \" << endl;\
	start = omp_get_wtime();\
	cout << \"The value classified to unknown point i.e. the point belongs to group: \" << classifyAPoint(arr, n, k, p) << endl;\
	end = omp_get_wtime();\
	dur = end - start;\
	cout << \"Time duration: \" << dur << endl;\
	cout << \"For parallel KNN: \" << endl;\
	start = omp_get_wtime();\
	cout << \"The value classified to unknown point i.e. the point belongs to group: \" << classifyAPointParallel(arr, n, k, p) << endl;\
	end = omp_get_wtime();\
	dur = end - start;\
	cout << \"Time duration: \" << dur << endl;\
	/*\
	Sample Input\
	1 12 0\
	2 5 0\
	5 3 1\
	3 2 1\
	3 6 0\
	1.5 9 1\
	7 2 1\
	6 1 1\
	3.8 3 1\
	3 10 0\
	5.6 4 1\
	4 2 1\
	3.5 8 0\
	2 11 0\
	2 5 1\
	2 9 0\
	1 7 0\
	*/\
	return 0;\
}\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h13()
def  h14():
  s="%%cu\
#include <bits/stdc++.h>\
#include <algorithm>\
#include <cuda.h>\
#include<omp.h>\
using namespace std;\
int knapSack(int W, int wt[], int val[], int n)\
{\
    // Base Case\
    if (n == 0 || W == 0)\
        return 0;\
    // If weight of the nth item is more than\
    // Knapsack capacity W, then this item cannot\
    // be included in the optimal solution\
    if (wt[n - 1] > W)\
        return knapSack(W, wt, val, n - 1);\
    // Return the maximum of two cases:\
    // (1) nth item included\
    // (2) not included\
    else\
        return max(\
            val[n - 1]\
                + knapSack(W - wt[n - 1], wt, val, n - 1),\
            knapSack(W, wt, val, n - 1));\
}\
// Kernel function to solve the knapsack problem in parallel\
_global_ void knapsack(int n, int capacity, int* weights, int* values, int* solution, int* start) \
{\
    // Calculate the thread index\
    int tid = blockIdx.x * blockDim.x + threadIdx.x;\
    // Check if the thread index is within the valid range\
    if (tid >= capacity + 1) \
    {\
        return;\
    }\
    // Iterate over the items, starting from the assigned start index for this thread\
    for (int i = start[tid]; i < n; i++) \
    {\
        // Check if the current item can be added to the knapsack\
        if (weights[i] <= tid)\
        {\
            // Calculate the temporary value if the current item is added\
            int temp = solution[tid - weights[i]] + values[i];\
            // Update the solution if the temporary value is higher\
            if (temp > solution[tid]) \
            {\
                solution[tid] = temp;\
                start[tid] = i;\
            }\
        }\
    }\
}\
int main() \
{\
    int n = 1000;\
    int capacity = 17;\
    int weights[n];\
    int values[n];\
    std::random_device rd;\
    std::mt19937 gen(rd());\
    int min = 1;  // Minimum value\
    int max = 100;  // Maximum value\
    std::uniform_int_distribution<> dis(min, max);\
    for (int i = 0; i < n; ++i) \
    {\
        weights[i] = dis(gen);\
    }\
    std::uniform_int_distribution<> dis1(min, max);\
    for (int i = 0; i < n; ++i) \
    {\
        values[i] = dis1(gen);\
    }\
    // Allocate memory on the GPU for variables\
    int* gpu_capacity, *gpu_weights, *gpu_values, *gpu_solution, *gpu_start;\
    cudaMalloc(&gpu_capacity, sizeof(int));\
    cudaMalloc(&gpu_weights, n * sizeof(int));\
    cudaMalloc(&gpu_values, n * sizeof(int));\
    cudaMalloc(&gpu_solution, (capacity + 1) * sizeof(int));\
    cudaMalloc(&gpu_start, (capacity + 1) * sizeof(int));\
    // Copy input data from host to device\
    cudaMemcpy(gpu_capacity, &capacity, sizeof(int), cudaMemcpyHostToDevice);\
    cudaMemcpy(gpu_weights, weights, n * sizeof(int), cudaMemcpyHostToDevice);\
    cudaMemcpy(gpu_values, values, n * sizeof(int), cudaMemcpyHostToDevice);\
    int threadsPerBlock = 256;\
    int blocksPerGrid = (capacity + threadsPerBlock - 1) / threadsPerBlock;\
    auto start = std::chrono::high_resolution_clock::now();\
    // Launch the kernel function on the GPU\
    knapsack <<<blocksPerGrid, threadsPerBlock>>>(n, capacity, gpu_weights, gpu_values, gpu_solution, gpu_start);\
    int* solution = new int[capacity + 1];\
    cudaMemcpy(solution, gpu_solution, (capacity + 1) * sizeof(int), cudaMemcpyDeviceToHost);\
    cout << \"Maximum Value: \" << solution[capacity] << endl;\
    auto end = std::chrono::high_resolution_clock::now();\
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();\
    // Print the execution time\
    std::cout << \"Execution Time for parallel knapsack: \" << duration << \" microseconds\" << std::endl;\
    start = std::chrono::high_resolution_clock::now();\
    cout <<\"maximum value \" <<knapSack(capacity, weights, values, n)<<endl;\
    end = std::chrono::high_resolution_clock::now();\
    duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();\
    // Print the execution time\
    std::cout << \"Execution Time for serial knapsack : \" << duration << \" microseconds\" << std::endl;\
    cudaFree(gpu_capacity);\
    cudaFree(gpu_weights);\
    cudaFree(gpu_values);\
    cudaFree(gpu_solution);\
    cudaFree(gpu_start);\
    delete[] solution;\
    return 0;\
}\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\+\
\\"
  print(s)
h14()