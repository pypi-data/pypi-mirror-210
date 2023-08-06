"""Script d'application de bruit Phasor en utilisant uniquement python"""
import math
import numpy as np


class PhasorGenerator:
    """
    Classe inutilisable dans l'état doit redéfinir:
     -exp
     -sin
     -cos
     -atan2
     -dot
     -vector_subtraction
     Aller voir l'implémentation:
     -Python : phasor_py.py
     -Numpy : phasor_numpy.py
     -Jax : phasor_jax.py
    """

    def __init__(self):
        pass

    def exp(self, x):
        """
            La fonction exponentielle
        """
        raise NotImplemented()

    def sin(self, x):
        """
            La fonction sinus
        """
        raise NotImplemented()

    def cos(self, x):
        """
            La fonction cosinus
        """
        raise NotImplemented()

    def atan2(self, x, y):
        """
            La fonction atan2
        """
        raise NotImplemented()

    def dot(self, v1, v2):
        """
        dot retourne le produit scalaire entre deux vecteurs (vector1 et vector2)
        """
        raise NotImplemented()

    def vector_subtraction(self, vector1: list, vector2: list):
        """
        vector_subtraction retourne la soustraction de deux vecteurs (vector1 et vector2)
        """
        raise NotImplemented()

    def gaussian(self, vector: list, bandwidth: float) -> float:
        """
        gaussian retourne le résultat du vecteur (vector) par la fonction gaussienne avec une largeur définie (bandwidth)
        """
        return self.exp(-math.pi * (bandwidth ** 2) * self.dot(vector, vector))

    def polar_coordinates_coefficients(self, x: list, kernel_array: list) -> list:
        """
        polar_coordinates_coefficients retourne la somme des coordonnées polaires des vecteurs (A vérifier par Alexis)
        """
        return [self.gaussian(self.vector_subtraction(x, kernel[0]), kernel[3]) * self.sin(
            -self.dot(self.vector_subtraction(x, kernel[0]), kernel[1]) * kernel[2]) for kernel in kernel_array], \
            [self.gaussian(self.vector_subtraction(x, kernel[0]), kernel[3]) * self.cos(
                -self.dot(self.vector_subtraction(x, kernel[0]), kernel[1]) * kernel[2]) for kernel in kernel_array]

    def phase_func(self, x: list, kernel_array: list) -> float:
        """
        phase_func retourne la phase du bruit calculé
        """
        l1, l2 = self.polar_coordinates_coefficients(x, kernel_array)
        return self.atan2(sum(l1), sum(l2))

    def phasor_noise(self, x: list, kernel_array: list) -> float:
        """
            phasor_noise retourne le sinus de la phase du bruit calculé
        """
        return self.sin(self.phase_func(x, kernel_array))


def timeperf(func):
    def inner(*args, **kargs):
        import time
        begin = time.perf_counter_ns()
        result = func(*args, **kargs)
        end = time.perf_counter_ns()
        return result, end - begin

    return inner


class PythonPhasorGenerator(PhasorGenerator):

    def exp(self, x):
        return math.exp(x)

    def sin(self, x):
        return math.sin(x)

    def cos(self, x):
        return math.cos(x)

    def atan2(self, x, y):
        return math.atan2(x, y)

    def dot(self, vector1, vector2):
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def vector_subtraction(self, vector1: list, vector2: list):
        return [vector1[0] - vector2[0], vector1[1] - vector2[1]]


class NumpyPhasorGenerator(PhasorGenerator):

    def exp(self, x):
        return np.exp(x)

    def sin(self, x):
        return np.sin(x)

    def cos(self, x):
        return np.cos(x)

    def atan2(self, x, y):
        return np.arctan2(x, y)

    def dot(self, vector1, vector2):
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def vector_subtraction(self, vector1: list, vector2: list):
        return vector1 - vector2


@timeperf
def apply_noise_python(x: list, y: list, kernels: list) -> list:
    """
    apply_function applique à une matrice la fonction de bruit Phasor avec les noyaux passés en arguments
    Matrice : X, Y -> np.meshgrid()
    Un noyau est défini par : [position, direction, frequence, largeur]
    """
    Z = list()
    phasor_generator = PythonPhasorGenerator()
    for i in range(len(x)):
        Z.insert(i, [])
        for j in range(len(y)):
            vector = x[i][j], y[i][j]
            Z[i].insert(j, phasor_generator.phasor_noise(vector,
                                                         kernels))
    return Z


def create_numpy_kernel(kernels, size_x, size_y):
    for i in range(len(kernels)):
        kernels[i][0] = np.array([np.full((size_x, size_y), kernels[i][0][0]),
                                  np.full((size_x, size_y), kernels[i][0][1])])
        kernels[i][1] = np.array([np.full((size_x, size_y), kernels[i][1][0]),
                                  np.full((size_x, size_y), kernels[i][1][1])])
    return kernels


@timeperf
def apply_noise_numpy(x: list, y: list, kernels: list, size: list) -> list:
    kernels = create_numpy_kernel(kernels, size[0], size[1])
    Z = NumpyPhasorGenerator().phasor_noise(np.array([x, y]), kernels)
    return Z
