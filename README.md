# MHD Aerospike Propulsion System 🚀

A computational aerospace engineering project exploring a hybrid propulsion architecture combining **ground-powered kinetic launch, atmospheric Magnetohydrodynamic (MHD) propulsion, and LH₂/LOX aerospike propulsion**.

<img width="1600" height="915" alt="image" src="https://github.com/user-attachments/assets/2cf59399-fccc-4d1e-8360-5e29123ac7b3" />

## Overview

The proposed architecture uses externally supplied kinetic energy to accelerate the vehicle before atmospheric flight. During high-speed atmospheric flight, incoming air is modeled as an electrically conductive medium and accelerated using electromagnetic forces. As atmospheric density decreases, the system transitions toward onboard LH₂/LOX chemical propulsion using an aerospike configuration.

The MHD propulsion mechanism is based on the Lorentz force:

$$
\mathbf{f} = \mathbf{J} \times \mathbf{B}
$$

where **J** is current density and **B** is magnetic flux density.

<img width="1902" height="1012" alt="image" src="https://github.com/user-attachments/assets/af393303-c92d-4ad9-bc91-2dac0748dd92" />

## What I Built

* Designed the complete hybrid propulsion architecture.
* Created a detailed **3D vehicle and propulsion model in Blender**.
* Developed a **custom physics simulation** to test the proposed architecture.
* Implemented computational models for vehicle dynamics, atmospheric conditions, propulsion stages, and electromagnetic acceleration.
* Built the simulation framework to investigate performance, energy requirements, losses, and system limitations.

## System Architecture

```text
Ground-Based Kinetic Launch
          ↓
   Hypersonic Flight
          ↓
 Atmospheric MHD Propulsion
          ↓
  Transition with Altitude
          ↓
     LH₂/LOX Aerospike
          ↓
      High-Altitude Flight
```

## Research Objective

The goal is to determine whether combining these propulsion regimes can provide a meaningful system-level advantage over simpler architectures.

Rather than assuming the concept works, the project uses computational modeling to identify **performance limits, energy losses, failure conditions, and areas requiring redesign**.

## Development Philosophy

**Concept → Architecture → Code → Simulation → Validation → Redesign**

The current implementation represents an evolving computational model. Results are treated as hypotheses to be tested and refined rather than validated aerospace performance claims.

## Technologies

* Python
* Numerical simulation
* Physics-based modeling
* Blender
* Computational aerospace engineering

## Status

🟡 **Active Development**

The project is progressing from conceptual architecture toward increasingly rigorous mathematical modeling and quantitative validation.
