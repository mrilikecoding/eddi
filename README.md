# Eddi: Emergent Dynamic Design Interface

**An early-stage exploration of movement-responsive environments**

> *"What if performers could directly shape their environment through movement, flattening the hierarchy between body and space?"*

Eddi is an experimental platform for creating interactive environmental systems that respond to human movement and gesture. While originally scoped around lighting design, the system could be extended to sound and other environmental modalities. This repository represents ongoing research and development work exploring the intersection of physical theater, computer vision, and environmental design.

📖 **[Full Documentation at eddi.readthedocs.io](https://eddi.readthedocs.io/)**

## Background & Inspiration

This project emerged from my Masters Thesis work at Georgia Tech on PI3E (Platform for Intelligent, Immersive, Interactive Environments), combining my background as a physical theater artist, musician, and computer scientist. The ideas here have been developed over years of teaching physical theater, training with physical theater companies, and directing shows where I've used these techniques to help ensembles work together. The work is deeply informed by training in various somatic and movement-based practices.

**Project Evolution**: PI3E/Lumi (thesis and prototype) → Eddi (modern architecture)

### Artistic Foundation
As a physical theater teaching artist, I've witnessed the transformative power of giving performers direct agency over their environment. In physical theater, the most compelling work emerges when performers can shape space through embodied expression - when the hierarchy between body and environment dissolves into collaborative creation.

Traditional theatrical hierarchies often separate designers and performers, leading to disjointed collaborations where lighting design happens independently of embodied exploration. This system doesn't aim to replace designers, but rather to provide tools that enable performer-driven design collaborations much earlier in the creative process. Performers can explore spatial and environmental possibilities alongside movement development, while designers can work with lived, embodied data rather than theoretical blocking.

Beyond collaborative benefits, the system opens new expressive possibilities: the power of improvising with an intelligent spatial agent that responds to and amplifies performer intention in real-time.

### Technical Inspiration  
The challenge: How do we create technological systems that empower performers to directly sculpt their environment through movement? How do we flatten the hierarchy between human expression and environmental response? This work represents an ongoing investigation into performer-controlled, responsive environments.

## Project Status: Early Development

🚧 **This is a work-in-progress research project** 🚧

Currently migrating from the original PI3E/Lumi implementation to a modern, extensible architecture. The implementation is in early stages.

### What's Working
- ✅ Legacy Kinect-based lighting control system
- ✅ Basic gesture recognition pipeline
- ✅ OSC/DMX communication for lighting control
- ✅ Modern Python project structure and CI/CD

### What's In Development  
- 🔄 Migrating core functionality to modern architecture
- 🔄 StreamPoseML integration for camera-based pose estimation
- 🔄 Plugin system for extensibility
- 🔄 Web-based configuration interfaces

### Future Vision
- ⏳ AI-powered movement analysis and response
- ⏳ Multi-user tracking and spatial awareness
- ⏳ Real-time performance tools for live theater
- ⏳ Educational interfaces for movement pedagogy
- ⏳ StreamPoseML integration enabling custom movement-based classification models
- ⏳ Sound design and multi-modal environmental control

## Core Concepts

### Performer Empowerment
Rather than external control systems, Eddi aims to extend the performer's body into the environment itself. Movement becomes a direct means of environmental sculpting - immediate, intuitive, and expressive.

### Embodied Agency
Drawing from somatic practices and physical theater training, the system is designed to respond to embodied intention and presence. Performers shape space through the quality of their inhabitation, not just their location within it.

### Flattened Hierarchy
The goal is to dissolve traditional separations between performer and environment, between "controller" and "controlled." Technology becomes an extension of expressive capacity rather than an external system to navigate.

## Technical Approach

### Movement Analysis
- **Novel Gesture Segmentation**: Techniques developed during Masters thesis research
- **MEI/MHI Processing**: Motion Energy/History Imaging for gesture recognition
- **Pose Estimation**: Integration with StreamPoseML for modern computer vision
- **Spatial Mapping**: Multi-zone environmental awareness
- **Quality Detection**: Exploring Laban Movement Analysis principles

### Response Generation
- **AI Director**: Decision-making system inspired by psychological arousal research
- **Pattern Sequencing**: Temporal coordination of environmental responses (lighting, sound, etc.)
- **Adaptive Learning**: Systems that evolve with repeated interaction

### Platform Design
- **Modular Architecture**: Plugin-based system for different input/output modalities
- **Multi-Modal Output**: Originally lighting-focused, extensible to sound and other environmental controls
- **Real-time Processing**: Low-latency response for live performance
- **Cross-Platform**: Designed to run on various hardware configurations

## Repository Structure

This repository contains both legacy code (original Lumi system) and new development (Eddi architecture):

```
├── src/
│   ├── eddi/           # New modular architecture (in development)
│   └── [legacy files]  # Original Lumi implementation (reference)
├── tests/              # Comprehensive test suite
└── docs/               # Documentation and development guidelines
```

## Getting Started

### Prerequisites
- Python 3.11+
- UV package manager
- For legacy system: Kinect sensor, QLC+ software

### Installation
```bash
git clone https://github.com/mrilikecoding/eddi.git
cd eddi
uv sync --dev
```

### Running the Legacy System
1. Set up QLC+ with DMX interface
2. Configure OSC input on 127.0.0.1:7700  
3. Start Kinect processing: `kinect_osc.pde` in Processing
4. Run: `python main.py`

### Development Commands
```bash
uv run eddi --help      # CLI interface (in development)
uv run pytest          # Run tests
uv run ruff check .     # Code quality checks
```

## Use Cases Under Exploration

### Performance Applications
- **Physical Theater**: Environments that extend performers' expressive range and spatial agency
- **Dance**: Spaces where choreography directly sculpts light, sound, and atmosphere
- **Music**: Audio-visual environments that performers can shape through gesture and movement quality
- **Sound Design**: Real-time sound generation and manipulation through embodied performance

### Educational Applications  
- **Movement Pedagogy**: Tools that help students experience their own spatial agency and expressive power
- **Empowerment Training**: Environments that make visible the impact of embodied presence and intention
- **Research**: Platforms for studying performer-environment collaboration and embodied agency

### Installation Art
- **Responsive Environments**: Spaces that adapt to and remember visitor presence
- **Community Interaction**: Public installations that respond to collective movement
- **Meditative Spaces**: Environments that support contemplative practice

## Research Interests

This project touches on several areas of ongoing investigation:

- **Embodied Cognition**: How environmental responsiveness affects human behavior and awareness
- **Human-Computer Interaction**: Designing interfaces that feel collaborative rather than controlling  
- **Performance Studies**: Technology's role in live, ephemeral artistic practice
- **Machine Learning**: Training systems to recognize qualitative aspects of movement
- **Environmental Psychology**: How responsive spaces affect wellbeing and creativity

## Contributing

This is an open research project. Contributions, ideas, and collaborations are welcome, especially from:

- Movement practitioners and somatic educators
- Lighting designers and environmental artists  
- Computer vision and ML researchers
- Performance technologists
- Anyone interested in responsive environments

Technical development guidelines are available in the repository documentation.

## Academic Context

This work builds on:
- **Masters Thesis Research** at Georgia Tech in computer science
- **Years of physical theater teaching** and movement practice
- **Interdisciplinary training** in performance, technology, and pedagogy
- **Collaboration** with artists, technologists, and researchers

## Philosophy

> *"The most profound technologies are those that disappear, leaving only enhanced human agency and expressive power."*

This project aims to create technology that extends rather than controls human expression - tools that flatten hierarchies and amplify our capacity to directly shape the world around us through embodied presence.

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Eddi is an experiment in making spaces more alive, more responsive, more collaborative.*