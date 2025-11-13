🚦 Traffic Light Optimization Using Image Processing and Fuzzy Logic

This project presents a dynamic traffic light control system that uses real-time image processing and fuzzy logic to optimize green light durations at intersections.
It aims to reduce average vehicle waiting times, improve traffic flow efficiency, and minimize fuel consumption by adapting to current traffic conditions.


📖 Overview

Traditional fixed-time traffic lights often fail to adapt to sudden traffic changes, leading to unnecessary waiting and congestion.
This project proposes a fuzzy logic-based dynamic control method that calculates the optimal green light duration for each signal phase based on the number of stopped and passing vehicles detected in real time.

System Highlights

🚗 Vehicle detection using YOLOv8 deep learning model.
🤖 Fuzzy logic controller for calculating adaptive green light durations.
🧠 Dynamic decision-making based on current traffic flow data.
🧩 Simulation with SUMO (Simulation of Urban Mobility) to evaluate performance.


🏗️ System Architecture

The system consists of four main components:
Image Processing Module (YOLOv8)
Detects vehicles in each direction from camera/video feeds.
Classifies objects by type and direction using polygonal region mapping.
Counts vehicles as stopped or passed based on movement across frames.

Fuzzy Logic Controller
Inputs: number of stopped and passing vehicles.
Output: optimal green light duration (10–70 seconds).
Uses 7-level membership functions (Very Low → Very High) and 25 fuzzy rules.

Traffic Simulation (SUMO)

Models a four-arm intersection.
Simulates different VPH (Vehicles Per Hour) rates per direction (e.g., East: 600, South: 1000, West: 800, North: 1200).
Compares dynamic fuzzy system with fixed-time systems (15s, 30s, 45s).
