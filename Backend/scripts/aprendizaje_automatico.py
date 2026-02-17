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
from keras.layers import Conv1D, MaxPooling1D
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt
from keras.optimizers import Adam


def entrenarRegresionLineal(nombreDataset):
    dataset = pd.read_csv(nombreDataset)
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values
    
    # --- CORRECCIÓN ---
    # Detecta dinámicamente el número de columnas de características
    num_features = X.shape[1]
    indices_features = list(range(num_features))
    X = transformarDataset(X, indices_features)
    # --- FIN CORRECCIÓN ---

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1)
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    return regressor

# --- FUNCIÓN MODIFICADA (Esta corrección ya la tenías) ---
def transformarDataset(x,posicionesDataset):
    """
    Transforma las columnas categóricas usando OneHotEncoder y devuelve un array denso.
    """
    # --- AÑADIR LOG ---
    # print(f"DEBUG [transformarDataset]: Recibidos datos con forma {x.shape}")
    # ------------------
    
    one_hot_enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

    ct = ColumnTransformer(
        [('one_hot_encoder', one_hot_enc, posicionesDataset)],
        remainder='passthrough'
    )

    x_transformed = ct.fit_transform(x)

    # --- AÑADIR LOG ---
    # print(f"DEBUG [transformarDataset]: Datos transformados a forma {x_transformed.shape}")
    # ------------------

    # Aseguramos que el tipo de dato sea float32 para TensorFlow
    return x_transformed.astype(np.float32)

def entrenarArbolDecision(nombreDataset, posVariablesIndependientes):
    dataset = pd.read_csv(nombreDataset)
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values
    
    # Asumimos que 'posVariablesIndependientes' es correcto, si no, necesita corrección dinámica
    X = transformarDataset(X, posVariablesIndependientes)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1)
    dtree = DecisionTreeClassifier()
    dtree.fit(X_train, y_train)
    return dtree


def predecirResultadoML(model, datosApredecir):
    resultado = pd.read_csv(datosApredecir, header=None).iloc[:, :].values
    
    # --- CORRECCIÓN ---
    num_features = resultado.shape[1]
    indices_features = list(range(num_features))
    prediccion = model.predict(transformarDataset(resultado, indices_features))
    # --- FIN CORRECCIÓN ---
    
    resultado = resultado.tolist()
    for indice, puntoVariacion in enumerate(resultado):
        puntoVariacion.append(prediccion[indice])
    return resultado



def guardarPredicciones(dataset, nombreArchivo):
    # Asumiendo que la regla de adaptación está en la última columna
    last_col_index = len(dataset[0]) - 1
    dataset = sorted(dataset, key=lambda x: x[last_col_index])
    with open(nombreArchivo, 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(dataset)

def aprendizajeSemiAutomatizado(datasetEtiquetado, datasetNoEtiquetado):
    etiquetados = pd.read_csv(datasetEtiquetado)
    noEtiquetados = pd.read_csv(datasetNoEtiquetado).iloc[:, :].values
    
    X_etiquetado = etiquetados.iloc[:, :-1].values
    y_etiquetado = etiquetados.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features_etiquetado = X_etiquetado.shape[1]
    indices_etiquetado = list(range(num_features_etiquetado))
    X_etiquetado = transformarDataset(X_etiquetado, indices_etiquetado)
    
    num_features_no_etiquetado = noEtiquetados.shape[1]
    indices_no_etiquetado = list(range(num_features_no_etiquetado))
    X_noetiquetado = transformarDataset(noEtiquetados, indices_no_etiquetado)
    # --- FIN CORRECCIÓN ---
    
    X_train_labeled, X_test_labeled, y_train_labeled, y_test_labeled = train_test_split(X_etiquetado, y_etiquetado,test_size=1, random_state=42)
    model = LabelPropagation()
    model.fit(X=np.vstack((X_train_labeled, X_noetiquetado)), y=np.concatenate((y_train_labeled, [-1] * len(X_noetiquetado))))
    return model

def entrenarRegresionLinealRegularizadaLasso(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features = X.shape[1]
    indices_features = list(range(num_features))
    X = transformarDataset(X, indices_features)
    # --- FIN CORRECCIÓN ---
    lasso = LassoCV(cv=5, random_state=0)
    lasso.fit(X,y)
    return lasso

def entrenarArbolesAleatorios(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features = X.shape[1]
    indices_features = list(range(num_features))
    X = transformarDataset(X, indices_features)
    # --- FIN CORRECCIÓN ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    rf = RandomForestClassifier(n_estimators=40, random_state=0)
    rf.fit(X_train, y_train)
    return rf

# Hay dos funciones duplicadas. He corregido la primera y comentado la segunda.
def entrenarArbolesAleatoriosRegresion(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features = X.shape[1]
    indices_features = list(range(num_features))
    X = transformarDataset(X, indices_features)
    # --- FIN CORRECCIÓN ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    rf = RandomForestRegressor(n_estimators=40, random_state=0)
    rf.fit(X_train, y_train)
    return rf

# def entrenarArbolesAleatoriosRegresion(dataset): # <-- Esta es un duplicado
#     ...


def entrenarNaiveBayes(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features = X.shape[1]
    indices_features = list(range(num_features))
    X = transformarDataset(X, indices_features)
    # --- FIN CORRECCIÓN ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    gnb = GaussianNB()
    gnb.fit(X_train, y_train)
    return gnb



def entrenarRedesNeuronales(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features = X.shape[1]
    indices_features = list(range(num_features))
    X = transformarDataset(X, indices_features)
    # --- FIN CORRECCIÓN ---
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
    # --- CORRECCIÓN ---
    num_features = resultado.shape[1]
    indices_features = list(range(num_features))
    prediccion = model.predict(transformarDataset(resultado, indices_features))
    # --- FIN CORRECCIÓN ---
    resultado = resultado.tolist()
    for indice, puntoVariacion in enumerate(resultado):
        puntoVariacion.append(prediccion[indice][0])
    return resultado


def entrenarKvecinos(dataset):
    data = pd.read_csv(dataset)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features = X.shape[1]
    indices_features = list(range(num_features))
    X = transformarDataset(X, indices_features)
    # --- FIN CORRECCIÓN ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, random_state=0)
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)
    return knn


def arbolesAleatoriosInverso(dataset, dato):
    data = pd.read_csv(dataset)
    y = data.iloc[:, -1].values  # Variable dependiente (la regla)
    y = y.reshape(-1, 1)
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Convierte todas las columnas de características en una sola string
    # .astype(str) es crucial si hay números mezclados con texto
    X = data.iloc[:, :-1].apply(lambda x: ",".join(x.astype(str)), axis=1)
    
    rf.fit(y, X)
    dato = np.array([dato]).reshape(-1, 1)
    return rf.predict(dato).tolist()[0].split(",")


def obtenerJSONPrediccion(data):
    reconfiguracion = {}
    for caracteristica in data:
        estado = False
        if " activada" in caracteristica:
            estado = True
            caracteristica = caracteristica.replace(" activada", "")
        else:
            caracteristica = caracteristica.replace(" desactivada", "")

        # --- INICIO DE LA MODIFICACIÓN ---
        # Normalizamos la clave para que coincida con el resto del sistema
        key_normalizada = caracteristica.replace(" ", "_").lower()
        reconfiguracion.update({key_normalizada : estado})
        # --- FIN DE LA MODIFICACIÓN ---

    return reconfiguracion


def autoencoder():
    # Cargar los datos de entrenamiento etiquetados
    train_labeled_data = pd.read_csv('data/dataset.csv')
    x_train_labeled = train_labeled_data.iloc[:, :-1].values
    # --- CORRECCIÓN ---
    num_features_labeled = x_train_labeled.shape[1]
    indices_labeled = list(range(num_features_labeled))
    x_train_labeled = transformarDataset(x_train_labeled, indices_labeled)
    # --- FIN CORRECCIÓN ---
    y_train_labeled = train_labeled_data.iloc[:, -1].values
    y_train_labeled = np.reshape(y_train_labeled, (-1, 1))

    # Cargar los datos de entrenamiento no etiquetados
    train_unlabeled_data = pd.read_csv('data/datos.csv')
    x_train_unlabeled = train_unlabeled_data.iloc[:, :].values
    # --- CORRECCIÓN ---
    num_features_unlabeled = x_train_unlabeled.shape[1]
    indices_unlabeled = list(range(num_features_unlabeled))
    x_train_unlabeled = transformarDataset(x_train_unlabeled, indices_unlabeled)
    # --- FIN CORRECCIÓN ---

    # Cargar los datos de prueba etiquetados
    test_data = pd.read_csv('data/datos_evaluacionmodelo.csv')
    x_test = test_data.iloc[:, :-1].values
    y_test = test_data.iloc[:, -1].values

    # Definir los parámetros de la red
    input_dim = x_train_labeled.shape[1] # Usar la forma dinámica
    hidden_dim = 256
    latent_dim = 2

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

    # Entrenar el modelo
    autoencoder.fit(x=np.concatenate((x_train_labeled, x_train_unlabeled), axis=0),
                    y=np.concatenate((y_train_labeled, np.zeros((x_train_unlabeled.shape[0], 1))), axis=0), batch_size=32, epochs=10,
                    validation_data=(x_test, y_test))
    return autoencoder

def entrenarRedNeuronalConvolucional():
    data = pd.read_csv('data/dataset.csv')
    X = data.iloc[:,:-1].values  # características
    y = data.iloc[:,-1 ].values  # objetivo
    # --- CORRECCIÓN ---
    num_features = X.shape[1]
    indices_features = list(range(num_features))
    X = transformarDataset(X, indices_features)
    # --- FIN CORRECCIÓN ---
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
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5]) # Mantenido (dataset diferente)

    # Cargar el conjunto de datos pequeño
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque_orig = df_peque.iloc[:,:-1].values  # características
    y_peque = df_peque.iloc[:,-1 ].values
    # --- CORRECCIÓN ---
    num_features_peque = x_peque_orig.shape[1]
    indices_peque = list(range(num_features_peque))
    x_peque = transformarDataset(x_peque_orig, indices_peque)
    # --- FIN CORRECCIÓN ---

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

    # --- CORRECCIÓN ---
    input_dim_peque = x_train_peque.shape[1] # Usar la forma dinámica
    modelo_peque = Sequential()
    modelo_peque.add(Dense(128, input_dim=input_dim_peque, activation='relu'))
    # --- FIN CORRECCIÓN ---
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
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5]) # Mantenido

    # Cargar el conjunto de datos pequeño
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque_orig = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features_peque = x_peque_orig.shape[1]
    indices_peque = list(range(num_features_peque))
    x_peque = transformarDataset(x_peque_orig, indices_peque)
    # --- FIN CORRECCIÓN ---

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
    # --- CORRECCIÓN ---
    base_model_peque = create_base_model(x_train_peque.shape[1]) # Usar la forma dinámica
    # --- FIN CORRECCIÓN ---
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
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5]) # Mantenido

    # Cargar el conjunto de datos pequeño
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque_orig = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features_peque = x_peque_orig.shape[1]
    indices_peque = list(range(num_features_peque))
    x_peque = transformarDataset(x_peque_orig, indices_peque)
    # --- FIN CORRECCIÓN ---
    encoding_dim = x_peque.shape[1]

    # Dividir los datos en entrenamiento y prueba
    x_train_grande, x_test_grande, y_train_grande, y_test_grande = train_test_split(x_grande, y_grande, test_size=0.2,
                                                                                    random_state=42)
    # (El split de 'peque' se hace más abajo)

    # Escalar los datos
    scaler_grande = MaxAbsScaler()
    x_train_grande_norm = scaler_grande.fit_transform(x_train_grande)
    x_test_grande_norm = scaler_grande.transform(x_test_grande)
    # --- CORRECCIÓN (sin .toarray()) ---
    x_train_grande = tf.convert_to_tensor(x_train_grande_norm, dtype=tf.float32)
    x_test_grande = tf.convert_to_tensor(x_test_grande_norm, dtype=tf.float32)

    # x_peque ya es un array denso por transformarDataset
    x_peque = tf.convert_to_tensor(x_peque, dtype=tf.float32)

    input_dim = x_train_grande.shape[1]
    input_data = Input(shape=(input_dim,))
    encoded = Dense(encoding_dim, activation='relu')(input_data)
    decoded = Dense(input_dim, activation='linear')(encoded)
    autoencoder = Model(input_data, decoded)
    encoder = Model(input_data, encoded)
    autoencoder.compile(optimizer='adam', loss='mean_squared_error')
    autoencoder.fit(x_train_grande, x_train_grande, epochs=50, batch_size=256,
                    validation_data=(x_test_grande, x_test_grande))

    # Dividir x_peque (tensor) y y_peque (numpy)
    x_train_peque, x_test_peque, y_train_peque, y_test_peque = train_test_split(x_peque.numpy(), y_peque, test_size=0.2, random_state=42)

    x_train_peque_encoded = encoder.predict(x_train_peque)
    x_test_peque_encoded = encoder.predict(x_test_peque)
    
    print("x_train_grande shape:", x_train_grande.shape)
    print("x_test_grande shape:", x_test_grande.shape)
    print("x_train_peque_encoded shape:", x_train_peque_encoded.shape)
    print("x_test_peque_encoded shape:", x_test_peque_encoded.shape)

    regression_model = Sequential()
    regression_model.add(Dense(128, activation='relu', input_shape=(encoding_dim,)))
    regression_model.add(Dense(64, activation='relu'))
    regression_model.add(Dense(1))

    regression_model.compile(optimizer='adam', loss='mean_squared_error')
    regression_model.fit(x_train_peque_encoded, y_train_peque, epochs=10,
                         validation_data=(x_test_peque_encoded, y_test_peque))


def autoEncoderRedesNeuronales2():
    df_grande = pd.read_csv('data/emisiones_aire_sinfiltrar.csv')
    x_grande = df_grande.iloc[:, :-1].values  # características
    y_grande = df_grande.iloc[:, -1].str.replace(',', '.').astype(float).values
    x_grande = transformarDataset(x_grande, [0, 1, 2, 3, 4, 5]) # Mantenido
    
    df_peque = pd.read_csv('data/dataset.csv')
    x_peque_orig = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    # --- CORRECCIÓN ---
    num_features_peque = x_peque_orig.shape[1]
    indices_peque = list(range(num_features_peque))
    x_peque = transformarDataset(x_peque_orig, indices_peque)
    # --- FIN CORRECCIÓN ---

    x_train_grande, x_test_grande, y_train_grande, y_test_grande = train_test_split(x_grande, y_grande, test_size=0.2,
                                                                                    random_state=42)
    x_train_peque, x_test_peque, y_train_peque, y_test_peque = train_test_split(x_peque, y_peque, test_size=0.2,
                                                                                random_state=42)
    
    # Autoencoder para el conjunto de datos grande
    scaler = MaxAbsScaler()
    x_train_grande_norm = scaler.fit_transform(x_train_grande)
    # --- CORRECCIÓN (sin .toarray()) ---
    x_train_grande = tf.convert_to_tensor(x_train_grande_norm, dtype=tf.float32)
    x_test_grande_norm = scaler.transform(x_test_grande)
    # --- CORRECCIÓN (sin .toarray()) ---
    x_test_grande = tf.convert_to_tensor(x_test_grande_norm, dtype=tf.float32)

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
    # ... (resto de la red) ...
    regression_model.add(Dense(128, activation='relu'))
    regression_model.add(BatchNormalization())
    regression_model.add(Dense(64, activation='relu'))
    regression_model.add(BatchNormalization())
    regression_model.add(Dense(32, activation='relu'))
    regression_model.add(BatchNormalization())
    regression_model.add(Dense(1))

    optimizer = keras.optimizers.Adam(learning_rate=0.01)

    regression_model.compile(optimizer=optimizer, loss='mean_squared_error')
    regression_model.fit(x_train_peque_encoded, y_train_peque, epochs=5000,
                         validation_data=(x_test_peque_encoded, y_test_peque))


def entrenamientoPorEtapas():
    # --- AÑADIR LOGS DE DIAGNÓSTICO ---
    print("\n" + "="*50)
    print("DEBUG [entrenamientoPorEtapas]: INICIANDO ENTRENAMIENTO...")
    
    # Cargar el conjunto de datos grande (pre-entrenamiento)
    df_grande = pd.read_csv('data/emisiones_aire_filtroMP.csv')
    print(f"DEBUG: Cargado 'emisiones_aire_filtroMP.csv'. Forma: {df_grande.shape}")
    
    # Cargar el conjunto de datos pequeño (entrenamiento/afinamiento)
    try:
        df_peque = pd.read_csv('data/dataset.csv')
        print(f"DEBUG: Cargado 'dataset.csv' (ENTRENAMIENTO). Forma: {df_peque.shape}")
    except FileNotFoundError:
        print("ERROR FATAL: No se encontró 'data/dataset.csv'.")
        return
        
    # Cargar datos de predicción (para la función anidada)
    try:
        df_prediccion = pd.read_csv('data/datos.csv', header=None)
        print(f"DEBUG: Cargado 'datos.csv' (PREDICCIÓN). Forma: {df_prediccion.shape}")
    except FileNotFoundError:
        print("ERROR FATAL: No se encontró 'data/datos.csv'.")
        return

    print("DEBUG: Verificación de consistencia de características:")
    # df_peque tiene la columna 'regla_adaptacion' que debe ser restada
    print(f"       Columnas de entrenamiento (dataset.csv): {df_peque.shape[1] - 1}")
    print(f"       Columnas de predicción (datos.csv): {df_prediccion.shape[1]}")
    
    if (df_peque.shape[1] - 1) != df_prediccion.shape[1]:
        print("\n¡ALERTA! Las formas NO COINCIDEN. El programa fallará.")
        print("       'dataset.csv' y 'datos.csv' no tienen el mismo número de características.")
        print("       Solución: Sigue los pasos para regenerar los archivos." + "\n")
    else:
        print("       ¡Las formas COINCIDEN! El pipeline continuará.")
        
    print("="*50 + "\n")
    # --- FIN DE LOGS DE DIAGNÓSTICO ---

    # --- INICIO CORRECCIÓN ---
    x_grande = df_grande.iloc[:, :-1].values  # características
    y_grande = df_grande.iloc[:, -1].str.replace(',', '.').astype(float).values
    # Corrección: Detectar columnas dinámicamente
    indices_grande = list(range(x_grande.shape[1]))
    x_grande = transformarDataset(x_grande, indices_grande)
    
    x_peque_orig = df_peque.iloc[:, :-1].values  # características
    y_peque = df_peque.iloc[:, -1].values
    # Corrección: Detectar columnas dinámicamente
    indices_peque = list(range(x_peque_orig.shape[1]))
    x_peque = transformarDataset(x_peque_orig, indices_peque)
    # --- FIN CORRECCIÓN ---

    x_train_grande, x_test_grande, y_train_grande, y_test_grande = train_test_split(x_grande, y_grande, test_size=0.2,
                                                                                    random_state=42)
    x_train_peque, x_test_peque, y_train_peque, y_test_peque = train_test_split(x_peque, y_peque, test_size=0.2,
                                                                                random_state=42)
    scaler = MaxAbsScaler()
    x_train_grande_norm = scaler.fit_transform(x_train_grande)
    # --- CORRECCIÓN (sin .toarray()) ---
    x_train_grande = tf.convert_to_tensor(x_train_grande_norm, dtype=tf.float32)
    x_test_grande_norm = scaler.transform(x_test_grande)
    # --- CORRECCIÓN (sin .toarray()) ---
    x_test_grande = tf.convert_to_tensor(x_test_grande_norm, dtype=tf.float32)

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

    # 1. Crea la capa Dense SIN los pesos
    feature_layer = Dense(128, activation='relu')

    # 2. Aplica la capa al tensor de entrada
    features = feature_layer(input_data_features)

    # 3. AHORA establece los pesos en la capa ya creada
    feature_layer.set_weights(hidden_layer_weights)

    # El resto del código es igual
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
    
    # --- CORRECCIÓN ---
    num_features = resultado.shape[1]
    indices_features = list(range(num_features))
    resultado_transformado = transformarDataset(resultado, indices_features)
    # --- FIN CORRECCIÓN ---

    resultado_resized = feature_extractor_resized.predict(resultado_transformado)
    resultado_features = feature_extractor.predict(resultado_resized)
    prediccion = model_peque.predict(resultado_features)
    resultado = resultado.tolist()
    for indice, puntoVariacion in enumerate(resultado):
        puntoVariacion.append(prediccion[indice][0])
    return resultado