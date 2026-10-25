#Logic Circuit Simulator 


A visual logic circuit simulator project I built for designing and testing combinational digital logic circuits.

I split the project into two parts:

A visual front-end written in Python using PyQt5 to place gates, move components, and wire up a schematic.

A fast evaluation backend in C++ that reads the schematic, builds the circuit graph in memory, and simulates all possible input combinations to generate a full truth table.

=============================================================

HOW IT WORKS (HIGH-LEVEL OVERVIEW)
=============================================================

Draw the Circuit:
You place inputs, logic gates (AND, OR, NOT), and an output node on the canvas, then connect them with wires.

Export the Netlist:
When you click "RUN SIMULATION", Python scans all the items in the scene, assigns unique IDs to each component, and writes a simple hardware netlist into "circuit.txt".

Launch the C++ Backend:
Python runs the compiled executable ("LogicSimulator.exe") as a subprocess.

Build the Graph and Simulate:
The C++ engine reads "circuit.txt", creates the corresponding gate objects, hooks up their input/output pointers according to the CONNECT statements, and evaluates the circuit across all 2^N input combinations.

Print the Truth Table:
The C++ engine prints the formatted truth table to stdout, which Python captures and displays in the console.


================================================================================
2. COMPONENT OVERVIEW

A. Graphical Front-End (main_gui.py)

GateNode: Movable gate container on the canvas that updates attached wires whenever moved.

Pin: Input/output connection points that validate and manage wire drag-and-drop actions.

Wire: Connects two pins and keeps line coordinates synchronized with gate movement.

CircuitSimulator: Main window that handles UI controls, generates the netlist, and calls the C++ backend.

B. Netlist Format (circuit.txt)
A plain text description that passes the circuit graph to the C++ solver, the possible commands are:

INPUT <name>
    
OUTPUT <name>

<gate type (and/or/not>  <name> (for example: AND G1)

CONNECT <source component> <target component> <index in target gate for source to be connected>
    (for example: CONNECT A G1 0, which means connect A to input number 0 for G1)

C. C++ Engine 

  The C++ is split into 3 files: main.cpp containts the main function and the table generation, Gate.h hold all the functions for managing a single gate, and Circuit.h holds all the functions for menaging a complete logical circuit

Gate Hierarchy: Abstract Gate base class with derived logic classes (AndGate, OrGate, NotGate, InputGate) implementing evaluate().

Circuit: reads circuit.txt, links gates via pointers, and resolves connections.

Simulation: Iterates through all 2^N input bit combinations and outputs the full truth table.

================================================================================
3. BUILD AND RUN INSTRUCTIONS
Prerequisites:

    Python 3.8+ with PyQt5:
    pip install PyQt5
    C++17 compatible compiler .



Building the C++ Engine:

Using Visual Studio:

    Open the project folder in Visual Studio (File -> Open -> Folder...).

    Let Visual Studio configure the CMake cache.

    Build the project using Ctrl+Shift+B (or Build -> Build All).

    Make sure the output path inside main_gui.py points to where the binary was generated (default is "out/build/x64-Debug/LogicSimulator.exe").

Using CMake CLI:
cmake -B out/build -S .
cmake --build out/build
Running the Project:

    Start the visual editor:
    python main_gui.py

    Add gates using the buttons on the left panel (INPUT, AND, OR, NOT, OUTPUT).

    Connect components by dragging wires between output pins and input pins.

    Click "RUN SIMULATION". The C++ backend will execute and display the truth table in your terminal.
