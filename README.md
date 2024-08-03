# Schnorr Signature for Blockchain 🌐

## Table of Contents
- [Background](#background)
- [Method](#method)
- [Experiments](#experiments)
- [Visualize](#visualize)
- [Setup and Example Run](#setup-and-example-run)
- [Simulation Table](#simulation-table)

## Background
Blockchain technology faces several challenges that hinder its adoption. One of the major issues is **scalability**. 🏗️

### Challenges with Blockchain Adoption
#### Scalability ⚖️
A major challenge of blockchain networks is related to the technical scalability of the network which can put a strain on the adoption process, especially for public blockchains. In contrast, legacy transaction networks are known for their ability to process thousands of transactions per second. Visa, for example, is capable of processing more than 2000 transactions per second. In contrast, the two largest blockchain networks, Bitcoin and Ethereum fall short when it comes to transaction speeds. The Bitcoin blockchain can process three to seven transactions per second, and Ethereum can handle approximately 20 transactions in a second. Compared to their centralized counterparts, this gap in performance deems the technology as non-viable for large-scale adoption. 

## Method
We can extend this [code](https://github.com/adilmoujahid/blockchain-python-tutorial/blob/master/blockchain/blockchain.py) to make it into an experimental framework for research like ours.

- Abstract out the hashing and verification process
- Ability to compute how much storage was used
- Ability to simulate throughput etc or at least keep track of it in a log

Then we can deploy instances across many servers and then collect simulation data from it.

## Experiments
We will conduct the following experiments:

- Size of block 📦
- Benchmark verification and signing time ⏱️
- Transaction throughput 🚀
- Block mining latency ⛏️
- Number of forks 🌿
- Consensus 🗳️

### Static Measurements
#### Size of Block 📏
- Stuff a block with n transactions and measure the size of the exported dictionary.
- Vary n in 0 U N
- Vary DSA in {schnorr, ecdsa}

#### Verification and Signing Latency ⏳
- Average over 10,000 transactions
- Vary DSA in {schnorr, ecdsa}
- Prepare the transactions without signing them, then sign and verify them.

### Dynamic Measurements
#### Block Mining Latency ⛏️
- For each difficulty in DIFF, measure how long it takes the network to mine a new block on average.
- Find the DIFFs that give us {1s, 15s, 60s}
- Mine 60 blocks varying DSA, N, and DIFF and measure:
  - Transaction Throughput
  - Simultaneous Forks
  - Longest Forks

## Visualize
- Network on a world map and their peer clusters if that matters (it might be why we have long forks).
- The blockchain and what the forks look like. Is there a consensus chain in the end?
- Time vs transactions submitted.

![Network Map](https://github.com/ahsueh1996/Schnorr_Blockchain/blob/master/Simulation.png)

## Setup and Example Run
```bash
cd ~
git clone https://github.com/ahsueh1996/Schnorr_Blockchain.git

apt-get --assume-yes install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6

wget -O anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh

chmod 777 anaconda.sh
./anaconda.sh -b

export PATH=~/anaconda3/bin:$PATH

conda init

cd ~/Schnorr_Blockchain

conda env create -f blockchain_conda_env_linux.yml

bash run.sh experiments/exp2_simulation_instance.py
bash run.sh experiments/exp2_master.py
```

## Simulation Table
| SIG     | Diff (p)  | Diff (s)  | T.lim | T.rate | T.transacted | T.gen | B.mined | Avg t/s | t.efficiency |
|---------|-----------|-----------|-------|--------|--------------|-------|---------|---------|--------------|
| Schnorr | 4         | 4.47209   | 10    | 3      | 556          | 664   | 50      | 1.24    | 0.837        |
|         | 1         | 2.6751    | 10    | 3      | 2046         | 1477  | 80      | 3.18    | 1.38524      |
|         | 5         | 37.925    | 10    | 3      | 247          | 176   | 15      | 0.1453  | 1.4          |
|         | 4         | 4.0159    | 50    | 15     | 362          | 531   | 50      | 0.90114 | 0.6817       |
|         | 4         | 26.11288  | 90    | 15     | 706          | 2990  | 50      | 0.5407  | 0.23612      |
|         | 4         | 18.6795   | 90    | 15     | 2031         | 2625  | 50      | 1.0447  | 0.77         |
| Ecdsa   | 4         | 3.6609    | 10    | 3      | 327          | 509   | 50      | 0.8909  | 0.6424       |
|         | 6         | 4.65255   | 10    | 3      | 619          | 630   | 50      | 1.2811  | 0.9825       |
|         | 5         | 60.06     | 10    | 15     | 462          | 921   | 15      | 0.17    | 0.50         |
|         | 5         | 55.819    | 10    | 3      | 373          | 181   | 15      | 0.16    | 2.06         |
|         | 4         | 4.49      | 10    | 3      | 340          | 197   | 15      | 1.725   | 1.7          |
|         | 1         | 0.66858   | 10    | 3      | 3224         | 1876  | 80      | 14.6899 | 1.718        |

