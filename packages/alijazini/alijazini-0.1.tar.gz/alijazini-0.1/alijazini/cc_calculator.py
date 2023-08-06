import numpy as np

from scipy.stats import spearmanr, kendalltau, pearsonr
from scipy.signal import coherence

from keras.metrics import MeanSquaredError, MeanAbsoluteError
from keras.layers import LSTM, Dense
from keras.models import Sequential

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR


def spearman_rank_cc_calculator(time_series1, time_series2):
    ranks1 = np.argsort(time_series1).argsort()
    ranks2 = np.argsort(time_series2).argsort()

    correlation, p_value = spearmanr(ranks1, ranks2)

    return correlation, p_value


def kendall_tau_cc_calculator(time_series1, time_series2):
    tau, p_value = kendalltau(time_series1, time_series2)

    return tau, p_value


def pearson_cc_calculator(time_series1, time_series2):
    correlation_coefficient, p_value = pearsonr(time_series1, time_series2)

    return correlation_coefficient, p_value


def cross_correlation_calculator(time_series1, time_series2):
    cross_correlation = np.correlate(time_series1, time_series2, mode='full').max()

    return cross_correlation


def coherence_calculator(time_series1, time_series2):
    f, Cxy = coherence(time_series1, time_series2, fs=1.0)
    avg_coherence = np.mean(Cxy)

    return avg_coherence


def LSTM_cc_calculator(time_series1, time_series2):
    scaler = MinMaxScaler(feature_range=(0, 1))
    variable1_normalized = scaler.fit_transform(time_series1.reshape(-1, 1))
    variable2_normalized = scaler.fit_transform(time_series2.reshape(-1, 1))
    window_size = 10
    X = np.array([time_series1[i:i + window_size] for i in range(len(variable1_normalized) - window_size)])
    y = np.array([time_series2[i + window_size] for i in range(len(variable2_normalized) - window_size)])

    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    y = np.reshape(y, (y.shape[0], 1))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(window_size, 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    model.fit(X_train, y_train, epochs=50, batch_size=32)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    y_train_pred = scaler.inverse_transform(y_train_pred)
    y_test_pred = scaler.inverse_transform(y_test_pred)
    y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

    # train_mse = np.mean((y_train_actual - y_train_pred)**2)
    # train_mae = np.mean(np.abs(y_train_actual - y_train_pred))
    # test_mse = np.mean((y_test_actual - y_test_pred)**2)
    # test_mae = np.mean(np.abs(y_test_actual - y_test_pred))

    train_LSTM_cc = np.corrcoef(y_train_actual.flatten(), y_train_pred.flatten())[0, 1]
    test_LSTM_cc = np.corrcoef(y_test_actual.flatten(), y_test_pred.flatten())[0, 1]

    return train_LSTM_cc, test_LSTM_cc


def LR_cc_calculator(time_series1, time_series2):
    scaler = MinMaxScaler(feature_range=(0, 1))
    variable1_normalized = scaler.fit_transform(time_series1.reshape(-1, 1))
    variable2_normalized = scaler.fit_transform(time_series2.reshape(-1, 1))

    window_size = 10
    X = np.array([time_series1[i:i + window_size] for i in range(len(variable1_normalized) - window_size)])
    y = np.array([time_series2[i + window_size] for i in range(len(variable2_normalized) - window_size)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)

    y_train_pred = linear_model.predict(X_train)
    y_test_pred = linear_model.predict(X_test)

    y_train_pred = scaler.inverse_transform(y_train_pred.reshape(-1, 1))
    y_test_pred = scaler.inverse_transform(y_test_pred.reshape(-1, 1))
    y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

    # mse = mean_squared_error(y_test, y_pred)
    # mae = mean_absolute_error(y_test, y_pred)

    train_LR_cc = np.corrcoef(y_train_actual.flatten(), y_train_pred.flatten())[0, 1]
    test_LR_cc = np.corrcoef(y_test_actual.flatten(), y_test_pred.flatten())[0, 1]

    return train_LR_cc, test_LR_cc


def SVM_cc_calculator(time_series1, time_series2):
    scaler = MinMaxScaler(feature_range=(0, 1))
    variable1_normalized = scaler.fit_transform(time_series1.reshape(-1, 1))
    variable2_normalized = scaler.fit_transform(time_series2.reshape(-1, 1))

    window_size = 10
    X = np.array([time_series1[i:i + window_size] for i in range(len(variable1_normalized) - window_size)])
    y = np.array([time_series2[i + window_size] for i in range(len(variable2_normalized) - window_size)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # svm_model = SVR(kernel='linear')
    svm_model = SVR(kernel='rbf')
    svm_model.fit(X_train, y_train)

    y_train_pred = svm_model.predict(X_train)
    y_test_pred = svm_model.predict(X_test)

    y_train_pred = scaler.inverse_transform(y_train_pred.reshape(-1, 1))
    y_test_pred = scaler.inverse_transform(y_test_pred.reshape(-1, 1))
    y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

    # mse = mean_squared_error(y_test, y_pred)
    # mae = mean_absolute_error(y_test, y_pred)

    train_SVM_cc = np.corrcoef(y_train_actual.flatten(), y_train_pred.flatten())[0, 1]
    test_SVM_cc = np.corrcoef(y_test_actual.flatten(), y_test_pred.flatten())[0, 1]

    return train_SVM_cc, test_SVM_cc


def NN_cc_calculator(time_series1, time_series2):
    scaler = MinMaxScaler(feature_range=(0, 1))
    variable1_normalized = scaler.fit_transform(time_series1.reshape(-1, 1))
    variable2_normalized = scaler.fit_transform(time_series2.reshape(-1, 1))

    window_size = 10
    X = np.array([time_series1[i:i + window_size] for i in range(len(variable1_normalized) - window_size)])
    y = np.array([time_series2[i + window_size] for i in range(len(variable2_normalized) - window_size)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=(window_size,)))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse', metrics=[MeanSquaredError(), MeanAbsoluteError()])
    model.fit(X_train, y_train, epochs=10, batch_size=32)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    y_train_pred = scaler.inverse_transform(y_train_pred.reshape(-1, 1))
    y_test_pred = scaler.inverse_transform(y_test_pred.reshape(-1, 1))
    y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

    # mse = mean_squared_error(y_test, y_pred)
    # mae = mean_absolute_error(y_test, y_pred)

    train_NN_cc = np.corrcoef(y_train_actual.flatten(), y_train_pred.flatten())[0, 1]
    test_NN_cc = np.corrcoef(y_test_actual.flatten(), y_test_pred.flatten())[0, 1]

    return train_NN_cc, test_NN_cc
