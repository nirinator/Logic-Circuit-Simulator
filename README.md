# Logic Circuit Simulator

A visual logic circuit simulator project I built for designing and testing combinational digital logic circuits.

I split the project into two parts:
- A visual front-end written in Python using PyQt5 to place gates, move components, and wire up a schematic.
- A fast evaluation backend in C++ that reads the schematic, builds the circuit graph in memory, and simulates all possible input combinations to generate a full truth table.

---

## 1. HOW IT WORKS (HIGH-LEVEL OVERVIEW)

- **Draw the Circuit:**  
  You place inputs, logic gates (AND, OR, NOT), and an output node on the canvas, then connect them with wires. You can also build sub-circuits and save them as reusable custom components (up to 6 components), which get added to the sidebar with an "✕" button to delete them.

- **Modes (Select vs. Delete):**
Added a mode toggle so you can easily switch between normal selection/wiring mode and a dedicated Delete mode to click and remove wires or gates.

- **Export the Netlist:**  
  When you click "RUN SIMULATION", Python scans all the items:
  
  - Inputs are sorted and named strictly by their creation order (IN1, IN2, IN3...), so moving them on screen doesn't mess up their order in the table.
  
  - If you used any Custom Components, Python flattens them into basic primitive gates (AND, OR, NOT) so the C++ backend doesn't need to know about complex sub-circuits.

  - It writes the clean hardware netlist into circuit.txt.

- **Launch the C++ Backend:**  
  Python runs the compiled executable (`LogicSimulator.exe`) as a subprocess.

- **Build the Graph and Simulate:**  
  The C++ engine reads `circuit.txt`, creates the corresponding gate objects, hooks up their input/output pointers according to the `CONNECT` statements, and evaluates the circuit across all $2^N$ input combinations.

- **Print the Truth Table:**  
  The C++ engine prints the formatted truth table to `stdout`, which Python captures and displays in the console.

---

## 2. COMPONENT OVERVIEW

### A. Graphical Front-End (`main_gui.py`)
- **GateNode:** Movable gate container on the canvas that updates attached wires whenever moved.
- **Pin:** Input/output connection points that validate and manage wire drag-and-drop actions.
- **Wire:** Connects two pins and keeps line coordinates synchronized with gate movement.
- **CircuitSimulator:** Main window that handles UI controls, generates the netlist, and calls the C++ backend.

### B. Netlist Format (`circuit.txt`)
A plain text description that passes the circuit graph to the C++ solver. The possible commands are:
- `INPUT <id>`
- `OUTPUT <id>`
- `<gate_type> <id>` (for example: `AND G1`)
- `CONNECT <src_id> <dst_id> <pin_index>` (for example: `CONNECT A G1 0`, which means connect A to input number 0 for G1)

### C. C++ Engine
The C++ is split into 3 files: 
- `main.cpp`: Contains the main function and the table generation.
- `Gate.h`: Holds all the classes and functions for managing gates.
- `Circuit.h`: Holds all the functions for managing a complete logical circuit.

Key mechanisms:
- **Gate Hierarchy:** Abstract `Gate` base class with derived logic classes (`AndGate`, `OrGate`, `NotGate`, `InputGate`) implementing `evaluate()`.
- **Circuit:** Reads `circuit.txt`, links gates via pointers, and resolves connections.
- **Simulation:** Iterates through all $2^N$ input bit combinations and outputs the full truth table.


