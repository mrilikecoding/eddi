Installation
============

System Requirements
-------------------

* Python 3.11+
* UV package manager (recommended) or pip
* Git

For legacy Kinect system:
* Kinect V2 sensor
* QLC+ software
* Processing IDE with P5OSC and SimpleOpenNI libraries

Development Installation
------------------------

1. **Clone the repository**

   .. code-block:: bash

      git clone https://github.com/mrilikecoding/eddi.git
      cd eddi

2. **Install dependencies with UV** (recommended)

   .. code-block:: bash

      uv sync --dev

3. **Alternative: Install with pip**

   .. code-block:: bash

      pip install -e ".[dev]"

4. **Install pre-commit hooks** (for contributors)

   .. code-block:: bash

      pre-commit install

Verify Installation
-------------------

Run the basic system check:

.. code-block:: bash

   uv run eddi doctor

This will verify your installation and check for available input/output devices.

Legacy System Setup
-------------------

For the original PI3E/Lumi system:

1. **Install QLC+**
   
   Download and install `QLC+ <https://www.qlcplus.org/>`_

2. **Configure DMX Interface**
   
   * Set USB DMX interface as output device
   * Configure OSC input on 127.0.0.1:7700 for universe 0

3. **Install Processing Libraries**
   
   In Processing IDE, install:
   * P5OSC
   * SimpleOpenNI

4. **Run Legacy System**

   .. code-block:: bash

      # Start Kinect processing
      # Open kinect_osc.pde in Processing and run
      
      # Run main system
      python main.py

Documentation Dependencies
--------------------------

To build documentation locally:

.. code-block:: bash

   pip install -r docs/requirements.txt
   cd docs
   make html

The built documentation will be in ``docs/build/html/``.

Troubleshooting
---------------

**UV not found**
   Install UV following instructions at `astral.sh/uv <https://astral.sh/uv/>`_

**Kinect not detected**
   Ensure Kinect drivers are properly installed and the sensor is connected

**QLC+ connection issues**
   Verify OSC input configuration and firewall settings

**Permission errors**
   On macOS/Linux, you may need to run with appropriate permissions for hardware access