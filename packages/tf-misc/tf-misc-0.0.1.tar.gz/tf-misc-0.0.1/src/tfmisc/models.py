import tensorflow as tf
import numpy as np

tf.keras.backend.set_floatx('float64')

class HypersphericalRotation(tf.keras.Model):
    '''
    Trainable hyperspherical rotation of a data set.
    '''

    def __init__(self, units=1, input_dim=1):
        super().__init__()

    #Consider using @property
    def set_angles(self, x):
        '''
        Computes hyperspherical angles of data points and sets a trainable
        angle in phase space.

        Parameters
        ----------
        x : tf.tensor[tf.float64]
            m x n data matrix

        Returns
        -------
        theta : tf.tensor
            Hyperspherical angles of data points.
        '''
        self.tau = self.add_weight(shape=(x.shape[1]-1,), initializer="uniform", trainable=True)
        def angle(x):
            theta = []
            for j in range(len(x)-1):
                case0 = tf.math.reduce_all(tf.math.equal(x[j+1:], 0.0))
                if case0:
                    theta.append(0.0)
                elif not tf.equal(j+1, len(x)-1):
                    theta.append(tf.math.acos(x[j] / tf.linalg.norm(x[j:])).numpy())
                else:
                    if tf.math.greater_equal(x[j], 0.0):
                        theta.append(tf.math.acos(x[j] / tf.linalg.norm(x[j:])).numpy())
                    else:
                        theta.append(2 * np.pi - tf.math.acos(x[j] / tf.linalg.norm(x[j:])).numpy())
            return tf.constant(theta, dtype=tf.float64)
        self.theta = tf.map_fn(angle, x) # Test if this line is still needed.
        
        
    def call(self, inputs):
        self.r = tf.norm(inputs, axis=1)

        y = []
        shifted = self.theta + self.tau

        for j in range(shifted.shape[1]+1):
            if j == 0:
                y.append(tf.reshape(
                    self.r * tf.cos(shifted[:,j]),
                    (-1,1)
                    ))
            elif j + 1 != shifted.shape[1]+1:
                y.append(tf.reshape(
                            self.r * tf.reduce_prod(tf.sin(shifted[:,:j]), axis=1) * tf.cos(shifted[:,j]),
                            (-1,1)
                            )
                         )
            else:
                y.append(tf.reshape(
                            self.r * tf.reduce_prod(tf.sin(shifted), axis=1),
                            (-1,1)
                            )
                         )
        return tf.concat(y, axis=1)


class SingularValueShift(tf.keras.Model):
    '''
    Trainable shift in the singular values of a matrix.
    '''
    
    def __init__(self):
        super().__init__()

    def pretrain(self, inputs):
        '''
        Find the singular value decomposition of a
        matrix.

        Parameters
        ----------
        X : tf.tensor
            m x n data matrix

        Returns
        -------
        : None
        '''
        s,u,v = tf.linalg.svd(inputs)
        self.s = s
        self.u = u
        self.v = v
        self.tau = tf.Variable(tf.random.uniform(s.shape, dtype=tf.float64), trainable=True)
    
    def call(self, inputs):
        s,u,v = tf.linalg.svd(inputs)
        self.s = s
        self.u = u
        self.v = v
        result = self.s + self.tau
        result = tf.linalg.diag(result)
        result = tf.matmul(self.u, result)
        result = tf.matmul(result, self.v, transpose_b=True)
        return result

class SVDProjection(tf.keras.Model):
    '''
    Projects data along singular vectors.
    '''
    def __init__(self):
        super().__init__()

    def fit(self, X):
        '''
        Find the singular value decomposition of a matrix,
        and then project the given data onto the singular
        vectors.

        Parameters
        ----------
        X : tf.tensor
            m x n data matrix

        Returns
        -------
        : None
        '''
        s, U, V = tf.linalg.svd(X)
        self.s = s
        self.total_s = tf.math.reduce_sum(self.s)
        self.normalized_s = self.s / self.total_s
        self.S = tf.linalg.diag(s)
        self.U = U
        self.V = V
        self.scores = tf.matmul(U, self.S)

    def call(self, X):
        '''
        Project a data matrix along singular vectors. The
        data need not be the same as used to find the singular
        value decomposition in the first place.

        Parameters
        ----------
        X : tf.tensor
            m x n data matrix

        Returns
        -------
         : tf.tensor
            Projected data.
        '''
        if hasattr(self, 'V'):
            return tf.matmul(X, self.V)
        else:
            self.fit(X)
            return tf.matmul(X, self.V)

if __name__ == '__main__':
    from objectives import ProductDeviations
    opt = tf.keras.optimizers.Nadam()
    loss = ProductDeviations()

    weights_dict = {}

    weight_callback = tf.keras.callbacks.LambdaCallback \
    ( on_epoch_end=lambda epoch, logs: weights_dict.update({epoch:model.get_weights()}))
    
    model = HypersphericalRotation()
    model.compile(optimizer=opt, loss=loss)
    X = np.arange(200).reshape(100,2)
    X = tf.convert_to_tensor(X, dtype=tf.float64)
    model.set_angles(X)

    history = model.fit(x=X,
              y=model(X),
              batch_size=X.shape[0],
              epochs=1000000, callbacks=weight_callback)

    Y = model(X)
    import matplotlib.pyplot as plt

    plt.plot(X[:,0], X[:,1])
    plt.plot(Y[:,0], Y[:,1])
    plt.show()

    weights = [i[0][0] for i in weights_dict.values()]
    losses = history.history['loss']

    plt.plot(weights, losses)
    plt.yscale('log')
    plt.show()

    plt.plot(losses)
    plt.yscale('log')
    plt.show()

    plt.plot(weights)
    plt.show()
    
