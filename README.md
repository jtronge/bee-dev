## bee-dev development container

This is a simple debian-based development container for running the Build and
Execute (BEE) workflow orchestration tool. This uses Docker for building, since
the Slurm install requires special privileges and then uses Charliecloud for
running the container.

To build the container you can run `./build`, which will require sudo or doas to
run docker. The container can then be started with `./start` at user-level.
Please edit the `CONF` file to your specific system setup.
