from sklearn.svm import LinearSVC, SVC
from sklearn.feature_extraction import DictVectorizer
import os
import json
import numpy as np
from tfidf import gettfidf


def svm_bagging(train_data, train_y, vali_data, vali_y, test_data, id=""):
    # svm_bagging_vec = DictVectorizer()
    # train_x = svm_bagging_vec.fit_transform(train_data)
    # vali_x = svm_bagging_vec.transform(vali_data)
    # test_x = svm_bagging_vec.transform(test_data)

    train_x, vali_x, test_x = gettfidf(train_data, vali_data, test_data)

    # 速度慢 找个时间跑一下做一个对比
    # svm = SVC(class_weight="balanced", verbose=True, gamma="auto")
    svm = LinearSVC(multi_class="ovr", class_weight="balanced", verbose=True)
    svm.fit(train_x, train_y)

    if not os.path.exists("model/bagging"):
        os.mkdir("model/bagging")
    print("SVM Bagging " + str(id) + " Test: ", svm.score(vali_x, vali_y))

    result = list(svm.predict(test_x))
    with open("model/bagging/svm_result_" + str(id) + ".json", "w") as f:
        json.dump(result, f)


def svm_ada_boost(train_data, train_y, vali_data, vali_y, test_data, id, weights, raw_data, raw_y):
    svm_ada_boost_vec = DictVectorizer()
    train_x = svm_ada_boost_vec.fit_transform(train_data)
    raw_x = svm_ada_boost_vec.transform(raw_data)
    vali_x = svm_ada_boost_vec.transform(vali_data)
    test_x = svm_ada_boost_vec.transform(test_data)

    svm = LinearSVC(multi_class="ovr", class_weight="balanced", verbose=True)
    svm.fit(train_x, train_y)

    result = svm.predict(raw_x)
    sigma = float(np.dot(np.array(result) != np.array(raw_y), weights))
    if not sigma > 0.5:
        beta = sigma / (1.0 - sigma)
        update = []
        for i in range(len(raw_y)):
            if raw_y[i] != result[i]:
                update.append(1)
            else:
                update.append(beta)
        weights = np.multiply(update, weights)
        weights = weights / np.sum(weights)
        if not os.path.exists("model/ada_boost"):
            os.mkdir("model/ada_boost")
        with open("model/ada_boost/svm_beta" + str(id) + ".txt", "w") as f:
            f.write(str(beta))

        print("SVM Ada_Boost " + str(id) + " Test: ", svm.score(vali_x, vali_y))
        result = list(svm.predict(test_x))
        with open("model/ada_boost/svm_result_" + str(id) + ".json", "w") as f:
            json.dump(result, f)

    return weights, sigma
