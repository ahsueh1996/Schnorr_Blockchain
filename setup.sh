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