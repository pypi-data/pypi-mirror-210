import deepdriver

from sklearn import svm, datasets

# Load training data
iris = datasets.load_iris()
X, y = iris.data, iris.target

# Model Training
clf = svm.SVC()
clf.fit(X, y)
deepdriver.save_model("sklearn","iris_model",clf)
print(deepdriver.serving_model("service.py"))