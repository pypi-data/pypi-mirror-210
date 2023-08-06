import toml
import numpy as np
from pathlib import Path

from typing import Union

from .utils import VALID_ROTATION_TYPES
from .pose import Pose
from .transform import Transform


class TransformSet:
    def __init__(self, transf_set: Union[str, Path, dict]) -> None:

        self.frames = {}
        if isinstance(transf_set, str) or isinstance(transf_set, Path):
            path = Path(transf_set)
            if not path.exists():
                raise ValueError(f'Input path ({path.as_posix()}) not found or does not exist.')

            self.__frame_data = toml.load(transf_set)
        elif isinstance(transf_set, dict):
            self.__frame_data = transf_set

        # Create dictionary of frames (from which we can create transformations)
        for frame_name, frame_data in self.__frame_data.items():
            self.add_frame(frame_name=frame_name, frame_data=frame_data)

        # Add base frame if not present
        if 'base' not in self.frame_names():
            base_frame = Pose(name='base')
            base_frame.position.zero()
            base_frame.orientation.identity()
            self.frames['base'] = base_frame


    # Setter methods
    def add_frame(self, frame_name: str, frame_data: Union[dict, Pose]) -> None:
        '''
        Add frame to transform set.

        Parameters
        ----------
        - `frame_name` (`str`): Name of new frame
        - `frame_data` (`dict | Pose`): Data of frame
        '''
        if frame_name == '' or frame_name in self.frame_names():
            raise ValueError(f"Invalid pose name {frame_name}. Please use a different name.")

        if isinstance(frame_data, Pose):
            new_frame = frame_data
            new_frame.name = frame_name

        elif isinstance(frame_data, dict):
            new_frame = Pose(name=frame_name)

            # Extract position
            new_frame.position.vector = frame_data['position']

            # Extract orientation
            orientation_value = frame_data['orientation']
            orientation_type = frame_data['orientation_type'].lower()
            degrees = 'degree' in frame_data['orientation_units'].lower()

            if orientation_type == 'euler':
                new_frame.orientation.from_euler('xyz', orientation_value, degrees=degrees)
            elif orientation_type == 'quaternion':
                new_frame.orientation.from_quat(orientation_value)
            elif orientation_type == 'angle-axis':
                new_frame.orientation.from_angle_axis(orientation_value)
            elif orientation_type == 'matrix':
                new_frame.orientation.from_matrix(orientation_value)
            else:
                raise ValueError(f'TransformSet - Invalid rotation type: {orientation_type}. Rotation type must be: {VALID_ROTATION_TYPES}')

        # Save new frame to self.frames
        self.frames[frame_name] = new_frame


    # Getter methods
    def frame_names(self) -> list:
        '''
        Return list of frame names.

        Returns
        -------
        - `list`: List of saved frame names
        '''
        return self.frames.keys()


    def change_frame(self, input_element, from_frame: str, to_frame: str) -> np.ndarray:
        '''
        Coordinate transformation of a pose (6D vector) from origin frame to target frame.

        A compound transformation from origin frame (defined in `from_frame` argument) to
        the target frame (defined in `to_frame` argument) is computed and applied to the
        input pose.

        Parameters
        ----------
        - `input` (`np.ndarray`): Input pose
        - `from_frame` (`str`): Name of origin frame
        - `to_frame` (`str`): Name of target frame

        Returns
        -------
        - `np.ndarray`: Transformed pose in target frame
        '''
        # Create compound transformation
        transformation = self.__create_compound_transf(from_frame=from_frame, to_frame=to_frame)

        return transformation.apply(input_element)


    def wrench_change_frame(self, wrench: np.ndarray, from_frame: str, to_frame: str) -> np.ndarray:
        '''
        Method to change frame of wrench vector.

        Method will perform simple rotation on forces (first three elements), and
        will rotate the total moments on the origin frame.

        Parameters
        ----------
        - `wrench` (`np.ndarray`): Input wrench array
        - `from_frame` (`str`): Name of origin frame
        - `to_frame` (`str`): Name of target frame

        Returns
        -------
        - `np.ndarray`: Transformed wrench array
        '''
        # Verify input
        if np.array(wrench).shape != (6,):
            raise ValueError('TransformSet - Invalid wrench input. Shape must be (6,)')

        # Create compound transformation
        transformation = self.__create_compound_transf(from_frame=from_frame, to_frame=to_frame)

        # Transform wrench
        force_at_orig = wrench[:3]
        torque_at_orig = wrench[3:]

        torque_at_dest = transformation.rotation.apply(np.cross(force_at_orig, transformation.translation) + torque_at_orig)
        force_at_dest = transformation.rotation.apply(force_at_orig)

        return np.hstack([force_at_dest, torque_at_dest])


    def transform_matrix(self, from_frame: str, to_frame: str, homogeneous: bool = True) -> np.ndarray:
        '''
        Return the transformation matrix to transform poses from origin
        frame to destination frame.

        Method will call the `__create_compound_transf()` method. Note that such a matrix
        can only be directly used for poses. Other calculations are required for wrench
        transformations.

        Parameters
        ----------
        - `from_frame` (`str`): Name of origin frame
        - `to_frame` (`str`): Name of target frame
        - `homogeneous` (`bool`): Option if matrix should be homogenous or not (3x4 or 4x4) (default: `True`)

        Returns
        -------
        - `np.ndarray`: Numpy matrix
        '''
        # Create compound transformation
        full_transf = self.__create_compound_transf(from_frame, to_frame)

        return full_transf.matrix(homogeneous=homogeneous)


    def __create_compound_transf(self, from_frame: str, to_frame: str) -> Transform:
        '''
        Method to create compound transform between two frames.

        Parameters
        ----------
        - `from_frame` (`str`): Name of origin frame
        - `to_frame` (`str`): Name of destination frame

        Returns
        -------
        - `Transform`: Transform object
        '''
        transformation = Transform(name=f'{from_frame}2{to_frame}', orig=from_frame, dest=to_frame)
        transformation.between_poses(pose_1=self.frames[from_frame], pose_2=self.frames[to_frame])

        return transformation
