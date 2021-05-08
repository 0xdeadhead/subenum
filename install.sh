#! /bin/bash

##Install dependencies
sudo apt update -y && sudo apt install -y build-essential make git software-properties-common wget gcc zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev
sudo add-apt-repository ppa:ubuntu-toolchain-r/test && sudo apt update && sudo apt install gcc-10 g++-10
## set default g++ to g++-10
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 100 --slave /usr/bin/g++ g++ /usr/bin/g++-10 --slave /usr/bin/gcov gcov /usr/bin/gcov-10
## soft link c++ from g++
sudo ln -s /usr/bin/g++ /usr/bin/c++

##Install python
function install_python {
    sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update
    sudo apt install python3.8
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 100
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo python3 get-pip.py

}

function install_cmake {
    sudo apt install ./bin/cmake_3.20.2-1_amd64.deb
}

function install_massdns {
    ##Install massdns
    git clone https://github.com/blechschmidt/massdns.git
    cd massdns/ && make && sudo mv bin/massdns /usr/bin/
    cd ..
}

function install_urldedupe {
    git clone https://github.com/ameenmaali/urldedupe.git
    cd urldedupe
    cmake CMakeLists.txt && make && chmod +x urldedupe && sudo mv urldedupe /usr/bin
    cd ..
}

##Install findomain
function install_findomain {
    chmod +x bin/findomain
    sudo mv bin/findomain /usr/bin/
}

function install_goutils {
    ##Install assetfinder
    go get -u github.com/tomnomnom/assetfinder

    ##Install subfinder
    GO111MODULE=on go get -u -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder

    ##Install crobat
    go get -u github.com/cgboal/sonarsearch/crobat

    ##Install shuffledns
    GO111MODULE=on go get -u -v github.com/projectdiscovery/shuffledns/cmd/shuffledns
}

##Install Golang
function install_golang {
    wget https://dl.google.com/go/go1.15.2.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.15.2.linux-amd64.tar.gz
    echo "export PATH=\"${PATH}:/usr/local/go/bin:${HOME}/go/bin\"" >>$HOME/.profile
    echo "export GOPATH=\"${HOME}/go\"" >>$HOME/.profile
    source $HOME/.profile
}

function configure_subenum {
    sudo pip3 install .
    cp -r subenum_config ~
}

function install_pythonutils {
    ##Install dnsvalidator
    git clone https://github.com/vortexau/dnsvalidator.git
    cd dnsvalidator/
    sudo python3 setup.py install
    cd ..
    ## Install subtrails
    git clone https://github.com/0xdeadhead/Subtrails.git
    cd Subtrails
    sudo pip3 install .
    cd ..
    ##Install dnsgen
    git clone https://github.com/ProjectAnte/dnsgen
    cd dnsgen
    sudo pip3 install .
    cd ..

}

function checkInstallations {
    clear
    echo -e "These tools are not found in path\n Install Manually"
    type python3.8 cmake g++ c++ urldedupe massdns findomain assetfinder subfinder crobat shuffledns go subenum dnsvalidator subtrails dnsgen pip3 2>&1 | grep "^-bash" | cut -d ":" -f 3
}

install_cmake
type massdns || install_massdns
type findomain || install_findomain
type go || install_golang
install_goutils
type python3 && dpkg --compare-versions "$(python3 --version | cut -f 2 -d ' ')" "lt" "3.7.0" && install_python
install_pythonutils
type massdns || install_massdns
type urldedupe || install_urldedupe
configure_subenum
checkInstallations
