Pennylane-noisy-qubit
=====================

A noisy qubit for Pennylane with adjustable systematic error

It can be used by simply importing pennylane after installing the package :

```
import pennylane as qml
```

The noise_model class defines the systematic and statistic noise applied in the circuit. A bunch of function defines the behavior of the circuit.
For example, a RX operator application will behave like

-RX(fxx(angle))-RY(fxy(angle)-RZ(fxz(angle)-

The out_distrib function defines the statistical error applied during the readout of the qubit.

Here is an example : 

```
class noise_model():
    def name(self):
        return "shift.3"
    def fxx(self,angle):
        return angle+.3
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


nm=noise_model()
```

The device is declared like a default qubit, the number of wire should always be one and the noise model has to be specified : 

```
dev2 = qml.device("noisy.qubit", wires=1, noise_model=nm)
```

The circuit is then defined "Pennylane style" : 

```
@qml.qnode(dev2,interface="torch")
def test_circuit2(x,y,z):
    qml.RX(x,wires=0)
    qml.RY(y,wires=0)
    qml.RZ(z,wires=0)
    return qml.expval(qml.PauliZ(0))
```

and used the usual way : 

```
print(test_circuit2(1.,2.,3.))
```