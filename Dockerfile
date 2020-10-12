
FROM fedora:latest

# Note: slurmrestd requires libyaml, http-parser and json-c-devel
RUN dnf -y group install "Development Tools" && \
    dnf -y group install "Development Libraries" && \
    dnf -y group install "C Development Tools and Libraries" && \
    dnf -y install cmake && \
    dnf -y install g++ && \
    dnf -y install docker && \
    dnf -y install git && \
    dnf -y install hostname && \
    dnf -y install munge && \
    dnf -y install munge-devel && \
    dnf -y install procps-ng && \
    dnf -y install python && \
    dnf -y install python-pip && \
    dnf -y install vim && \
    dnf -y install tmux && \
    dnf -y install jansson && \
    dnf -y install jansson-devel && \
    dnf -y install libyaml && \
    dnf -y install libyaml-devel && \
    dnf -y install http-parser && \
    dnf -y install http-parser-devel && \
    dnf -y install json-c && \
    dnf -y install json-c-devel && \
    dnf -y install bzip2

# Install libjwt
RUN source /etc/profile && \
    curl -O -L https://github.com/benmcollins/libjwt/archive/v1.12.0.tar.gz && \
    tar -xvf v1.12.0.tar.gz && \
    cd libjwt-1.12.0 && \
    autoreconf -fiv && \
    ./configure --prefix=/usr --disable-valgrind --disable-doxygen-doc && \
    make && \
    make install

# Install Charliecloud (the fedora package is out of date)
RUN curl -O -L https://github.com/hpc/charliecloud/releases/download/v0.16/charliecloud-0.16.tar.gz && \
    tar -xvf charliecloud-0.16.tar.gz && \
    cd charliecloud-0.16 && \
    ./configure --prefix=/usr --libdir=/usr/lib && \
    make && \
    make install

# TODO: Changing permissions of the munge directories may not be necessary
RUN curl -O -L https://download.schedmd.com/slurm/slurm-20.02.3.tar.bz2 && \
    tar -xvf slurm-20.02.3.tar.bz2 && \
    cd slurm-20.02.3 && \
    ./configure --prefix=/usr --with-hdf5 --with-rrdtool --with-munge --with-jwt --enable-slurmrestd && \
    make && \
    make install && \
    useradd slurm && \
    mkdir -p /var/spool/slurm && \
    chown slurm /var/spool/slurm && \
    mkdir -p /var/spool/slurmd && \
    chown slurm /var/spool/slurmd && \
    mkdir -p /etc/slurm && \
    chown -R munge:munge /var/run/munge && \
    chown -R munge:munge /var/lib/munge

# Stop warnings about *_state files not existing
RUN touch /var/spool/slurm/node_state && \
    chown slurm:slurm /var/spool/slurm/node_state && \
    touch /var/spool/slurm/job_state && \
    chown slurm:slurm /var/spool/slurm/job_state && \
    touch /var/spool/slurm/trigger_state && \
    chown slurm:slurm /var/spool/slurm/trigger_state

# Generate the JWT key
# Note: AuthAltTypes=auth/jwt must be specified in slurm.conf
RUN openssl genrsa -out /var/spool/slurm/jwt_hs256.key 4096 && \
    chown slurm:slurm /var/spool/slurm/jwt_hs256.key && \
    chmod 0700 /var/spool/slurm/jwt_hs256.key

# Use `scontrol token` to generate a token
# See <https://slurm.schedmd.com/jwt.html>

COPY cgroup.conf cgroup_allowed_devices_file.conf slurm.conf.template /etc/
# Make sure that the CONF file is properly configured
COPY init rcfile bee-setup CONF /

VOLUME /data

ENTRYPOINT /init

