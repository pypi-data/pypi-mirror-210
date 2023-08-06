"""本地数据验证 demo."""

import os
from typing import Tuple

from alphafed.scheduler import DataChecker


class DatasetCheckerDemo(DataChecker):

    def __init__(self):
        self.root_dir = '/data/alphamed-federated/FedIRM/'

    def verify_data(self) -> Tuple[bool, str]:
        """数据集的校验具体逻辑."""
        if not os.path.isdir(self.root_dir):
            return False, f'The directory of data does not exist: {self.root_dir}'

        return True, 'Varification Complete.'
