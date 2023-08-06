from pennylane import QubitDevice
import pennylane as qml
import numpy as np
import torch

class noise_model():
    def name(self):
        return "shift.3"
    def fxx(self,angle):
        return angle
    def fxy(self,angle):
        return 0.0
    def fxz(self,angle):
        return 0.0
    def fyx(self,angle):
        return 0.0
    def fyy(self,angle):
        return angle
    def fyz(self,angle):
        return 0.0
    def fzx(self,angle):
        return 0.0
    def fzy(self,angle):
        return 0.0
    def fzz(self,angle):
        return angle
    def hx(self):
        return 0;
    def hy(self):
        return 0;
    def hz(self):
        return 0;
    def out_distrib(self):
        return 0.0#np.random.normal(loc=0,scale=0.01)

default_nm=noise_model()
    
class noisy_qubit(QubitDevice):
    """Pennylane qubit with noise model"""
    name = 'noisy_qubit'
    short_name = 'noisy.qubit'
    pennylane_requires = '>=0.1.0'
    version = '0.0.1'
    author = 'Frederic Magniette'
    operations = {"RX", "RY", "RZ", "Hadamard"}
    observables = {"PauliZ", "PauliX", "PauliY"}

    def __init__(self, wires, shots=None, analytic=None,noise_model=default_nm):
        super().__init__(wires=1, shots=shots)
        if wires!=1:
            print("Warning: this device only accept 1 wire, reshaping to 1 wire")
        self.dev=qml.device("default.qubit",wires=1)
        self.reset()
        self.nm=noise_model

    def build_circuit(self):
        #print("build_circuit")
        for op in self.noisy_ops:
            qml.apply(op)
        return qml.expval(self.observable)
        
    def apply(self,operations, **kwargs):
        #print("apply")
        self.noisy_ops=[]
        for op in operations:
            if op.name=="RX":
                angle=op.parameters[0]
                self.noisy_ops.append(qml.RX(self.nm.fxx(angle),wires=0))
                self.noisy_ops.append(qml.RY(self.nm.fxy(angle),wires=0))
                self.noisy_ops.append(qml.RZ(self.nm.fxz(angle),wires=0))
            elif op.name=="RY":
                angle=op.parameters[0]
                self.noisy_ops.append(qml.RY(self.nm.fyy(angle),wires=0))
                self.noisy_ops.append(qml.RX(self.nm.fyx(angle),wires=0))
                self.noisy_ops.append(qml.RZ(self.nm.fyz(angle),wires=0))
            elif op.name=="RZ":
                angle=op.parameters[0]
                self.noisy_ops.append(qml.RZ(self.nm.fzz(angle),wires=0))
                self.noisy_ops.append(qml.RX(self.nm.fzx(angle),wires=0))
                self.noisy_ops.append(qml.RY(self.nm.fzy(angle),wires=0))
            elif op.name=="Hadamard":
                self.noisy_ops.append(qml.Hadamard(wires=0))
                self.noisy_ops.append(qml.RZ(self.nm.hx(),wires=0))
                self.noisy_ops.append(qml.RX(self.nm.hy(),wires=0))
                self.noisy_ops.append(qml.RY(self.nm.hz(),wires=0))
            else:
                print("unknown operation ",op)
        #print(self.noisy_ops)


    def expval(self, observable, shot_range=None, bin_size=None):
        #print("expval")
        self.observable=observable
        self.circuit=qml.QNode(self.build_circuit,self.dev)
        #you can uncomment this line if you want to see the resulting circuit
        #print(qml.draw(self.circuit)())
        value=self.circuit()+self.nm.out_distrib()
        #print("value=",value)
        return value

    
    def reset(self):
        #print("reset")
        self.noisy_ops=[]
