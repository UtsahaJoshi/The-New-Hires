from models import User, Ticket, TicketStatus, TicketPriority
import asyncio
import base64
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

class RepoRequest(BaseModel):
    repo_name: str = "the-new-hire-simulation"

# ============== PROJECT TEMPLATE FILES ==============

INDEX_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskMaster - Todo App</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <!-- BUG #1: Login form has no error handling -->
        <div id="login-section" class="section">
            <h1>TaskMaster</h1>
            <p class="subtitle">Your Personal Task Manager</p>
            <form id="login-form">
                <input type="text" id="username" placeholder="Username">
                <input type="password" id="password" placeholder="Password">
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
            <p id="login-error" class="error"></p>
        </div>

        <!-- Main App Section (hidden by default) -->
        <div id="app-section" class="section hidden">
            <header>
                <h1>My Tasks</h1>
                <!-- BUG #6: Logout button doesn't work -->
                <button id="logout-btn" class="btn btn-secondary">Logout</button>
            </header>

            <!-- BUG #3: Add task form missing validation -->
            <form id="task-form">
                <input type="text" id="task-input" placeholder="Enter a new task...">
                <input type="date" id="task-due-date">
                <select id="task-priority">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                </select>
                <button type="submit" class="btn btn-primary">Add Task</button>
            </form>

            <!-- BUG #7: Filter doesn't work -->
            <div class="filters">
                <button class="filter-btn active" data-filter="all">All</button>
                <button class="filter-btn" data-filter="active">Active</button>
                <button class="filter-btn" data-filter="completed">Completed</button>
            </div>

            <!-- BUG #8: Task count shows wrong number -->
            <div class="task-stats">
                <span id="task-count">0 tasks</span>
                <span id="completed-count">0 completed</span>
            </div>

            <ul id="task-list"></ul>

            <!-- BUG #11: Clear completed doesn't work -->
            <button id="clear-completed" class="btn btn-danger">Clear Completed</button>
        </div>
    </div>

    <script src="utils.js"></script>
    <script src="api.js"></script>
    <script src="app.js"></script>
</body>
</html>
'''

STYLES_CSS = '''/* TaskMaster Styles */
/* BUG #2: No dark mode support - needs to be implemented */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f5f5f5;
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 600px;
    margin: 0 auto;
}

.section {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.hidden {
    display: none !important;
}

h1 {
    color: #333;
    margin-bottom: 10px;
}

.subtitle {
    color: #666;
    margin-bottom: 20px;
}

/* Form Styles */
form {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

input, select {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
}

input:focus, select:focus {
    outline: none;
    border-color: #007bff;
}

/* Button Styles */
.btn {
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.2s;
}

.btn-primary {
    background-color: #007bff;
    color: white;
}

.btn-primary:hover {
    background-color: #0056b3;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-danger {
    background-color: #dc3545;
    color: white;
}

/* BUG #9: Task items not styled properly - missing hover states */
.task-item {
    display: flex;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #eee;
    gap: 12px;
}

.task-item.completed .task-text {
    text-decoration: line-through;
    color: #999;
}

.task-text {
    flex: 1;
}

.task-priority {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.priority-high {
    background-color: #ffe0e0;
    color: #d32f2f;
}

.priority-medium {
    background-color: #fff3e0;
    color: #f57c00;
}

.priority-low {
    background-color: #e8f5e9;
    color: #388e3c;
}

/* Filters */
.filters {
    display: flex;
    gap: 10px;
    margin: 20px 0;
}

.filter-btn {
    padding: 8px 16px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 20px;
    cursor: pointer;
}

.filter-btn.active {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
}

.task-stats {
    display: flex;
    justify-content: space-between;
    color: #666;
    font-size: 14px;
    margin-bottom: 15px;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

#task-form {
    flex-direction: row;
    flex-wrap: wrap;
}

#task-input {
    flex: 1;
    min-width: 200px;
}

#task-list {
    list-style: none;
    margin: 20px 0;
}

.error {
    color: #dc3545;
    font-size: 14px;
    margin-top: 10px;
}

/* BUG #10: Delete button has no styles */
.delete-btn {
    /* TODO: Add styles for delete button */
}

/* TODO: BUG #2 - Add dark mode styles here */
/* .dark-mode { } */
'''

APP_JS = '''// TaskMaster Application
// WARNING: This code has INTENTIONAL BUGS for training purposes

let tasks = [];
let currentFilter = 'all';
let isLoggedIn = false;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('task-form').addEventListener('submit', handleAddTask);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('clear-completed').addEventListener('click', clearCompletedTasks);
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', handleFilter);
    });
    
    // Load tasks from localStorage
    loadTasks();
}

// BUG #1: Login throws 500 error - missing input validation
function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // BUG: No null/empty check causes error
    if (username.length < 1) {  // This should check for empty string properly
        // BUG: This error is not displayed to user properly
        throw new Error("Username cannot be empty");  // This crashes instead of showing error
    }
    
    // BUG: Password validation missing entirely
    // TODO: Add password validation
    
    // Simulate login
    isLoggedIn = true;
    showApp();
}

// BUG #6: Logout doesn't work - missing implementation
function handleLogout() {
    // TODO: Implement logout functionality
    console.log("Logout clicked");  // Only logs, doesn't actually logout
    // isLoggedIn = false;
    // showLogin();
}

function showApp() {
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('app-section').classList.remove('hidden');
}

function showLogin() {
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('app-section').classList.add('hidden');
}

// BUG #3: Add task has no validation
function handleAddTask(e) {
    e.preventDefault();
    
    const taskInput = document.getElementById('task-input');
    const dueDateInput = document.getElementById('task-due-date');
    const priorityInput = document.getElementById('task-priority');
    
    // BUG: No validation - allows empty tasks
    const task = {
        id: Date.now(),
        text: taskInput.value,  // Can be empty!
        dueDate: dueDateInput.value,
        priority: priorityInput.value,
        completed: false
    };
    
    tasks.push(task);
    saveTasks();
    renderTasks();
    
    // BUG #4: Form doesn't clear after submit
    // taskInput.value = '';  // Commented out - form doesn't reset
}

// BUG #5: Delete task has wrong logic
function deleteTask(id) {
    // BUG: Uses wrong comparison - string vs number
    tasks = tasks.filter(task => task.id != id);  // Should use strict equality
    saveTasks();
    renderTasks();
}

function toggleTask(id) {
    const task = tasks.find(t => t.id === id);
    if (task) {
        task.completed = !task.completed;
        saveTasks();
        renderTasks();
    }
}

// BUG #7: Filter doesn't work properly
function handleFilter(e) {
    const filter = e.target.dataset.filter;
    currentFilter = filter;
    
    // BUG: Only updates visual state, doesn't re-render tasks
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    
    // TODO: Call renderTasks() here
}

function renderTasks() {
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';
    
    let filteredTasks = tasks;
    
    // BUG #7 continued: Filter logic exists but isn't called from handleFilter
    if (currentFilter === 'active') {
        filteredTasks = tasks.filter(t => !t.completed);
    } else if (currentFilter === 'completed') {
        filteredTasks = tasks.filter(t => t.completed);
    }
    
    filteredTasks.forEach(task => {
        const li = document.createElement('li');
        li.className = `task-item ${task.completed ? 'completed' : ''}`;
        li.innerHTML = `
            <input type="checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTask(${task.id})">
            <span class="task-text">${task.text}</span>
            <span class="task-priority priority-${task.priority}">${task.priority}</span>
            <span class="task-due">${task.dueDate || 'No date'}</span>
            <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
        `;
        taskList.appendChild(li);
    });
    
    updateTaskCount();
}

// BUG #8: Task count shows wrong number
function updateTaskCount() {
    const totalCount = tasks.length;
    const completedCount = tasks.filter(t => t.completed).length;
    
    // BUG: Displays "tasks" even for 1 task (should be "task")
    document.getElementById('task-count').textContent = `${totalCount} tasks`;
    
    // BUG: Completed count doesn't update properly
    document.getElementById('completed-count').textContent = `${completedCount} completed`;
}

// BUG #11: Clear completed doesn't work
function clearCompletedTasks() {
    // BUG: Logic is inverted - keeps completed instead of removing them
    tasks = tasks.filter(t => t.completed);  // Wrong! Should be !t.completed
    saveTasks();
    renderTasks();
}

// BUG #12: LocalStorage not working properly
function saveTasks() {
    // BUG: Saves to wrong key
    localStorage.setItem('taskmaster_tasks', JSON.stringify(tasks));
}

function loadTasks() {
    // BUG: Loads from different key than saveTasks
    const saved = localStorage.getItem('tasks');  // Should be 'taskmaster_tasks'
    if (saved) {
        tasks = JSON.parse(saved);
        renderTasks();
    }
}
'''

UTILS_JS = '''// Utility Functions
// BUG #4 (partial): This file needs refactoring - messy code

// TODO: This code is messy and needs cleanup

function formatDate(d) {
var date = new Date(d);
var m = date.getMonth() + 1;
var day = date.getDate();
var y = date.getFullYear();
return m + "/" + day + "/" + y;
}

function validateEmail(e) {
// messy regex
var re = /^(([^<>()\\[\\]\\\\.,;:\\s@"]+(\\.[^<>()\\[\\]\\\\.,;:\\s@"]+)*)|(".+"))@((\\[[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\])|(([a-zA-Z\\-0-9]+\\.)+[a-zA-Z]{2,}))$/;
return re.test(String(e).toLowerCase());
}

// no comments, unclear function name
function x(a, b) {
return a + b;
}

// duplicate code
function add(num1, num2) {
return num1 + num2;
}

// deeply nested, hard to read
function checkUser(user) {
if (user) {
if (user.name) {
if (user.name.length > 0) {
if (user.email) {
if (validateEmail(user.email)) {
return true;
} else {
return false;
}
} else {
return false;
}
} else {
return false;
}
} else {
return false;
}
} else {
return false;
}
}

// magic numbers
function calculateDiscount(price) {
if (price > 100) {
return price * 0.1;
} else if (price > 50) {
return price * 0.05;
} else {
return 0;
}
}

// TODO: Need to add proper error handling
// TODO: Need to add JSDoc comments
// TODO: Need to refactor nested if statements
// TODO: Remove duplicate functions
'''

API_JS = '''// API Helper Functions
// Note: This is a mock API for demonstration

const API_BASE = '/api';

// Mock API calls - in real app, these would call actual endpoints
async function apiLogin(username, password) {
    // Simulated delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Mock validation
    if (username === 'admin' && password === 'password') {
        return { success: true, user: { name: username } };
    }
    return { success: false, error: 'Invalid credentials' };
}

async function apiGetTasks() {
    await new Promise(resolve => setTimeout(resolve, 300));
    return { success: true, tasks: [] };
}

async function apiSaveTask(task) {
    await new Promise(resolve => setTimeout(resolve, 200));
    return { success: true, task };
}

async function apiDeleteTask(id) {
    await new Promise(resolve => setTimeout(resolve, 200));
    return { success: true };
}
'''

README_MD = '''# TaskMaster - Todo Application

A simple task management application.

## Getting Started

<!-- BUG #4 (README): Missing installation steps -->

TODO: Add installation instructions

## Features

- Add tasks
- Mark tasks complete
- Filter tasks
- Delete tasks

## Known Issues

This project has several bugs that need to be fixed. Check the issue tracker for details.

## Contributing

Please fix the bugs listed in the issue tracker.
'''

# ============== END PROJECT TEMPLATE FILES ==============

@router.post("/generate-repo")
async def generate_repository(request: RepoRequest, user_id: int, db: AsyncSession = Depends(get_db)):
    # Fetch user to get token
    from sqlalchemy.future import select
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.access_token:
        raise HTTPException(status_code=401, detail="User not authenticated with GitHub")

    import httpx
    async with httpx.AsyncClient() as client:
        # Create Repo
        response = await client.post(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"token {user.access_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={
                "name": request.repo_name,
                "private": False,
                "description": "TaskMaster Todo App - Simulation Repository for The New Hire",
                "auto_init": True
            }
        )
        
        if response.status_code not in [200, 201]:
            if response.status_code == 422:
                return {"message": "Repository already exists", "repo_url": f"https://github.com/{user.username}/{request.repo_name}"}
            print(f"GitHub Error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to create repository")
            
        data = response.json()
        repo_url = data["html_url"]
        
        # Helper function to push file to GitHub
        async def push_file(path: str, content: str, message: str):
            encoded = base64.b64encode(content.encode()).decode()
            await client.put(
                f"https://api.github.com/repos/{user.username}/{request.repo_name}/contents/{path}",
                headers={
                    "Authorization": f"token {user.access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "message": message,
                    "content": encoded
                }
            )
        
        # Push all project files
        await push_file("index.html", INDEX_HTML, "Add main HTML file")
        await push_file("styles.css", STYLES_CSS, "Add CSS styles")
        await push_file("app.js", APP_JS, "Add main application logic")
        await push_file("utils.js", UTILS_JS, "Add utility functions")
        await push_file("api.js", API_JS, "Add API helper functions")
        await push_file("README.md", README_MD, "Update README")
        
        # Push CI/CD workflow
        ci_content = """name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint JavaScript
        run: echo "Linting JavaScript files..."
      - name: Run tests
        run: echo "Running tests..."
"""
        await push_file(".github/workflows/ci.yml", ci_content, "Add CI/CD workflow")
        
        # SEED 12 TICKETS FOR 7-DAY SPRINT
        now = datetime.now()
        seed_tickets = [
            # Day 1 - Critical bugs
            Ticket(
                title="Fix Login Error Handling", 
                description="The login form crashes with a 500 error when username is empty. Add proper validation and error display in app.js handleLogin function.", 
                type="bug",
                priority=TicketPriority.CRITICAL,
                story_points=3,
                status=TicketStatus.TODO,
                assignee_id=user.id,
                due_date=now + timedelta(days=1)
            ),
            Ticket(
                title="Implement Dark Mode", 
                description="Add dark mode toggle and styles. The CSS file has placeholder comments for dark mode that need to be implemented.", 
                type="story",
                priority=TicketPriority.MEDIUM,
                story_points=5,
                status=TicketStatus.BACKLOG,
                assignee_id=user.id,
                due_date=now + timedelta(days=5)
            ),
            # Day 2
            Ticket(
                title="Add Task Form Validation", 
                description="The add task form accepts empty tasks. Add validation to prevent empty task submission in handleAddTask function.", 
                type="bug",
                priority=TicketPriority.HIGH,
                story_points=2,
                status=TicketStatus.TODO,
                assignee_id=user.id,
                due_date=now + timedelta(days=2)
            ),
            Ticket(
                title="Fix Form Not Clearing After Submit", 
                description="After adding a task, the form inputs don't reset. Uncomment and fix the form clearing code in handleAddTask.", 
                type="bug",
                priority=TicketPriority.MEDIUM,
                story_points=1,
                status=TicketStatus.TODO,
                assignee_id=user.id,
                due_date=now + timedelta(days=2)
            ),
            # Day 3
            Ticket(
                title="Fix Delete Task Logic", 
                description="Delete task uses wrong comparison operator. Change from != to !== for strict equality in deleteTask function.", 
                type="bug",
                priority=TicketPriority.HIGH,
                story_points=1,
                status=TicketStatus.TODO,
                assignee_id=user.id,
                due_date=now + timedelta(days=3)
            ),
            Ticket(
                title="Implement Logout Functionality", 
                description="Logout button is broken - handler logs to console but doesn't actually log out. Implement handleLogout function properly.", 
                type="bug",
                priority=TicketPriority.HIGH,
                story_points=2,
                status=TicketStatus.TODO,
                assignee_id=user.id,
                due_date=now + timedelta(days=3)
            ),
            # Day 4
            Ticket(
                title="Fix Task Filter Not Working", 
                description="Filter buttons update visual state but don't re-render the task list. Add renderTasks() call in handleFilter function.", 
                type="bug",
                priority=TicketPriority.MEDIUM,
                story_points=2,
                status=TicketStatus.BACKLOG,
                assignee_id=user.id,
                due_date=now + timedelta(days=4)
            ),
            Ticket(
                title="Fix Task Count Grammar", 
                description="Task count shows '1 tasks' instead of '1 task'. Fix pluralization in updateTaskCount function.", 
                type="bug",
                priority=TicketPriority.LOW,
                story_points=1,
                status=TicketStatus.BACKLOG,
                assignee_id=user.id,
                due_date=now + timedelta(days=4)
            ),
            # Day 5
            Ticket(
                title="Style Delete Button", 
                description="Delete button has no styles - looks ugly. Add proper styles for .delete-btn in styles.css.", 
                type="task",
                priority=TicketPriority.LOW,
                story_points=1,
                status=TicketStatus.BACKLOG,
                assignee_id=user.id,
                due_date=now + timedelta(days=5)
            ),
            Ticket(
                title="Add Task Item Hover States", 
                description="Task items need hover states for better UX. Add :hover styles for .task-item in CSS.", 
                type="task",
                priority=TicketPriority.LOW,
                story_points=1,
                status=TicketStatus.BACKLOG,
                assignee_id=user.id,
                due_date=now + timedelta(days=5)
            ),
            # Day 6
            Ticket(
                title="Fix Clear Completed Logic", 
                description="Clear completed button has inverted logic - it removes active tasks and keeps completed ones. Fix the filter in clearCompletedTasks.", 
                type="bug",
                priority=TicketPriority.HIGH,
                story_points=1,
                status=TicketStatus.BACKLOG,
                assignee_id=user.id,
                due_date=now + timedelta(days=6)
            ),
            # Day 7
            Ticket(
                title="Fix LocalStorage Key Mismatch", 
                description="Tasks don't persist across refreshes because saveTasks and loadTasks use different localStorage keys. Make them consistent.", 
                type="bug",
                priority=TicketPriority.CRITICAL,
                story_points=2,
                status=TicketStatus.BACKLOG,
                assignee_id=user.id,
                due_date=now + timedelta(days=7)
            ),
        ]
        
        db.add_all(seed_tickets)
        await db.commit()
        
        return {"message": "Repository and 12 tickets created successfully!", "repo_url": repo_url}

@router.get("/checklist")
async def get_onboarding_checklist(user_id: int):
    # Static checklist for now
    return [
        {"id": 1, "task": "Clone the repository", "completed": False, "xp": 50},
        {"id": 2, "task": "Open the project in your editor", "completed": False, "xp": 25},
        {"id": 3, "task": "Open index.html in browser", "completed": False, "xp": 25},
        {"id": 4, "task": "Find and fix your first bug", "completed": False, "xp": 100},
        {"id": 5, "task": "Commit your fix", "completed": False, "xp": 50},
        {"id": 6, "task": "Complete your first Standup", "completed": False, "xp": 50},
        {"id": 7, "task": "Submit a Pull Request", "completed": False, "xp": 100},
    ]

