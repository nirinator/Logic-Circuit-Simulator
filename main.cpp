#include <iostream>
#include <cmath>
#include "Gate.h" 
#include "Circuit.h"


//this function receives a pointer to the circuit and the number of inputs. it iterates on all the possible inputs given the number of input pins
//using setInputs it sets the values of the input pins, and using evaluate it calculates the output of these given pins.
//
void printTruthTable(Circuit& circuit, int numInputs) {
    int numCombinations = 1 << numInputs;

    std::cout << "\n--- Truth Table ---" << std::endl;

    // 1. הדפסת שמות הפינים לפי הסדר (IN1, IN2, ...)
    for (int j = 1; j <= numInputs; j++) {
        std::cout << "IN" << j << " ";
    }
    std::cout << "| OUT" << std::endl;

    // 2. קו מפריד ויזואלי
    std::string separator(numInputs * 4 + 6, '-');
    std::cout << separator << std::endl;

    // 3. הדפסת ערכי הטבלה
    for (int i = 0; i < numCombinations; i++) {
        std::vector<bool> currentInputs(numInputs);

        for (int j = 0; j < numInputs; j++) {
            // IN1 הוא הביט המשמעותי (MSB)
            currentInputs[numInputs - 1 - j] = (i >> j) & 1;
        }

        circuit.setInputs(currentInputs);

        // הדפסת ערך כל כניסה מתחת לכותרת שלה
        for (int j = 0; j < numInputs; j++) {
            std::cout << " " << currentInputs[j] << "  ";
        }
        std::cout << "|  " << circuit.evaluate() << std::endl;
    }
    std::cout << std::endl;
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