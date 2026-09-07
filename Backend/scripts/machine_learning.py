"""Legacy machine-learning experiments for adaptation-rule prediction."""

import csv

import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from keras import backend as K
from keras.layers import BatchNormalization, Conv1D, Dense, Flatten, Input
from keras.models import Model, Sequential
from keras.regularizers import l1
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LassoCV, LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, OneHotEncoder, StandardScaler
from sklearn.semi_supervised import LabelPropagation
from sklearn.tree import DecisionTreeClassifier


LABELED_DATASET_PATH = "data/dataset.csv"
CONFIGURATIONS_PATH = "data/configurations.csv"
EVALUATION_DATASET_PATH = "data/model_evaluation_data.csv"
UNFILTERED_EMISSIONS_PATH = "data/unfiltered_air_emissions.csv"
FILTERED_EMISSIONS_PATH = "data/particulate_matter_filtered_air_emissions.csv"


def transform_dataset(data, categorical_columns):
    """One-hot encode categorical columns and return a dense float32 array."""
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    transformer = ColumnTransformer(
        [("one_hot_encoder", encoder, categorical_columns)],
        remainder="passthrough",
    )
    return transformer.fit_transform(data).astype(np.float32)


def _transform_all_features(features):
    return transform_dataset(features, list(range(features.shape[1])))


def train_linear_regression(dataset_path):
    """Train a linear regressor from a labeled dataset."""
    dataset = pd.read_csv(dataset_path)
    features = _transform_all_features(dataset.iloc[:, :-1].values)
    labels = dataset.iloc[:, -1].values
    train_features, _test_features, train_labels, _test_labels = train_test_split(
        features, labels, test_size=1
    )
    model = LinearRegression()
    model.fit(train_features, train_labels)
    return model


def train_decision_tree(dataset_path, categorical_columns):
    """Train a decision-tree classifier from categorical features."""
    dataset = pd.read_csv(dataset_path)
    features = transform_dataset(dataset.iloc[:, :-1].values, categorical_columns)
    labels = dataset.iloc[:, -1].values
    train_features, _test_features, train_labels, _test_labels = train_test_split(
        features, labels, test_size=1
    )
    model = DecisionTreeClassifier()
    model.fit(train_features, train_labels)
    return model


def predict_model_results(model, prediction_data_path):
    """Append model predictions to configuration rows."""
    rows = pd.read_csv(prediction_data_path, header=None).values
    predictions = model.predict(_transform_all_features(rows))
    results = rows.tolist()
    for index, configuration in enumerate(results):
        configuration.append(predictions[index])
    return results


def save_predictions(dataset, output_path):
    """Sort predictions by adaptation rule and write them without a header."""
    adaptation_rule_index = len(dataset[0]) - 1
    sorted_dataset = sorted(dataset, key=lambda row: row[adaptation_rule_index])
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        csv.writer(output_file).writerows(sorted_dataset)


def train_label_propagation(labeled_dataset_path, unlabeled_dataset_path):
    """Train label propagation from labeled and unlabeled rows."""
    labeled_data = pd.read_csv(labeled_dataset_path)
    unlabeled_features = pd.read_csv(unlabeled_dataset_path).values
    labeled_features = _transform_all_features(labeled_data.iloc[:, :-1].values)
    labeled_targets = labeled_data.iloc[:, -1].values
    unlabeled_features = _transform_all_features(unlabeled_features)
    train_features, _test_features, train_targets, _test_targets = train_test_split(
        labeled_features, labeled_targets, test_size=1, random_state=42
    )
    model = LabelPropagation()
    model.fit(
        np.vstack((train_features, unlabeled_features)),
        np.concatenate((train_targets, [-1] * len(unlabeled_features))),
    )
    return model


def train_lasso_regression(dataset_path):
    """Train a cross-validated Lasso regressor."""
    dataset = pd.read_csv(dataset_path)
    features = _transform_all_features(dataset.iloc[:, :-1].values)
    labels = dataset.iloc[:, -1].values
    model = LassoCV(cv=5, random_state=0)
    model.fit(features, labels)
    return model


def train_random_forest_classifier(dataset_path):
    """Train a random-forest classifier."""
    dataset = pd.read_csv(dataset_path)
    features = _transform_all_features(dataset.iloc[:, :-1].values)
    labels = dataset.iloc[:, -1].values
    train_features, _test_features, train_labels, _test_labels = train_test_split(
        features, labels, test_size=1, random_state=0
    )
    model = RandomForestClassifier(n_estimators=40, random_state=0)
    model.fit(train_features, train_labels)
    return model


def train_random_forest_regressor(dataset_path):
    """Train a random-forest regressor."""
    dataset = pd.read_csv(dataset_path)
    features = _transform_all_features(dataset.iloc[:, :-1].values)
    labels = dataset.iloc[:, -1].values
    train_features, _test_features, train_labels, _test_labels = train_test_split(
        features, labels, test_size=1, random_state=0
    )
    model = RandomForestRegressor(n_estimators=40, random_state=0)
    model.fit(train_features, train_labels)
    return model


def train_naive_bayes(dataset_path):
    """Train a Gaussian naive Bayes classifier."""
    dataset = pd.read_csv(dataset_path)
    features = _transform_all_features(dataset.iloc[:, :-1].values)
    labels = dataset.iloc[:, -1].values
    train_features, _test_features, train_labels, _test_labels = train_test_split(
        features, labels, test_size=1, random_state=0
    )
    model = GaussianNB()
    model.fit(train_features, train_labels)
    return model


def train_neural_network(dataset_path):
    """Train a single-layer regression network."""
    dataset = pd.read_csv(dataset_path)
    features = _transform_all_features(dataset.iloc[:, :-1].values)
    labels = dataset.iloc[:, -1].values
    train_features, _test_features, train_labels, _test_labels = train_test_split(
        features, labels, test_size=1, random_state=0
    )

    def rectified_linear_activation(value):
        return K.relu(value, alpha=0.0, max_value=None)

    model = Sequential([Dense(1, input_dim=features.shape[1], activation=rectified_linear_activation)])
    model.compile(loss="mean_squared_error", optimizer="sgd")
    model.fit(train_features, train_labels, epochs=650, batch_size=10)
    return model


def predict_neural_network_results(model, prediction_data_path):
    """Append neural-network predictions to configuration rows."""
    rows = pd.read_csv(prediction_data_path, header=None).values
    predictions = model.predict(_transform_all_features(rows))
    results = rows.tolist()
    for index, configuration in enumerate(results):
        configuration.append(predictions[index][0])
    return results


def train_knn_classifier(dataset_path):
    """Train a k-nearest-neighbors classifier."""
    dataset = pd.read_csv(dataset_path)
    features = _transform_all_features(dataset.iloc[:, :-1].values)
    labels = dataset.iloc[:, -1].values
    train_features, _test_features, train_labels, _test_labels = train_test_split(
        features, labels, test_size=1, random_state=0
    )
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(train_features, train_labels)
    return model


def predict_configuration_from_adaptation_rule(dataset_path, adaptation_rule):
    """Invert the labeled dataset by predicting a configuration from its rule."""
    dataset = pd.read_csv(dataset_path)
    rules = dataset.iloc[:, -1].values.reshape(-1, 1)
    configurations = dataset.iloc[:, :-1].apply(
        lambda row: ",".join(row.astype(str)), axis=1
    )
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(rules, configurations)
    query = np.array([adaptation_rule]).reshape(-1, 1)
    return model.predict(query).tolist()[0].split(",")


def configuration_to_json(configuration_tokens):
    """Convert canonical feature-state tokens into a flat configuration object."""
    configuration = {}
    for token in configuration_tokens:
        if token.endswith(" enabled"):
            feature_key = token.removesuffix(" enabled")
            is_enabled = True
        else:
            feature_key = token.removesuffix(" disabled")
            is_enabled = False
        configuration[feature_key.replace(" ", "_").lower()] = is_enabled
    return configuration


def train_autoencoder():
    """Train an autoencoder from labeled and generated configurations."""
    labeled_data = pd.read_csv(LABELED_DATASET_PATH)
    labeled_features = _transform_all_features(labeled_data.iloc[:, :-1].values)
    labeled_targets = np.reshape(labeled_data.iloc[:, -1].values, (-1, 1))
    unlabeled_features = _transform_all_features(
        pd.read_csv(CONFIGURATIONS_PATH).values
    )
    test_data = pd.read_csv(EVALUATION_DATASET_PATH)
    test_features = test_data.iloc[:, :-1].values
    test_targets = test_data.iloc[:, -1].values

    input_dimension = labeled_features.shape[1]
    inputs = Input(shape=(input_dimension,))
    encoded = Dense(256, activation="relu")(inputs)
    latent = Dense(2, activation="linear")(encoded)
    decoded = Dense(256, activation="relu")(latent)
    outputs = Dense(input_dimension, activation="linear")(decoded)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer="adam", loss="mse")
    model.fit(
        x=np.concatenate((labeled_features, unlabeled_features), axis=0),
        y=np.concatenate((labeled_targets, np.zeros((unlabeled_features.shape[0], 1))), axis=0),
        batch_size=32,
        epochs=10,
        validation_data=(test_features, test_targets),
    )
    return model


def train_convolutional_neural_network():
    """Train and evaluate a convolutional network."""
    dataset = pd.read_csv(LABELED_DATASET_PATH)
    features = _transform_all_features(dataset.iloc[:, :-1].values)
    labels = dataset.iloc[:, -1].values
    train_features, test_features, train_labels, test_labels = train_test_split(
        features, labels, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    train_features = np.expand_dims(scaler.fit_transform(train_features), axis=-1)
    test_features = np.expand_dims(scaler.transform(test_features), axis=-1)
    model = Sequential([
        Conv1D(32, 3, activation="relu", input_shape=train_features.shape[1:]),
        Conv1D(64, 3, activation="relu"),
        Flatten(),
        Dense(64, activation="relu"),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss="binary_crossentropy", metrics=["accuracy"])
    loss, accuracy = model.evaluate(test_features, test_labels)
    print(f"Loss: {loss}; accuracy: {accuracy}")


def _load_transfer_datasets(emissions_path=UNFILTERED_EMISSIONS_PATH):
    large_dataset = pd.read_csv(emissions_path)
    large_features = transform_dataset(large_dataset.iloc[:, :-1].values, [0, 1, 2, 3, 4, 5])
    large_targets = large_dataset.iloc[:, -1].str.replace(",", ".").astype(float).values
    small_dataset = pd.read_csv(LABELED_DATASET_PATH)
    small_features = _transform_all_features(small_dataset.iloc[:, :-1].values)
    small_targets = small_dataset.iloc[:, -1].values
    return large_features, large_targets, small_features, small_targets


def _split_and_scale_transfer_data(emissions_path=UNFILTERED_EMISSIONS_PATH):
    large_features, large_targets, small_features, small_targets = _load_transfer_datasets(emissions_path)
    large_train, large_test, large_y_train, large_y_test = train_test_split(large_features, large_targets, test_size=0.2, random_state=42)
    small_train, small_test, small_y_train, small_y_test = train_test_split(small_features, small_targets, test_size=0.2, random_state=42)
    scaler = StandardScaler(with_mean=False)
    large_train = scaler.fit_transform(large_train)
    large_test = scaler.transform(large_test)
    small_train = scaler.fit_transform(small_train)
    small_test = scaler.transform(small_test)
    return large_train, large_test, large_y_train, large_y_test, small_train, small_test, small_y_train, small_y_test


def train_transfer_learning_model():
    """Train a transfer-learning regressor across both datasets."""
    data = _split_and_scale_transfer_data()
    large_train, large_test, large_y_train, large_y_test, small_train, small_test, small_y_train, small_y_test = data
    source_model = Sequential([Dense(128, activation="relu", input_shape=(large_train.shape[1],)), Dense(64, activation="relu"), Dense(1, activation="linear")])
    source_model.compile(optimizer="adam", loss="mean_squared_error", metrics=["mae"])
    source_model.fit(large_train, large_y_train, epochs=10, validation_data=(large_test, large_y_test))
    target_model = Sequential([Dense(128, input_dim=small_train.shape[1], activation="relu"), Dense(64, activation="relu"), Dense(32, activation="relu")])
    target_model.compile(loss="mean_squared_error", optimizer="adam")
    for index in range(len(source_model.layers) - 1):
        target_model.layers[index].set_weights(source_model.layers[index].get_weights())
    target_model.fit(small_train, small_y_train, epochs=10, validation_data=(small_test, small_y_test))
    mean_absolute_error = target_model.evaluate(small_test, small_y_test)
    print(f"Mean absolute error: {mean_absolute_error:.4f}")


def create_base_model(input_dimension):
    """Build the shared dense feature extractor."""
    inputs = Input(shape=(input_dimension,))
    features = Dense(128, activation="relu")(inputs)
    features = Dense(64, activation="relu")(features)
    features = Dense(32, activation="relu")(features)
    return Model(inputs=inputs, outputs=features)


def train_final_transfer_networks():
    """Train source and target transfer networks."""
    data = _split_and_scale_transfer_data()
    large_train, large_test, large_y_train, large_y_test, small_train, small_test, small_y_train, small_y_test = data
    source_base = create_base_model(large_train.shape[1])
    target_base = create_base_model(small_train.shape[1])
    source_model = Model(source_base.input, Dense(1, activation="linear")(source_base.output))
    source_model.compile(loss="mean_squared_error", optimizer="adam")
    source_model.fit(large_train, large_y_train, epochs=10, validation_data=(large_test, large_y_test))
    for index, layer in enumerate(source_base.layers):
        target_base.layers[index].set_weights(layer.get_weights())
    target_model = Model(target_base.input, Dense(1, activation="linear")(target_base.output))
    target_model.compile(loss="mean_squared_error", optimizer="adam")
    target_model.fit(small_train, small_y_train, epochs=10, validation_data=(small_test, small_y_test))
    mean_absolute_error = target_model.evaluate(small_test, small_y_test)
    print(f"Mean absolute error: {mean_absolute_error:.4f}")


def train_neural_autoencoder():
    """Train an emissions encoder and adaptation regressor."""
    large_features, large_targets, small_features, small_targets = _load_transfer_datasets()
    large_train, large_test, _large_y_train, _large_y_test = train_test_split(large_features, large_targets, test_size=0.2, random_state=42)
    scaler = MaxAbsScaler()
    large_train = tf.convert_to_tensor(scaler.fit_transform(large_train), dtype=tf.float32)
    large_test = tf.convert_to_tensor(scaler.transform(large_test), dtype=tf.float32)
    encoding_dimension = small_features.shape[1]
    inputs = Input(shape=(large_train.shape[1],))
    encoded = Dense(encoding_dimension, activation="relu")(inputs)
    autoencoder = Model(inputs, Dense(large_train.shape[1], activation="linear")(encoded))
    encoder = Model(inputs, encoded)
    autoencoder.compile(optimizer="adam", loss="mean_squared_error")
    autoencoder.fit(large_train, large_train, epochs=50, batch_size=256, validation_data=(large_test, large_test))
    small_train, small_test, small_y_train, small_y_test = train_test_split(small_features, small_targets, test_size=0.2, random_state=42)
    train_encoded = encoder.predict(small_train)
    test_encoded = encoder.predict(small_test)
    regression_model = Sequential([Dense(128, activation="relu", input_shape=(encoding_dimension,)), Dense(64, activation="relu"), Dense(1)])
    regression_model.compile(optimizer="adam", loss="mean_squared_error")
    regression_model.fit(train_encoded, small_y_train, epochs=10, validation_data=(test_encoded, small_y_test))


def train_neural_autoencoder_v2():
    """Train staged autoencoders and an adaptation regressor."""
    large_features, large_targets, small_features, small_targets = _load_transfer_datasets()
    large_train, large_test, _large_y_train, _large_y_test = train_test_split(large_features, large_targets, test_size=0.2, random_state=42)
    small_train, small_test, small_y_train, small_y_test = train_test_split(small_features, small_targets, test_size=0.2, random_state=42)
    large_scaler = MaxAbsScaler()
    large_train = tf.convert_to_tensor(large_scaler.fit_transform(large_train), dtype=tf.float32)
    large_test = tf.convert_to_tensor(large_scaler.transform(large_test), dtype=tf.float32)
    small_scaler = MinMaxScaler()
    small_train = tf.convert_to_tensor(small_scaler.fit_transform(small_train), dtype=tf.float32)
    small_test = tf.convert_to_tensor(small_scaler.transform(small_test), dtype=tf.float32)
    large_inputs = Input(shape=(large_train.shape[1],))
    large_encoded = Dense(small_train.shape[1], activation="relu")(large_inputs)
    large_autoencoder = Model(large_inputs, Dense(large_train.shape[1], activation="linear")(large_encoded))
    large_encoder = Model(large_inputs, large_encoded)
    large_autoencoder.compile(optimizer="adam", loss="mean_squared_error")
    large_autoencoder.fit(large_train, large_train, epochs=50, batch_size=256, validation_data=(large_test, large_test))
    small_inputs = Input(shape=(small_train.shape[1],))
    resized = Dense(large_train.shape[1], activation="linear")(small_inputs)
    small_encoded = large_encoder(resized)
    small_autoencoder = Model(small_inputs, Dense(small_train.shape[1], activation="linear")(small_encoded))
    small_encoder = Model(small_inputs, small_encoded)
    small_autoencoder.compile(optimizer="adam", loss="mean_squared_error")
    small_autoencoder.fit(small_train, small_train, epochs=50, batch_size=256, validation_data=(small_test, small_test))
    train_encoded = small_encoder.predict(small_train)
    test_encoded = small_encoder.predict(small_test)
    regression_model = Sequential([Dense(256, activation="relu", input_shape=(small_train.shape[1],), kernel_regularizer=l1(0.001)), BatchNormalization(), Dense(128, activation="relu"), BatchNormalization(), Dense(64, activation="relu"), BatchNormalization(), Dense(32, activation="relu"), BatchNormalization(), Dense(1)])
    regression_model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.01), loss="mean_squared_error")
    regression_model.fit(train_encoded, small_y_train, epochs=5000, validation_data=(test_encoded, small_y_test))


def train_staged_transfer_model():
    """Train staged transfer models and return configuration predictions."""
    print("\n" + "=" * 50)
    print("DEBUG [train_staged_transfer_model]: STARTING TRAINING")
    try:
        large_dataset = pd.read_csv(FILTERED_EMISSIONS_PATH)
        small_dataset = pd.read_csv(LABELED_DATASET_PATH)
        prediction_dataset = pd.read_csv(CONFIGURATIONS_PATH, header=None)
    except FileNotFoundError as error:
        print(f"FATAL ERROR: Required dataset was not found: {error.filename}")
        return None
    print(f"DEBUG: Loaded {FILTERED_EMISSIONS_PATH}; shape={large_dataset.shape}")
    print(f"DEBUG: Loaded {LABELED_DATASET_PATH}; shape={small_dataset.shape}")
    print(f"DEBUG: Loaded {CONFIGURATIONS_PATH}; shape={prediction_dataset.shape}")
    if small_dataset.shape[1] - 1 != prediction_dataset.shape[1]:
        print("WARNING: Training and prediction feature counts do not match.")
    else:
        print("Feature counts match; the pipeline will continue.")
    large_features = _transform_all_features(large_dataset.iloc[:, :-1].values)
    large_targets = large_dataset.iloc[:, -1].str.replace(",", ".").astype(float).values
    small_features = _transform_all_features(small_dataset.iloc[:, :-1].values)
    small_targets = small_dataset.iloc[:, -1].values
    large_train, large_test, large_y_train, large_y_test = train_test_split(large_features, large_targets, test_size=0.2, random_state=42)
    small_train, small_test, small_y_train, small_y_test = train_test_split(small_features, small_targets, test_size=0.2, random_state=42)
    large_scaler = MaxAbsScaler()
    large_train = tf.convert_to_tensor(large_scaler.fit_transform(large_train), dtype=tf.float32)
    large_test = tf.convert_to_tensor(large_scaler.transform(large_test), dtype=tf.float32)
    small_scaler = MinMaxScaler()
    small_train = tf.convert_to_tensor(small_scaler.fit_transform(small_train), dtype=tf.float32)
    small_test = tf.convert_to_tensor(small_scaler.transform(small_test), dtype=tf.float32)
    large_inputs = Input(shape=(large_train.shape[1],))
    hidden = Dense(128, activation="relu")(large_inputs)
    hidden = BatchNormalization()(hidden)
    for width in (64, 32, 16, 8):
        hidden = Dense(width, activation="relu")(hidden)
    source_model = Model(large_inputs, Dense(1)(hidden))
    source_model.compile(optimizer=keras.optimizers.Adagrad(learning_rate=0.01), loss="mean_squared_error")
    source_model.fit(large_train, large_y_train, epochs=200, batch_size=32, validation_data=(large_test, large_y_test))
    feature_layer = Dense(128, activation="relu")
    feature_inputs = Input(shape=(large_train.shape[1],))
    extracted_features = feature_layer(feature_inputs)
    feature_layer.set_weights(source_model.layers[1].get_weights())
    feature_extractor = Model(feature_inputs, extracted_features)
    resize_inputs = Input(shape=(small_train.shape[1],))
    resize_model = Model(resize_inputs, Dense(large_train.shape[1], activation="linear")(resize_inputs))
    small_train_features = feature_extractor.predict(resize_model.predict(small_train))
    small_test_features = feature_extractor.predict(resize_model.predict(small_test))
    target_inputs = Input(shape=(small_train_features.shape[1],))
    target_model = Model(target_inputs, Dense(1)(Dense(64, activation="relu")(target_inputs)))
    target_model.compile(optimizer="adam", loss="mean_squared_error")
    target_model.fit(small_train_features, small_y_train, epochs=1500, batch_size=32, validation_data=(small_test_features, small_y_test))
    return predict_deep_neural_network_results(target_model, resize_model, feature_extractor, CONFIGURATIONS_PATH)


def predict_deep_neural_network_results(model, resize_model, feature_extractor, prediction_data_path):
    """Append staged-network predictions to configuration rows."""
    rows = pd.read_csv(prediction_data_path, header=None).values
    transformed_rows = _transform_all_features(rows)
    predictions = model.predict(feature_extractor.predict(resize_model.predict(transformed_rows)))
    results = rows.tolist()
    for index, configuration in enumerate(results):
        configuration.append(predictions[index][0])
    return results
