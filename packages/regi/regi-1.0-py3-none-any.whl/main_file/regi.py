#simple linear regression model
import numpy as np

# define a function to calculate the slope and y-intercept of the line
def linear_regression(x, y):
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    numerator = 0
    denominator = 0
    
    for i in range(n):
        numerator += (x[i] - x_mean) * (y[i] - y_mean)
        denominator += (x[i] - x_mean) ** 2
        
    slope = numerator / denominator
    y_intercept = y_mean - slope * x_mean
    
    return slope, y_intercept

# define a function to make predictions using the calculated slope and y-intercept
def predict(x, slope, y_intercept):
    y_pred = slope * x + y_intercept
    return y_pred

# example usage
np.random.seed(0)
x = np.random.rand(100, 1)
y = 2 + 3 * x + np.random.randn(100, 1)

slope, y_intercept = linear_regression(x, y)
print('slope:', slope)
print('y-intercept:', y_intercept)

x_new = 6
y_pred = predict(x_new, slope, y_intercept)
print('predicted value for x = {}:'.format(x_new), y_pred)



#polynomial regression
import numpy as np

# define a function to create a polynomial feature matrix
def create_polynomial_features(x, degree):
    x_poly = np.zeros((len(x), degree))
    
    for i in range(degree):
        x_poly[:, i] = x ** (i+1)
    
    return x_poly

# define a function to perform polynomial regression
def polynomial_regression(x, y, degree):
    x_poly = create_polynomial_features(x, degree)
    model = np.linalg.lstsq(x_poly, y, rcond=None)[0]
    
    return model

# define a function to make predictions using the polynomial model
def predict(x, model):
    y_pred = np.zeros_like(x)
    
    for i in range(len(model)):
        y_pred += model[i] * x ** (i+1)
    
    return y_pred

# example usage
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])
degree = 2

model = polynomial_regression(x, y, degree)
print('polynomial coefficients:', model)

x_new = np.array([6])
x_new_poly = create_polynomial_features(x_new, degree)
y_pred = predict(x_new_poly, model)
print('predicted value for x = {}:'.format(x_new[0]), y_pred[0])

#multiple linear regression
import numpy as np

# define a function to perform multiple linear regression
def multiple_linear_regression(x, y):
    X = np.column_stack((np.ones(len(x)), x)) # add a column of ones for the intercept term
    model = np.linalg.lstsq(X, y, rcond=None)[0]
    
    return model

# define a function to make predictions using the multiple linear regression model
def predict(x, model):
    X = np.column_stack((np.ones(len(x)), x))
    y_pred = np.dot(X, model)
    
    return y_pred

# example usage
X = np.random.rand(100, 3)
# Generate random output data
y = 3*X[:,0] + 2*X[:,1] - 5*X[:,2] + np.random.randn(100)

#x1 = np.array([1, 2, 3, 4, 5])
#x2 = np.array([2, 4, 5, 4, 5])
#y = np.array([5, 7, 8, 8, 10])

#X = np.column_stack((x1, x2))
model = multiple_linear_regression(X, y)
print('intercept and coefficients:', model)

X_new = np.random.rand(3, 3) # new values of x1, x2, and x3
y_pred = predict(X_new, model)
print('predicted values:', y_pred)
