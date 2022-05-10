FROM debian:11

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y git curl vim tmux screen gcc make openmpi-bin \
                       libopenmpi-dev python3 python3-venv python3-requests \
                       mariadb-server
# install Charliecloud
ENV CHARLIECLOUD_INSTALL=/opt/charliecloud-0.27
RUN curl -O -L https://github.com/hpc/charliecloud/releases/download/v0.27/charliecloud-0.27.tar.gz && \
    tar -xvf charliecloud-0.27.tar.gz && \
    cd charliecloud-0.27 && \
    ./configure --prefix=$CHARLIECLOUD_INSTALL && \
    make && \
    make install && \
    printf "export PATH=$CHARLIECLOUD_INSTALL/bin:\$PATH\n" > /etc/profile.d/charliecloud.sh

# install Slurm and munge
RUN apt-get install -y slurmd slurmctld slurmrestd munge && \
    rm -f /etc/munge/munge.key && \
    mungekey -c && \
    mkdir -p /var/spool/slurmctld

# TODO: add mariadab and slurmdbd configuration here if needed

# editor configuration
RUN printf "syntax on\n" > /etc/vim/vimrc && \
    printf "filetype indent off\n" >> /etc/vim/vimrc && \
    printf "set mouse-=a\n" >> /etc/vim/vimrc

COPY init init.py /
