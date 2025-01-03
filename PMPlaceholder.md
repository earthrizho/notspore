# Project Timeline Manager - User Guide

## Overview
The Project Timeline Manager is an interactive web application for managing and visualizing project tasks with subtasks, designed specifically for project management in landscaping and construction projects.

## Main Features

### 1. Gantt Chart Visualization
- Located at the top of the page
- Shows all tasks and subtasks in a timeline format
- Color-coded by team member (Christian: blue, Jordan: purple, Crew: pink)
- Interactive features:
  - Hover over tasks to see details
  - Zoom and pan capabilities
  - Click and drag to select regions
  - Export chart as image

### 2. Daily Task View
- Organized horizontally by date
- Each day shows:
  - Day of week and date
  - Team members working that day
  - List of tasks in expandable sections

### 3. Task Management
Each task displays:
- Task name
- Assigned team member
- Start and end times
- Subtasks (if any)
- Control buttons:
  - Add Subtask
  - Edit
  - Delete

### 4. Subtask Features
Within each task:
- View existing subtasks
- Add new subtasks
- Each subtask shows:
  - Name
  - Assigned team member
  - Start/end times
  - Delete option

### 5. Adding New Tasks
Form at bottom of page includes:
- Task Name
- Team Member Assignment
- Start Date and Time
- End Date and Time
- Automatically includes capability for subtasks

### 6. Data Export
- Export button to download task data as CSV
- Includes all tasks and subtasks
- Preserves timing and assignment information

## How to Use

### Adding a New Task
1. Scroll to "Add New Task" at bottom of page
2. Fill in task details:
   - Enter task name
   - Select team member
   - Set start and end dates/times
3. Click "Add Task"

### Managing Subtasks
1. Click on any task to expand
2. Click "Add Subtask"
3. Fill in subtask details:
   - Name
   - Assigned team member
   - Timing
4. Click "Add Subtask" to save

### Viewing Schedule
1. Gantt chart shows overall timeline
2. Daily view shows detailed breakdown
3. Expand tasks to see subtasks
4. Use hover features for quick info

### Editing and Deleting
- Use Edit button to modify tasks
- Delete button removes tasks
- Subtasks can be deleted individually
- Changes update immediately in both views

## Technical Notes
- All times are in 24-hour format
- Dates are in YYYY-MM-DD format
- Tasks persist between sessions
- Export feature creates backup of all data 