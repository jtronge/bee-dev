#!/usr/bin/env python3
"""
Init script for configuring and starting Slurm and Munge and a shell for
development. Upon exit from the shell, all Slurm and Munge processes started
here should be killed.
"""
import os
import pwd
import shutil
import socket
import subprocess
import sys
import time


def write_slurm_conf(fname, hostname, node_config, munge_socket, user, log_dir,
                     spool_dir, slurmctld_pid, slurmd_pid):
    """Write the slurm configuration out to a file."""
    with open(fname, 'w') as fp:

        def output(fmt, *pargs, **kwargs):
            s = fmt.format(*pargs, **kwargs)
            print(s, file=fp)

        # SlurmctldHost=$HOSTNAME
        output("""
ClusterName=bee-dev
MpiDefault=pmix
ProctrackType=proctrack/pgid
ReturnToService=2
SlurmctldPort=7777
SlurmdPort=8989

SwitchType=switch/none

TaskPlugin=task/affinity

InactiveLimit=0
KillWait=30
MinJobAge=300
Waittime=0

SchedulerType=sched/backfill
SelectType=select/cons_tres
SelectTypeParameters=CR_Core

AccountingStorageType=accounting_storage/none
JobCompType=jobcomp/none
JobAcctGatherType=jobacct_gather/none
SlurmdDebug=info
AuthType=auth/munge
""")
        output('SlurmctldHost={}', hostname)
        output('SlurmctldPidFile={}', slurmctld_pid)
        output('SlurmdPidFile={}', slurmd_pid)
        output('StateSaveLocation={}', os.path.join(spool_dir, 'slurmctld'))
        output('SlurmdSpoolDir={}', os.path.join(spool_dir, 'slurmd'))
        output('SlurmctldLogFile={}', os.path.join(log_dir, 'slurmctld.log'))
        output('SlurmdLogFile={}', os.path.join(log_dir, 'slurmd.log'))
        output('SlurmUser={}', user)
        output('SlurmdUser={}', user)
        output('AuthInfo=socket={}', munge_socket)
        output(node_config)
        output('PartitionName=debug Nodes=ALL Default=YES MaxTime=INFINITE State=UP')


SLURM_CONF = '/tmp/slurm.conf'
MUNGE_SOCKET = '/tmp/munge.sock'
MUNGE_LOG = '/tmp/munge.log'
MUNGE_PID = '/tmp/munge.pid'
SLURM_USER = pwd.getpwuid(os.getuid()).pw_name
SLURM_LOG = '/tmp/slurm_log'
SLURM_SPOOL = '/tmp/slurm_spool'
SLURMCTLD_PID = '/tmp/slurmctld.pid'
SLURMD_PID = '/tmp/slurmd.pid'

os.makedirs(SLURM_LOG, exist_ok=True)
os.makedirs(SLURM_SPOOL, exist_ok=True)

if shutil.which('slurmd') is None:
    sys.exit('slurmd is missing; something was configured wrong')
hostname = socket.gethostname()
# get the node configuration
cp = subprocess.run(['slurmd', '-C'], stdout=subprocess.PIPE)
output = cp.stdout.decode()
node_config = output.split('\n')[0]
# write the slurm config
write_slurm_conf(SLURM_CONF, hostname, node_config, MUNGE_SOCKET, SLURM_USER,
                 log_dir=SLURM_LOG, spool_dir=SLURM_SPOOL,
                 slurmctld_pid=SLURMCTLD_PID, slurmd_pid=SLURMD_PID)
# TODO: there should be some more error checks here
# start munge
munge_proc = subprocess.Popen([
    'munged',
    '-f', '-F',
    '-S', MUNGE_SOCKET,
    '--log-file', MUNGE_LOG,
    '--pid-file', MUNGE_PID,
])
time.sleep(1)
# start slurm daemons
env = dict(os.environ)
env['SLURM_CONF'] = SLURM_CONF
slurmctld_proc = subprocess.Popen(['slurmctld', '-D'], env=env)
slurmd_proc = subprocess.Popen(['slurmd', '-D'], env=env)
# final shell for user interaction
subprocess.run(['/bin/bash'], env=env)
print('Killing processes')
slurmd_proc.kill()
slurmctld_proc.kill()
munge_proc.kill()
