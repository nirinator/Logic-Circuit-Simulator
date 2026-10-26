# import all the PyQt5 libraries, and also subprocess so we could run the C++ code from here
import os
import json
import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QMainWindow,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsLineItem,
    QInputDialog, QMessageBox, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen, QColor, QPainter, QFont

# here we define the wires, we use super() to inherit all the properties from PyQt5, this would repeat along the program
# we define the start of the wire and its end in the current moment.
# update_positions updates the position of the wire end
# we defince mousePressEvent and remove_wire which check whether we are in erase mode when the mouse is clocked over the wire, and if so we erase it
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
        if end is not None:
            self.setLine(start.x(), start.y(), end.x(), end.y())

    def mousePressEvent(self, event):
        window = self.scene().views()[0].window()
        if getattr(window, 'mode', 'SELECT') == "DELETE":
            self.remove_wire()
            event.accept()
        else:
            super().mousePressEvent(event)

    def remove_wire(self):
        if self.start_pin and self in self.start_pin.wires:
            self.start_pin.wires.remove(self)
        if self.end_pin and self in self.end_pin.wires:
            self.end_pin.wires.remove(self)
        if self.scene():
            self.scene().removeItem(self)

# here we define the pins. every pin has a (x,y) coordinates, it is either in or out, it has an index and it is part of a gate (so that moving the gate would also move its pins).
# mousePressEvent, mouseMoveEvent and mouseReleaseEvent function manage the events where we press the mouse, move it and release it respectively.
# we use here extensively the built-in tools of PyQt5 library
# mouseReleaseEvent checks when we release the mouse whether we left it on a pin, and if not it erases the wire.
# mousePressEvent checks first of all whether we are in erase mode, if so it erases the gate to which the pin is connected together with the pin, otherwise it stretches a new wire
class Pin(QGraphicsEllipseItem):
    def __init__(self, x, y, pin_type, parent=None, index=0):
        super().__init__(x, y, 10, 10, parent)
        self.setBrush(QBrush(QColor("black")))
        self.pin_type = pin_type
        self.index = index
        self.wires = []
        self.drag_wire = None

    def mousePressEvent(self, event):
        window = self.scene().views()[0].window()
        if getattr(window, 'mode', 'SELECT') == "DELETE":
            if self.parentItem():
                self.parentItem().remove_gate()
            event.accept()
            return

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
# the itemChange makes sure that when we move the gate, wires move along
class GateNode(QGraphicsRectItem):
    def __init__(self, x, y, gate_type, num_inputs=2, num_outputs=1, custom_template=None):
        height = max(50, max(num_inputs, num_outputs) * 25 + 15)
        super().__init__(0, 0, 100, height)
        self.setPos(x, y)

        self.gate_type = gate_type
        self.custom_template = custom_template

        if gate_type in ["INPUT", "OUTPUT"]:
            self.setBrush(QBrush(QColor("lightblue")))
        elif custom_template:
            self.setBrush(QBrush(QColor("#FFE4B5")))
        else:
            self.setBrush(QBrush(QColor("lightgray")))

        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)

        self.text = QGraphicsTextItem(gate_type, self)
        self.text.setPos(15, height / 2 - 12)

        self.pins = []

        if gate_type == "INPUT":
            self.out_pin = Pin(95, height / 2 - 5, 'out', self, index=0)
            self.pins.append(self.out_pin)
        elif gate_type == "OUTPUT":
            self.in_pin1 = Pin(-5, height / 2 - 5, 'in', self, index=0)
            self.pins.append(self.in_pin1)
        elif gate_type in ["AND", "OR"]:
            self.out_pin = Pin(95, height / 2 - 5, 'out', self, index=0)
            in_pin1 = Pin(-5, 10, 'in', self, index=0)
            in_pin2 = Pin(-5, 30, 'in', self, index=1)
            self.pins.extend([self.out_pin, in_pin1, in_pin2])
        elif gate_type == "NOT":
            self.out_pin = Pin(95, height / 2 - 5, 'out', self, index=0)
            in_pin1 = Pin(-5, height / 2 - 5, 'in', self, index=0)
            self.pins.extend([self.out_pin, in_pin1])
        else:
            step_in = height / (num_inputs + 1)
            for i in range(num_inputs):
                p = Pin(-5, step_in * (i + 1) - 5, 'in', self, index=i)
                self.pins.append(p)

            step_out = height / (num_outputs + 1)
            for j in range(num_outputs):
                p = Pin(95, step_out * (j + 1) - 5, 'out', self, index=j)
                self.pins.append(p)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            for pin in self.pins:
                for wire in pin.wires:
                    wire.update_positions()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        window = self.scene().views()[0].window()
        if getattr(window, 'mode', 'SELECT') == "DELETE":
            self.remove_gate()
            event.accept()
        else:
            super().mousePressEvent(event)

    def remove_gate(self):
        scene = self.scene()
        if not scene:
            return

        for pin in self.pins:
            for wire in list(pin.wires):
                wire.remove_wire()

        scene.removeItem(self)


# here we define the class that dictates the simulation, using the built-in function of PyQt5 we describe what would appear on the screen setup (button etc)
# the function add_gate
class CircuitSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mode = "SELECT"
        self.custom_components = {}
        self.MAX_CUSTOM_COMPONENTS = 6
        self.input_counter = 1
        self._creation_counter = 0

        self.setWindowTitle("Logic Circuit Simulator Pro")
        self.setGeometry(100, 100, 1100, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.toolbar_layout = QVBoxLayout()

        mode_layout = QHBoxLayout()
        self.btn_select = QPushButton("Select (Arrow)")
        self.btn_select.clicked.connect(self.set_select_mode)
        mode_layout.addWidget(self.btn_select)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.set_delete_mode)
        mode_layout.addWidget(self.btn_delete)
        self.toolbar_layout.addLayout(mode_layout)

        btn_run = QPushButton("▶ RUN SIMULATION")
        btn_run.setStyleSheet("background-color: lightgreen; font-weight: bold; padding: 10px;")
        btn_run.clicked.connect(self.run_simulation)
        self.toolbar_layout.addWidget(btn_run)

        lbl_standard = QLabel("Standard Components")
        lbl_standard.setFont(QFont("Arial", 9, QFont.Bold))
        self.toolbar_layout.addWidget(lbl_standard)

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

        self.toolbar_layout.addWidget(btn_add_in)
        self.toolbar_layout.addWidget(btn_add_out)
        self.toolbar_layout.addWidget(btn_add_and)
        self.toolbar_layout.addWidget(btn_add_or)
        self.toolbar_layout.addWidget(btn_add_not)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.toolbar_layout.addWidget(separator)

        self.lbl_custom = QLabel("Custom Components (0/6)")
        self.lbl_custom.setFont(QFont("Arial", 9, QFont.Bold))
        self.toolbar_layout.addWidget(self.lbl_custom)

        btn_create_sub = QPushButton("📦 Create Component")
        btn_create_sub.setStyleSheet("background-color: #FFA500; font-weight: bold; padding: 6px;")
        btn_create_sub.clicked.connect(self.create_custom_component)
        self.toolbar_layout.addWidget(btn_create_sub)

        self.custom_buttons_layout = QVBoxLayout()
        self.toolbar_layout.addLayout(self.custom_buttons_layout)

        self.toolbar_layout.addStretch()

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 2000, 2000)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        main_layout.addLayout(self.toolbar_layout)
        main_layout.addWidget(self.view)

        self.load_custom_components_from_file()

#set_select_mode and set_delete_mode are controlled by the upper buttons
    def set_select_mode(self):
        self.mode = "SELECT"
        self.view.viewport().setCursor(Qt.ArrowCursor)

    def set_delete_mode(self):
        self.mode = "DELETE"
        self.view.viewport().setCursor(Qt.CrossCursor)

#add_gate generates the right gate. is it is an input, it gives it a name that correspones to its order of generation
    def add_gate(self, gate_type):
        new_gate = GateNode(100, 100, gate_type)

        self._creation_counter += 1
        new_gate.creation_order = self._creation_counter

        if gate_type == "INPUT":
            name = f"IN{self.input_counter}"
            new_gate.node_id = name
            new_gate.text.setPlainText(name)
            self.input_counter += 1

        self.scene.addItem(new_gate)

#add_custom_gate works similarly to add_gate, but for custom gates
    def add_custom_gate(self, name):
        tmpl = self.custom_components[name]
        new_gate = GateNode(150, 150, name, num_inputs=tmpl["num_inputs"],
                            num_outputs=tmpl["num_outputs"], custom_template=tmpl)
        self._creation_counter += 1
        new_gate.creation_order = self._creation_counter
        self.scene.addItem(new_gate)
#we dont want to lose the custom components each time we close the program, so we copy them to a json file, which using load_custom_components_from_file are being regenerated in the bank.
    def save_custom_components_to_file(self):
        try:
            with open("custom_components.json", "w", encoding="utf-8") as f:
                json.dump(self.custom_components, f, indent=4)
        except Exception as e:
            print(f"Error saving custom components: {e}")

    def load_custom_components_from_file(self):
        if not os.path.exists("custom_components.json"):
            return

        try:
            with open("custom_components.json", "r", encoding="utf-8") as f:
                self.custom_components = json.load(f)

            for name, tmpl in self.custom_components.items():
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)

                btn_del_comp = QPushButton("✕")
                btn_del_comp.setFixedWidth(28)
                btn_del_comp.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
                btn_del_comp.clicked.connect(lambda _, n=name, w=row_widget: self.delete_custom_component(n, w))
                row_layout.addWidget(btn_del_comp)

                btn_custom = QPushButton(f"Add {name}")
                btn_custom.setStyleSheet("background-color: #FFE4B5; font-weight: bold;")
                btn_custom.clicked.connect(lambda _, n=name: self.add_custom_gate(n))
                row_layout.addWidget(btn_custom)

                self.custom_buttons_layout.addWidget(row_widget)

            count = len(self.custom_components)
            self.lbl_custom.setText(f"Custom Components ({count}/{self.MAX_CUSTOM_COMPONENTS})")
        except Exception as e:
            print(f"Error loading custom components: {e}")

    def delete_custom_component(self, name, row_widget):
        if name in self.custom_components:
            del self.custom_components[name]

        row_widget.deleteLater()
        self.save_custom_components_to_file()

        count = len(self.custom_components)
        self.lbl_custom.setText(f"Custom Components ({count}/{self.MAX_CUSTOM_COMPONENTS})")

#create_custom_component saves a custom component whose logic is identical to the logical tree present on the screen
#it stores all the data about the gates and connections, and when it later sends description of this instance to the C++ code, it doesnt send it as a custon component, but rather as a sent of the basic gates and connections.
#when a custom component is saved, it appears in the components bank and can henceforth be used like the basic and or not gates
#notice that next to every custom component there is an x button that allows to erase it, and that there is a limit to how many custom components can be staved
    def create_custom_component(self):
        if len(self.custom_components) >= self.MAX_CUSTOM_COMPONENTS:
            QMessageBox.warning(
                self,
                "Limit Reached",
                f"You have reached the maximum limit of {self.MAX_CUSTOM_COMPONENTS} custom components!\n"
                "Cannot create any more custom components."
            )
            return

        nodes = [item for item in self.scene.items() if isinstance(item, GateNode)]
        inputs = [n for n in nodes if n.gate_type == "INPUT"]
        outputs = [n for n in nodes if n.gate_type == "OUTPUT"]

        if not inputs or not outputs:
            QMessageBox.warning(
                self,
                "Error",
                "A custom component requires at least one INPUT and one OUTPUT on the canvas!"
            )
            return

        name, ok = QInputDialog.getText(self, "New Component", "Enter custom component name (e.g. AND3):")
        if not ok or not name.strip():
            return

        name = name.strip().upper()
        if name in self.custom_components or name in ["AND", "OR", "NOT", "INPUT", "OUTPUT"]:
            QMessageBox.warning(self, "Error", "Component name already exists or is reserved.")
            return

        inputs.sort(key=lambda n: n.y())
        outputs.sort(key=lambda n: n.y())

        id_map = {node: f"SUB_{idx}" for idx, node in enumerate(nodes)}

        internal_gates = []
        for node in nodes:
            if node.gate_type not in ["INPUT", "OUTPUT"]:
                internal_gates.append({
                    "id": id_map[node],
                    "type": node.gate_type,
                    "template": node.custom_template
                })

        connections = []
        wires = [item for item in self.scene.items() if isinstance(item, Wire)]
        for wire in wires:
            if wire.start_pin and wire.end_pin:
                s_pin = wire.start_pin if wire.start_pin.pin_type == 'out' else wire.end_pin
                t_pin = wire.end_pin if wire.start_pin.pin_type == 'out' else wire.start_pin

                connections.append({
                    "src_node": id_map[s_pin.parentItem()],
                    "dst_node": id_map[t_pin.parentItem()],
                    "dst_pin_idx": t_pin.index
                })

        self.custom_components[name] = {
            "num_inputs": len(inputs),
            "num_outputs": len(outputs),
            "input_map": [id_map[inp] for inp in inputs],
            "output_map": [id_map[out] for out in outputs],
            "internal_gates": internal_gates,
            "connections": connections
        }

        self.save_custom_components_to_file()

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        btn_del_comp = QPushButton("✕")
        btn_del_comp.setFixedWidth(28)
        btn_del_comp.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
        btn_del_comp.clicked.connect(lambda _, n=name, w=row_widget: self.delete_custom_component(n, w))
        row_layout.addWidget(btn_del_comp)

        btn_custom = QPushButton(f"Add {name}")
        btn_custom.setStyleSheet("background-color: #FFE4B5; font-weight: bold;")
        btn_custom.clicked.connect(lambda _, n=name: self.add_custom_gate(n))
        row_layout.addWidget(btn_custom)

        self.custom_buttons_layout.addWidget(row_widget)

        count = len(self.custom_components)
        self.lbl_custom.setText(f"Custom Components ({count}/{self.MAX_CUSTOM_COMPONENTS})")

        QMessageBox.information(
            self,
            "Success",
            f"Custom component '{name}' created successfully!\n({count}/{self.MAX_CUSTOM_COMPONENTS} used)"
        )

#the run_simulation function translates the logical circuit into the txt file according to the agreed format. it then runs LogicSimulator.exe which contains the cpp codes, and receives from it the truth table.
    def run_simulation(self):
        nodes = [item for item in self.scene.items() if isinstance(item, GateNode)]
        # here we sort the inputs by the order in which they are generated, it would be the order in which they would appear in the truth table
        nodes.sort(key=lambda n: getattr(n, 'creation_order', 0))
        wires = [item for item in self.scene.items() if isinstance(item, Wire)]


        id_counters = {"OUTPUT": 1, "AND": 1, "OR": 1, "NOT": 1}
        for node in nodes:
            gtype = node.gate_type
            if gtype != "INPUT":
                idx = id_counters.get(gtype, 1)
                node.node_id = f"{gtype}_{idx}"
                id_counters[gtype] = idx + 1

        final_gates = []
        final_connects = []
        final_output = None
        pin_mappings = {}


        for node in nodes:
            if node.gate_type == "INPUT":
                final_gates.append(f"INPUT {node.node_id}")


        for node in nodes:
            if node.gate_type == "INPUT":
                continue

            if node.custom_template:
                tmpl = node.custom_template
                sub_id_map = {}
                for g in tmpl["internal_gates"]:
                    sub_id_map[g["id"]] = f"{node.node_id}_{g['id']}"
                    final_gates.append(f"{g['type']} {sub_id_map[g['id']]}")

                for conn in tmpl["connections"]:
                    if conn["src_node"] in tmpl["input_map"]:
                        inp_idx = tmpl["input_map"].index(conn["src_node"])
                        pin_mappings[(node.node_id, inp_idx, 'in')] = (sub_id_map[conn["dst_node"]],
                                                                       conn["dst_pin_idx"])
                    elif conn["dst_node"] in tmpl["output_map"]:
                        out_idx = tmpl["output_map"].index(conn["dst_node"])
                        pin_mappings[(node.node_id, out_idx, 'out')] = (sub_id_map[conn["src_node"]], 0)
                    else:
                        final_connects.append(
                            f"CONNECT {sub_id_map[conn['src_node']]} {sub_id_map[conn['dst_node']]} {conn['dst_pin_idx']}"
                        )
            else:
                if node.gate_type != "OUTPUT":
                    final_gates.append(f"{node.gate_type} {node.node_id}")


        # here all the wires are listed, their source and destination
        for wire in wires:
            if wire.start_pin and wire.end_pin:
                s_pin = wire.start_pin if wire.start_pin.pin_type == 'out' else wire.end_pin
                t_pin = wire.end_pin if wire.start_pin.pin_type == 'out' else wire.start_pin

                s_node = s_pin.parentItem()
                t_node = t_pin.parentItem()

                if s_node.custom_template:
                    src_id, _ = pin_mappings.get((s_node.node_id, s_pin.index, 'out'), (s_node.node_id, 0))
                else:
                    src_id = s_node.node_id

                if t_node.gate_type == "OUTPUT":
                    final_output = f"OUTPUT {src_id}"
                elif t_node.custom_template:
                    target_id, target_pin_idx = pin_mappings.get(
                        (t_node.node_id, t_pin.index, 'in'), (t_node.node_id, t_pin.index)
                    )
                    final_connects.append(f"CONNECT {src_id} {target_id} {target_pin_idx}")
                else:
                    final_connects.append(f"CONNECT {src_id} {t_node.node_id} {t_pin.index}")

        # the wires and gates are copied into the output list
        lines = final_gates + final_connects
        if final_output:
            lines.append(final_output)

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