# 🚀 Quick Start Guide - Interactive Todo App

## Starting the App

```bash
cd console-app
uv run todo
```

You'll see:

```
╔═══════════════════════════════════════╗
║   📋 Console Todo Application v1.0   ║
╚═══════════════════════════════════════╝

✨ Manage your tasks with style! ✨

todo> _
```

## 5-Minute Tutorial

### 1️⃣ Add Your First Task (Interactive Prompts!)

```bash
todo> add
➕ Add New Task

  Title: Buy groceries
  Description: Milk, eggs, bread, butter

✓ Task added successfully!

  ID: 1
  Title: Buy groceries
  Description: Milk, eggs, bread, butter
  Status: Pending
  Created: 2026-01-01 12:30:45
```

**Pro Tip**: Type `add` and press Enter - then you'll be prompted for title and description step-by-step! No quotes needed!

### 2️⃣ View Your Tasks

```bash
todo> list
```

You'll see a single table with all your tasks:
- **Pending** tasks with 🟡 yellow status
- **Completed** tasks with 🟢 green status
- All in one organized table!

### 3️⃣ Complete a Task (Interactive!)

```bash
todo> done
✓ Mark Task as Done

  Task ID: 1

✓ Task #1 marked as completed!

  ID: 1
  Title: Buy groceries
  Description: Milk, eggs, bread, butter
  Status: Completed
  Created: 2026-01-01 12:30:45
```

**Pro Tip**: Just type `done` and it will ask for the task ID!

### 4️⃣ Add More Tasks

```bash
todo> add "Finish project" "Complete all pending work"
✓ Task added successfully!

  ID: 2
  ...
```

### 5️⃣ Update a Task (Shows Current Values!)

```bash
todo> update
✏️  Update Task

  Task ID: 2

  Current:
  Title: Finish project
  Description: Complete all pending work

  New Title: Finish hackathon
  New Description: Complete Phase-1 todo app

✓ Task #2 updated successfully!
```

**Pro Tip**: Just type `update` - it will show you the current task and ask for new values!

### 6️⃣ Delete a Task (With Confirmation!)

```bash
todo> delete
🗑️  Delete Task

  Task ID: 1

  Task to delete:
  Title: Buy groceries
  Description: Milk, eggs, bread, butter

  Delete this task? (yes/no): yes

✓ Task #1 deleted successfully!
  Deleted: "Buy groceries"
  Note: Other task IDs remain unchanged
```

**Important**:
- Shows you the task before deleting (safety!)
- Task IDs never change! If you delete task #1, the next task you add will get ID #3 (not #1)

### 7️⃣ Get Help Anytime

```bash
todo> help
```

Shows all available commands and examples.

### 8️⃣ Exit the App

```bash
todo> exit
👋 Goodbye! Your tasks are saved.
```

## 💡 Pro Tips

### Interactive Prompts = No Quotes Needed! 🎉
The NEW interactive mode means you don't need quotes anymore:
```bash
✅ New way: Just type 'add' and answer the prompts!
✅ Old way still works: add "Buy milk" "From the store"

# Interactive is easier!
todo> add
  Title: Buy milk
  Description: From the store
```

### Shortcuts
- `ls` = `list` (shorter to type)
- `del` = `delete` (shorter to type)
- Ctrl+C = Shows exit message (use `exit` instead)

### Data Persistence
Your tasks are automatically saved to `tasks.json` after every change. They'll be there when you restart the app!

### ID Stability Feature
```bash
todo> add "Task 1" "First"
todo> add "Task 2" "Second"
todo> add "Task 3" "Third"

# IDs: 1, 2, 3

todo> delete 2

# IDs: 1, 3 (not renumbered!)

todo> add "Task 4" "Fourth"

# New task gets ID 4 (not 2!)
```

This prevents confusion when referencing tasks.

### Clear All Tasks
```bash
todo> clear
⚠️  Clear all tasks? (yes/no): yes
✓ All tasks cleared!
  Deleted: 3 task(s)
  ID counter reset to 1
```

**Warning**: This is the ONLY command that resets the ID counter to 1.

## 🎨 Color Guide

When you run `list`, you'll see:

- 🟣 **Magenta** = Task IDs
- 🔵 **Cyan** = Headers and borders
- 🟡 **Yellow** = Pending tasks
- 🟢 **Green** = Completed tasks
- ⚪ **Dim White** = Timestamps

## 🔥 Common Workflows

### Daily Task Management
```bash
# Morning: Add today's tasks
todo> add "Morning standup" "Team sync at 9 AM"
todo> add "Code review" "Review PR #123"
todo> add "Lunch break" "12:00 PM"

# Throughout day: Mark as done
todo> done 1
todo> done 2

# Evening: Check what's left
todo> list
```

### Project Planning
```bash
todo> add "Design database schema" "Plan tables and relationships"
todo> add "Implement API endpoints" "REST API with FastAPI"
todo> add "Write tests" "Unit and integration tests"
todo> add "Deploy to production" "AWS deployment"

# Update as needed
todo> update 1 "Design database schema" "Added user and task tables"
```

### Quick Check
```bash
# Just see what you have
todo> list

# Exit immediately if done
todo> exit
```

## ❓ Need Help?

Inside the app:
```bash
todo> help
```

Or check the full documentation:
- `README.md` - Complete feature guide
- `TEST-RESULTS.md` - All features tested and validated

## 🎉 That's It!

You're now ready to use the Console Todo App like a pro!

**Remember**: 
- Start with `uv run todo`
- All commands inside the app
- `exit` to quit
- Your tasks are always saved!

Happy task managing! 📋✨
