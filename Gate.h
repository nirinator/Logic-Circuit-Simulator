#pragma once
#include <iostream>
#include <vector>

class LogicGate {
protected:
    std::vector<LogicGate*> inputConnections;

public:
    //constructor: for every gate/input it generates a vector the length of the number of its inputs
    LogicGate(int numInputs) : inputConnections(numInputs, nullptr) {}

    //deconstructor for the mentioned above
    virtual ~LogicGate() = default;

    //this function is called by the target gate and receives the source gate, and to which index of the target gate it should be connected to
    void connectInput(int index, LogicGate* sourceGate) {
        if (index >= 0 && index < inputConnections.size()) {
            inputConnections[index] = sourceGate;
        }
        else {
            std::cerr << "Error: Invalid connection index." << std::endl;
        }
    }

    //there isnt a LogicGate component in the simulation, it just the mother class out of which the derived classes make use.
    //It allows the function to operate using polymorphism: the inputConnections function for example does do the same for each gate
    //for and/or it would produce a vector of the length of 2, but for not it would be of the length of 1
    virtual bool calculateOutput() const = 0;
};



//here we describe the properties of each type of gate: how many inputs does it receive, and how does it calculate the output. Here we can witness the backswars calculation mentioned in Circuit.h:
//each gate makes a logical operation on its inputs, where iech input is the output calculation of the previous gate.
class AndGate : public LogicGate {
public:
    AndGate() : LogicGate(2) {}

    bool calculateOutput() const override {
        if (!inputConnections[0] || !inputConnections[1]) return false;

        return inputConnections[0]->calculateOutput() && inputConnections[1]->calculateOutput();
    }
};

class OrGate : public LogicGate {
public:
    OrGate() : LogicGate(2) {}

    bool calculateOutput() const override {
        if (!inputConnections[0] || !inputConnections[1]) return false;

        return inputConnections[0]->calculateOutput() || inputConnections[1]->calculateOutput();
    }
};

class NotGate : public LogicGate {
public:
    NotGate() : LogicGate(1) {} 

    bool calculateOutput() const override {
        if (!inputConnections[0]) return false;

        return !inputConnections[0]->calculateOutput();
    }
};


//here we describe the properties of the input: it inherits all the properties of a gate, but it has 0 inputs, its values (which it returns when called by a gate) is
//equal to the values set to the input by setValue each time it is called in Circuit.h (which is itself called by main.cpp each time it calculates the output for a set of inputs)
class InputPin : public LogicGate {
private:
    bool value;
public:
    InputPin() : LogicGate(0) {}

    void setValue(bool val) {
        value = val;
    }

    bool calculateOutput() const override {
        return value;
    }
};
