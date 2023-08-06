This GitHub repository contains a versatile and extensive set of deep learning models that have been tailored to align and restore 4D-STEM data. These models have been developed by Ivan Lobato (Ivanlh20@gmail.com) and are designed to provide an all-in-one solution for researchers, engineers, and electron microscopy enthusiasts who want to utilize the latest advancements in neural network technology to improve the quality of their CBED patterns.

# Advanced 4D-STEM Ptychography: Neural Networks for Precise CBED Alignment and Restoration
I.Lobato<sup>1</sup>, C. Huang<sup>1</sup>, A.I. Kirkland<sup>1,2,3</sup>

<sup>1</sup>The Rosalind Franklin Institute, Harwell Science and Innovation Campus, Didcot, OX11 0FA, UK

<sup>2</sup>Department of Materials, University of Oxford, Parks Road, Oxford OX1 3PH, UK

<sup>3</sup>Electron Physical Sciences Imaging Centre, Diamond Light Source Ltd., Harwell Science and Innovation Campus, Didcot, OX11 0DE, UK

Paper: http://arxiv.org

## Overview
Scanning transmission electron microscopy (STEM) is a powerful technique for materials analysis, offering imaging, diffraction and spectroscopic capabilities. With the development of high-speed pixelated electron detectors, 4D-STEM experiments that enable the acquisition of the complete electron distribution for each STEM probe position in diffraction or real space are now possible. Electron ptychography, a particular 4D-STEM acquisition geometry, reconstructs the specimen transmission function from a set of redundant convergent-beam electron diffraction (CBED) patterns. Achieving high signal-to-noise ratio (SNR) and precise alignment of CBED patterns is crucial for high-quality reconstructions. In this study, we describe three innovative neural networks to address these challenges and enhance 4D-STEM performance.

Each network was trained on 3.0 million simulated data points; 1.0 million were generated using the multislice algorithm with various microscope parameters and a diverse set of crystalline samples. In addition, low-resolution projected potentials were obtained by restoring experimental low-resolution images and used as input for the classical multislice simulations. To diversify the potentials and improve generalisation, we employed the stable diffusion network, which allows for the generation of a variety of input images.

The first neural network, c_cbed, accurately identifies the centres of CBED patterns, a critical step for optimal alignment. This network employs model-based deep learning methods that integrate partial domain knowledge through mathematical structures tailored for specific problems and data-driven learning. The second neural network improves the SNR of CBED patterns through restoration, essential for high-quality reconstructions. The third network, rc_cbed, combines the functionalities of the first two networks, allowing for simultaneous re-centring and restoration/in-painting of CBED patterns. Our restoration architecture is based on Attention Squeeze U-Net and ResUnet.

These state-of-the-art neural networks have the potential to significantly advance the study of beam-sensitive specimens, paving the way for more accurate and efficient investigations in materials science and biology. The source code and trained models for our approach are made available in the accompanying repository.

# Installation via Pip
## Quick install
Below are the quick versions of the installation commands. For detailed instructions, please refer to the section below.

### Linux

- **GPU support**

	```bash
	conda install -c conda-forge cudatoolkit=11.8.0
	pip install nvidia-cudnn-cu11==8.6.0.163
	mkdir -p $CONDA_PREFIX/etc/conda/activate.d
	echo 'CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
	echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
	source $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
	python -m pip install tensorflow==2.12.* tk_cbed
	```

- **CPU-only support**
	```bash
	python -m pip install tensorflow-cpu==2.12.* tk_cbed
	```

### Windows
- **GPU support**
	```bash
	conda install -c conda-forge cudatoolkit=11.2.* cudnn=8.1.*
	mkdir -p $CONDA_PREFIX/etc/conda/activate.d
	echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
	python -m pip install tensorflow==2.10.* tk_cbed
	```
- **CPU-only support**
	```bash
	python -m pip install tensorflow-cpu==2.10.* tk_cbed
	```

## Step-by-Step Install
Below are the step-by-step instructions for installing the package with and without GPU support.

To utilize **tk_cbed**, you'll need to install TensorFlow. If you plan to use GPU acceleration, the installation of CUDA libraries is also necessary. The required version of TensorFlow for **tk_cbed** varies depending on your operating system. We recommend installing TensorFlow within a virtual environment to prevent conflicts with other packages.

## 1. Install Miniconda and create an environment
[miniconda](https://docs.conda.io/en/latest/miniconda.html) is the recommended approach for installing TensorFlow with GPU support. It creates a separate environment to avoid changing any installed software in your system. This is also the easiest way to install the required software especially for the GPU setup.

Let us start by creating a new conda environment and activate it with the following command:
```bash
conda create -n py310_gpu python=3.10.*
conda activate py310_gpu
```

## 2. Setting up GPU (optional)
If you plan to run TensorFlow on a GPU, you'll need to install the NVIDIA GPU driver and then install CUDA and cuDNN using Conda. You can use the following command to install them:

### **Linux**
On Linux, you can install and use the latest TensorFlow version that is linked to a specific CUDA version using the following command:
```bash
conda install -c conda-forge cudatoolkit=11.8.0
pip install nvidia-cudnn-cu11==8.6.0.163
```

The first command installs the CUDA toolkit, which is a set of software tools used to accelerate applications on NVIDIA GPUs. The second command installs the cuDNN library, which is an optimized deep neural network library for NVIDIA GPUs.

To ensure that the system paths recognize CUDA when your environment is activated, you can run the following commands ([Tensorflow step by step](https://www.tensorflow.org/install/pip#linux_1)):

```bash
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
echo 'CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
```

These commands create a shell script in the activate.d directory, which sets the `LD_LIBRARY_PATH` environment variable when your environment is activated. This allows TensorFlow to locate the CUDA libraries that it needs to run on the GPU.

### Ubuntu 22.04
In Ubuntu 22.04, you may encounter the following error:
```bash
Can't find libdevice directory ${CUDA_DIR}/nvvm/libdevice.
...
Couldn't invoke ptxas --version
...
InternalError: libdevice not found at ./libdevice.10.bc [Op:__some_op]
```

To fix this error, you will need to run the following commands. 
```bash
# Install NVCC
conda install -c nvidia cuda-nvcc=11.3.58
# Configure the XLA cuda directory
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
printf 'export XLA_FLAGS=--xla_gpu_cuda_data_dir=$CONDA_PREFIX/lib/\n' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
source $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
# Copy libdevice file to the required path
mkdir -p $CONDA_PREFIX/lib/nvvm/libdevice
cp $CONDA_PREFIX/lib/libdevice.10.bc $CONDA_PREFIX/lib/nvvm/libdevice/
```

### **Windows**
For TensorFlow version 2.10.* on Windows, which was the last TensorFlow release to support GPU on native Windows, you can install the NVIDIA GPU driver and then install the following specific version of CUDA and cuDNN using Conda:

```bash
conda install -c conda-forge cudatoolkit=11.2.* cudnn=8.1.*
```

To ensure that the system paths recognize CUDA when your environment is activated, you can run the following commands:

```bash
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
```
These commands create a shell script in the activate.d directory, which sets the LD_LIBRARY_PATH environment variable when your environment is activated. This allows TensorFlow to locate the CUDA libraries that it needs to run on the GPU.

## 3. Install Tensorflow
After installing the CUDA libraries, you can install TensorFlow. The required version of TensorFlow varies depending on your operating system.

### **Linux**
On Linux, install TensorFlow version 2.12.* using pip:

- **GPU support**
	```bash
	pip install tensorflow==2.12.*
	```

- **CPU-only support**
	```bash
	pip install tensorflow-cpu==2.12.*
	```

Note that running on CPU may be slower than running on a GPU, but it should still be functional.

### **Windows**
On Windows, the last version of TensorFlow that supported GPU on native Windows was 2.10.*. Starting with TensorFlow 2.11, you'll need to install TensorFlow in WSL2 or install tensorflow-cpu instead.

- **GPU support**
	```bash
	pip install tensorflow==2.10.*
	```

- **CPU-only support**
	```bash
	pip install tensorflow-cpu==2.10.*
	```

With these installations, you should now have TensorFlow set up with GPU support (if applicable).

## 4. Install tk_cbed

### Option 1: Install from PIP
After installing TensorFlow, you can install **tk_cbed** using pip:
```bash
pip install tk_cbed
```

This command will install the latest version of **tk_cbed** and its required dependencies.

## Option 2: Install from Git-Clone
This option is ideal if you want to edit the code. Clone the repository:
```bash
$ git clone https://github.com/Ivanlh20/tk_cbed.git
```

Then, change into its directory and install it using pip:
```bash
pip install -e .
```

You are now ready to run **tk_cbed**.

## 5. Python example
You can now use tk_cbed in your Python code. The code example includes three pre-trained networks, `c_cbed`, `r_cbed`, and `rc_cbed`. The `c_cbed` network detects the center of the CBED patterns, while the `r_cbed` network improves the signal-to-noise ratio (SNR) of CBED patterns through restoration, essential for high-quality reconstructions. The `rc_cbed` network combines the functionalities of the first two networks, allowing for simultaneous re-centring and restoration/in-painting of CBED patterns.

```python
import os
import numpy as np
import matplotlib

# Check if running on remote SSH and use appropriate backend for matplotlib
remote_ssh = "SSH_CONNECTION" in os.environ
matplotlib.use('Agg' if remote_ssh else 'TkAgg')
import matplotlib.pyplot as plt

def fcn_set_gpu_id(gpu_visible_devices: str = "0") -> None:
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ['CUDA_VISIBLE_DEVICES'] = gpu_visible_devices

# Set the GPU ID to be used
fcn_set_gpu_id("0")

from tk_cbed import load_network, load_sim_test_data

# Plot the simulation results for the given data and network.
def plot_sim_results(x, y, y_p, net_name):
    n_data = x.shape[0]
    
    if net_name == 'c_cbed':
        fig, axs = plt.subplots(1, n_data, figsize=(48, 6))

        p_c = np.array(x.shape[1:3], np.float32)/2
        
        for ik in range(n_data):
            x_ik = x[ik, :, :, 0].squeeze()
            y_p_ik = p_c + y_p[ik, ...].squeeze()
            y_ik = p_c + y[ik, ...].squeeze()

            axs[ik].imshow(x_ik, cmap='gray')
            axs[ik].set_xticks([])
            axs[ik].set_yticks([])
            axs[ik].grid(False)
            axs[ik].plot(y_ik[0], y_ik[1], '+r', markersize=10, markeredgewidth=3, label='Ground Truth')
            axs[ik].plot(y_p_ik[0], y_p_ik[1], '+b', markersize=10, markeredgewidth=3, label='c_cbed prediction')
            axs[ik].set_title(f"Error: {np.linalg.norm(y_ik-y_p_ik):.2f} px", fontsize=14)
            axs[ik].legend()
    else:
        fig, axs = plt.subplots(3, n_data, figsize=(48, 6))

        for ik in range(n_data):
            x_ik = x[ik, :, :, 0].squeeze()
            y_p_ik = y_p[ik, :, :, 0].squeeze()
            y_ik = y[ik, :, :, 0].squeeze()

            ir = 0
            axs[ir][ik].imshow(x_ik, cmap='viridis')
            axs[ir][ik].set_xticks([])
            axs[ir][ik].set_yticks([])
            axs[ir][ik].grid(False)
            
            if ik == 0:
                axs[ir][ik].set_ylabel(f"Detected CBED", fontsize=14, )

            ir = 1
            axs[ir][ik].imshow(y_p_ik, cmap='viridis')
            axs[ir][ik].set_xticks([])
            axs[ir][ik].set_yticks([])
            axs[ir][ik].grid(False)

            if ik == 0:
                axs[ir][ik].set_ylabel(f"Restored CBED", fontsize=14)
            
            ir = 2
            axs[ir][ik].imshow(y_ik, cmap='viridis')
            axs[ir][ik].set_xticks([])
            axs[ir][ik].set_yticks([])
            axs[ir][ik].grid(False)

            if ik == 0:
                axs[ir][ik].set_ylabel(f"Ground truth CBED", fontsize=14)

    if remote_ssh:
        plt.savefig(f"net_name.png", format='png')
    else:
        fig.show()
   
def fcn_inference():
    """
    Perform inference on test data using a pre-trained model and visualize the results.
    """
    # Select one of the available networks from [c_cbed, r_cbed, rc_cbed]
    net_name = 'r_cbed'

    # Load its corresponding data
    x, y = load_sim_test_data(net_name)
    
    # Load its corresponding model
    tk_cbed_nn = load_network(net_name)
    tk_cbed_nn.summary()

    batch_size = 8

    # Perform predictions on test data
    y_p = tk_cbed_nn.predict(x, batch_size)

    # Plot the results
    plot_sim_results(x, y, y_p, net_name)
            
    print('Done')

if __name__ == '__main__':
    fcn_inference()
```

Figures 1, 2, and 3 display the output images produced by the code using the pre-trained networks for `c_cbed`, `r_cbed`, and `rc_cbed`, respectively.

![](images/c_cbed.png)

Figure 1 displays random simulated CBED patterns that include the most relevant sources of noise during the detection process. This network employs model-based deep learning methods that integrate partial domain knowledge through mathematical structures tailored for specific problems and data-driven learning. The red dots represent the ground truth positions of the CBED pcenter, and the blue dots represent the predicted positions of the CBED center.

![](images/r_cbed.png)

Figure 2 illustrates simulated CBED patterns that include the most relevant sources of noise during the detection process. The `r_cbed` network improves the SNR of CBED patterns through restoration, essential for high-quality reconstructions. The first row depicts the input CBED patterns, the second row exhibits the restored CBED patterns, and the third row displays the ground truth CBED patterns.

![](images/rc_cbed.png)

Figure 3 illustrates simulated CBED patterns that include the most relevant sources of noise during the detection process. The `rc_cbed` network combines the functionalities of the first two networks, allowing for simultaneous re-centring and restoration/in-painting of CBED patterns. The first row depicts the input CBED patterns, the second row exhibits the restored CBED patterns, and the third row displays the ground truth CBED patterns.

## 5. Performance
The architecture of **tk_cbed** has been optimized to run on a standard desktop computer, and its performance can be significantly improved by utilizing GPU acceleration.

## 6. How to cite:
**Please cite tk_cbed in your publications if it helps your research:**

```bibtex
    @article{LCK_2023,
      Author = {I.Lobato and C. Huang and A.I. Kirkland},
      Journal = {Ultramicroscopy},
      Title = {Advanced 4D-STEM Ptychography: Neural Networks for Precise CBED Alignment and Restoration},
      Year = {2023},
      volume  = {xxx},
      pages   = {xxx-xxx}
    }