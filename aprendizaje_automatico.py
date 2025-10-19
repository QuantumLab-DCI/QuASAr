import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, MinMaxScaler, MaxAbsScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.semi_supervised import LabelPropagation
from scipy.sparse import csr_matrix
from keras.layers import BatchNormalization
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error
from keras.regularizers import l1, l2
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers import Dense, GaussianNoise
from keras import backend as K
from keras.layers import Input
from keras.models import Model
from sklearn.neighbors import KNeighborsClassifier
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers.convolutional import Conv1D, MaxPooling1D
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt
from keras.optimizers import Adam


def entrenarRegresionLineal(nombreDataset):
    dataset = pd.read_csv(nombreDataset)
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values
    X = transformarDataset(X,[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1)
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    return regressor

def transformarDataset(x,posicionesDataset):
    ct = ColumnTransformer([('one_hot_encoder', OneHotEncoder(),posicionesDataset)], remainder='passthrough')
    x = ct.fit_transform(x)
    return x

def entrenarArbolDecision(nombreDataset, posVariablesIndependientes):
    dataset = pd.read_csv(nombreDataset)
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values
    X = transformarDataset(X, posVariablesIndependientes)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1)
    dtree = DecisionTreeClassifier()
    dtree.fit(X_train, y_train)
    return dtree


def predecirResultadoML(model, datosApredecir):
    resultado = pd.read_csv(datosApredecir, header=None).iloc[:, :].values
    prediccion = model.predict(transformarDataset(resultado, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    resultado = resultado.tolist()
    for indice, puntoVariacion in enumerate(resultado):
        puntoVariacion.append(prediccion[indice])
    return resultado



def guardarPredicciones(dataset, nombreArchivo):
    dataset = sorted(dataset, key=lambda x: x[10])
    with open(nombreArchivo, 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(dataset)

def aprendizajeSemiAutomatizado(datasetEtiquetado, datasetNoEtiquetado):
    etiquetados = pd.read_csv(datasetEtiquetado)
    noEtiquetados = pd.read_csv(datasetNoEtiquetado).iloc[:, :].values
    X_etiquetado = etiquetados.iloc[:, :-1].values
    y_etiquetado = etiquetados.iloc[:, -1].values
    X_etiquetado = transformarDataset(X_etiquetado, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_noetiquetado = transformarDataset(noEtiquetados, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train_labeled, X_test_labeled, y_train_labeled, y_test_labeled = train_test_split(X_etiquetado, y_etiquetado,test_size=1, random_state=42)
    model = LabelPropagation()
    model.fit(X=np.vstack((X_train_labeled, X_noetiquetado)), y=np.concatenate((y_train_labeled, [-1] * len(X_noetiquetado))))
    return model

def entrenarRegresionLinealRegularizadaLasso(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    X = transformarDataset(X, [0,1,2,3,4,5,6, 7, 8, 9])
    lasso = LassoCV(cv=5, random_state=0)
    # entrena el modelo con los datos de entrenamiento
    lasso.fit(X,y)
    return lasso

def entrenarArbolesAleatorios(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    X = transformarDataset(X, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    rf = RandomForestClassifier(n_estimators=40, random_state=0)
    rf.fit(X_train, y_train)
    return rf

def entrenarArbolesAleatoriosRegresion(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    X = transformarDataset(X, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    rf = RandomForestRegressor(n_estimators=40, random_state=0)
    rf.fit(X_train, y_train)
    return rf

def entrenarArbolesAleatoriosRegresion(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    X = transformarDataset(X, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    rf = RandomForestRegressor(n_estimators=40, random_state=0)
    rf.fit(X_train, y_train)
    return rf


def entrenarNaiveBayes(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    X = transformarDataset(X, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    gnb = GaussianNB()
    gnb.fit(X_train, y_train)
    return gnb



def entrenarRedesNeuronales(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    X = transformarDataset(X, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)

    def custom_activation(x):
        return K.relu(x, alpha=0.0, max_value=None)
    model = Sequential()
    model.add(Dense(1, input_dim=X.shape[1], activation=custom_activation))
    model.compile(loss='mean_squared_error', optimizer='sgd')
    model.fit(X_train, y_train, epochs=650, batch_size=10)
    return model

def predecirResultadoRedesNeuronales(model, datosApredecir):
    resultado = pd.read_csv(datosApredecir, header=None).iloc[:, :].values
    prediccion = model.predict(transformarDataset(resultado, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    resultado = resultado.tolist()
    for indice, puntoVariacion in enumerate(resultado):
        puntoVariacion.append(prediccion[indice][0])
    return resultado


def entrenarKvecinos(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    X = transformarDataset(X, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)
    return knn


def arbolesAleatoriosInverso(dataset, dato):
    data = pd.read_csv(dataset)
    #X = data.iloc[:, :-1]  # Variables independientes
    y = data.iloc[:, -1].values  # Variable dependiente
    y = y.reshape(-1, 1)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    X = data.iloc[:, :-1].apply(lambda x: ",".join(x), axis=1)
    rf.fit(y, X)
    dato = np.array([dato]).reshape(-1, 1)
    return rf.predict(dato).tolist()[0].split(",")


def obtenerJSONPrediccion(data):
    reconfiguracion = {}
    for caracteristica in data:
        estado =False
        if " activada" in caracteristica:
            estado = True
            caracteristica = caracteristica.replace(" activada", "")
        else:
            caracteristica = caracteristica.replace(" desactivada", "")
        print(caracteristica)
        reconfiguracion.update({caracteristica : estado})
    return reconfiguracion


def autoencoder():
    # Definir los parámetros de la red
    input_dim = 10  # Número de características de entrada
    hidden_dim = 256  # Número de neuronas en la capa oculta
    latent_dim = 2  # Número de dimensiones en la representación latente

    # Definir la estructura de la red
    inputs = tf.keras.layers.Input(shape=(input_dim,))
    encoder = tf.keras.layers.Dense(hidden_dim, activation='relu')(inputs)
    z = tf.keras.layers.Dense(latent_dim, activation='linear')(encoder)
    decoder = tf.keras.layers.Dense(hidden_dim, activation='relu')(z)
    outputs = tf.keras.layers.Dense(input_dim, activation='linear')(decoder)

    # Definir el modelo
    autoencoder = tf.keras.models.Model(inputs=inputs, outputs=outputs)

    # Compilar el modelo
    autoencoder.compile(optimizer='adam', loss='mse')

    # Cargar los datos de entrenamiento etiquetados
    train_labeled_data = pd.read_csv('data/dataset.csv')
    x_train_labeled = train_labeled_data.iloc[:, :-1].values
    x_train_labeled = transformarDataset(x_train_labeled, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    y_train_labeled = train_labeled_data.iloc[:, -1].values
    y_train_labeled = np.reshape(y_train_labeled, (-1, 1))

    # Cargar los datos de entrenamiento no etiquetados
    train_unlabeled_data = pd.read_csv('data/datos.csv')
    x_train_unlabeled = train_unlabeled_data.iloc[:, :].values
    x_train_unlabeled = transformarDataset(x_train_unlabeled, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    # Cargar los datos de prueba etiquetados
    test_data = pd.read_csv('data/datos_evaluacionmodelo.csv')
    x_test = test_data.iloc[:, :-1].values
    y_test = test_data.iloc[:, -1].values

    # Entrenar el modelo
    autoencoder.fit(x=np.concatenate((x_train_labeled, x_train_unlabeled), axis=0),
                    y=np.concatenate((y_train_labeled, np.zeros((x_train_unlabeled.shape[0], 1))), axis=0), batch_size=32, epochs=10,
                    validation_data=(x_test, y_test))
    return autoencoder

def entrenarRedNeuronalConvolucional():
    data = pd.read_csv('data/dataset.csv')
    X = data.iloc[:,:-1].values  # características
    y = data.iloc[:,-1 ].values  # objetivo
    X = transformarDataset(X, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    X_train_cnn = np.expand_dims(X_train, axis=-1)
    X_test_cnn = np.expand_dims(X_test, axis=-1)

    input_shape = X_train_cnn.shape[1:]

    model = Sequential()
    model.add(Conv1D(32, 3, activation='relu', input_shape=input_shape))
    model.add(Conv1D(64, 3, activation='relu'))
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    loss, accuracy = model.evaluate(X_test_cnn, y_test)
    print(f"Loss: {loss}, Accuracy: {accuracy}")


def funcion():
    # Cargar el conjunto de datos grande
    df_grande = pd.read_csv('data/emisiones_aire_sinfiltrar.csv')
    x_grande = df_grande.iloc[:,:-1].values  # características
    y_grande = df_grande.iloc[:,-1 ].str.replace(',', '.').astype(float).values
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5])

    # Cargar el conjunto de datos pequeño
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque = df_peque.iloc[:,:-1].values  # características
    y_peque = df_peque.iloc[:,-1 ].values
    x_peque = transformarDataset(x_peque, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    # Dividir los datos en entrenamiento y prueba
    x_train_grande, x_test_grande, y_train_grande, y_test_grande = train_test_split(x_grande, y_grande, test_size=0.2,
                                                                                    random_state=42)
    x_train_peque, x_test_peque, y_train_peque, y_test_peque = train_test_split(x_peque, y_peque, test_size=0.2,
                                                                                random_state=42)

    # Escalar los datos
    scaler = StandardScaler(with_mean=False)
    x_train_grande = scaler.fit_transform(x_train_grande)
    x_test_grande = scaler.transform(x_test_grande)
    x_train_peque = scaler.fit_transform(x_train_peque)
    x_test_peque = scaler.transform(x_test_peque)

    # Crear y entrenar la MLP con el conjunto de datos grande
    input_dim_grande = x_train_grande.shape[1]
    modelo = Sequential([
        Dense(128, activation='relu', input_shape=(input_dim_grande,)),
        Dense(64, activation='relu'),
        Dense(1, activation='linear'),
    ])

    modelo.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

    modelo.fit(x_train_grande, y_train_grande, epochs=10, validation_data=(x_test_grande, y_test_grande))

    modelo_peque = Sequential()
    modelo_peque.add(Dense(128, input_dim=10, activation='relu'))
    modelo_peque.add(Dense(64, activation='relu'))
    modelo_peque.add(Dense(32, activation='relu'))
    #modelo_peque.add(Dense(1, activation='linear'))

    modelo_peque.compile(loss='mean_squared_error', optimizer='adam')
    for i in range(len(modelo.layers) - 1):
        modelo_peque.layers[i].set_weights(modelo.layers[i].get_weights())
    modelo_peque.fit(x_train_peque, y_train_peque, epochs=10, validation_data=(x_test_peque, y_test_peque))

    # Evaluar el rendimiento del modelo en el conjunto de datos pequeño
    mae = modelo_peque.evaluate(x_test_peque, y_test_peque)
    print(f'Mean Absolute Error: {mae:.4f}')

def create_base_model(input_dim):
    inputs = Input(shape=(input_dim,))
    x = Dense(128, activation='relu')(inputs)
    x = Dense(64, activation='relu')(x)
    x = Dense(32, activation='relu')(x)
    return Model(inputs=inputs, outputs=x)

def redesNeuronalesFinales():
    df_grande = pd.read_csv('data/emisiones_aire_sinfiltrar.csv')
    x_grande = df_grande.iloc[:, :-1].values  # características
    y_grande = df_grande.iloc[:, -1].str.replace(',', '.').astype(float).values
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5])

    # Cargar el conjunto de datos pequeño
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    x_peque = transformarDataset(x_peque, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    # Dividir los datos en entrenamiento y prueba
    x_train_grande, x_test_grande, y_train_grande, y_test_grande = train_test_split(x_grande, y_grande, test_size=0.2,
                                                                                    random_state=42)
    x_train_peque, x_test_peque, y_train_peque, y_test_peque = train_test_split(x_peque, y_peque, test_size=0.2,
                                                                                random_state=42)

    # Escalar los datos
    scaler = StandardScaler(with_mean=False)
    x_train_grande = scaler.fit_transform(x_train_grande)
    x_test_grande = scaler.transform(x_test_grande)
    x_train_peque = scaler.fit_transform(x_train_peque)
    x_test_peque = scaler.transform(x_test_peque)

    base_model_grande = create_base_model(x_train_grande.shape[1])
    base_model_peque = create_base_model(10)
    output_grande = Dense(1, activation='linear')(base_model_grande.output)
    modelo_grande = Model(inputs=base_model_grande.input, outputs=output_grande)
    modelo_grande.compile(loss='mean_squared_error', optimizer='adam')
    modelo_grande.fit(x_train_grande, y_train_grande, epochs=10, validation_data=(x_test_grande, y_test_grande))
    for i, layer in enumerate(base_model_grande.layers):
        base_model_peque.layers[i].set_weights(layer.get_weights())
    output_peque = Dense(1, activation='linear')(base_model_peque.output)
    modelo_peque = Model(inputs=base_model_peque.input, outputs=output_peque)
    modelo_peque.compile(loss='mean_squared_error', optimizer='adam')
    modelo_peque.fit(x_train_peque, y_train_peque, epochs=10, validation_data=(x_test_peque, y_test_peque))
    mae = modelo_peque.evaluate(x_test_peque, y_test_peque)
    print(f'Mean Absolute Error: {mae:.4f}')

def autoEncoderRedesNeuronales():
    df_grande = pd.read_csv('data/emisiones_aire_sinfiltrar.csv')
    x_grande = df_grande.iloc[:, :-1].values  # características
    y_grande = df_grande.iloc[:, -1].str.replace(',', '.').astype(float).values
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5])

    # Cargar el conjunto de datos pequeño
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    x_peque = transformarDataset(x_peque, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    encoding_dim = x_peque.shape[1]

    # Dividir los datos en entrenamiento y prueba
    x_train_grande, x_test_grande, y_train_grande, y_test_grande = train_test_split(x_grande, y_grande, test_size=0.2,
                                                                                    random_state=42)
    x_train_peque, x_test_peque, y_train_peque, y_test_peque = train_test_split(x_peque, y_peque, test_size=0.2,
                                                                                random_state=42)

    # Escalar los datos
    x_train_grande = tf.convert_to_tensor(x_train_grande.toarray())
    x_test_grande = tf.convert_to_tensor(x_test_grande.toarray())
    x_peque = csr_matrix(x_peque)
    x_test_peque = tf.convert_to_tensor(x_test_peque)

    input_dim = x_train_grande.shape[1]

    # Capa de entrada
    input_data = Input(shape=(input_dim,))

    # Capa de codificación
    encoded = Dense(encoding_dim, activation='relu')(input_data)

    # Capa de decodificación
    decoded = Dense(input_dim, activation='linear')(encoded)

    # Modelo autoencoder completo
    autoencoder = Model(input_data, decoded)

    # Modelo de codificación (reducido)
    encoder = Model(input_data, encoded)

    autoencoder.compile(optimizer='adam', loss='mean_squared_error')
    autoencoder.fit(x_train_grande, x_train_grande, epochs=50, batch_size=256,
                    validation_data=(x_test_grande, x_test_grande))

    print("x_train_grande shape:", x_train_grande.shape)
    print("x_test_grande shape:", x_test_grande.shape)
    print("x_train_peque shape:", x_train_peque.shape)
    print("x_test_peque shape:", x_test_peque.shape)
    x_train_peque_encoded = encoder.predict(x_train_peque)
    x_test_peque_encoded = encoder.predict(x_test_peque)

    regression_model = Sequential()
    regression_model.add(Dense(128, activation='relu', input_shape=(encoding_dim,)))
    regression_model.add(Dense(64, activation='relu'))
    regression_model.add(Dense(1))

    regression_model.compile(optimizer='adam', loss='mean_squared_error')
    regression_model.fit(x_train_peque_encoded, y_train_peque, epochs=10,
                         validation_data=(x_test_peque_encoded, y_test_peque))


def autoEncoderRedesNeuronales2():
    # ... (código previo omitido para facilitar la lectura)
    df_grande = pd.read_csv('data/emisiones_aire_sinfiltrar.csv')
    x_grande = df_grande.iloc[:, :-1].values  # características
    y_grande = df_grande.iloc[:, -1].str.replace(',', '.').astype(float).values
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5])
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    x_peque = transformarDataset(x_peque, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    x_train_grande, x_test_grande, y_train_grande, y_test_grande = train_test_split(x_grande, y_grande, test_size=0.2,
                                                                                    random_state=42)
    x_train_peque, x_test_peque, y_train_peque, y_test_peque = train_test_split(x_peque, y_peque, test_size=0.2,
                                                                                random_state=42)

    # Cargar el conjunto de datos pequeño
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    x_peque = transformarDataset(x_peque, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    # Autoencoder para el conjunto de datos grande
    scaler = MaxAbsScaler()
    x_train_grande_norm = scaler.fit_transform(x_train_grande)
    x_train_grande = tf.convert_to_tensor(x_train_grande_norm.toarray(), dtype=tf.float32)
    x_test_grande_norm = scaler.transform(x_test_grande)
    x_test_grande = tf.convert_to_tensor(x_test_grande_norm.toarray(), dtype=tf.float32)

    scalerMinmax = MinMaxScaler()
    x_train_peque_norm = scalerMinmax.fit_transform(x_train_peque)
    x_train_peque = tf.convert_to_tensor(x_train_peque_norm, dtype=tf.float32)
    x_test_peque_norm = scalerMinmax.transform(x_test_peque)
    x_test_peque = tf.convert_to_tensor(x_test_peque_norm, dtype=tf.float32)

    input_dim_grande = x_train_grande.shape[1]
    input_data_grande = Input(shape=(input_dim_grande,))
    encoded_grande = Dense(x_peque.shape[1], activation='relu')(input_data_grande)
    decoded_grande = Dense(input_dim_grande, activation='linear')(encoded_grande)
    autoencoder_grande = Model(input_data_grande, decoded_grande)
    encoder_grande = Model(input_data_grande, encoded_grande)
    autoencoder_grande.compile(optimizer='adam', loss='mean_squared_error')
    autoencoder_grande.fit(x_train_grande, x_train_grande, epochs=50, batch_size=256,
                           validation_data=(x_test_grande, x_test_grande))



    input_dim_peque = x_train_peque.shape[1]
    input_data_peque = Input(shape=(input_dim_peque,))
    resized_peque = Dense(input_dim_grande, activation='linear')(input_data_peque)
    encoded_peque = encoder_grande(resized_peque)
    decoded_peque = Dense(input_dim_peque, activation='linear')(encoded_peque)
    autoencoder_peque = Model(input_data_peque, decoded_peque)
    encoder_peque = Model(input_data_peque, encoded_peque)
    autoencoder_peque.compile(optimizer='adam', loss='mean_squared_error')

    autoencoder_peque.fit(x_train_peque, x_train_peque, epochs=50, batch_size=256,
                          validation_data=(x_test_peque, x_test_peque))

    x_train_peque_encoded = encoder_peque.predict(x_train_peque)
    x_test_peque_encoded = encoder_peque.predict(x_test_peque)

    # ... (código de regresión no modificado)
    regression_model = Sequential()
    #regression_model.add(GaussianNoise(0.01, input_shape=(x_train_peque.shape[1],)))
    regression_model.add(Dense(256, activation='relu', input_shape=(x_train_peque.shape[1],), kernel_regularizer=l1(0.001)))
    regression_model.add(BatchNormalization())
    #regression_model.add(Dropout(0.3))
    #regression_model.add(Dense(256, activation='relu', kernel_regularizer=l2(0.001)))
    #regression_model.add(Dropout(0.3))
    regression_model.add(Dense(128, activation='relu'))
    regression_model.add(BatchNormalization())
    #regression_model.add(Dropout(0.3))
    regression_model.add(Dense(64, activation='relu'))
    regression_model.add(BatchNormalization())
    #regression_model.add(Dropout(0.3))
    regression_model.add(Dense(32, activation='relu'))
    regression_model.add(BatchNormalization())
    regression_model.add(Dense(1))

    optimizer = keras.optimizers.Adam(learning_rate=0.01)

    regression_model.compile(optimizer=optimizer, loss='mean_squared_error')
    regression_model.fit(x_train_peque_encoded, y_train_peque, epochs=5000,
                         validation_data=(x_test_peque_encoded, y_test_peque))


def entrenamientoPorEtapas():
    # ... (código previo omitido para facilitar la lectura)
    df_grande = pd.read_csv('data/emisiones_aire_filtroMP.csv')
    x_grande = df_grande.iloc[:, :-1].values  # características
    y_grande = df_grande.iloc[:, -1].str.replace(',', '.').astype(float).values
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5])
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    x_peque = transformarDataset(x_peque, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    x_train_grande, x_test_grande, y_train_grande, y_test_grande = train_test_split(x_grande, y_grande, test_size=0.2,
                                                                                    random_state=42)
    x_train_peque, x_test_peque, y_train_peque, y_test_peque = train_test_split(x_peque, y_peque, test_size=0.2,
                                                                                random_state=42)
    scaler = MaxAbsScaler()
    x_train_grande_norm = scaler.fit_transform(x_train_grande)
    x_train_grande = tf.convert_to_tensor(x_train_grande_norm.toarray(), dtype=tf.float32)
    x_test_grande_norm = scaler.transform(x_test_grande)
    x_test_grande = tf.convert_to_tensor(x_test_grande_norm.toarray(), dtype=tf.float32)

    scalerMinmax = MinMaxScaler()
    x_train_peque_norm = scalerMinmax.fit_transform(x_train_peque)
    x_train_peque = tf.convert_to_tensor(x_train_peque_norm, dtype=tf.float32)
    x_test_peque_norm = scalerMinmax.transform(x_test_peque)
    x_test_peque = tf.convert_to_tensor(x_test_peque_norm, dtype=tf.float32)

    input_dim_grande = x_train_grande.shape[1]
    input_data_grande = Input(shape=(input_dim_grande,))
    hidden_layer_grande = Dense(128, activation='relu')(input_data_grande)
    #hidden_layer_grande = Dropout(0.1)(hidden_layer_grande)  # Añade Dropout
    hidden_layer_grande = BatchNormalization()(hidden_layer_grande)
    hidden_layer_grande = Dense(64, activation='relu')(hidden_layer_grande)
    #idden_layer_grande = Dropout(0.1)(hidden_layer_grande)  # Añade Dropout
    hidden_layer_grande = Dense(32, activation='relu')(hidden_layer_grande)
    hidden_layer_grande = Dense(16, activation='relu')(hidden_layer_grande)
    hidden_layer_grande = Dense(8, activation='relu')(hidden_layer_grande)
    output_layer_grande = Dense(1)(hidden_layer_grande)

    model_grande = Model(inputs=input_data_grande, outputs=output_layer_grande)
    #optimizer = keras.optimizers.Adam(learning_rate=0.03)
    optimizer = keras.optimizers.Adagrad(learning_rate=0.01)
    model_grande.compile(optimizer= optimizer, loss='mean_squared_error')

    model_grande.fit(x_train_grande, y_train_grande, epochs=200, batch_size=32,
                     validation_data=(x_test_grande, y_test_grande))
    # Obtén los pesos de la capa oculta
    hidden_layer_weights = model_grande.layers[1].get_weights()

    # Crea un nuevo modelo que utiliza estos pesos para transformar los datos
    input_data_features = Input(shape=(input_dim_grande,))
    features = Dense(128, activation='relu', weights=hidden_layer_weights)(input_data_features)
    feature_extractor = Model(inputs=input_data_features, outputs=features)

    input_dim_peque = x_train_peque.shape[1]
    input_data_peque_resized = Input(shape=(input_dim_peque,))
    resized_layer = Dense(input_dim_grande, activation='linear')(input_data_peque_resized)
    feature_extractor_resized = Model(inputs=input_data_peque_resized, outputs=resized_layer)


    # Transforma los datos usando el extractor de características
    x_train_peque_resized = feature_extractor_resized.predict(x_train_peque)
    x_test_peque_resized = feature_extractor_resized.predict(x_test_peque)
    x_train_peque_features = feature_extractor.predict(x_train_peque_resized)
    x_test_peque_features = feature_extractor.predict(x_test_peque_resized)
    input_dim_features = x_train_peque_features.shape[1]
    input_data_peque = Input(shape=(input_dim_features,))
    hidden_layer_peque = Dense(64, activation='relu')(input_data_peque)
    output_layer_peque = Dense(1)(hidden_layer_peque)

    model_peque = Model(inputs=input_data_peque, outputs=output_layer_peque)
    model_peque.compile(optimizer='adam', loss='mean_squared_error')

    model_peque.fit(x_train_peque_features, y_train_peque, epochs=1500, batch_size=32,
                    validation_data=(x_test_peque_features, y_test_peque))

    return predecirResultadoRedesNeuronalesProfundas(model_grande, model_peque, feature_extractor_resized, feature_extractor, "data/datos.csv")


def predecirResultadoRedesNeuronalesProfundas(model_grande, model_peque, feature_extractor_resized, feature_extractor, datosApredecir):
    resultado = pd.read_csv(datosApredecir, header=None).iloc[:, :].values
    resultado_transformado = transformarDataset(resultado, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    resultado_resized = feature_extractor_resized.predict(resultado_transformado)
    resultado_features = feature_extractor.predict(resultado_resized)
    prediccion = model_peque.predict(resultado_features)
    resultado = resultado.tolist()
    for indice, puntoVariacion in enumerate(resultado):
        puntoVariacion.append(prediccion[indice][0])
    return resultado







