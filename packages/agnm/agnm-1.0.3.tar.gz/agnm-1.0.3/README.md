# Physics equations of motion solver
This is a package for physics motion calculations.

# Installation
```pip install agnm```

# Usage
### Displacement
Displacement is calculated using formula: 
```math
x = (vi-vf)/2*t 
```

```python
from agnm.motion import displacement

displacement(1, 2.3, 3)  # output: 2.65
# or use named variables
displacement(vf=2.3, t=1, vi=3)  # output: 2.65
```

### Change in position
Change in position is calculated using formula: 
```math
x = vi*t+1/2*a*t^2
```

```python
from agnm.motion import change_in_position

change_in_position(1, 3, 2)  # output: 12.0
# or use named variables
change_in_position(a=2, t=3, vi=1)  # output: 12.0
```

### Final velocity
Final velocity is calculated using one of formulas: 
```math
vf = (vi^2+2a*x)^1/2
vf = vi+a*t
```

```python
from agnm.motion import v_final

# using first equation
v_final(vi=1, a=3, x_delta=1.5)  # output: 10.0
# using second equation
v_final(vi=1, a=2.3, t=2)  # output: 5.6
```

### Average velocity
Average velocity is calculated using one of formulas: 
```math
va = x/t
va = (vi+vf)/2
```

```python
from agnm.motion import v_average

# using first equation
v_average(x_delta=1, t=3)  #output: 0.3333333333333333
# using second equation
v_average(vi=1, vf=2.6)  #output: 0.8
```

### Acceleration
Acceleration velocity is calculated using one of formulas: 
```math
a = v/t
a = (vf+vi)/t
```

```python
from agnm.motion import acceleration

# using first equation
acceleration(v_delta=5, t=2.5)
#output: 2.0
# using second equation
acceleration(vi=1, vf=6, t=2.5)
#output: 2.0
```