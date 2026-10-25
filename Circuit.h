#include <vector>
#include "Gate.h"
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <string>

//the generate 2 vectors to hold pointerL one for all the gates, one only for the inputs
//(since we dont want the code to brows through all the gates when it looks to insert inputs, only the relevant ones)
//and and an addition pointer to the output
class Circuit {
private:
    std::vector<LogicGate*> allGates;

    std::vector<InputPin*> inputPins;

    LogicGate* outputGate = nullptr;

//just a standard deconstructor.
public:
    ~Circuit() {
        for (int i = 0; i < allGates.size(); i++) {
            delete allGates[i]; 
        }
    }

//here is a set of commands that the code executed each time it receives and input, a certain gate, or an output
//it generates the relevant instance of a class (described in Gate.h), and store the pointer to it in the relevant vectors
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

    NotGate* createNotGate() {
        NotGate* gate = new NotGate();
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


//the code receives the txt file from the Python code. it looks for the first word in each line
//if is in an input/output/gate it istores it in the unordered map
//if it is a connect command: connect comand has 3 parameters: the name of the source gate, the name of the target gate, and to which input of the target gate we want to connect the source gate
//using the gatemap we make pointers to the two relevant gates, and then we use connectInput to connect to the target gate the source gate in the right index (in Gate.h, every gate has
//a constructor that makes a vector that holds the inputs of the gate. What happens when we want to calculate the output, we go backwards: every gate looks at its previous gates up until the inputs are reached.
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
            else if (command == "OR") {
                ss >> name;
                gateMap[name] = createOrGate();
            }
            else if (command == "NOT") {
                ss >> name;
                gateMap[name] = createNotGate();
            }
            else if (command == "CONNECT") {
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

