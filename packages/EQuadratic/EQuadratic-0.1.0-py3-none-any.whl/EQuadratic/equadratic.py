import math

class Quadratic:
    def __init__(self, value_a, value_b, value_c):
        """
        Sets up a quadratic equation
        :param value_a: a coefficient in the equation
        :param value_b: b coefficient in the equation
        :param value_c: c coefficient in the equation
        """
        self.a = (value_a)
        self.b = (value_b)
        self.c = (value_c)

    def roots(self):
        """Returns the x-intercepts (roots) of the equation"""
        try:
            numerator1 = -self.b + math.sqrt((self.b ** (2) - (4) * self.a * self.c))
            numerator2 = -self.b - math.sqrt((self.b ** 2) - (4 * self.a * self.c))
            return (numerator1/2 * self.a, numerator2/2 * self.a)
        except:
            return None # in case of any no REAL roots

    def analysis(self):
        """uses discriminant to analyze and return how many REAL roots said equation has"""
        discriminant = (self.b ** 2) - (4 * self.a * self.c)
        if discriminant > 0:
            return 2
        elif discriminant == 0:
            return 1
        else:
            return 0 # no real roots

    def vertex(self):
        h = -(self.b/2 * self.a)
        k = (self.a * (h ** 2)) + (self.b * h) + self.c
        return (h, k)



