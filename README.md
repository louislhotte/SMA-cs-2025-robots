# SMA-cs-2025-robots
A repository to build the self-organization of robots in a hostile environment

# Problem Overview and Constraints

## Problem Overview
The objective is to model and simulate a multi-agent system of robots that collect, transform, and transport hazardous waste in a hostile environment. The environment consists of different radioactive zones, and the robots must work within their capabilities to efficiently manage waste disposal. The mission involves:
- **Collecting** waste from designated areas.
- **Transforming** waste from one type to another.
- **Transporting** transformed waste to a secure disposal area.
- **Navigating** the environment while adhering to movement restrictions imposed by radioactivity levels.

## Environmental Constraints
The environment is divided into three distinct zones, each with increasing levels of radioactivity:
1. **Zone 1 (Low Radioactivity)**: Contains randomly placed green waste.
2. **Zone 2 (Medium Radioactivity)**: Intermediate area for waste transformation.
3. **Zone 3 (High Radioactivity)**: Final destination where transformed red waste must be stored.

Waste types:
- **Green Waste**: Initial waste collected from Zone 1.
- **Yellow Waste**: Transformed from green waste.
- **Red Waste**: Transformed from yellow waste and stored in Zone 3.

## Robot Constraints
Three types of robots operate under specific constraints:
### Green Robot:
- Moves within **Zone 1 only**.
- Collects 2 green wastes → Transforms into 1 yellow waste.
- Transports 1 yellow waste eastward.

### Yellow Robot:
- Moves within **Zones 1 and 2**.
- Collects 2 yellow wastes → Transforms into 1 red waste.
- Transports 1 red waste eastward.

### Red Robot:
- Moves within **Zones 1, 2, and 3**.
- Collects 1 red waste → Transports it to the waste disposal zone in Zone 3.

## Simulation Considerations
- **Agent Behavior**: Robots operate through a cycle of perception, deliberation, and action.
- **Environmental Constraints**: Robots cannot exceed their designated zones.
- **Collaboration Strategies**: Future steps may introduce communication between robots to improve efficiency.
- **Uncertainty Handling**: Further extensions may introduce uncertainties in waste collection and robot actions.

The implementation will involve defining robot agent classes, environmental objects, and a simulation model to observe and optimize robot behavior in waste management.

