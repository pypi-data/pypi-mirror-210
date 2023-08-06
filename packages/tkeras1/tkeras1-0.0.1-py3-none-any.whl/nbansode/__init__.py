from collections import Counter
  
def count_in_list(l, word):
  c = Counter(l)
  return c[word]

def h1():
  s="\'import pandas as pd\n\'+\n\
\'import numpy as np\n\'+\n\
\'df = pd.read_csv(\'HousingData.csv\')\n\'+\n\
\'df = df.fillna(df.mean())\n\'+\n\
\'from sklearn.model_selection import train_test_split\n\'+\n\
\'\n\'+\n\
\'X = df.loc[:, df.columns != \'MEDV\']\n\'+\n\
\'y = df.loc[:, df.columns == \'MEDV\']\n\'+\n\
\'X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=123)\n\'+\n\
\'from sklearn.preprocessing import MinMaxScaler\n\'+\n\
\'mns = MinMaxScaler()\n\'+\n\
\'mns.fit(X_train)\n\'+\n\
\'X_train = mns.transform(X_train)\n\'+\n\
\'X_test = mns.transform(X_test)\n\'+\n\
\'pip install mord\n\'+\n\
\'import numpy as np\n\'+\n\
\'# from sklearn.datasets import load_boston\n\'+\n\
\'from sklearn.model_selection import train_test_split\n\'+\n\
\'from sklearn.linear_model import LinearRegression, Lasso\n\'+\n\
\'from sklearn.preprocessing import PolynomialFeatures, StandardScaler\n\'+\n\
\'from sklearn.pipeline import make_pipeline\n\'+\n\
\'from sklearn.metrics import mean_squared_error, r2_score\n\'+\n\
\'from sklearn.cross_decomposition import PLSRegression\n\'+\n\
\'from mord import OrdinalRidge\n\'+\n\
\'from tabulate import tabulate\n\'+\n\
\'\n\'+\n\
\'\n\'+\n\
\'\n\'+\n\
\'X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\'+\n\
\'\n\'+\n\
\'# Polynomial Regression\n\'+\n\
\'poly_reg = make_pipeline(PolynomialFeatures(degree=2), StandardScaler(), LinearRegression())\n\'+\n\
\'poly_reg.fit(X_train, y_train)\n\'+\n\
\'y_pred_poly = poly_reg.predict(X_test)\n\'+\n\
\'poly_mse = mean_squared_error(y_test, y_pred_poly)\n\'+\n\
\'poly_r2 = r2_score(y_test, y_pred_poly)\n\'+\n\
\'\n\'+\n\
\'# Lasso Regression\n\'+\n\
\'lasso_reg = make_pipeline(StandardScaler(), Lasso(alpha=0.1))\n\'+\n\
\'lasso_reg.fit(X_train, y_train)\n\'+\n\
\'y_pred_lasso = lasso_reg.predict(X_test)\n\'+\n\
\'lasso_mse = mean_squared_error(y_test, y_pred_lasso)\n\'+\n\
\'lasso_r2 = r2_score(y_test, y_pred_lasso)\n\'+\n\
\'\n\'+\n\
\'# Partial Least Squares Regression\n\'+\n\
\'pls_reg = make_pipeline(StandardScaler(), PLSRegression(n_components=5))\n\'+\n\
\'pls_reg.fit(X_train, y_train)\n\'+\n\
\'y_pred_pls = pls_reg.predict(X_test)\n\'+\n\
\'pls_mse = mean_squared_error(y_test, y_pred_pls)\n\'+\n\
\'pls_r2 = r2_score(y_test, y_pred_pls)\n\'+\n\
\'\n\'+\n\
\'# Ordinal Regression\n\'+\n\
\'ordinal_reg = OrdinalRidge(alpha=0.1)\n\'+\n\
\'ordinal_reg.fit(X_train, y_train)\n\'+\n\
\'y_pred_ordinal = ordinal_reg.predict(X_test)\n\'+\n\
\'ordinal_mse = mean_squared_error(y_test, y_pred_ordinal)\n\'+\n\
\'ordinal_r2 = r2_score(y_test, y_pred_ordinal)\n\'+\n\
\'\n\'+\n\
\'# Linear Regression\n\'+\n\
\'linear_reg = LinearRegression()\n\'+\n\
\'linear_reg.fit(X_train, y_train)\n\'+\n\
\'y_pred_linear = linear_reg.predict(X_test)\n\'+\n\
\'linear_mse = mean_squared_error(y_test, y_pred_linear)\n\'+\n\
\'linear_r2 = r2_score(y_test, y_pred_linear)\n\'+\n\
\'\n\'+\n\
\'\n\'+\n\
\'table = [\n\'+\n\
\'    [\"Polynomial Regression\", poly_mse, poly_r2],\n\'+\n\
\'    [\"Lasso Regression\", lasso_mse, lasso_r2],\n\'+\n\
\'    [\"Partial Least Squares Regression\", pls_mse, pls_r2],\n\'+\n\
\'    [\"Ordinal Regression\", ordinal_mse, ordinal_r2],\n\'+\n\
\'    [\"Linear Regression\", linear_mse, linear_r2]\n\'+\n\
\']\n\'+\n\
\'\n\'+\n\
\'\n\'+\n\
\'headers = [\"Model\", \"Mean Squared Error\", \"R2 Score\"]\n\'+\n\
\'print(tabulate(table, headers, tablefmt=\"grid\"))\n\'+\n\
\'\n\'+\n\
\'from keras.models import Sequential\n\'+\n\
\'from keras.layers import Dense\n\'+\n\
\'model = Sequential()\n\'+\n\
\'\n\'+\n\
\'model.add(Dense(128, input_shape=(13, ), activation=\'relu\', name=\'dense_1\'))\n\'+\n\
\'model.add(Dense(64,activation = \'relu\',name = \'dense_2\'))\n\'+\n\
\'model.add(Dense(1,activation = \'linear\',name = \'dense_output\'))\n\'+\n\
\'\n\'+\n\
\'model.compile(optimizer = \'adam\',loss = \'mse\',metrics = [\'mae\'])\n\'+\n\
\'model.summary()\n\'+\n\
\'history = model.fit(X_train,y_train,epochs = 100,validation_split = 0.05,verbose = 1)\n\'+\n\
\'mse_nn, mae_nn = model.evaluate(X_test, y_test)\n\'+\n\
\'\n\'+\n\
\'print(\'Mean squared error on test data: \', mse_nn)\n\'+\n\
\'print(\'Mean absolute error on test data: \', mae_nn)\n\'+\n\
\'import matplotlib.pyplot as plt\n\'+\n\
\'lossv = []\n\'+\n\
\'\n\'+\n\
\'for epoch in range(100):\n\'+\n\
\'    history =  model.fit(X_train,y_train,epochs = 10,validation_split = 0.05,verbose = 1)\n\'+\n\
\'    lossv += history.history[\'loss\']\n\'+\n\
\'plt.plot(lossv)\';+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\\"
  print(s)
h1()
def  h2():
  s="import numpy as np\n\
from keras import models, layers, optimizers\n\
from keras.preprocessing.text import Tokenizer\n\
from keras.utils import pad_sequences\n\
from tensorflow.keras.utils import to_categorical\n\
import pandas as pd\n\
from sklearn import preprocessing\n\
# Load the data\n\
df=pd.read_csv(\"IMDB Dataset.csv\")\n\
train_df = df.sample(frac=0.8, random_state=25)\n\
test_df = df.drop(train_df.index)\n\
print(train_df)\n\
print(test_df)\n\
# Tokenize the text data\n\
tokenizer = Tokenizer(num_words=10000)\n\
tokenizer.fit_on_texts(train_df[\'review\'].tolist())\n\
# Convert the text data to sequences of integers\n\
train_sequences = tokenizer.texts_to_sequences(train_df[\'review\'].tolist())\n\
test_sequences = tokenizer.texts_to_sequences(test_df[\'review\'].tolist())\n\
# Pad the sequences to a fixed length\n\
max_length = 100\n\
train_data = pad_sequences(train_sequences, maxlen=max_length)\n\
test_data = pad_sequences(test_sequences, maxlen=max_length)\n\
# Convert the labels to categorical\n\
label_encoder = preprocessing.LabelEncoder()\n\
train_labels= label_encoder.fit_transform(train_df[\'sentiment\'])\n\
#train_labels = to_categorical(train_df[\'sentiment\'])\n\
model = models.Sequential()\n\
model.add(layers.Embedding(10000, 64, input_length=max_length))\n\
model.add(layers.Flatten())\n\
model.add(layers.Dense(32, activation=\'relu\'))\n\
model.add(layers.Dropout(0.5))\n\
model.add(layers.Dense(1, activation=\'sigmoid\'))\n\
model.compile(optimizer=\'adam\', loss=\'binary_crossentropy\', metrics=[\'accuracy\'])\n\
history = model.fit(train_data, train_labels, epochs=10, batch_size=32, validation_split=0.2)\n\
test_labels= label_encoder.fit_transform(test_df[\'sentiment\'])\n\
print(test_labels[2])\n\
#test_labels = to_categorical(test_df[\'sentiment\'])\n\
test_loss, test_acc = model.evaluate(test_data, test_labels)\n\
print(\'Test accuracy:\', test_acc)\n\
import matplotlib.pyplot as plt\n\
plt.plot(history.history[\'loss\'], label=\'Training Loss\')\n\
plt.plot(history.history[\'val_loss\'], label=\'Validation Loss\')\n\
plt.xlabel(\'Epoch\')\n\
plt.ylabel(\'Loss\')\n\
plt.legend()\n\
plt.show()\n\
plt.plot(history.history[\'accuracy\'], label=\'Training Accuracy\')\n\
plt.plot(history.history[\'val_accuracy\'], label=\'Validation Accuracy\')\n\
plt.xlabel(\'Epoch\')\n\
plt.ylabel(\'Accuracy\')\n\
plt.legend()\n\
plt.show()\n\
predictions = model.predict(test_data)\n\
text = tokenizer.sequences_to_texts(test_data)\n\
pred = np.zeros(len(predictions))\n\
for i, score in enumerate(predictions):\n\
    pred[i] = np.round(score)\n\
predicted_sentiments = [\'positive\' if label == 1 else \'negative\' for label in pred]    \n\
print(f\"Review text: {text[4]}\n\")\n\
print(f\"Review : {predicted_sentiments[4]}\")\n\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\+\n\
\\"
  print(s)
h2()
def  h3():
  s="import pandas as pd\n\
import numpy as np\n\
fashion_train_df = pd.read_csv(\'fashion_minst/fashion-mnist_train.csv\', sep=\',\')\n\
fashion_test_df = pd.read_csv(\'fashion_minst/fashion-mnist_test.csv\', sep=\',\')\n\
import matplotlib.pyplot as plt\n\
import seaborn as sbn\n\
training = np.asarray(fashion_train_df, dtype=\'float32\')\n\
height = 10\n\
width = 10\n\
fig, axes = plt.subplots(nrows=width, ncols=height, figsize=(17,17))\n\
axes = axes.ravel()  # this flattens the 15x15 matrix into 225\n\
n_train = len(training)\n\
for i in range(0, height*width):\n\
    index = np.random.randint(0, n_train)\n\
    axes[i].imshow(training[index, 1:].reshape(28,28))\n\
    axes[i].set_title(int(training[index, 0]), fontsize=8)\n\
    axes[i].axis(\'off\')\n\
plt.subplots_adjust(hspace=0.5)\n\
from sklearn.model_selection import train_test_split\n\
training = np.asarray(fashion_train_df, dtype=\'float32\')\n\
X_train = training[:, 1:].reshape([-1,28,28,1])\n\
X_train = X_train/255   \n\
y_train = training[:, 0]\n\
testing = np.asarray(fashion_test_df, dtype=\'float32\')\n\
X_test = testing[:, 1:].reshape([-1,28,28,1])\n\
X_test = X_test/255    \n\
y_test = testing[:, 0]\n\
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=5) \n\
from sklearn.metrics import confusion_matrix, classification_report\n\
from keras.models import Sequential\n\
from keras.layers import Conv2D, MaxPooling2D, Dropout, Dense, Flatten\n\
from keras.optimizers import Adam\n\
from keras.callbacks import TensorBoard\n\
from keras.utils import to_categorical\n\
cnn_model = Sequential()\n\
cnn_model.add(Conv2D(filters=64, kernel_size=(3,3), input_shape=(28,28,1), activation=\'relu\'))\n\
cnn_model.add(MaxPooling2D(pool_size = (2,2)))\n\
cnn_model.add(Dropout(rate=0.3))\n\
cnn_model.add(Flatten())\n\
cnn_model.add(Dense(units=32, activation=\'relu\'))\n\
cnn_model.add(Dense(units=10, activation=\'sigmoid\'))\n\
cnn_model.compile(optimizer=Adam(lr=0.001), loss=\'sparse_categorical_crossentropy\', metrics=[\'accuracy\'])\n\
cnn_model.summary()\n\
cnn_model.fit(x=X_train, y=y_train, batch_size=512, epochs=100, validation_data=(X_val, y_val))\n\
eval_result = cnn_model.evaluate(X_test, y_test)\n\
print(\"Accuracy :\",(eval_result[1]))\n\
y_pred = cnn_model.predict(x=X_test)\n\
y_pred[2].argmax()\n\
y_pred = [pred.argmax() for pred in y_pred]\n\
height = 10\n\
width = 10\n\
fig, axes = plt.subplots(nrows=width, ncols=height, figsize=(20,20))\n\
axes = axes.ravel()\n\
for i in range(0, height*width):\n\
    index = np.random.randint(len(y_pred))\n\
    axes[i].imshow(X_test[index].reshape((28,28)))\n\
    axes[i].set_title(\"True Class : {:0.0f}\nPrediction : {:d}\".format(y_test[index],y_pred[index]))\n\
    axes[i].axis(\'off\')\n\
plt.subplots_adjust(hspace=0.9, wspace=0.5)\n\
cm = confusion_matrix(y_test, y_pred)\n\
plt.figure(figsize=(10,5))\n\
sbn.heatmap(cm, annot=True)\n\
# Classification Report \n\
num_classes = 10\n\
class_names = [\"class {}\".format(i) for i in range(num_classes)]\n\
cr = classification_report(y_test, y_pred, target_names=class_names)\n\
print(cr)\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h3()
def  h4():
  s="from google.colab import drive\n\
drive.mount(\'/content/drive\')\n\
DATA_PATH=\"/content/drive/MyDrive/dataset/PlantVillage\"\n\
import pandas as pd\n\
import numpy as np\n\
import matplotlib.pyplot as plt\n\
import cv2\n\
import os\n\
import seaborn as sns\n\
import tensorflow as tf\n\
from tensorflow.keras.models import *\n\
from tensorflow.keras.layers import *\n\
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array\n\
for cat in os.listdir(DATA_PATH):\n\
    path = os.path.join(DATA_PATH, cat)\n\
    for img in os.listdir(path):\n\
        image = cv2.imread(os.path.join(path, img), cv2.IMREAD_UNCHANGED)\n\
        plt.imshow(image)\n\
        plt.title(f\'{cat}\')\n\
        plt.show()\n\
        break\n\
IMG_SHAPE = (224, 224)\n\
INPUT_SHAPE = [224, 224, 3]\n\
EPOCHS = 10\n\
BS = 32\n\
img_data_gen = ImageDataGenerator(rescale=1./255, rotation_range=0.2, horizontal_flip=True, vertical_flip=True,\n\
                                 shear_range=0.2, validation_split=0.25)\n\
train_data_gen = img_data_gen.flow_from_directory(DATA_PATH, batch_size=BS, subset=\'training\', \n\
                                                  class_mode=\'categorical\', shuffle=True) \n\
val_data_gen = img_data_gen.flow_from_directory(DATA_PATH, batch_size=BS, subset=\'validation\', \n\
                                                  class_mode=\'categorical\', shuffle=True) \n\
label = train_data_gen.class_indices\n\
label\n\
img = train_data_gen.__getitem__(11)[0]\n\
plt.imshow(img[0])\n\
#plt.title(label[11])\n\
plt.figure(figsize=(16,10))\n\
for i in range(15):\n\
    plt.subplot(5, 3, i+1)\n\
    img = train_data_gen.__getitem__(i)[0]\n\
    plt.imshow(img[0])\n\
    plt.xticks()\n\
    plt.show()\n\
def model_building(model_name, INPUT_SHAPE=INPUT_SHAPE):\n\
    print(\'Model Initialization started\')\n\
    base_model = model_name(include_top=False, weights=\'imagenet\', input_shape=INPUT_SHAPE)\n\
    for layers in base_model.layers:\n\
        layers.trainable = False\n\
    print(\'Model Initialization finished\')\n\
    #model creation\n\
    print(\'Model creation started\')\n\
    inp_model = base_model.output\n\
    x = GlobalAveragePooling2D()(inp_model)\n\
    x = Dense(128, activation = \'relu\')(x)\n\
    x = Dense(15, activation = \'sigmoid\')(x)\n\
    model = Model(inputs = base_model.input, outputs = x)\n\
    #model summary\n\
    print(\'Model summary\')\n\
    #model.summary()\n\
    #model compilation\n\
    model.compile(optimizer = \'adam\', metrics=[\'accuracy\'], loss = \'categorical_crossentropy\')\n\
    history = model.fit(train_data_gen, validation_data=val_data_gen, \n\
                       validation_steps=len(val_data_gen)//BS,\n\
                        steps_per_epoch=len(train_data_gen)//BS,\n\
                       batch_size=BS, \n\
                       epochs=EPOCHS)\n\
    print(\'Model Building Finished\')\n\
    !mkdir -p saved_model\n\
    model.save(f\'saved_model/{model_name}_1.h5\')\n\
    print(\'Model was saved\')\n\
    return history\n\
def evaluation_plot(model):\n\
    sns.set_style(\'whitegrid\')\n\
    plt.figure(figsize=(10, 8))\n\
    plt.plot(model[\'loss\'], label = \'loss\')\n\
    plt.plot(model[\'accuracy\'], label = \'accuracy\')\n\
    plt.plot(model[\'val_loss\'], label = \'val_loss\')\n\
    plt.plot(model[\'val_accuracy\'], label = \'val_accuracy\')\n\
    plt.legend()\n\
    plt.title(\'Model Evaluation\')\n\
    plt.show()\n\
from tensorflow.keras.applications.vgg16 import VGG16\n\
vgg16_hist = model_building(VGG16)\n\
evaluation_plot(vgg16_hist.history)\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h4()
def  h5():
  s="import pandas as pd\n\
import numpy as np\n\
base = \"Recurrent Neural Network\"\n\
train_data = pd.read_csv(base+\"/Stock_Price_Train.csv\")\n\
train_data.head()\n\
train = train_data.loc[:,[\'Open\']].values\n\
train\n\
from sklearn.preprocessing import MinMaxScaler\n\
scaler = MinMaxScaler(feature_range = (0,1))\n\
train_scaled = scaler.fit_transform(train)\n\
train_scaled\n\
X_train = []\n\
y_train = []\n\
timesteps = 50\n\
for i in range(timesteps, 1258):\n\
    X_train.append(train_scaled[i-timesteps:i, 0])\n\
    y_train.append(train_scaled[i, 0])\n\
X_train, y_train = np.array(X_train), np.array(y_train)\n\
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))\n\
from keras.models import Sequential\n\
from keras.layers import Dense\n\
from keras.layers import SimpleRNN\n\
from keras.layers import Dropout\n\
regressor = Sequential()\n\
regressor.add(SimpleRNN(units = 50,activation=\'tanh\', return_sequences = True, input_shape = (X_train.shape[1], 1)))\n\
regressor.add(Dropout(0.2))\n\
regressor.add(SimpleRNN(units = 50,activation=\'tanh\', return_sequences = True))\n\
regressor.add(Dropout(0.2))\n\
regressor.add(SimpleRNN(units = 50,activation=\'tanh\', return_sequences = True))\n\
regressor.add(Dropout(0.2))\n\
regressor.add(SimpleRNN(units = 50))\n\
regressor.add(Dropout(0.2))\n\
regressor.add(Dense(units = 1))\n\
regressor.compile(optimizer = \'adam\', loss = \'mean_squared_error\')\n\
regressor.fit(X_train, y_train, epochs = 100, batch_size = 32)\n\
test_data = pd.read_csv(base+\'/Stock_Price_Test.csv\')\n\
test_data.head()\n\
real_stock_price = test_data.loc[:,[\'Open\']].values\n\
real_stock_price\n\
total_data = pd.concat((train_data[\'Open\'],test_data[\'Open\']),axis=0)\n\
inputs = total_data[len(total_data)-len(test_data)-timesteps:].values.reshape(-1,1)\n\
inputs = scaler.transform(inputs) #min max scaler\n\
X_test = []\n\
for i in range(timesteps, 70):\n\
    X_test.append(inputs[i-timesteps:i, 0])\n\
X_test = np.array(X_test)\n\
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))\n\
predicted_stock_price = regressor.predict(X_test)\n\
predicted_stock_price = scaler.inverse_transform(predicted_stock_price)\n\
plt.plot(real_stock_price,color=\'red\',label=\'Real Google Stock Price\')\n\
plt.plot(predicted_stock_price,color=\'blue\',label=\'Predicted Google Stock Price\')\n\
plt.title(\'Google Stoc Price Prediction\')\n\
plt.xlabel(\'Time\')\n\
plt.ylabel(\'Google Stock Price\')\n\
plt.legend()\n\
plt.show()\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h5()
def  h6():
  s="import pandas as pd\n\
import numpy as np\n\
df = pd.read_csv(\"letter-recognition.csv\", sep = \",\")\n\
df=df.iloc[:,1:]\n\
from sklearn.model_selection import train_test_split\n\
X = df.iloc[:, 1 : 17]\n\
y = df.select_dtypes(include = [object])\n\
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=10)\n\
from sklearn.preprocessing import StandardScaler\n\
scaler = StandardScaler()\n\
scaler.fit(X_train)\n\
X_train = scaler.transform(X_train)\n\
X_test = scaler.transform(X_test)\n\
!pip install yellowbrick\n\
#!pip install yellowbrick\n\
from sklearn.neural_network import MLPClassifier\n\
from sklearn.metrics import accuracy_score\n\
from yellowbrick.classifier import ConfusionMatrix\n\
mlp = MLPClassifier(hidden_layer_sizes = (250, 300), max_iter = 1000000, activation = \'logistic\')\n\
cm = ConfusionMatrix(mlp, classes=\"A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z\".split(\',\'))\n\
cm.fit(X_train, y_train.values.ravel())\n\
cm.score(X_test, y_test)\n\
predictions = cm.predict(X_test)\n\
print(predictions)\n\
print(\"Accuracy: \", accuracy_score(y_test, predictions))\n\
from sklearn.metrics import classification_report\n\
print(classification_report(y_test, predictions, digits=5))\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h6()
def  h7():
  s="// design and implement parallel breath first search and depth first search based on existing algorithm using openMP use Tree or an undirected graph for bfs and dfs\n\
#include <bits/stdc++.h>\n\
#include <omp.h>\n\
#include <chrono>\n\
using namespace std::chrono;\n\
using namespace std;\n\
int N;\n\
vector<int> graph [100000];\n\
void bfs(int start) {\n\
	vector<bool> vis(N);\n\
	queue<int> q;\n\
	q.push(start);\n\
	while(!q.empty()) {\n\
		int cur = q.front();\n\
		q.pop();\n\
		if(!vis[cur]) {\n\
			vis[cur] = 1; cout << cur <<\" \";\n\
			#pragma omp parallel for\n\
			for (int next: graph[cur]) {\n\
				if(!vis[next]) q.push(next);			\n\
			}		\n\
		}	\n\
	}\n\
}\n\
void sbfs(int start) {\n\
	vector<bool> vis(N);\n\
	queue<int> q;\n\
	q.push(start);\n\
	while(!q.empty()) {\n\
		int cur = q.front();\n\
		q.pop();\n\
		if(!vis[cur]) {\n\
			vis[cur] = 1; cout << cur <<\" \";\n\
			for (int next: graph[cur]) {\n\
				if(!vis[next]) q.push(next);			\n\
			}		\n\
		}	\n\
	}\n\
}\n\
int main(){\n\
	int n;cin>>N>>n;\n\
	for(int i=0;i<n;i++){\n\
		int a,b;\n\
		cin>>a>>b;\n\
		graph[a].push_back(b);\n\
		graph[b].push_back(a);\n\
	}\n\
	int startn;cin>>startn;\n\
	auto start = high_resolution_clock::now();\n\
	sbfs(startn);\n\
	auto stop = high_resolution_clock::now();\n\
   	auto duration = duration_cast<microseconds>(stop - start);\n\
	cout<<\" time taken by seq bfs: \"<<duration.count()<<endl;\n\
	start = high_resolution_clock::now();\n\
	bfs(startn);\n\
	stop = high_resolution_clock::now();\n\
   	duration = duration_cast<microseconds>(stop - start);\n\
	cout<<\" time taken by parallel bfs: \"<<duration.count()<<endl;	\n\
	return 0;\n\
}\n\
/*\n\
9 10\n\
1 2\n\
2 3\n\
2 4\n\
3 5\n\
5 7\n\
6 1\n\
8 3\n\
3 5\n\
6 8\n\
9 1\n\
1\n\
*/\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h7()
def  h8():
  s="#include<bits/stdc++.h>\n\
#include<omp.h>\n\
using namespace std;\n\
void serial_bubble_sort(vector<int> &arr, int n)\n\
{\n\
	int i, j;\n\
    	for (i = 0; i < n - 1; i++) {\n\
        	for (j = 0; j < n - i - 1; j++) {\n\
            		if (arr[j] > arr[j + 1]) \n\
                		swap(arr[j], arr[j + 1]);\n\
       		}\n\
    	}\n\
}\n\
void parallel_bubble_sort(vector<int> &arr, int n)\n\
{\n\
	int phase, i;\n\
    	for (phase = 0; phase < n; phase++) {\n\
        	if (phase % 2 == 0) {  \n\
            		#pragma omp parallel for private(i)\n\
            		for (i = 2; i < n; i += 2) {\n\
                		if (arr[i - 1] > arr[i]) \n\
		            		swap(arr[i-1], arr[i]);\n\
                	}\n\
            	}\n\
        	else {  \n\
            		#pragma omp parallel for private(i)\n\
            		for (i = 1; i < n; i += 2) {\n\
                		if (arr[i - 1] > arr[i]) \n\
		            		swap(arr[i-1], arr[i]);\n\
                	}\n\
            	}\n\
        }\n\
}\n\
void merge(vector<int> &arr, int l, int m, int r) \n\
{\n\
	int n1 = m - l + 1;\n\
	int n2 = r - m;\n\
	int L[n1], R[n2];\n\
	int i, j, k;\n\
	for (i = 0; i < n1; i++)\n\
		L[i] = arr[l + i];\n\
	for (j = 0; j < n2; j++)\n\
		R[j] = arr[m + 1 + j];\n\
	i = 0;\n\
	j = 0;\n\
	k = l;\n\
	while (i < n1 && j < n2) {\n\
		if (L[i] <= R[j]) {\n\
	    		arr[k] = L[i];\n\
	    		i++;\n\
		}\n\
		else {\n\
	    		arr[k] = R[j];\n\
	    		j++;\n\
		}\n\
		k++;\n\
	}\n\
	while (i < n1) {\n\
		arr[k] = L[i];\n\
		i++;\n\
		k++;\n\
	}\n\
	while (j < n2) {\n\
		arr[k] = R[j];\n\
		j++;\n\
		k++;\n\
	}\n\
}\n\
void serial_merge_sort(vector<int> &arr, int l, int r)\n\
{\n\
	if (l < r) \n\
	{\n\
        	int m = l + (r - l) / 2;\n\
		serial_merge_sort(arr, l, m);\n\
		serial_merge_sort(arr, m + 1, r);\n\
        	merge(arr, l, m, r);\n\
    	}\n\
}\n\
void parallel_merge_sort(vector<int> &arr, int l, int r)\n\
{\n\
	if (l < r) \n\
	{\n\
        	int m = l + (r - l) / 2;\n\
        	#pragma omp parallel sections\n\
        	{\n\
            		#pragma omp section\n\
            		{\n\
                		parallel_merge_sort(arr, l, m);\n\
            		}\n\
            		#pragma omp section\n\
            		{\n\
                		parallel_merge_sort(arr, m + 1, r);\n\
            		}\n\
        	}\n\
        	merge(arr, l, m, r);\n\
    	}\n\
}\n\
int main()\n\
{\n\
	int n; \n\
	cout<<\"\n Enter the size of the array : \";\n\
	cin>>n;\n\
	vector<int> arr, arr1, arr2, arr3, arr4;\n\
	for(int i=0; i<n; i++)\n\
		arr.push_back(rand()%500);\n\
	cout<<endl;\n\
	double start, end;\n\
	cout<<\"\n**************** SERIAL BUBBLE SORT *****************\n\";\n\
	arr1 = arr;\n\
	start = omp_get_wtime();\n\
	serial_bubble_sort(arr1, n);\n\
	end = omp_get_wtime();\n\
	cout<<\"\n Time taken = \"<<end-start<<\" seconds.\n\";\n\
	cout<<\"\n**************** PARALLEL BUBBLE SORT *****************\n\";\n\
	arr2 = arr;\n\
	start = omp_get_wtime();\n\
	parallel_bubble_sort(arr2, n);\n\
	end = omp_get_wtime();\n\
	cout<<\"\n Time taken = \"<<end-start<<\" seconds.\n\";\n\
	cout<<\"\n**************** SERIAL MERGE SORT *****************\n\";\n\
	arr3 = arr;\n\
	start = omp_get_wtime();\n\
	serial_merge_sort(arr3, 0, n);\n\
	end = omp_get_wtime();\n\
	cout<<\"\n Time taken = \"<<end-start<<\" seconds.\n\";\n\
	cout<<\"\n**************** PARALLEL MERGE SORT *****************\n\";\n\
	arr4 = arr;\n\
	start = omp_get_wtime();\n\
	parallel_merge_sort(arr4, 0, n);\n\
	end = omp_get_wtime();\n\
	cout<<\"\n Time taken = \"<<end-start<<\" seconds.\n\";\n\
	return 0;\n\
}\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h8()
def  h9():
  s="#include <bits/stdc++.h>\n\
#include <omp.h>\n\
using namespace std;\n\
int arr[]={2 ,1 ,5 ,7 ,6 ,3};\n\
int n=6;\n\
void max_reduction(){\n\
	int maximum=arr[0];\n\
	#pragma omp parallel for reduction(max:maximum)\n\
	for(int i=0;i<n;i++){\n\
		if(arr[i]>maximum){\n\
			maximum=arr[i];		\n\
		}	\n\
	}\n\
	cout<<\"maximum element is: \"<<maximum<<endl;\n\
}\n\
void min_reduction(){\n\
	int minimum=arr[0];\n\
	#pragma omp parallel for reduction(min:minimum)\n\
	for(int i=0;i<n;i++){\n\
		if(arr[i]<minimum){\n\
			minimum=arr[i];		\n\
		}	\n\
	}\n\
	cout<<\"minimum element is: \"<<minimum<<endl;\n\
}\n\
void sum_reduction(){\n\
	int total=0;\n\
	#pragma omp parallel for reduction(+:total)\n\
	for(int i=0;i<n;i++){\n\
		total=total+arr[i]\n\
	}\n\
	cout<<\"sum of element is: \"<<total<<endl;\n\
}\n\
void avg_reduction(){\n\
	int total=0;\n\
	#pragma omp parallel for reduction(+:total)\n\
	for(int i=0;i<n;i++){\n\
		total=total+arr[i]\n\
	}\n\
	cout<<\"avg of element is: \"<<(total/(double)n)<<endl;\n\
}\n\
int main(){\n\
	min_reduction();\n\
	max_reduction();\n\
	sum_reduction();\n\
	avg_reduction();\n\
	return 0;\n\
}\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h9()
def  h10():
  s="#include <iostream>\n\
#include <vector>\n\
#include <cstdlib>\n\
#include <ctime>\n\
using namespace std;\n\
__global__ void vector_add(int *a, int *b, int *c, int n) {\n\
    int i = threadIdx.x + blockIdx.x * blockDim.x;\n\
    if (i < n) {\n\
        c[i] = a[i] + b[i];\n\
    }\n\
}\n\
int main() {\n\
    const int n = 100;  // Length of vectors\n\
    std::vector<int> a(n), b(n), c(n);\n\
    // Initialize vectors with random values\n\
    std::srand(std::time(nullptr));\n\
    for (int i = 0; i < n; ++i) {\n\
        a[i] = std::rand() % 100;\n\
        b[i] = std::rand() % 100;\n\
    }\n\
    // Allocate memory on device\n\
    int *d_a, *d_b, *d_c;\n\
    cudaMalloc(&d_a, n * sizeof(int));\n\
    cudaMalloc(&d_b, n * sizeof(int));\n\
    cudaMalloc(&d_c, n * sizeof(int));\n\
    // Copy input data from host to device\n\
    cudaMemcpy(d_a, a.data(), n * sizeof(int), cudaMemcpyHostToDevice);\n\
    cudaMemcpy(d_b, b.data(), n * sizeof(int), cudaMemcpyHostToDevice);\n\
    // Launch kernel\n\
    const int block_size = 256;\n\
    const int num_blocks = (n + block_size - 1) / block_size;\n\
    vector_add<<<num_blocks, block_size>>>(d_a, d_b, d_c, n);\n\
    // Copy output data from device to host\n\
    cudaMemcpy(c.data(), d_c, n * sizeof(int), cudaMemcpyDeviceToHost);\n\
    // Free memory on device\n\
    cudaFree(d_a);\n\
    cudaFree(d_b);\n\
    cudaFree(d_c);\n\
    // Print results\n\
    std::cout << \"Vector a: \";\n\
    for (int i = 0; i < n; ++i) {\n\
        std::cout << a[i] << \" \";\n\
    }\n\
    std::cout << std::endl;\n\
    std::cout << \"Vector b: \";\n\
    for (int i = 0; i < n; ++i) {\n\
        std::cout << b[i] << \" \";\n\
    }\n\
    std::cout << std::endl;\n\
    std::cout << \"Vector c: \";\n\
    for (int i = 0; i < n; ++i) {\n\
        std::cout << c[i] << \" \";\n\
    }\n\
    std::cout << std::endl;\n\
    return 0;\n\
}\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h10()
def  h11():
  s="#include <iostream>\n\
#include <cstdlib>\n\
#include <cstdio>\n\
#include <ctime>\n\
#define TILE_WIDTH 32\n\
__global__ void matrixMult(int *a, int *b, int *c, int n)\n\
{\n\
    int row = blockIdx.y * blockDim.y + threadIdx.y;\n\
    int col = blockIdx.x * blockDim.x + threadIdx.x;\n\
    if (row < n && col < n) {\n\
        int sum = 0;\n\
        for (int i = 0; i < n; ++i) {\n\
            sum += a[row * n + i] * b[i * n + col];\n\
        }\n\
        c[row * n + col] = sum;\n\
    }\n\
}\n\
int main()\n\
{\n\
    int n;\n\
    n=4;\n\
    // allocate memory for matrices on host\n\
    int *a = new int[n * n];\n\
    int *b = new int[n * n];\n\
    int *c = new int[n * n];\n\
    // initialize matrices with random values\n\
    std::srand(std::time(0));\n\
    for (int i = 0; i < n * n; ++i) {\n\
        a[i] = std::rand() % 10;\n\
        b[i] = std::rand() % 10;\n\
    }\n\
    // allocate memory for matrices on device\n\
    int *dev_a, *dev_b, *dev_c;\n\
    cudaMalloc(&dev_a, n * n * sizeof(int));\n\
    cudaMalloc(&dev_b, n * n * sizeof(int));\n\
    cudaMalloc(&dev_c, n * n * sizeof(int));\n\
    // copy matrices from host to device\n\
    cudaMemcpy(dev_a, a, n * n * sizeof(int), cudaMemcpyHostToDevice);\n\
    cudaMemcpy(dev_b, b, n * n * sizeof(int), cudaMemcpyHostToDevice);\n\
    // launch kernel\n\
    dim3 dimGrid((n - 1) / TILE_WIDTH + 1, (n - 1) / TILE_WIDTH + 1, 1);\n\
    dim3 dimBlock(TILE_WIDTH, TILE_WIDTH, 1);\n\
    matrixMult<<<dimGrid, dimBlock>>>(dev_a, dev_b, dev_c, n);\n\
    // copy result matrix from device to host\n\
    cudaMemcpy(c, dev_c, n * n * sizeof(int), cudaMemcpyDeviceToHost);\n\
    // print result matrix\n\
 std::cout << \"Result matrix:\n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        for (int j = 0; j < n; ++j) {\n\
            std::cout << a[i * n + j] << \" \";\n\
        }\n\
        std::cout << \"\n\";\n\
    }\n\
 std::cout << \"Result matrix:\n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        for (int j = 0; j < n; ++j) {\n\
            std::cout << b[i * n + j] << \" \";\n\
        }\n\
        std::cout << \"\n\";\n\
    }\n\
    std::cout << \"Result matrix:\n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        for (int j = 0; j < n; ++j) {\n\
            std::cout << c[i * n + j] << \" \";\n\
        }\n\
        std::cout << \"\n\";\n\
    }\n\
    // free memory on device\n\
    cudaFree(dev_a);\n\
    cudaFree(dev_b);\n\
    cudaFree(dev_c);\n\
    // free memory on host\n\
    delete[] a;\n\
    delete[] b;\n\
    delete[] c;\n\
    return 0;\n\
}\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h11()
def  h12():
  s="#include <bits/stdc++.h>\n\
#include <omp.h>\n\
using namespace std;\n\
// Function to generate a random dataset\n\
void generate_dataset(vector<double>& x, vector<double>& y, int n) {\n\
    srand(time(nullptr));\n\
    for (int i = 0; i < n; i++) {\n\
        double xi = rand() / (double)RAND_MAX;\n\
        double yi = 2 * xi + 1 + rand() / (double)RAND_MAX;\n\
        x.push_back(xi);\n\
        y.push_back(yi);\n\
    }\n\
}\n\
// Function to perform normal linear regression\n\
void normal_linear_regression(vector<double>& x, vector<double>& y, double& slope, double& intercept) {\n\
    double sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;\n\
    int n = x.size();\n\
    for (int i = 0; i < n; i++) {\n\
        sum_x += x[i];\n\
        sum_y += y[i];\n\
        sum_xy += x[i] * y[i];\n\
        sum_x2 += x[i] * x[i];\n\
    }\n\
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);\n\
    intercept = (sum_y - slope * sum_x) / n;\n\
}\n\
// Function to perform parallel linear regression using OpenMP\n\
void parallel_linear_regression(vector<double>& x, vector<double>& y, double& slope, double& intercept) {\n\
    double sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;\n\
    int n = x.size();\n\
    #pragma omp parallel for reduction(+:sum_x,sum_y,sum_xy,sum_x2)\n\
    for (int i = 0; i < n; i++) {\n\
        sum_x += x[i];\n\
        sum_y += y[i];\n\
        sum_xy += x[i] * y[i];\n\
        sum_x2 += x[i] * x[i];\n\
    }\n\
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);\n\
    intercept = (sum_y - slope * sum_x) / n;\n\
}\n\
int main() {\n\
    // Generate a random dataset\n\
    vector<double> x, y;\n\
    int n = 10000000;\n\
    generate_dataset(x, y, n);\n\
    // Perform normal linear regression and measure the time it takes\n\
    double slope, intercept;\n\
    auto start = chrono::high_resolution_clock::now();\n\
    normal_linear_regression(x, y, slope, intercept);\n\
    auto stop = chrono::high_resolution_clock::now();\n\
    auto duration = chrono::duration_cast<chrono::microseconds>(stop - start);\n\
    cout << \"Normal linear regression took \" << duration.count() << \" microseconds.\" << endl;\n\
    // Perform parallel linear regression using OpenMP and measure the time it takes\n\
    start = chrono::high_resolution_clock::now();\n\
    parallel_linear_regression(x, y, slope, intercept);\n\
    stop = chrono::high_resolution_clock::now();\n\
    duration = chrono::duration_cast<chrono::microseconds>(stop - start);\n\
    cout << \"Parallel linear regression using OpenMP took \" << duration.count() << \" microseconds.\" << endl;\n\
    return 0;\n\
}\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h12()
def  h13():
  s="#include <bits/stdc++.h>\n\
#include <omp.h>\n\
using namespace std;\n\
struct Point{\n\
	int val;	 \n\
	double x, y;	 \n\
	double distance; \n\
};\n\
bool comparison(Point a, Point b){\n\
	return (a.distance < b.distance);\n\
}\n\
int classifyAPoint(Point arr[], int n, int k, Point p){\n\
	for (int i = 0; i < n; i++){\n\
		arr[i].distance = sqrt((arr[i].x - p.x) * (arr[i].x - p.x) + (arr[i].y - p.y) * (arr[i].y - p.y));\n\
	}\n\
	sort(arr, arr+n, comparison);\n\
	int freq1 = 0;	 \n\
	int freq2 = 0;	\n\
	for (int i = 0; i < k; i++){\n\
		if (arr[i].val == 0){\n\
			freq1++;\n\
		}\n\
		else if (arr[i].val == 1){\n\
			freq2++;\n\
		}\n\
	}\n\
	return (freq1 > freq2 ? 0 : 1);\n\
}\n\
int classifyAPointParallel(Point arr[], int n, int k, Point p){\n\
	#pragma omp parallel\n\
	for (int i = 0; i < n; i++){\n\
		arr[i].distance = sqrt((arr[i].x - p.x) * (arr[i].x - p.x) + (arr[i].y - p.y) * (arr[i].y - p.y));\n\
	}\n\
	sort(arr, arr+n, comparison);\n\
	int freq1 = 0;	 \n\
	int freq2 = 0;	\n\
	for (int i = 0; i < k; i++){\n\
		if (arr[i].val == 0){\n\
		#pragma omp critical\n\
			freq1++;\n\
		}\n\
		else if (arr[i].val == 1){\n\
		#pragma omp critical\n\
			freq2++;\n\
		}\n\
	}\n\
	return (freq1 > freq2 ? 0 : 1);\n\
}\n\
int main(){\n\
	cout << \"Enter number of points: \";\n\
	int n;\n\
	cin >> n; \n\
	Point arr[n];\n\
	for(int i=0;i<n;i++){\n\
		cin >> arr[i].x;\n\
		cin >> arr[i].y;\n\
		cin >> arr[i].val; \n\
	}\n\
	Point p;\n\
	cout << \"Enter x and y co-ordinate of point P: \";\n\
	cin >> p.x >> p.y;\n\
	int k;\n\
	cout << \"Enter value of k: \";\n\
	cin >> k;\n\
	double start=0, end =0, dur = 0;\n\
	cout << \"For serial KNN: \" << endl;\n\
	start = omp_get_wtime();\n\
	cout << \"The value classified to unknown point i.e. the point belongs to group: \" << classifyAPoint(arr, n, k, p) << endl;\n\
	end = omp_get_wtime();\n\
	dur = end - start;\n\
	cout << \"Time duration: \" << dur << endl;\n\
	cout << \"For parallel KNN: \" << endl;\n\
	start = omp_get_wtime();\n\
	cout << \"The value classified to unknown point i.e. the point belongs to group: \" << classifyAPointParallel(arr, n, k, p) << endl;\n\
	end = omp_get_wtime();\n\
	dur = end - start;\n\
	cout << \"Time duration: \" << dur << endl;\n\
	/*\n\
	Sample Input\n\
	1 12 0\n\
	2 5 0\n\
	5 3 1\n\
	3 2 1\n\
	3 6 0\n\
	1.5 9 1\n\
	7 2 1\n\
	6 1 1\n\
	3.8 3 1\n\
	3 10 0\n\
	5.6 4 1\n\
	4 2 1\n\
	3.5 8 0\n\
	2 11 0\n\
	2 5 1\n\
	2 9 0\n\
	1 7 0\n\
	*/\n\
	return 0;\n\
}\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h13()
def  h14():
  s="%%cu\n\
#include <bits/stdc++.h>\n\
#include <algorithm>\n\
#include <cuda.h>\n\
#include<omp.h>\n\
using namespace std;\n\
int knapSack(int W, int wt[], int val[], int n)\n\
{\n\
    // Base Case\n\
    if (n == 0 || W == 0)\n\
        return 0;\n\
    // If weight of the nth item is more than\n\
    // Knapsack capacity W, then this item cannot\n\
    // be included in the optimal solution\n\
    if (wt[n - 1] > W)\n\
        return knapSack(W, wt, val, n - 1);\n\
    // Return the maximum of two cases:\n\
    // (1) nth item included\n\
    // (2) not included\n\
    else\n\
        return max(\n\
            val[n - 1]\n\
                + knapSack(W - wt[n - 1], wt, val, n - 1),\n\
            knapSack(W, wt, val, n - 1));\n\
}\n\
// Kernel function to solve the knapsack problem in parallel\n\
_global_ void knapsack(int n, int capacity, int* weights, int* values, int* solution, int* start) \n\
{\n\
    // Calculate the thread index\n\
    int tid = blockIdx.x * blockDim.x + threadIdx.x;\n\
    // Check if the thread index is within the valid range\n\
    if (tid >= capacity + 1) \n\
    {\n\
        return;\n\
    }\n\
    // Iterate over the items, starting from the assigned start index for this thread\n\
    for (int i = start[tid]; i < n; i++) \n\
    {\n\
        // Check if the current item can be added to the knapsack\n\
        if (weights[i] <= tid)\n\
        {\n\
            // Calculate the temporary value if the current item is added\n\
            int temp = solution[tid - weights[i]] + values[i];\n\
            // Update the solution if the temporary value is higher\n\
            if (temp > solution[tid]) \n\
            {\n\
                solution[tid] = temp;\n\
                start[tid] = i;\n\
            }\n\
        }\n\
    }\n\
}\n\
int main() \n\
{\n\
    int n = 1000;\n\
    int capacity = 17;\n\
    int weights[n];\n\
    int values[n];\n\
    std::random_device rd;\n\
    std::mt19937 gen(rd());\n\
    int min = 1;  // Minimum value\n\
    int max = 100;  // Maximum value\n\
    std::uniform_int_distribution<> dis(min, max);\n\
    for (int i = 0; i < n; ++i) \n\
    {\n\
        weights[i] = dis(gen);\n\
    }\n\
    std::uniform_int_distribution<> dis1(min, max);\n\
    for (int i = 0; i < n; ++i) \n\
    {\n\
        values[i] = dis1(gen);\n\
    }\n\
    // Allocate memory on the GPU for variables\n\
    int* gpu_capacity, *gpu_weights, *gpu_values, *gpu_solution, *gpu_start;\n\
    cudaMalloc(&gpu_capacity, sizeof(int));\n\
    cudaMalloc(&gpu_weights, n * sizeof(int));\n\
    cudaMalloc(&gpu_values, n * sizeof(int));\n\
    cudaMalloc(&gpu_solution, (capacity + 1) * sizeof(int));\n\
    cudaMalloc(&gpu_start, (capacity + 1) * sizeof(int));\n\
    // Copy input data from host to device\n\
    cudaMemcpy(gpu_capacity, &capacity, sizeof(int), cudaMemcpyHostToDevice);\n\
    cudaMemcpy(gpu_weights, weights, n * sizeof(int), cudaMemcpyHostToDevice);\n\
    cudaMemcpy(gpu_values, values, n * sizeof(int), cudaMemcpyHostToDevice);\n\
    int threadsPerBlock = 256;\n\
    int blocksPerGrid = (capacity + threadsPerBlock - 1) / threadsPerBlock;\n\
    auto start = std::chrono::high_resolution_clock::now();\n\
    // Launch the kernel function on the GPU\n\
    knapsack <<<blocksPerGrid, threadsPerBlock>>>(n, capacity, gpu_weights, gpu_values, gpu_solution, gpu_start);\n\
    int* solution = new int[capacity + 1];\n\
    cudaMemcpy(solution, gpu_solution, (capacity + 1) * sizeof(int), cudaMemcpyDeviceToHost);\n\
    cout << \"Maximum Value: \" << solution[capacity] << endl;\n\
    auto end = std::chrono::high_resolution_clock::now();\n\
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();\n\
    // Print the execution time\n\
    std::cout << \"Execution Time for parallel knapsack: \" << duration << \" microseconds\" << std::endl;\n\
    start = std::chrono::high_resolution_clock::now();\n\
    cout <<\"maximum value \" <<knapSack(capacity, weights, values, n)<<endl;\n\
    end = std::chrono::high_resolution_clock::now();\n\
    duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();\n\
    // Print the execution time\n\
    std::cout << \"Execution Time for serial knapsack : \" << duration << \" microseconds\" << std::endl;\n\
    cudaFree(gpu_capacity);\n\
    cudaFree(gpu_weights);\n\
    cudaFree(gpu_values);\n\
    cudaFree(gpu_solution);\n\
    cudaFree(gpu_start);\n\
    delete[] solution;\n\
    return 0;\n\
}\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\+\n\n\
\\"
  print(s)
h14()