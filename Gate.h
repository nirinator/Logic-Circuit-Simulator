#pragma once
#include <iostream>
#include <vector>

class LogicGate {
protected:
    std::vector<LogicGate*> inputConnections;

public:
    LogicGate(int numInputs) : inputConnections(numInputs, nullptr) {}

    virtual ~LogicGate() = default;

    void connectInput(int index, LogicGate* sourceGate) {
        if (index >= 0 && index < inputConnections.size()) {
            inputConnections[index] = sourceGate;
        }
        else {
            std::cerr << "Error: Invalid connection index." << std::endl;
        }
    }

    virtual bool calculateOutput() const = 0;
};

class InputPin : public LogicGate {
private:
    bool value;
public:
    InputPin() : LogicGate(0), value(false) {} 

    void setValue(bool val) { 
        value = val; 
    }

    bool calculateOutput() const override { 
        return value; 
    } 
};

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

        return !inputConnections[0];
    }
};

