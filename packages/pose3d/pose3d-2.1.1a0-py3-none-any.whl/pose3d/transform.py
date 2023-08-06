import numpy as np
from typing import Tuple, Union

from .et import ET
from .er import ER

from .pose import Pose

from .utils import valid_dim

class Transform:
    def __init__(self, name: str, orig: str = 'origin', dest: str = 'destination', te_dim: int = 3, re_dim: int = 3) -> None:
        # Set strings
        self.name = name
        self.origin = orig
        self.destination = dest

        # Init translation and rotation members
        if valid_dim(te_dim):
            self.translation = ET(dim = te_dim)

        if valid_dim(re_dim):
            self.rotation = ER(dim = re_dim)

    # Setter functions
    def between_poses(self, pose_1: Pose, pose_2: Pose) -> None:
        '''
        Compute transform between 2 3D poses. This instance of Transform
        will be modified to compute the transform from pose_1 to pose_2.

        Parameters
        ----------
        - `pose_1` (`Pose`): Origin pose.
        - `pose_2` (`Pose`): Destination pose.
        '''
        if pose_1.dims() != pose_2.dims():
            raise AttributeError(f'Number of dimensions between both poses do not match: pose_1.dims() = {pose_1.dims()} and pose_2.dims = {pose_2.dims()}.')

        # Modify dimension of transformation depending on pose_1 and pose_2
        if pose_1.position.dim != self.translation.dim:
            self.translation = ET(dim=pose_1.position.dim)

        if pose_1.orientation.dim != self.rotation.dim:
            self.rotation = ER(dim=pose_1.orientation.dim)

        # Compute rotation from pose_1 to pose_2
        self.rotation.from_matrix(np.dot(np.linalg.inv(pose_2.orientation.as_matrix()), pose_1.orientation.as_matrix()))
        self.translation.vector = pose_2.position.vector - pose_1.position.vector

    def identity(self) -> None:
        '''
        Set the transformation to zero and the rotation to identity.
        '''
        self.translation.zero()
        self.rotation.identity()

    def inv(self) -> None:
        '''
        Set the transformation it's inverse.
        '''
        self.rotation.inv()
        self.translation.vector = -self.rotation.apply(self.translation.vector)

    def random(self) -> None:
        '''
        Set a random transformation.
        '''
        self.translation.random()
        self.rotation.random()

    # Getter functions
    def dims(self) -> Tuple[int, int]:
        '''
        Returns the dimensions of the translation and rotation (in that order).

        Returns
        -------
        - `tuple[int, int]`: Dimension of translation and rotation (in that order)
        '''
        return self.translation.dim, self.rotation.dim

    def matrix(self, homogeneous: bool = True) -> np.ndarray:
        '''
        Return the transformation matrix.

        Returns
        -------
        - `np.ndarray`: Transformation matrix
        '''
        matrix = np.eye(max(self.dims()) + 1)

        if self.origin != self.destination:
            matrix[:self.rotation.dim, :self.rotation.dim] = self.rotation.as_matrix()
            matrix[:self.translation.dim, -1] = self.translation.vector

        if not homogeneous:
            return matrix[:-1, :]

        return matrix

    # Computation functions
    def apply(self, io_element: Union[Pose, np.ndarray]) -> Union[Pose, np.ndarray]:
        '''
        Apply transformation to `io`.

        Parameters
        ----------
        - `io_element` (`Union[Pose, np.ndarray]`): Element to apply transformation to

        Returns
        -------
        - `Union[Pose, np.ndarray]`: Output pose/vector
        '''
        # If io_element is a Pose
        if isinstance(io_element, Pose):
            output = Pose(et_dim=io_element.position.dim, er_dim=io_element.orientation.dim)
            output.position.vector = io_element.position.vector
            output.orientation.from_quat(io_element.orientation.as_quat())

            output.orientation.from_matrix(np.dot(self.rotation.as_matrix(), output.orientation.as_matrix()))
            output.position.vector = self.rotation.apply(output.position.vector) + self.translation.vector

        # If io_element is a numpy vector
        if isinstance(io_element, np.ndarray):
            output = io_element.copy()
            output = self.rotation.apply(output) + self.translation.vector

        return output

    # Operator overloads
    def __repr__(self) -> str:
        return f'''Transform - {self.name}:
        Translation: {self.translation.__repr__}
        Rotation:    {self.rotation.__repr__}'''

    def __str__(self) -> str:
        return f'Translation: {self.translation.__repr__}\nRotation:    {self.rotation.__repr__}'

    def __eq__(self, other: object) -> bool:
        return self.translation == other.translation and self.rotation == other.rotation

    def __ne__(self, other: object) -> bool:
        return self.translation != other.translation or self.rotation != other.rotation
