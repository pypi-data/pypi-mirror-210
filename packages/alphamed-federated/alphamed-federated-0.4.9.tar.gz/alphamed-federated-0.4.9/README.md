# AlphaMed

AlphaMed 是一个基于区块链技术的去中心化联邦学习解决方案，旨在使医疗机构能够在保证其医疗数据隐私和安全的同时，实现多机构联合建模。医疗机构可以在本地节点实现模型的训练，并支持以匿名的身份将加密的参数共享至聚合节点，从而实现更安全、可信的联邦学习。

相比于传统的联邦学习，AlphaMed 平台不仅能够确保只有合法的且经过许可的参与者才能加入网络，同时支持节点的匿名化的参与联合建模。同时，区块链的共识算法能够确保网络中的节点得到一直的决策，恶意的参与者或者数据投毒等攻击将被拒绝，从而保证了联邦学习更好的安全性。

在联邦学习的过程中，各个参与方都受到智能合约的约束，并且所有的事件、操作都将被记录在区块链的分布式账本上，可追溯、可审计，使得联合机器学习的安全性和隐私保护能力极大的提升。

[开始构建第一个联邦学习任务](src/alphafed/docs/fed_avg/README.md)

[在不同结构的数据源之间构建异构联邦学习任务](src/alphafed/docs/hetero_nn/README.md)

如果 AlphaMed 平台预置的现有算法依然无法满足业务需要，还可以自行设计联邦学习算法，并使其运行在 AlphaMed 平台之上。[这里](src/alphafed/docs/customized_scheduler/README.md)展示了如果自定义联邦学习算法，并通过 AlphaMed 平台实际执行联邦学习任务。为了帮助开发者调试自己的代码，AlphaMed 平台还提供了一套[模拟运行环境](src/alphafed/docs/mock/README.md)，以在本地节点模拟实际运行环境，包括联邦学习运行环境。

AlphaMed 平台除面向算法工程师提供了开发联邦学习模型的支持外，还面向模型使用者提供了预训练模型的支持。与传统预训练模型相比，AlphaMed 平台上的预训练模型支持功能更为强大、使用更为方便。在 AlphaMed 平台上，不仅可以寻找并下载心仪的预训练模型，更可以利用私有数据微调、部署预训练模型，使其更加适配于私有的业务数据。

AlphaMed 平台预置了一定数量的预训练模型，同时也支持第三方开发者开发上传自己的预训练模型。[这里展示了如何设计自己的预训练模型。](src/alphafed/docs/auto_ml/README.md)

## 项目目录说明

src/alphafed  
├── auto_ml  *AutoML 模块*  
│   └── cvat  *CVAT 工具*  
├── contractor  *合约消息工具*  
├── data_channel  *数据传输工具*  
├── docs  *说明文档*  
│   ├── auto_ml  *AutoML 说明文档*  
│   ├── customized_scheduler  *自定义调度器说明文档*  
│   ├── fed_avg  *FedAvg 横向联邦说明文档*  
│   ├── hetero_nn  *HeteroNN 异构联邦说明文档*  
│   ├── mock  *模拟调试说明文档*  
│   └── tutorial  *tutorial 示例说明文档，包含所有主要功能*  
├── examples  *脚本测试代码 / 示例代码*  
├── fed_avg  *FedAvg 横向联邦模块*  
├── hetero_nn  *HeteroNN 异构联邦模块*  
│   └── psi  *隐私求交模块*  
├── secure  *安全工具*  
├── fs.py  *文件系统工具*  
├── loggers.py  *日志工具*  
├── mock.py  *模拟调试工具*  
└── utils.py  *其它工具*
