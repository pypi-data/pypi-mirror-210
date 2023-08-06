import os
import sys
import pandas as pd
import numpy as np

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.wrappers.scikit_learn import KerasClassifier

from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer, confusion_matrix
from sklearn.metrics import roc_auc_score, precision_score, f1_score, recall_score, accuracy_score

#https://scikit-learn.org/stable/auto_examples/model_selection/plot_multi_metric_evaluation.html
#https://scikit-learn.org/stable/modules/model_evaluation.html

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dd8.connectivity.crypto.ftx_ as ftx_

# split a multivariate sequence into samples
def split_sequences(sequences, n_steps, n_classes):
	X, y = list(), list()
	for i in range(len(sequences)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the dataset
		if end_ix > len(sequences):
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequences[i:end_ix, :-n_classes], sequences[end_ix-1, -n_classes:]
		X.append(seq_x)
		y.append(seq_y)
	return np.array(X), np.array(y)

def create_model(n_steps: int, n_features: int, n_classes: int, epochs: int, verbose: int = 0):
    model = Sequential()
    model.add(Conv1D(filters=64, kernel_size=96, activation='relu', input_shape=(n_steps, n_features)))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(50, activation='relu'))
    model.add(Dense(n_classes, activation='softmax'))
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model    

if __name__ == '__main__':
    n_steps = 288
    n_train, n_validate, n_test = (0.7, 0.2, 0.1)
    #n_classes = 4

    ## Reading Data
    data = pd.read_csv('BTC-PERP.csv')
    data.dropna(how='any', inplace=True)
    #y = data.loc[:, 'class']
    n_classes = len(data.loc[:, 'class'].unique())
    #n_classes = 1
    data.drop(['timestamp', 'open', 'high', 'low', 'close', 'volume'], axis=1, inplace=True)
    dummies = pd.get_dummies(data.loc[:, 'class'])
    data.drop(['class'], axis=1, inplace=True)
    data = data.join(dummies)
    

    ## Splitting Data
    n_rows = data.shape[0]
    n_rows_train = int(n_train * n_rows)
    n_rows_validate = int((n_train + n_validate) * n_rows)    

    train = data.loc[:n_rows_validate, :]
    #validate = data.loc[n_rows_train:n_rows_test, :]
    test = data.loc[n_rows_validate:, :]

    print('training data: ', train.shape)
    print('test data: ', test.shape)


    X, y = split_sequences(train.values, n_steps, n_classes)
    X.astype('float32')
    y.astype('uint8')
    y = np.argmax(y, axis=1)
    print('features: ', X.shape)
    print('labels: ', y.shape)

    X_test, y_test = split_sequences(test.values, n_steps, n_classes)
    X_test.astype('float32')
    y_test.astype('uint8')
    y_test = np.argmax(y_test, axis=1)

    print('test features: ', X_test.shape)
    print('test labels: ', y_test.shape)

    n_features = X[0].shape[1]
    clf = KerasClassifier(build_fn = create_model, n_steps=n_steps, n_features=n_features, n_classes=n_classes, epochs=100, verbose=1)

    pipe = Pipeline(steps=[('clf', clf)])
    param_grid = {
        # "pca__n_components": [5, 15, 30, 45, 60],
        # "logistic__C": np.logspace(-4, 4, 4),
    }
    #scoring = {'f1':make_scorer(f1_score, greater_is_better=True, average='micro')}
    tscv = TimeSeriesSplit(n_splits=5).split(X)

    #search = GridSearchCV(pipe, cv=tscv, param_grid = param_grid, scoring = scoring, refit='f1', n_jobs=3, return_train_score = True)
    #search = GridSearchCV(pipe, cv=tscv, param_grid = param_grid, n_jobs=1, return_train_score = True)
    search = GridSearchCV(pipe, param_grid = param_grid, n_jobs=1, return_train_score = True)
    

    # model = Sequential()
    # model.add(Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(n_steps, n_features)))
    # model.add(MaxPooling1D(pool_size=2))
    # model.add(Flatten())
    # model.add(Dense(50, activation='relu'))
    # model.add(Dense((n_classes), activation='softmax'))
    # model.compile(optimizer='adam', loss='categorical_crossentropy')

    search.fit(X, y)
    results = search.cv_results_
    print(results)



    y_pred = search.predict(X_test)
    
    # # Model Evaluation metrics 
    # print('Accuracy Score : ' + str(accuracy_score(y_test_rounded,y_pred_rounded)))
    # print('Precision Score : ' + str(precision_score(y_test_rounded,y_pred_rounded)))
    # print('Recall Score : ' + str(recall_score(y_test_rounded,y_pred_rounded)))
    # print('F1 Score : ' + str(f1_score(y_test_rounded,y_pred_rounded,labels=np.unique(y_pred))))
    # cm = confusion_matrix(y_test_rounded, y_pred_rounded)
    # print(cm)    

    print('Accuracy Score : ' + str(accuracy_score(y_test,y_pred)))
    print('Precision Score : ' + str(precision_score(y_test,y_pred, average='micro')))
    print('Recall Score : ' + str(recall_score(y_test,y_pred, average='micro')))
    print('F1 Score : ' + str(f1_score(y_test,y_pred,labels=np.unique(y_pred), average='micro')))    
    cm = confusion_matrix(y_test, y_pred)
    print(cm)