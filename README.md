



# 🎮 CallumConsole

**CallumConsole** is a fantasy console built for creativity, classrooms, and coders. It runs sandboxed cartridges written in Python using a secure scripting engine powered by RestrictedPython.  
Designed and maintained by [glkdrlgkrlzflnjkgh](https://github.com/glkdrlgkrlzflnjkgh)

---

## 🚀 Features

- 🕹️ Sprite rendering with a 16-color palette  
- 🎮 Input mapping for arrow keys + A/B + START/SELECT buttons  
- 🧠 Secure sandbox with safe globals and built-in guards  
- 📦 Cartridge system with `setup()` and `update()` hooks  
- 🧵 Threading support via a custom `Thread` wrapper  
- 🖨️ Print capture with `[CART OUTPUT]` logging  
- 🧱 MIT licensed and fully open source

---

## 📘 API Highlights (Implemented)

Cartridges can use these built-in functions:

| API | Description |
|-----|-------------|
| `draw_sprite(x, y)` | Draws the default 8×8 sprite at `(x, y)` |
| `draw_custom_sprite(sprite, x, y)` | Renders a user-defined sprite (up to 16×16) |
| `get_input()` | Returns a dictionary of key states: `left`, `right`, `up`, `down`, `a`, `b` |
| `quit()` | Gracefully exits the cartridge |
| `Thread(target)` | Runs a function in a background thread (sandboxed) |
| `print()` | Captured and displayed as `[CART OUTPUT]` in the console |

---

## 📂 Cartridge Format

Cartridges are `.callumcart` files containing Python code. Each cartridge should define:

```python
def setup():
    # Called once at startup

def update():
    # Called every frame
```

---

## 🛡️ Safety First

- Uses `RestrictedPython` to sandbox cartridge code  
- Only whitelisted modules (`math`, `random`) are exposed  
- Custom guards for safe iteration and dictionary access  
- No access to `os`, `sys`, or dangerous built-ins

---

## 📜 License

CallumConsole is licensed under the [MIT License](LICENSE).


