# 🐒 MonkeyTracker: Budget & Expense Tracker

Hello, this is my first Python project hope you enjoy it. if you try it out and have any ideas I could or feature implementation just shoot me a message and I will see about it. Yes, I am new the code is not the cleanest. Since it's my first project in this language. As I add more features I will work on breaking down the files.

MonkeyTracker is a tool designed to help you keep track of your expenses and how much money is coming in.
![MonkeyTracker Logo](C:\Dev\PythonProjects\TheMonkeyTracker\images\icons8-monkey-96.png) 
Monkey a lil ugly I know bare with me. Baby steps lads.
 ![Screenshot 2023-10-07 120257](https://github.com/HowLoveLee/TheMonkeyTracker/assets/78504600/daa8dd9d-b8fe-4c87-8cd4-f77cd96f37b6)
 ![File](https://github.com/HowLoveLee/TheMonkeyTracker/assets/78504600/a25572ab-4ee8-46cb-9967-ec9a07e6b93a)
![edit](https://github.com/HowLoveLee/TheMonkeyTracker/assets/78504600/c828da77-0235-4de6-81e9-2058a8229a6a)


## 🌟 Features (Work in progress)
Chef give me a few days don't fire me yet
## Libraries used:
- PYQT6
- SeaBorn
- PANDAS
- Matplotlib
 
## 📅 Future Plans, Will be added slowly, running out of time lately.

# MonkeyTracker Roadmap

## Menubar

### File
- :white_check_mark: New
- :white_check_mark: Load
- :white_check_mark: Save
  - ! Add a small panel that is green and says "Saved!"
- :white_check_mark: Save As
  - ! Add a small panel that is green and says "Saved! To path:"
- :white_check_mark: Settings
- [ ] Export To PDF
  - ! Exported to:
- :white_check_mark: Exit
  - # Dialog to prevent accidental loss of the current sheet for all exit actions.

### Edit (Complex task, timeline uncertain)
- [ ] Undo
- [ ] Redo
- [ ] Copy
- [ ] Paste
- [ ] Cut
- [ ] Select All
- [ ] Delete
- [ ] Find

### Server
- [ ] Download Sheet
- [ ] Upload Sheet

---

## Table Panel

### Columns
- :white_check_mark: Type of Expense
- :white_check_mark: Name of Expense
- :white_check_mark: Summary
- :white_check_mark: Date Due
- :white_check_mark: Audit Date
- :white_check_mark: Proof of Receipt
- :white_check_mark: Total Amount
- :white_check_mark: Commit Action
  - ! Potential addition: "From" column to indicate the payment method

### Features
- :white_check_mark: Add Row
- :white_check_mark: Delete Row
- :white_check_mark: Commit All Rows
- :white_check_mark: Total Pre
- :white_check_mark: Total Committed

### Filters
- [ ] Date Filter
  - Dropdown with 2 date selectors (From & To)
- [ ] Expense Category Filter
  - Dropdown with Tick Buttons next to categories.
- [ ] Reset Filter
  - Label to remove all filters and show the complete table.
     -Filter from a specific date to another date example (Show 6/21/2023-10/07/2023)
     -Expense Name, Expense Type, Expenses OVER $<Inset amount>, Expenses UNDER $<Inset amount>
---

## Settings

### Tables
- [ ] Category Editor (Add, Delete, Edit categories)
  - [ ] Expenses
  - [ ] Income
  - [ ] Budget

### Shortcuts
- [ ] Overview
  - Non-editable field listing shortcuts.
- [ ] Edit
  - Editable list of shortcuts, each with a corresponding button to set new input. Save/Cancel buttons.
  - Writes to a file for dynamic reading.

### Integrations
- [ ] File Management
  - Allows choosing where files are stored.

     
- **Expenses&Incomes Tab UI:** 
  - Run Statistics will be deleted no longer using Plotly, might use it to teleport to the expense chart breakdown of each % for the categories.
  - Filter options

- **Budget Tab UI:** 
  - Double Table with previews. Left will preview Net worth, right will preview Expenses over time.
  - Underneath we will have 3 buttons \Conditional Statements\Budgetting Goals\Debt Management
 
- **Settings:**
   -There is an unholy amount of work to be done to the settings but as you can see in the image, these are the functions I wish to have in the future.
  ![Settings](https://github.com/HowLoveLee/TheMonkeyTracker/assets/78504600/55d83fbb-f326-4d7e-ad21-b971ae27e85f)
- **Interactive Pie Charts:** Analyze your expenses with an interactive pie chart, and get a detailed breakdown with just a click.
- **Conditional Statements:**
   -Ability to create statements such as "For the next[dropdown(Week, Month, 6 Months, Year)]. I want to set a budget of [Insert Amount]. For the category[dropdown(Select Category)] and I want to stay within [QSpinBox(input a %)]
    - With this, you will be able to create budgets and see how you are doing in realtime when you edit the expenses table. to see how far or close you are to your goals. the % setting is to give you a warning when you reach a certain threshold, What is this for? Well next to the Conditions there will be a progress bar so you can see how close you will be to your goal when clicked it'll show you how close you are and if you get over the threshold the war will turn red and tell you how much you are going to push the goal out.
  -Debt Management is a whole other demon I will not give any further information on its function until I complete the other features.
