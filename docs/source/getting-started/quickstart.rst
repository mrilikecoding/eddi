Quick Start
===========

This guide will get you up and running with Eddi quickly.

.. note::
   Since Eddi is in early development, this quickstart focuses on the legacy PI3E/Lumi system.
   Modern Eddi architecture documentation will be added as development progresses.

Legacy System Quick Start
--------------------------

1. **Hardware Setup**

   * Connect Kinect V2 sensor
   * Set up lighting equipment with DMX interface
   * Launch QLC+ software

2. **Start the System**

   .. code-block:: bash

      # Terminal 1: Start Kinect processing
      # Open kinect_osc.pde in Processing and run

      # Terminal 2: Start main system  
      python main.py

3. **Test Movement**

   Stand in front of the Kinect and move around. You should see lighting responses to your gestures.

Modern Eddi (In Development)
----------------------------

.. code-block:: bash

   # Check system status
   uv run eddi doctor

   # List available devices
   uv run eddi devices list

   # Run with default configuration (when available)
   uv run eddi run

Next Steps
----------

* :doc:`concepts` - Understand the system philosophy
* :doc:`../architecture/overview` - Learn the system architecture  
* :doc:`../legacy/lumi-setup` - Detailed legacy system setup
* :doc:`../development/contributing` - Join the development effort