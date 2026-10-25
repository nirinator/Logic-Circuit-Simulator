#include <iostream>
#include <cmath>
#include "Gate.h" 
#include "Circuit.h"


//this function receives a pointer to the circuit and the number of inputs. it iterates on all the possible inputs given the number of input pins
//using setInputs it sets the values of the input pins, and using evaluate it calculates the output of these given pins.
//
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

//this is the main function, it receives a text file from the python code that contains the commands that describe the logical gate tree
//it checks whether there is more that 0 input pins, and if so it calculates the logical table.
int main() {
    Circuit myCircuit;

    std::cout << "Loading circuit from file..." << std::endl;

    myCircuit.loadFromFile("circuit.txt");

    int inputsCount = myCircuit.getNumInputs();

    if (inputsCount > 0) {
        printTruthTable(myCircuit, inputsCount);
    }
    else {
        std::cout << "No inputs found in the circuit file." << std::endl;
    }

    return 0;
}