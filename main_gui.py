# import all the PyQt5 libraries, and also subprocess so we could run the C++ code from here
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QGraphicsRectItem, \
    QGraphicsTextItem, QGraphicsEllipseItem, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsLineItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen, QColor, QPainter



# here we define the wires, we use super() to inherit all the properties from PyQt5, this would repeat along the program
# we define the start of the wire and its end in the current moment.
# update_positions updates the position of the wire end
class Wire(QGraphicsLineItem):
    def __init__(self, start_pin, end_pos):
        super().__init__()
        self.start_pin = start_pin
        self.end_pin = None
        self.setPen(QPen(Qt.black, 3))
        self.setZValue(-1)
        self.update_positions(end_pos)

    def update_positions(self, current_mouse_pos=None):
        start = self.start_pin.mapToScene(self.start_pin.boundingRect().center())
        if self.end_pin:
            end = self.end_pin.mapToScene(self.end_pin.boundingRect().center())
        else:
            end = current_mouse_pos
        self.setLine(start.x(), start.y(), end.x(), end.y())


# here we define the pins. every pin has a (x,y) coordinates, it is either in or out, it has an index and it is part of a gate (so that moving the gate would also move its pins).
# mousePressEvent, mouseMoveEvent and mouseReleaseEvent function manage the events where we press the mouse, move it and release it respectively.
# we use here extensively the built-in tools of PyQt5 library
# mouseReleaseEvent checks when we release the mouse whether we left it on a pin, and if not it erases the wire.
class Pin(QGraphicsEllipseItem):
    def __init__(self, x, y, pin_type, parent=None, index=0):
        super().__init__(x, y, 10, 10, parent)
        self.setBrush(QBrush(QColor("black")))
        self.pin_type = pin_type
        self.index = index
        self.wires = []
        self.drag_wire = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_wire = Wire(self, event.scenePos())
            self.scene().addItem(self.drag_wire)
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_wire:
            self.drag_wire.update_positions(event.scenePos())
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.drag_wire:
            items = self.scene().items(event.scenePos())
            connected_pin = None

            for item in items:
                if isinstance(item, Pin) and item != self and item.pin_type != self.pin_type:
                    connected_pin = item
                    break

            if connected_pin:
                self.drag_wire.end_pin = connected_pin
                self.drag_wire.update_positions()
                self.wires.append(self.drag_wire)
                connected_pin.wires.append(self.drag_wire)
            else:
                self.scene().removeItem(self.drag_wire)

            self.drag_wire = None
        event.accept()


# here we define the gates. We define the visual properties of the gates, we connect pins to them depending on the logical role of the gate.
# the itemChange makes sure that when we move the gate, wires move alongץ
class GateNode(QGraphicsRectItem):
    def __init__(self, x, y, gate_type):
        super().__init__(0, 0, 100, 50)
        self.setPos(x, y)

        if gate_type in ["INPUT", "OUTPUT"]:
            self.setBrush(QBrush(QColor("lightblue")))
        else:
            self.setBrush(QBrush(QColor("lightgray")))

        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)

        self.gate_type = gate_type

        # טקסט קבוע לפי סוג השער
        self.text = QGraphicsTextItem(gate_type, self)
        self.text.setPos(25, 10)

        self.pins = []

        # בניית הפינים לפי סוג הרכיב עם אינדקס מוגדר
        if gate_type == "INPUT":
            self.out_pin = Pin(95, 20, 'out', self, index=0)
            self.pins.append(self.out_pin)
        elif gate_type == "OUTPUT":
            self.in_pin1 = Pin(-5, 20, 'in', self, index=0)
            self.pins.append(self.in_pin1)
        else:
            self.out_pin = Pin(95, 20, 'out', self, index=0)
            self.pins.append(self.out_pin)

            if gate_type in ["AND", "OR"]:
                in_pin1 = Pin(-5, 10, 'in', self, index=0)  # כניסה עליונה = 0
                in_pin2 = Pin(-5, 30, 'in', self, index=1)  # כניסה תחתונה = 1
                self.pins.extend([in_pin1, in_pin2])
            elif gate_type == "NOT":
                in_pin1 = Pin(-5, 20, 'in', self, index=0)  # כניסה יחידה = 0
                self.pins.append(in_pin1)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            for pin in self.pins:
                for wire in pin.wires:
                    wire.update_positions()
        return super().itemChange(change, value)


# here we define the class that dictates the simulation, using the built-in function of PyQt5 we describe what would appear on the screen setup (button etc)
# the function add_gate
class CircuitSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logic Circuit Simulator Pro")
        self.setGeometry(100, 100, 1024, 768)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        toolbar_layout = QVBoxLayout()

        # הוספת כפתור ההרצה
        btn_run = QPushButton("▶ RUN SIMULATION")
        btn_run.setStyleSheet("background-color: lightgreen; font-weight: bold; padding: 10px;")
        btn_run.clicked.connect(self.run_simulation)

        # הוספת כפתורי קלט/פלט ושערים
        btn_add_in = QPushButton("Add INPUT")
        btn_add_in.setStyleSheet("background-color: lightblue;")
        btn_add_in.clicked.connect(lambda: self.add_gate("INPUT"))

        btn_add_out = QPushButton("Add OUTPUT")
        btn_add_out.setStyleSheet("background-color: lightblue;")
        btn_add_out.clicked.connect(lambda: self.add_gate("OUTPUT"))

        btn_add_and = QPushButton("Add AND Gate")
        btn_add_and.clicked.connect(lambda: self.add_gate("AND"))

        btn_add_or = QPushButton("Add OR Gate")
        btn_add_or.clicked.connect(lambda: self.add_gate("OR"))

        btn_add_not = QPushButton("Add NOT Gate")
        btn_add_not.clicked.connect(lambda: self.add_gate("NOT"))

        toolbar_layout.addWidget(btn_run)
        toolbar_layout.addWidget(btn_add_in)
        toolbar_layout.addWidget(btn_add_out)
        toolbar_layout.addWidget(btn_add_and)
        toolbar_layout.addWidget(btn_add_or)
        toolbar_layout.addWidget(btn_add_not)
        toolbar_layout.addStretch()

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 2000, 2000)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.view)

    def add_gate(self, gate_type):
        new_gate = GateNode(100, 100, gate_type)
        self.scene.addItem(new_gate)


    def run_simulation(self):
        #the simulation counts all the gates and gives them distinct names, and stores them.
        nodes = [item for item in self.scene.items() if isinstance(item, GateNode)]
        id_counters = {"INPUT": 1, "OUTPUT": 1, "AND": 1, "OR": 1, "NOT": 1}

        for node in nodes:
            node.node_id = f"{node.gate_type}_{id_counters[node.gate_type]}"
            id_counters[node.gate_type] += 1

        lines = []

        for node in nodes:
            if node.gate_type != "OUTPUT":
                lines.append(f"{node.gate_type} {node.node_id}")

        wires = [item for item in self.scene.items() if isinstance(item, Wire)]

        #here all the wires are listed, their source and destination
        for wire in wires:
            if wire.start_pin and wire.end_pin:
                if wire.start_pin.pin_type == 'out':
                    source_pin, target_pin = wire.start_pin, wire.end_pin
                else:
                    source_pin, target_pin = wire.end_pin, wire.start_pin

                source_node = source_pin.parentItem()
                target_node = target_pin.parentItem()

                if source_node and target_node:
                    if target_node.gate_type == "OUTPUT":
                        lines.append(f"OUTPUT {source_node.node_id}")
                    else:
                        pin_index = target_pin.index
                        lines.append(f"CONNECT {source_node.node_id} {target_node.node_id} {pin_index}")

        # the wires and gates are copied into the output list
        netlist_text = "\n".join(lines)
        with open("circuit.txt", "w") as f:
            f.write(netlist_text)

        print("--- Circuit exported to circuit.txt ---")
        print("Generated Netlist for C++:\n" + netlist_text)

        # the Python code goes to the LogicSimulator.exe that contains the access to the C++ codes (defined by the CMakeLists.txt)
        # the Python code receives the console output of main.cpp, and prints it in its own console.
        try:
            print("Running C++ Engine...")

            exact_path = "out/build/x64-Debug/LogicSimulator.exe"

            result = subprocess.run([exact_path], capture_output=True, text=True, check=True)
            print("--- C++ Output ---")
            print(result.stdout)
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircuitSimulator()
    window.show()
    sys.exit(app.exec_())