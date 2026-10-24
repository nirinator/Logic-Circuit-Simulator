#include <iostream>
#include <cmath>
#include "Gate.h" 
#include "Circuit.h"

void printTruthTable(Circuit& circuit, int numInputs) {
    int numCombinations = 1 << numInputs;

    std::cout << "--- Truth Table ---" << std::endl;

    for (int i = 0; i < numCombinations; i++) {
        std::vector<bool> currentInputs(numInputs);

        for (int j = 0; j < numInputs; j++) {
            currentInputs[numInputs - 1 - j] = (i >> j) & 1;
        }

        circuit.setInputs(currentInputs);

        for (bool val : currentInputs) std::cout << val << " ";
        std::cout << " | " << circuit.evaluate() << std::endl;
    }
}

int main() {
    Circuit myCircuit;

    std::cout << "Loading circuit from file..." << std::endl;

    myCircuit.loadFromFile("C:/Users/nirin/Logic-Circuit-Simulator/test1.txt");

    int inputsCount = myCircuit.getNumInputs();

    if (inputsCount > 0) {
        printTruthTable(myCircuit, inputsCount);
    }
    else {
        std::cout << "No inputs found in the circuit file." << std::endl;
    }

    return 0;
}