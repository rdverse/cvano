#FROM pytorch/pytorch:latest
FROM pytorch/pytorch:2.1.2-cuda11.8-cudnn8-devel

# for cpu only setup on vm or desktop
#FROM intel/intel-optimized-pytorch
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update

#COPY XAI_VISION /app/XAI_VISION/

# change directory 
#WORKDIR /app/XAI_VISION/depthmodels

# Run commands to set up the environment (assuming you have a conda environment.yml file)
# If not, you can create your Conda environment manually
#RUN conda env create --name torchNewPy

#RUN apt-get update && apt-get install -y libgl1-mesa-glx && apt-get install -y libglib2.0-0 # sel2 sel37
#COPY XAI_VISION/depthmodels/environment.yml /app/
#RUN conda env create -f environment.yml

# RUN conda init bash

#RUN conda activate torchNewPy

# Activate the Conda environment
#SHELL ["conda", "run", "-n", "torchNewPy", "/bin/bash", "-c"]
# RUN apt-get install vim -y
# RUN apt-get install tmux -y 
#RUN cd /app/XAI_VISION/depthmodels
#RUN bash dir_setup.sh
