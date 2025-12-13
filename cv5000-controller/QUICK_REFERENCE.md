# CV-5000 Controller - Quick Reference Card

## 🚀 Quick Start

```python
from src.device import CV5000Device

device = CV5000Device(port="COM4", debug=True)
device.connect()
device.initialize()
# ... use device ...
device.disconnect()
```

---

## 📋 All Methods at a Glance

### 🔌 Connection
```python
device.connect()                    # Connect to device
device.disconnect()                 # Disconnect
device.is_connected()               # Check connection
device.initialize()                 # 🆕 Initialize device
```

### ℹ️ Device Information
```python
device.get_version()                # Get software/controller version
device.get_current_values()         # 🆕 Get current device values
device.reset()                      # Reset device
device.get_state()                  # Get cached state
```

### 👁️ Prescription
```python
# Basic
device.set_prescription(
    r_sph=-1.50, r_cyl=-0.50, r_axis=90,
    l_sph=-2.00, l_cyl=-0.75, l_axis=180
)

# With chart/mode (enhanced) ⚡
device.set_prescription(
    r_sph=-1.50, r_cyl=-0.50, r_axis=90,
    l_sph=-2.00, l_cyl=-0.75, l_axis=180,
    chart=1, mode=1, display=2
)

# Convenience methods
device.set_sphere_both(-1.50)       # Both eyes
device.set_cylinder_both(-0.50)     # Both eyes
device.reset_to_zero()              # Reset all to 0
```

### 📏 PD
```python
device.set_pd(64.0)                 # Set pupillary distance
```

### 📊 Charts
```python
# Simple switching 🆕
device.switch_chart(1)              # Chart 1
device.switch_chart(2)              # Chart 2

# Complex patterns 🆕
device.set_chart_pattern(1)         # Basic chart 1
device.set_chart_pattern(12)        # Chart 1, pattern 2
device.set_chart_pattern(47)        # Special pattern

# Axis mode 🆕
device.set_axis_mode('R', 25, 2)    # Right eye, 25°, mode 2
device.set_axis_mode('L', 25, 1)    # Left eye, 25°, mode 1

# Legacy
device.show_echart()                # Show E-chart
device.set_chart_line(5)            # Select line 5
```

---

## 🎯 Common Workflows

### Complete Exam
```python
device = CV5000Device(port="COM4")
device.connect()
device.initialize()

# Chart 1 - Distance
device.switch_chart(1)
device.set_prescription(
    r_sph=-1.00, r_cyl=-0.50, r_axis=90,
    l_sph=-1.25, l_cyl=-0.50, l_axis=85,
    chart=1, display=2
)

# Chart 2 - Near
device.switch_chart(2)
device.set_prescription(chart=2, display=2)

# Set PD
device.set_pd(64.0)

device.disconnect()
```

### Quick Prescription
```python
device = CV5000Device(port="COM4")
device.connect()
device.initialize()
device.set_prescription(r_sph=-1.50, l_sph=-2.00)
device.set_pd(64.0)
device.disconnect()
```

### Chart Testing
```python
device = CV5000Device(port="COM4")
device.connect()
device.initialize()

for chart in [1, 2, 3, 4, 5]:
    device.switch_chart(chart)
    time.sleep(1)

device.disconnect()
```

---

## 📊 Value Ranges

| Parameter | Min | Max | Step | Example |
|-----------|-----|-----|------|---------|
| Sphere | -20.00 | +20.00 | 0.25 | -1.50 |
| Cylinder | -6.00 | 0.00 | 0.25 | -0.50 |
| Axis | 0 | 180 | 1 | 90 |
| PD | 50.0 | 80.0 | 0.5 | 64.0 |
| Chart | 1 | 9 | 1 | 2 |
| Mode | 1 | 2 | 1 | 1 |
| Display | 0 or 2 | - | - | 2 |

---

## 🆕 What's New in v2.0

| Feature | Before | After |
|---------|--------|-------|
| Commands | 2 types | 6 types |
| Methods | 3 | 10 |
| Coverage | 33% | 100% ✅ |
| Initialization | ❌ | ✅ |
| Version Query | ❌ | ✅ |
| Chart Control | ❌ | ✅ |
| Chart Patterns | ❌ | ✅ |
| Axis Modes | ❌ | ✅ |
| Mode Params | ❌ | ✅ |

---

## 🔍 Debug Mode

```python
device = CV5000Device(port="COM4", debug=True)
```

Output:
```
TX: 01 72 0D 04
    <SOH>r<CR><EOT>
RX: 01 65 72 0D 30 31 0D 04
    <SOH>er<CR>01<CR><EOT>
```

---

## ⚠️ Common Issues

### Port Already in Use
```python
# Close other programs using COM4
# Or try a different port
device = CV5000Device(port="COM5")
```

### Permission Denied (Windows)
```
Run Python as Administrator
```

### Device Not Responding
```python
device.reset()          # Try reset
device.initialize()     # Re-initialize
```

---

## 📖 More Documentation

- **Complete API:** `README_UPDATED.md`
- **Protocol Details:** `PROTOCOL_COMPLETE.md`
- **Examples:** `examples/complete_workflow.py`
- **Migration Guide:** `CONTROLLER_UPDATES_SUMMARY.md`

---

## 🎓 Tips

1. **Always initialize** after connecting
2. **Use debug mode** when developing
3. **Cache state** is automatically maintained
4. **Chart/mode params** are optional (use defaults)
5. **Test on demo** mode before hardware

---

**Version:** 2.0 (Complete Edition)  
**Coverage:** 100% ✅  
**Status:** Production Ready

