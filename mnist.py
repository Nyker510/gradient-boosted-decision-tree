import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_openml
from sklearn.metrics import accuracy_score

import gbdtree as gb
import gbdtree.functions as fn
from gbdtree.utils import get_logger

logger = get_logger(__name__)


def load_mnist():
    X, y = fetch_openml('mnist_784', version=1, return_X_y=True)
    y = np.asarray(y, dtype=np.int)
    logger.info('This is MNIST Original dataset')
    logger.debug('finish fetch datasets')

    # target of image number.
    # note: it is difficult problem to decide 3 and 8.
    target = 3, 8
    logger.info('target: {0},{1}'.format(*target))

    idx = (y == target[0]) | (y == target[1])
    logger.debug(idx.shape)
    x = X[idx] / 255.
    y = y[idx]
    y = np.where(y == target[0], 0., 1.)
    return x, y


if __name__ == '__main__':
    x, y = load_mnist()
    logger.info(len(x))

    # split train and test dataset
    # I shoud have use sklearn.cross_validation.train_test_split...
    np.random.seed(71)
    perm = np.random.permutation(len(y))
    x_train, t_train = x[perm[:2000]], y[perm[:2000]]
    x_test, t_test = x[perm[2000:]], y[perm[2000:]]

    logger.info('training datasize: {0}'.format(t_train.shape[0]))
    logger.info('test datasize: {0}'.format(t_test.shape[0]))

    # setup regression object for training and
    # loss function for evaluating the predict quarity
    regobj = fn.CrossEntropy()
    loss = fn.logistic_loss

    clf = gb.GradientBoostedDT(regobj, loss, num_iter=40, eta=.4, max_leaves=15, max_depth=5, gamma=.1)
    clf.fit(x_train, t_train, validation_data=(x_test, t_test), verbose=1)
    f_importance = clf.feature_importance()
    pd.Series(f_importance).reset_index().to_csv('feature_importance.csv', index=False)
    plt.title('seqence of training and test loss')
    plt.plot(clf.training_loss, 'o-', label='training loss')
    plt.plot(clf.validation_loss, 'o-', label='test loss')
    plt.yscale('log')
    plt.legend()
    plt.show()

    pred_prob = clf.predict(x_test)
    pred_cls = np.where(pred_prob > .5, 1., .0)
    df_pred = pd.DataFrame({'probability': pred_prob, 'predict': pred_cls, 'true': t_test})
    df_pred.to_csv('predict.csv')
    acc = accuracy_score(t_test, pred_cls)
    logger.info('validation accuracy:{0}'.format(acc))
