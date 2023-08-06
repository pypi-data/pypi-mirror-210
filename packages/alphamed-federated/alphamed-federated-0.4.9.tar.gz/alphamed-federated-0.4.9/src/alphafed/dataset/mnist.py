"""FedMNIST: A Federated Learning Enabled Extension of the MNIST Dataset

Please Note: This is not the FEMNIST dataset.
"""

from typing import Any, Callable, List

import torch
from torch import Tensor
from torchvision.datasets.mnist import MNIST


class FedMNIST(MNIST):
    """A Federated Learning Enabled Extension of the MNIST Dataset.

    Args:
        root (string): Root directory of dataset where ``FedMNIST/raw/train-images-idx3-ubyte``
            and  ``FedMNIST/raw/t10k-images-idx3-ubyte`` exist.
        train (bool, optional): If True, creates dataset from ``train-images-idx3-ubyte``,
            otherwise from ``t10k-images-idx3-ubyte``.
        download (bool, optional): If True, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        client_ids: The MNIST dataset is divided into 10 equal parts, with each client_id
            corresponding to one portion of the data to simulate different participants
            having different data. client_ids can either be an int value representing the
            loading of a portion of data, or an int array indicating the loading of all
            specified portions in the list. The value range of client_ids is from 1 to 10,
            inclusive on both ends.
    """

    def __init__(self,
                 root: str,
                 train: bool = True,
                 transform: Callable[..., Any] | None = None,
                 target_transform: Callable[..., Any] | None = None,
                 download: bool = False,
                 client_ids: int | List[int] = list(range(1, 11))) -> None:
        assert (
            (isinstance(client_ids, int) and 0 < client_ids < 11)
            or (isinstance(client_ids, list)
                and all(isinstance(_id, int) and 0 < _id < 11 for _id in client_ids))
        ), f'Invalid Client IDs, they must be an int or a list of int in the range of [1, 10]'
        self.client_ids = [client_ids] if isinstance(client_ids, int) else client_ids
        self.client_ids = list(set(self.client_ids))
        self.client_ids.sort()

        super().__init__(root=root,
                         train=train,
                         transform=transform,
                         target_transform=target_transform,
                         download=download)

    mirrors = [
        "https://alphamed-share-1309103037.cos.ap-beijing.myqcloud.com/dataset/",
        "http://yann.lecun.com/exdb/mnist/",
        "https://ossci-datasets.s3.amazonaws.com/mnist/",
    ]

    resources = [
        ("train-images-idx3-ubyte.gz", "f68b3c2dcbeaaa9fbdd348bbdeb94873"),
        ("train-labels-idx1-ubyte.gz", "d53e105ee54ea40749a09fcbcd1e9432"),
        ("t10k-images-idx3-ubyte.gz", "9fb629c4189551a2d022fa330f9573f3"),
        ("t10k-labels-idx1-ubyte.gz", "ec29112dd5afa0611ce80d1b7f02629c"),
    ]

    def __repr__(self) -> str:
        lines = super().__repr__().split('\n')
        indent = " " * self._repr_indent
        lines.append(f'{indent}Features: [image, label]')
        lines.append(f'{indent}Available Client IDs: [1, 2, ..., 10]')
        lines.append(f'{indent}Current Client IDs: {self.client_ids}')
        return '\n'.join(lines)

    def _load_data(self):
        data, targets = super()._load_data()
        client_data: Tensor = None
        client_targets: Tensor = None
        slice_size = 6000 if self.train else 1000
        for client_id in self.client_ids:
            data_slice = data[slice_size * (client_id - 1) : slice_size * client_id]
            if client_data is None:
                client_data = data_slice
            else:
                client_data = torch.cat([client_data, data_slice], dim=0)
            targets_slice = targets[slice_size * (client_id - 1) : slice_size * client_id]
            if client_targets is None:
                client_targets = targets_slice
            else:
                client_targets = torch.cat([client_targets, targets_slice], dim=0)
        return client_data, client_targets
