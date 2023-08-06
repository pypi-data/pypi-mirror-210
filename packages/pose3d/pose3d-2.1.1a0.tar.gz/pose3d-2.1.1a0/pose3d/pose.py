from .et import ET
from .er import ER
from typing import Tuple

from .utils import valid_dim

class Pose:
    def __init__(self, name: str = '', et_dim: int = 3, er_dim: int = 3) -> None:
        '''
        The `__init__` function is called when a new instance of the `Pose` class is created.
        It initializes all of the variables in the class and sets them to their default values.

        Parameters
        ----------
        - `name` (`str`): Set the name of the object (default: '')
        - `et_dim` (`int`): Set the dimension of the position member (default: 3)
        - `er_dim` (`int`): Set the dimension of the orientation member (default: 3)
        '''
        self.name = name

        if valid_dim(et_dim):
            self.position = ET(dim=et_dim)

        if valid_dim(er_dim):
            self.orientation = ER(dim=er_dim)

    # Setter functions
    def random(self) -> None:
        '''
        Sets the position and orientation to random values.
        '''
        self.orientation.random()
        self.position.random()

    def zero(self) -> None:
        '''
        Sets the position vector to zero and orientation to identity.
        '''
        self.orientation.identity()
        self.position.zero()

    # Getter functions
    def dims(self) -> Tuple[int, int]:
        '''
        Returns the dimensions of the position and orientation (in that order).

        Returns
        -------
        - `tuple[int, int]`: Dimension of position and orientation (in that order)
        '''
        return self.position.dim, self.orientation.dim

    # Operator overloads
    def __str__(self) -> str:
        return f'''Pose - {self.name}:
        Position:    {self.position.__repr__}
        Orientation: {self.orientation.__repr__}'''

    def __repr__(self) -> str:
        return f'Position:    {self.position.__repr__}\nOrientation: {self.orientation.__repr__}'

    def __eq__(self, other) -> bool:
        if isinstance(other, Pose) and other.dims() == self.dims():
            return self.orientation == other.orientation and self.position == other.position

        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, Pose) and other.dims() == self.dims():
            return self.orientation != other.orientation or self.position != other.position

        return False
