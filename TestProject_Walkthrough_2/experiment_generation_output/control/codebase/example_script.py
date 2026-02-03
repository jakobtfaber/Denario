# filename: codebase/example_script.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def load_data(file_path):
    data = pd.read_csv(file_path)
    return data


def preprocess_data(data):
    # Assuming the last column is the target
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]
    return X, y


def train_model(X_train, y_train):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print('Accuracy:', accuracy)


def main():
    data = load_data('data/dataset.csv')
    X, y = preprocess_data(data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)


if __name__ == '__main__':
    main()