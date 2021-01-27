# linear_reg_house.py

from sklearn import datasets ## imports datasets from scikit-learn
import numpy as np
import pandas as pd# define the data/predictors as the pre-set feature names
import statsmodels.api as sm  

data = datasets.load_boston() ## loads Boston dataset from datasets library 
df = pd.DataFrame(data.data, columns=data.feature_names)

# Put the target (housing value -- MEDV) in another DataFrame
target = pd.DataFrame(data.target, columns=["MEDV"])
# === reg with no intercept ===
X = df["RM"]
y = target["MEDV"]

# Note the difference in argument order
model = sm.OLS(y, X).fit()
predictions = model.predict(X) # make the predictions by the model

# Print out the statistics
model.summary()

# === reg with intercept ===
X = df["RM"]
y = target["MEDV"]
X = sm.add_constant(X) ## let's add an intercept (beta_0) to our model

# Note the difference in argument order
model = sm.OLS(y, X).fit()
predictions = model.predict(X) # make the predictions by the model

# Print out the statistics
model.summary()

# ====reg with multiple x ===
X = df[["RM", "LSTAT"]]
y = target["MEDV"]
model = sm.OLS(y, X).fit()
predictions = model.predict(X)
model.summary()
# === use sklearn
from sklearn import linear_model
X = df
y = target["MEDV"]
lm = linear_model.LinearRegression()
model = lm.fit(X,y)
predictions = lm.predict(X)
print(predictions)
lm.score(X,y)
lm.coef_
lm.intercept_

