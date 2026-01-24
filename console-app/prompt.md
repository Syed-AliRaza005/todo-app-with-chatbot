# Role: Senior Python Agentic Developer
# Task: Persistent In-Memory Todo CLI with Rich UI

You are an expert Python developer. Your goal is to build a robust CLI Todo application using Python 3.13+ and UV.

## Core Features & Logic:
1. **Task Schema**:
   - `id`: Unique Integer.
   - `title`: String.
   - `description`: String.
   - `status`: 'Pending' or 'Completed'.
   - `timestamp`: Date and Time of creation (e.g., YYYY-MM-DD HH:MM).

2. **Advanced Requirements**:
   - **Persistence**: Data runtime mein memory mein rahega, lekin har change par `tasks.json` mein save hoga taake restart par purana data wapis aa jaye.
   - **ID Stability**: Task delete karne se baaki IDs change nahi hongi. 
   - **Clear Command**: `clear` command se saara data delete hoga aur ID counter wapis 1 se start hoga.
   - **Rich UI**: `Rich` library use karke colorful tables banayein. Tasks ko teen sections mein dikhayein: [All Tasks], [Pending], aur [Completed].

3. **CLI Commands**:
   - `add`: Title aur Description ke saath task add karein (Auto-capture current Date/Time).
   - `list`: Categorized table dikhayein.
   - `update <id>`: Details edit karein.
   - `delete <id>`: Specific task remove karein.
   - `done <id>`: Task complete mark karein.
   - `clear`: Reset everything.

## Implementation Instructions:
- Use `uv` for project initialization and dependency management.
- Libraries: `rich` for UI, `json` for storage, `datetime` for timestamps.
- Code Structure: Modular (e.g., `models.py`, `database.py`, `app.py`).