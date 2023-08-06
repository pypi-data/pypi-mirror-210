import numpy as np
from typing import Union

from .utils import valid_dim

class ET:
    def __init__(self, name: str = '', dim: int = 3, vector: Union[np.ndarray, list] = None) -> None:
        '''
        The `__init__` function is called when a new instance of the `ET` class is created.
        It initializes all of the variables in the class and sets them to their default values.

        By default, the `self.__vector` member value is set to zero.

        Parameters
        ----------
        - `name` (`str`): Set the name of the object (default: '')
        - `dim` (`int`): Set the dimension of the vector (default: 3)
        - `vector` (`np.ndarray|list`): Set value of vector at `__init__` (default: `None`)
        '''
        self.name = name

        if valid_dim(dim):
            self.__dim = dim

        if vector is None:
            self.__vector = np.zeros(self.__dim)
        else:
            if valid_dim(len(vector)):
                self.__dim = len(vector)
                self.__vector = np.array(vector)

    # Getter functions
    @property
    def dim(self) -> int:
        '''
        Return the number of dimensions.

        Returns
        -------
        - `int`: Value of `self.__dim` member
        '''
        return self.__dim

    @property
    def vector(self) -> np.ndarray:
        '''
        Return the value of the `self.__vector` member.

        Returns
        -------
        - `np.ndarray`: Value of `self.__vector` member
        '''
        return self.__vector

    @property
    def x(self) -> float:
        '''
        Return the first element of the `self.__vector` member.

        Returns
        -------
        - `float`: First element of the `self.__vector` member
        '''
        return float(self.vector[0])

    @property
    def y(self) -> float:
        '''
        Return the second element of the `self.__vector` member.

        Returns
        -------
        - `float`: Second element of the `self.__vector` member
        '''
        return float(self.vector[1])

    @property
    def z(self) -> float:
        '''
        Return the third element of the `self.__vector` member.

        Note: This function will only work for `ET` classes set to 3 dimensions.

        Returns
        -------
        - `float`: Third element of the `self.__vector` member
        '''
        return float(self.vector[2])

    # Setter functions
    def random(self) -> None:
        '''
        The `random` function sets the `self.__vector` member to a random state.
        '''
        self.vector = np.random.uniform(0, 1, size=self.vector.shape)

    @vector.setter
    def vector(self, vector: Union[np.ndarray, list]) -> None:
        '''
        The `vector` function sets the `self.__vector` to the input vector.

        The function also checks whether the input dimension matches the class dimension.

        Parameters
        ----------
        - `vector` (`Union[np.ndarray, list]`): Input vector
        '''
        if isinstance(vector, list):
            vector = np.array(vector)

        if vector.shape != self.__vector.shape:
            raise ValueError(
                f'Input vector dimension ({vector.shape[0]}) does not match the set dimension ({self.__vector.shape[0]}).'
            )

        self.__vector = vector

    def zero(self) -> None:
        '''
        The `zero` function sets the `self.__vector` to zero.
        '''
        self.vector = np.zeros(self.dim)

    def inv(self) -> None:
        '''
        The `inv` function sets the `self.__vector` member to its inverse (negative value).
        '''
        self.vector = -self.vector

    # Operator overloads
    def __str__(self) -> str:
        return f'ET{self.__dim} - {self.name}: {self.vector}'

    def __repr__(self) -> str:
        return f'{self.vector}'

    def __add__(self, other):
        if isinstance(other, ET):
            if other.vector.shape == self.vector.shape:
                return ET(name=f'Sum of {self.name} and {other.name}',
                          vector=self.vector + other.vector)

        elif isinstance(other, np.ndarray):
            if other.shape == self.vector.shape:
                return ET(name=self.name,
                           vector=self.vector + other)

        raise TypeError(f'Input parameter is {type(other)}, not ET or np.ndarray as expected.')

    def __sub__(self, other):
        if isinstance(other, ET):
            if other.vector().shape == self.vector.shape:
                return ET(name=f'Sum of {self.name} and {other.name}',
                          vector=self.vector - other.vector)

        elif isinstance(other, np.ndarray):
            if other.shape == self.vector.shape:
                return ET(name=self.name,
                           vector=self.vector - other)

        raise TypeError(f'Input parameter is {type(other)}, not ET or np.ndarray as expected.')

    def __iadd__(self, other):
        if not isinstance(other, (ET, np.ndarray)):
            raise TypeError(f'Input parameter is {type(other)}, not ET or np.ndarray as expected.')

        if isinstance(other, ET):
            if other.vector.shape == self.vector.shape:
                self.vector = self.vector + other.vector

        elif isinstance(other, np.ndarray):
            if other.shape == self.vector.shape:
                self.vector = self.vector + other

    def __isub__(self, other):
        if isinstance(other, ET):
            if other.vector().shape == self.vector.shape:
                self.vector = self.vector - other.vector

        elif isinstance(other, np.ndarray):
            if other.shape == self.vector.shape:
                self.vector = self.vector - other

        raise TypeError(f'Input parameter is {type(other)}, not ET or np.ndarray as expected.')

    def __eq__(self, other):
        if isinstance(other, ET):
            return np.array_equal(self.vector, other.vector)

        elif isinstance(other, np.ndarray):
            return np.array_equal(self.vector, other)

        raise TypeError(f'Input parameter is {type(other)}, not ET or np.ndarray as expected.')

    def __ne__(self, other):
        if isinstance(other, ET):
            return not np.array_equal(self.vector, other.vector)

        elif isinstance(other, np.ndarray):
            return not np.array_equal(self.vector, other)

        raise TypeError(f'Input parameter is {type(other)}, not ET or np.ndarray as expected.')

    def __neg__(self):
        self.vector = -self.vector

    def __abs__(self):
        self.vector = abs(self.vector)
