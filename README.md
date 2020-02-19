# Danbach AGV High-Level Command API
The Danbach AGV can be controlled using modbus TCP.
The default modbus host address is 192.168.10.30:502.
This API provode a set of straight-forward control commands to control the AGV based on the register table provided by Danbach.

# API list

## Initialization
The following command create an AGV client to the modbus host.
```python
d = Danbach_AGV(lwheel_scale, rwheel_scale, ip, port, timeout)
```

### parameters
 - `lwheel_scale`: the odometer scale for left wheel, ticks/metre (default = 1.0)
 - `rwheel_scale`: the odometer scale for right wheel, ticks/metre (default = 1.0)
 - `ip`: ip address to the modbus host (default = '192.168.10.30')
 - `port`: port to the modbus host (default = 502)
 - `timeout`: timeout for the modbus TCP protocol (default = 7e-3)

After the AGV client is successful created, use the following commands to establish/drop the connection.
```python
d.connect()
# ... other stuff
d.disconnect()
```

## Forward
Tell the AGV to move forward a constant distance (unit = metre) with a default/assigned speed.
```python
d.forward(1)      # forward 1 metre with default speed
d.forward(3, 400) # forward 3 metres with speed = 400 odometre ticks per second
```

## Back
Tell the AGV to move ack a constant distance (unit = metre) with a default/assigned speed.
```python
d.back(2)         # move back 2 metres with default speed
d.back(2, 400)    # move back 2 metres with speed = 400 odometre ticks per second
```

## Pivot 
Pivoting is an action that turns the AGV by rotating two wheels at opposite directions.
Perform pivoting with a given radian value with default/assigned speed.
```python
d.pivot(pi/2)       # turn pi/2 counter-clockwise
d.pivod(-pi/2, 400) # turn pi/2 clockwise with wheel speed = 400 odometer ticks per second
```

## Steer 
Steering is an action that turns the AGV by locking one wheel while rotating another one.
Perform steering with a given radian value with a default/assigned wheel speed.
```python
d.steer(pi/2, direction=1)  # turn pi/2 by advancing right wheel
d.steer(pi/2, direction=-1) # turn pi/2 by reverseing left wheel
```


