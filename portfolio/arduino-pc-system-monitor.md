# Arduino PC System Monitor with TinyML

This project is a hardware-based system monitor that tracks PC resources (CPU, RAM, GPU, VRAM) and automatically adjusts the PC's power mode. It uses a TinyML (Support Vector Machine) classification model running on an Arduino Leonardo to predict the current workload and switch power profiles accordingly.

## Key Features

* **Real-time Hardware Monitoring:** Collects and processes CPU, RAM, GPU, and VRAM utilization metrics.
* **TinyML Classification:** Utilizes a lightweight SVM model trained with scikit-learn and exported via `micromlgen` to run entirely on the Arduino microcontroller.
* **Dynamic Power Management:** Interfaces with Linux's `powerprofilesctl` to automatically switch between `power-saver`, `balanced`, and `performance` modes based on the predicted system load.
* **Serial Communication:** Reliable two-way communication between the Python host script and the Arduino Leonardo.
* **Custom Dataset Collection:** Includes a built-in logger to manually tag data (Idle, Daily Use, Heavy Load) and build a customized training dataset.

## Technologies Used

* **Hardware:** Arduino Leonardo
* **Languages:** Python, C++
* **Machine Learning:** scikit-learn, SVM, TinyML
* **Tools & Libraries:** PlatformIO, `micromlgen`, `psutil`, `pyserial`, `nvidia-ml-py`
