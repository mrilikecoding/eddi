System Architecture Overview
============================

Eddi's architecture focuses on performer empowerment - enabling direct environmental control through movement and gesture.

High-Level Architecture
-----------------------

.. mermaid::

   graph TD
       A[Input Devices] --> B[Core Engine]
       B --> C[Processing Pipeline]
       C --> D[AI Director]
       D --> E[Sequencer]
       E --> F[Output Devices]
       
       A1[Kinect V2] --> A
       A2[StreamPoseML] --> A
       A3[Custom Cameras] --> A
       
       C1[Gesture Recognition] --> C
       C2[Spatial Processing] --> C
       C3[Pattern Generation] --> C
       
       F1[DMX Lighting] --> F
       F2[OSC Output] --> F
       F3[Sound Systems] --> F
       F4[Web Visualization] --> F
       
       G[Plugin System] --> B
       H[Configuration Manager] --> B
       I[Event System] --> B

Core Components
---------------

Engine
~~~~~~
The central orchestrator that manages the entire system lifecycle, coordinates between components, and maintains real-time performance requirements.

AI Director
~~~~~~~~~~~
Makes smart decisions about environmental responses based on movement input, using psychology research principles to amplify performer intention.

Processing Pipeline
~~~~~~~~~~~~~~~~~~~
Transforms raw movement data into meaningful gesture and spatial information using segmentation techniques developed during thesis research.

Plugin System
~~~~~~~~~~~~~
Enables extensibility for new input devices, processing algorithms, and output modalities without modifying core system code.

Design Principles
-----------------

Performer Empowerment
~~~~~~~~~~~~~~~~~~~~~
Technology extends the performer's body into the environment itself. Movement becomes direct environmental sculpting.

Flattened Hierarchy
~~~~~~~~~~~~~~~~~~~
Dissolves traditional separations between performer and environment, controller and controlled.

Real-time Responsiveness
~~~~~~~~~~~~~~~~~~~~~~~~
Maintains <100ms latency for immediate environmental response to movement.

Modular Extensibility
~~~~~~~~~~~~~~~~~~~~~
Plugin-based architecture allows for new capabilities without system redesign.

Component Interaction
---------------------

.. mermaid::

   sequenceDiagram
       participant Performer
       participant Input as Input Device
       participant Engine as Core Engine
       participant Processor as Processing Pipeline
       participant Director as AI Director
       participant Output as Output Device
       
       Performer->>Input: Physical Movement
       Input->>Engine: PoseData
       Engine->>Processor: Process(PoseData)
       Processor->>Director: GestureData
       Director->>Director: Analyze & Decide
       Director->>Engine: EnvironmentalCommand
       Engine->>Output: Execute(Command)
       Output->>Performer: Environmental Response

Migration Strategy
------------------

The current architecture represents a migration from the original PI3E/Lumi system:

.. mermaid::

   graph LR
       A[Legacy Lumi] --> B[Reference & Analysis]
       B --> C[Eddi Architecture Design]
       C --> D[Component Migration]
       D --> E[Feature Parity Testing]
       E --> F[Legacy Deprecation]
       
       A1[lumi.py] --> C
       A2[director.py] --> C  
       A3[sequencer.py] --> C
       A4[spatial_light_controller.py] --> C
       
       C --> D1[eddi/core/engine.py]
       C --> D2[eddi/core/director.py]
       C --> D3[eddi/core/sequencer.py]
       C --> D4[eddi/processing/spatial.py]