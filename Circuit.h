#include <vector>
#include "Gate.h"
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <string>

class Circuit {
private:
    std::vector<LogicGate*> allGates;

    std::vector<InputPin*> inputPins;

    LogicGate* outputGate = nullptr;

public:
    ~Circuit() {
        for (int i = 0; i < allGates.size(); i++) {
            delete allGates[i]; 
        }
    }


    InputPin* createInputPin() {
        InputPin* pin = new InputPin();
        allGates.push_back(pin);
        inputPins.push_back(pin);
        return pin;
    }

    AndGate* createAndGate() {
        AndGate* gate = new AndGate();
        allGates.push_back(gate);
        return gate;
    }

    OrGate* createOrGate() {
        OrGate* gate = new OrGate();
        allGates.push_back(gate);
        return gate;
    }

    void setOutputGate(LogicGate* gate) {
        outputGate = gate;
    }


    void setInputs(const std::vector<bool>& values) {
        if (values.size() != inputPins.size()) {
            std::cerr << "Error: Number of inputs doesn't match pins." << std::endl;
            return;
        }
        for (int i = 0; i < values.size(); i++) {
            inputPins[i]->setValue(values[i]);
        }
    }

    bool evaluate() const {
        if (outputGate == nullptr) return false;
        return outputGate->calculateOutput();
    }

    std::unordered_map<std::string, LogicGate*> gateMap;

public:
    void loadFromFile(const std::string& filename) {
        std::ifstream file(filename);
        std::string line, command, name, target, type;
        int pinIndex;

        while (std::getline(file, line)) {
            std::stringstream ss(line);
            ss >> command;

            if (command == "INPUT") {
                ss >> name;
                gateMap[name] = createInputPin();
            }
            else if (command == "AND") {
                ss >> name;
                gateMap[name] = createAndGate();
            }
            else if (command == "CONNECT") {
                // דוגמה: CONNECT A G1 0
                ss >> name >> target >> pinIndex;
                LogicGate* sourceGate = gateMap[name];
                LogicGate* targetGate = gateMap[target];
                targetGate->connectInput(pinIndex, sourceGate);
            }
            else if (command == "OUTPUT") {
                ss >> name;
                setOutputGate(gateMap[name]);
            }
        }
    }
    int getNumInputs() const {
        return inputPins.size();
    }
};

