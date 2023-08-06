ER_TOLERANCE = 1e-10
ET_TOLERANCE = 1e-10

def valid_dim(input_dim: int) -> bool:
    '''
    Check if an input dimension value is valid for `pose3d` application

    Parameters
    ----------
    - `input_dim` (`int`): Input dimension

    Returns
    -------
    - `bool`: True if valid dimension.
    '''
    valid_dims = [2, 3]

    if input_dim not in valid_dims:
        raise ValueError(f'Input value for dim argument ({input_dim}) is not valid. Use one of the following: {valid_dims}.')

    return True

VALID_ROTATION_TYPES = ['euler', 'quaternion', 'angle-axis', 'matrix', 'rodrigues']
