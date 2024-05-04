# Use CUDA 12.3.2 base image with Ubuntu 22.04
FROM nvidia/cuda:12.3.2-base-ubuntu22.04

# Update package information and install dependencies
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -yq \
    git \
    bzip2 \
    wget \
    unzip \
    python3-pip \
    python3.10-dev \
    cmake \
    libgl1-mesa-dev \
    python-is-python3 \
    libgtk2.0-dev

# Clone repositories and set up necessary files
ADD . /app
WORKDIR /app

# Install required Python packages
RUN pip install numpy \
    dlib \
    -r requirements.txt

# Install Real-ESRGAN dependencies
RUN pip install basicsr facexlib gfpgan

# Use sed to modify the degradations.py file
RUN sed -i 's/from torchvision.transforms.functional_tensor import rgb_to_grayscale/from torchvision.transforms.functional import rgb_to_grayscale/' /usr/local/lib/python3.10/dist-packages/basicsr/data/degradations.py

# Setup Real-ESRGAN
RUN cd Real-ESRGAN && \
    pip install -r requirements.txt && \
    python setup.py develop && \
    cd ../



# Determine the location of the basicsr package directory
#RUN python3 -c "import basicsr; import os; print(os.path.dirname(basicsr.__file__))"

# Copy the modified basicsr files
#COPY patches /usr/local/lib/python3.10/site-packages/basicsr/data/degradations.py


# RUN cd Real-ESRGAN && \
#     python inference_realesrgan.py -n RealESRGAN_x4plus -i inputs --outscale 3.5 --face_enhance -g 0 && \
#     cd ..

# Set working directory
WORKDIR /app

# Default command to run
CMD ["python3", "run.py"]
