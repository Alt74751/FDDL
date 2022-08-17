# FDDL
FDDL is a cooperative cache approach.  
This repository contains cache environment and interaction between nodes of FDDL.

The implementation of Federated Learning can be referenced to [FedAvg](https://github.com/WHDY/FedAvg/) and [adaptive-federated-learning](https://github.com/IBM/adaptive-federated-learning).

The implementation of Deep Reinforcement Leanring can be referenced to [ElegantRL](https://github.com/AI4Finance-Foundation/ElegantRL).

The dataset is built in the following form:

  - Prepare the original dataset as: 
    > <timestamp, contentID, contentSize>

  - Extract features as:
    > <timestamp, contentID, contentSize, frequency, timestamp between two same content, interval between two same content, frequency in different time spans>
