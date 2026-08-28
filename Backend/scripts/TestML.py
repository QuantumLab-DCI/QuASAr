import aprendizaje_automatico
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, binarize
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.semi_supervised import LabelPropagation
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error, auc, r2_score
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from keras.models import Sequential
from keras.layers import Dense
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.metrics import roc_auc_score
from sklearn import datasets, metrics, model_selection, svm
import matplotlib.pyplot as plt
from keras.optimizers import Adam

def evaluarAutoencoder():
    data = pd.read_csv("data/dataset.csv")
    X_test = aprendizaje_automatico.transformarDataset(data.iloc[:, :-1].values, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    y_test = data.iloc[:, -1].values
    y_test = np.array(y_test).ravel()
    modelo = aprendizaje_automatico.autoencoder()
    aprendizaje_automatico.guardarPredicciones(aprendizaje_automatico.predecirResultadoML(modelo,"data/datos.csv"),"data/datasetAutoencoder.csv")
def generarCurvasROC():
    data = pd.read_csv("data/dataset.csv")
    X_test = aprendizaje_automatico.transformarDataset(data.iloc[:, :-1].values, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    y_test = data.iloc[:, -1].values
    y_test = np.array(y_test).ravel()
    modelos = [
        aprendizaje_automatico.entrenarRegresionLineal("data/dataset.csv"),
        aprendizaje_automatico.entrenarRedesNeuronales("data/dataset.csv"),
        aprendizaje_automatico.entrenarRegresionLinealRegularizadaLasso("data/dataset.csv")
    ]
    fig, ax = plt.subplots()
    for modelo in modelos:
        # Realiza las predicciones en los datos de prueba
        y_pred = modelo.predict(X_test, probabilities=True)
        y_pred = np.array(y_pred).ravel()
        # Calcula el AUC de la curva ROC
        auc = roc_auc_score(y_test, y_pred, multi_class='ovo', average=None)

        # Traza la curva ROC en el eje
        metrics.plot_roc_curve(modelo, X_test, y_test, ax=ax, name=f'{type(modelo).__name__}, AUC={auc:.2f}')

    # Añade una línea diagonal para representar el clasificador aleatorio
    ax.plot([0, 1], [0, 1], linestyle='--', color='r', label='Clasificador aleatorio')

    # Añade una leyenda y un título al gráfico
    ax.legend()
    ax.set_title('Curvas ROC')

    # Muestra el gráfico
    plt.show()

def generarComparacion():
    data = pd.read_csv("data/dataset.csv")
    X_test = aprendizaje_automatico.transformarDataset(data.iloc[:, :-1].values, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    y_test = data.iloc[:, -1].values
    y_test = np.array(y_test).ravel()
    modelos = [
        aprendizaje_automatico.entrenarRegresionLineal("data/dataset.csv"),
        aprendizaje_automatico.entrenarRedesNeuronales("data/dataset.csv"),
        aprendizaje_automatico.entrenarRegresionLinealRegularizadaLasso("data/dataset.csv")
    ]
    y_predRegresionLineal = modelos[0].predict(X_test)
    y_predRedesNeuronales = modelos[1].predict(X_test)
    y_predRegresionLinealRegularizada = modelos[2].predict(X_test)
    print("regresion lineal", len(y_predRegresionLineal))
    print("redes neuronales", len(y_predRedesNeuronales))
    print("regresion lineal regularizada", len(y_predRegresionLinealRegularizada))
    # Calcular el coeficiente de determinación R^2 para cada modelo
    r2_1 = r2_score(y_test, y_predRegresionLineal)
    r2_2 = r2_score(y_test, y_predRedesNeuronales)
    r2_3 = r2_score(y_test, y_predRegresionLinealRegularizada)

    # Crear el gráfico de dispersión
    #
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_predRegresionLineal, label=f'Modelo regresión lineal múltiple (R²={r2_1:.2f})')
    plt.scatter(y_test, y_predRedesNeuronales, label=f'Modelo redes neuronales (R²={r2_2:.2f})')
    plt.scatter(y_test, y_predRegresionLinealRegularizada, label=f'Modelo regresión lineal regularizada (R²={r2_3:.2f})')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=3)
    plt.xlabel('Valor real')
    plt.ylabel('Predicción')
    plt.title('Comparación de modelos de regresión')
    plt.legend()
    plt.show()

def generarComparacionDatosNoEtiquetados():
    datosApredecir = pd.read_csv("data/datos.csv",header=None)
    resultadoApredecir = aprendizaje_automatico.transformarDataset(datosApredecir.iloc[:, :].values,[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    modelos = [
        aprendizaje_automatico.entrenarRegresionLineal("data/dataset.csv"),
        aprendizaje_automatico.entrenarRedesNeuronales("data/dataset.csv"),
        aprendizaje_automatico.entrenarRegresionLinealRegularizadaLasso("data/dataset.csv")
    ]
    fig, ax = plt.subplots()
    ax.set_xlabel('Valores predichos')
    ax.set_ylabel('Valores reales')
    ax.set_title('Comparación de modelos de regresión')
    contador = [i + 1 for i in range(32)]
    for modelo in modelos:
        y_pred = modelo.predict(resultadoApredecir)
        ax.scatter(contador, y_pred, alpha=0.5,
                   label=type(modelo).__name__)

    ax.legend()
    plt.show()

def generarCurvasROC2():
    data = pd.read_csv("data/dataset.csv")
    X_test = aprendizaje_automatico.transformarDataset(data.iloc[:, :-1].values, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    y_test = data.iloc[:, -1].values
    y_test = np.array(y_test).ravel()
    modelos = [
        aprendizaje_automatico.entrenarRegresionLineal("data/dataset.csv"),
        aprendizaje_automatico.entrenarRedesNeuronales("data/dataset.csv"),
        aprendizaje_automatico.entrenarRegresionLinealRegularizadaLasso("data/dataset.csv")
    ]
    fig, ax = plt.subplots()
    for modelo in modelos:
        # Realiza las predicciones en los datos de prueba
        y_pred = modelo.predict(X_test)
        if type(modelo).__name__ == "LinearRegression":
            y_pred = binarize(y_pred.reshape(1, -1), threshold=0.5)[0]
        else:
            y_pred = modelo.predict(X_test, probabilities=True)
            y_pred = y_pred[:, 1]

        # Calcula el AUC de la curva ROC
        auc = roc_auc_score(y_test, y_pred, multi_class='ovo', average=None)

        # Traza la curva ROC en el eje
        metrics.plot_roc_curve(modelo, X_test, y_test, ax=ax, name=f'{type(modelo).__name__}, AUC={auc:.2f}')

    # Añade una línea diagonal para representar el clasificador aleatorio
    ax.plot([0, 1], [0, 1], linestyle='--', color='r', label='Clasificador aleatorio')

    # Añade una leyenda y un título al gráfico
    ax.legend()
    ax.set_title('Curvas ROC')

    # Muestra el gráfico
    plt.show()

def generarComparacionEvaluacionModelos():
    data = pd.read_csv("data/datos_evaluacionmodelo.csv",header=None)
    X_test = aprendizaje_automatico.transformarDataset(data.iloc[:, :-1].values, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    y_test = data.iloc[:, -1].values
    y_test = np.array(y_test).ravel()
    modelos = [
        aprendizaje_automatico.entrenarRegresionLineal("data/dataset.csv"),
        aprendizaje_automatico.entrenarRedesNeuronales("data/dataset.csv"),
        aprendizaje_automatico.entrenarRegresionLinealRegularizadaLasso("data/dataset.csv")
    ]
    print("largo data",len(X_test))
    y_predRegresionLineal = modelos[0].predict(X_test)
    y_predRedesNeuronales = modelos[1].predict(X_test)
    y_predRegresionLinealRegularizada = modelos[2].predict(X_test)
    print("regresion lineal", len(y_predRegresionLineal))
    print("redes neuronales", len(y_predRedesNeuronales))
    print("regresion lineal regularizada", len(y_predRegresionLinealRegularizada))
    # Calcular el coeficiente de determinación R^2 para cada modelo
    r2_1 = r2_score(y_test, y_predRegresionLineal)
    r2_2 = r2_score(y_test, y_predRedesNeuronales)
    r2_3 = r2_score(y_test, y_predRegresionLinealRegularizada)

    # Crear el gráfico de dispersión
    #
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_predRegresionLineal, label=f'Modelo regresión lineal múltiple (R²={r2_1:.2f})')
    plt.scatter(y_test, y_predRedesNeuronales, label=f'Modelo redes neuronales (R²={r2_2:.2f})')
    plt.scatter(y_test, y_predRegresionLinealRegularizada, label=f'Modelo regresión lineal regularizada (R²={r2_3:.2f})')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=3)
    plt.xlabel('Valor real')
    plt.ylabel('Predicción')
    plt.title('Comparación de modelos de regresión')
    plt.legend()
    plt.show()
def filtrar_csv(input_file, output_file, columna, valor):
    with open(input_file, 'r', newline='', encoding='utf-8') as archivo_entrada:
        with open(output_file, 'w', newline='', encoding='utf-8') as archivo_salida:
            lector = csv.reader(archivo_entrada, delimiter=',')
            escritor = csv.writer(archivo_salida, delimiter=',')

            # Copiar la cabecera del archivo original al archivo filtrado
            cabecera = next(lector)
            escritor.writerow(cabecera)

            # Filtrar y guardar filas en el nuevo archivo
            for fila in lector:
                if fila[columna] == valor:
                    escritor.writerow(fila)





#generarComparacionEvaluacionModelos()
#evaluarAutoencoder()

aprendizaje_automatico.guardarPredicciones(
        aprendizaje_automatico.entrenamientoPorEtapas(),
    "data/datos_redesneuronalesprofundas.csv")

#revisar encoders, quizas puedo agregar el datos csv como el ultimo encoder