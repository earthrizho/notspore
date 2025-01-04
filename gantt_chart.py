import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit as st
from material_management import display_materials_dashboard

def create_gantt_chart(tasks):
    """
    Create an interactive Gantt chart from a list of task dictionaries with subtasks.
    """
    # Flatten tasks and subtasks into a single list for the chart
    flat_tasks = []
    for task in tasks:
        # Add main task
        flat_tasks.append({
            'Task': task['Task'],
            'Start': task['Start'],
            'End': task['End'],
            'Assigned To': task['Assigned To'],
            'Is Subtask': False
        })
        # Add subtasks indented and with a visual connector
        if 'Subtasks' in task and task['Subtasks']:
            for subtask in task['Subtasks']:
                flat_tasks.append({
                    'Task': f"     ↳ {subtask['Task']}", # Better visual hierarchy
                    'Start': subtask['Start'],
                    'End': subtask['End'],
                    'Assigned To': subtask['Assigned To'],
                    'Is Subtask': True
                })
    
    # Convert to DataFrame and sort by start time and assignment
    df = pd.DataFrame(flat_tasks)
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End']) + timedelta(hours=1)
    df = df.sort_values(['Start', 'Assigned To'])
    
    # Prepare data with better tooltips
    ff_data = []
    for _, task in df.iterrows():
        ff_data.append(dict(
            Task=task['Task'],
            Start=task['Start'],
            Finish=task['End'],
            Resource=task['Assigned To'],
            Description=(
                f"<b>{task['Task']}</b><br>"
                f"<b>Assigned to:</b> {task['Assigned To']}<br>"
                f"<b>Start:</b> {task['Start'].strftime('%I:%M %p')}<br>"  # 12-hour format
                f"<b>End:</b> {task['End'].strftime('%I:%M %p')}<br>"
                f"<b>Duration:</b> {(task['End'] - task['Start']).total_seconds() / 3600:.1f} hours"
            )
        ))
    
    # Use more intuitive colors
    colors = {
        'Christian': 'rgb(53, 138, 192)',  # Softer blue
        'Jordan': 'rgb(122, 73, 163)',     # Softer purple
        'Crew': 'rgb(191, 87, 0)'          # Orange-brown
    }
    
    # Create the chart with improved settings
    fig = ff.create_gantt(
        ff_data,
        colors=colors,
        index_col='Resource',
        show_colorbar=True,
        showgrid_x=True,
        showgrid_y=True,
        height=600,
        width=None,
        bar_width=0.4,        # Wider bars
        show_hover_fill=True,
        group_tasks=False
    )
    
    # Update layout for better readability
    fig.update_layout(
        title={
            'text': 'Project Timeline',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'family': 'Arial'}
        },
        xaxis_title='Time',
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial",
            bordercolor='#666666'
        ),
        margin=dict(l=200, r=50, t=80, b=50),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            bordercolor='#666666',
            borderwidth=1
        ),
        xaxis=dict(
            tickformat='%I:%M %p',     # 12-hour time format
            tickangle=30,              # More readable angle
            tickmode='linear',
            dtick='H2',               # Show every 2 hours
            linecolor='#666666'       # Darker axis line
        ),
        yaxis=dict(
            title=None,
            showgrid=True,
            ticktext=df['Task'].tolist(),  # Use task names for y-axis labels
            tickvals=list(range(len(df))),  # Position of labels
            tickmode='array',
            linecolor='#666666'
        )
    )
    
    return fig

def add_subtask_form(task_idx):
    """Display form for adding subtasks"""
    st.subheader("Add Subtask")
    subtask_name = st.text_input("Subtask Name", key=f"subtask_name_{task_idx}")
    assigned_to = st.selectbox("Assigned To", ["Christian", "Jordan", "Crew"], key=f"subtask_assigned_{task_idx}")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", key=f"subtask_start_date_{task_idx}")
        start_time = st.time_input("Start Time", key=f"subtask_start_time_{task_idx}")
    with col2:
        end_date = st.date_input("End Date", key=f"subtask_end_date_{task_idx}")
        end_time = st.time_input("End Time", key=f"subtask_end_time_{task_idx}")
    
    if st.button("Add Subtask", key=f"add_subtask_{task_idx}"):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        
        new_subtask = {
            "Task": subtask_name,
            "Assigned To": assigned_to,
            "Start": start_datetime.strftime("%Y-%m-%d %H:%M"),
            "End": end_datetime.strftime("%Y-%m-%d %H:%M")
        }
        
        if 'Subtasks' not in st.session_state.tasks[task_idx]:
            st.session_state.tasks[task_idx]['Subtasks'] = []
        
        st.session_state.tasks[task_idx]['Subtasks'].append(new_subtask)
        st.success("Subtask added successfully!")
        st.rerun()

def display_task_with_subtasks(task, i, day_tasks):
    """Display a task and its subtasks in the UI"""
    with st.expander(f"{task['Task']}"):
        # Main task info in single line
        col1, col2, col3, col4, col5 = st.columns([6, 1, 1, 1, 1])
        with col1:
            st.write(f"**{task['Assigned To']}** • {task['Start'].split(' ')[1]} - {task['End'].split(' ')[1]}")
        with col2:
            completed = task.get('Completed', False)
            if st.button("✓" if completed else "○", 
                        key=f"complete_{i}",
                        help="Toggle completion",
                        type="secondary",
                        use_container_width=True):
                st.session_state.tasks[i]['Completed'] = not completed
                st.rerun()
        with col3:
            if st.button("ⓘ", key=f"details_{i}", help="Show details", type="secondary", use_container_width=True):
                st.session_state[f"show_details_{i}"] = not st.session_state.get(f"show_details_{i}", False)
        with col4:
            if st.button("+", key=f"show_subtask_form_{i}", help="Add subtask", type="secondary", use_container_width=True):
                st.session_state[f"show_subtask_form_{i}"] = True
        with col5:
            if st.button("×", key=f"delete_{i}", help="Delete task", type="secondary", use_container_width=True):
                st.session_state.tasks.pop(i)
                st.rerun()
        
        # Show full details if details button was clicked
        if st.session_state.get(f"show_details_{i}", False):
            with st.container():
                st.caption(f"""
                Start: {task['Start']}
                End: {task['End']}
                Assigned To: {task['Assigned To']}
                """)
        
        # Display subtasks if they exist
        if 'Subtasks' in task and task['Subtasks']:
            st.caption("Subtasks:")
            for j, subtask in enumerate(task['Subtasks']):
                # Create a more compact subtask display
                with st.container():
                    col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
                    with col1:
                        st.write(f"└ {subtask['Task']}")
                    with col2:
                        st.write(f"{subtask['Assigned To'][0]}")  # Just first initial
                    with col3:
                        if st.button("ⓘ", key=f"info_subtask_{i}_{j}", help="Show details", type="secondary", use_container_width=True):
                            with st.container():
                                st.caption(f"""
                                {subtask['Task']}
                                Assigned to: {subtask['Assigned To']}
                                Start: {subtask['Start']}
                                End: {subtask['End']}
                                """)
                    with col4:
                        if st.button("×", key=f"delete_subtask_{i}_{j}", help="Delete subtask", type="secondary", use_container_width=True):
                            st.session_state.tasks[i]['Subtasks'].pop(j)
                            st.rerun()
        
        # Show subtask form if button was clicked
        if st.session_state.get(f"show_subtask_form_{i}", False):
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    subtask_name = st.text_input("Name", key=f"subtask_name_{i}")
                    assigned_to = st.selectbox("Assign to", ["Christian", "Jordan", "Crew"], key=f"subtask_assigned_{i}")
                with col2:
                    start_time = st.time_input("Start", key=f"subtask_start_time_{i}")
                    end_time = st.time_input("End", key=f"subtask_end_time_{i}")
                
                if st.button("Add", key=f"add_subtask_{i}"):
                    start_date = datetime.strptime(task['Start'], "%Y-%m-%d %H:%M").date()
                    start_datetime = datetime.combine(start_date, start_time)
                    end_datetime = datetime.combine(start_date, end_time)
                    
                    new_subtask = {
                        "Task": subtask_name,
                        "Assigned To": assigned_to,
                        "Start": start_datetime.strftime("%Y-%m-%d %H:%M"),
                        "End": end_datetime.strftime("%Y-%m-%d %H:%M")
                    }
                    
                    if 'Subtasks' not in st.session_state.tasks[i]:
                        st.session_state.tasks[i]['Subtasks'] = []
                    
                    st.session_state.tasks[i]['Subtasks'].append(new_subtask)
                    st.session_state[f"show_subtask_form_{i}"] = False
                    st.rerun()

def create_kpi_dashboard(tasks):
    """Create KPI dashboard showing task completion status"""
    
    # Calculate overall metrics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.get('Completed', False))
    
    # Calculate team metrics
    team_metrics = {}
    for task in tasks:
        assignee = task['Assigned To']
        if assignee not in team_metrics:
            team_metrics[assignee] = {'total': 0, 'completed': 0}
        team_metrics[assignee]['total'] += 1
        if task.get('Completed', False):
            team_metrics[assignee]['completed'] += 1
    
    # Calculate completion percentage
    task_completion = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Create two columns: one for metrics, one for progress bar
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create single row of columns for all metrics
        metric_cols = st.columns(4)
        
        # Overall completion in first column
        metric_cols[0].metric(
            "Overall Completion",
            f"{task_completion:.1f}%",
            f"{completed_tasks} of {total_tasks} tasks"
        )
        
        # Team member metrics in remaining columns
        for idx, (member, metrics) in enumerate(team_metrics.items()):
            completion_rate = (metrics['completed'] / metrics['total'] * 100) if metrics['total'] > 0 else 0
            metric_cols[idx + 1].metric(
                member,
                f"{completion_rate:.1f}%",
                f"{metrics['completed']} of {metrics['total']} tasks"
            )
    
    with col2:
        # Create progress bar with custom styling
        st.markdown("""
            <style>
            .stProgress > div > div > div > div {
                background-color: rgb(14, 167, 97);
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Overall progress bar
        st.markdown("### Project Progress")
        st.progress(task_completion / 100)
    
    st.markdown("---")

def main():
    st.set_page_config(layout="wide")
    
    # Initialize test_date if not exists
    if 'test_date' not in st.session_state:
        st.session_state.test_date = datetime(2025, 1, 6)  # Start date of project
    
    # Add date controls in sidebar
    with st.sidebar:
        st.subheader("Test Date Controls")
        col1, col2 = st.columns(2)
        with col1:
            new_date = st.date_input("Date", 
                                   st.session_state.test_date.date(),
                                   key="test_date_picker")
        with col2:
            new_time = st.time_input("Time", 
                                   st.session_state.test_date.time(),
                                   key="test_time_picker")
        
        if st.button("Update Test Date", key="update_test_date"):
            st.session_state.test_date = datetime.combine(new_date, new_time)
            st.rerun()
        
        # Display current test date
        st.caption(f"Current test date: {st.session_state.test_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Add custom CSS to remove button backgrounds and padding
    st.markdown("""
        <style>
        /* Override Streamlit's default button styles */
        div[data-testid="stHorizontalBlock"] button {
            background: none;
            border: none;
            padding: 0;
            margin: 0;
            box-shadow: none;
            transform: scale(0.8);  /* Reduce size by 20% */
        }
        
        /* Target button containers */
        div[class*="stButton"] {
            background: none;
            border: none;
            padding: 0;
            margin: 0;
            box-shadow: none;
            transform: scale(0.8);  /* Reduce size by 20% */
        }
        
        /* Target the button element itself */
        button[kind="secondary"] {
            background: none !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
            font-size: 0.8em !important;  /* Reduce font size by 20% */
            transform: scale(0.8);  /* Reduce size by 20% */
            transform-origin: center;  /* Scale from center */
        }
        
        /* Remove padding from columns */
        div[data-testid="column"] {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Compact containers */
        div[data-testid="stExpander"] {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        .stMarkdown {
            padding: 0 !important;
            margin: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Project Timeline Manager")
    
    # Initialize session state for tasks with default data
    if 'tasks' not in st.session_state:
        st.session_state.tasks = [
            {
                "Task": "Mark flagstone pathway locations",
                "Assigned To": "Christian",
                "Start": "2025-01-06 08:00",
                "End": "2025-01-06 10:00",
                "Completed": False,  # Add completion status
                "Subtasks": [
                    {
                        "Task": "Measure and mark corners",
                        "Assigned To": "Christian",
                        "Start": "2025-01-06 08:00",
                        "End": "2025-01-06 09:00",
                        "Completed": False
                    },
                    {
                        "Task": "Place temporary markers",
                        "Assigned To": "Christian",
                        "Start": "2025-01-06 09:00",
                        "End": "2025-01-06 10:00"
                    }
                ]
            },
            {"Task": "Install steel edging (pathway & greenhouse)", "Assigned To": "Christian", "Start": "2025-01-06 10:00", "End": "2025-01-06 12:00", "Subtasks": []},
            {"Task": "Complete bog filter installation", "Assigned To": "Christian", "Start": "2025-01-06 13:00", "End": "2025-01-06 15:00", "Subtasks": []},
            {"Task": "Handle greenhouse and deck fixes/finishing", "Assigned To": "Christian", "Start": "2025-01-06 15:00", "End": "2025-01-06 17:00", "Subtasks": []},
            {"Task": "Gather trashcan pad leveling input", "Assigned To": "Christian", "Start": "2025-01-06 09:00", "End": "2025-01-06 10:00", "Subtasks": []},
            {"Task": "Flagstone pathway installation", "Assigned To": "Crew", "Start": "2025-01-06 08:00", "End": "2025-01-07 16:00", "Subtasks": []},
            {"Task": "Plant area around the pond", "Assigned To": "Crew", "Start": "2025-01-06 08:00", "End": "2025-01-07 16:00", "Subtasks": []},
            {"Task": "Tree planting (Persimmon, Mexican Plum)", "Assigned To": "Crew", "Start": "2025-01-06 13:00", "End": "2025-01-07 15:00", "Subtasks": []},
            {"Task": "Oversee driveway demo", "Assigned To": "Christian", "Start": "2025-01-07 08:00", "End": "2025-01-07 12:00", "Subtasks": []},
            {"Task": "Install steel edging (back of pergola bed)", "Assigned To": "Christian", "Start": "2025-01-07 13:00", "End": "2025-01-07 17:00", "Subtasks": []},
            {"Task": "Supervise permeable paver installation", "Assigned To": "Jordan", "Start": "2025-01-08 08:00", "End": "2025-01-09 17:00", "Subtasks": []},
            {"Task": "Oversee centerpiece planting (pergola)", "Assigned To": "Jordan", "Start": "2025-01-08 09:00", "End": "2025-01-08 12:00", "Subtasks": []},
            {"Task": "Flagstone pathway edging & finishing", "Assigned To": "Jordan", "Start": "2025-01-08 13:00", "End": "2025-01-08 17:00", "Subtasks": []},
            {"Task": "Trashcan pad leveling", "Assigned To": "Jordan", "Start": "2025-01-09 08:00", "End": "2025-01-10 12:00", "Subtasks": []},
            {"Task": "Final walkthrough & punch list", "Assigned To": "Jordan", "Start": "2025-01-10 13:00", "End": "2025-01-10 17:00", "Subtasks": []},
            {"Task": "Crew picks up 1 pallet of flagstone from Whittlesey", "Assigned To": "Crew", "Start": "2025-01-06 07:00", "End": "2025-01-06 09:00", "Subtasks": []},
            {"Task": "Material pickup: plants, soil, mulch", "Assigned To": "Crew", "Start": "2025-01-06 07:00", "End": "2025-01-06 09:00", "Subtasks": []},
            {"Task": "Material pickup: wood & stain for deck", "Assigned To": "Crew", "Start": "2025-01-07 07:00", "End": "2025-01-07 09:00", "Subtasks": []}
        ]
    
    # Add tabs for different views
    tab1, tab2 = st.tabs(["Timeline", "Materials"])
    
    with tab1:
        if st.session_state.tasks:
            # Replace Gantt chart with KPI dashboard
            create_kpi_dashboard(st.session_state.tasks)
            
            # Add material preview
            if 'materials' in st.session_state and st.session_state.materials:
                with st.expander("Materials Needed Today", expanded=True):
                    # Use test date instead of now()
                    today = st.session_state.test_date.date()
                    materials_data = [{
                        'Material': m.name,
                        'Quantity': f"{m.quantity} {m.unit}",
                        'Task': m.task,
                        'Status': m.status,
                        'Supplier': m.supplier,
                        'Delivery': m.delivery_method
                    } for m in st.session_state.materials 
                      if m.needed_by.date() == today]
                    
                    if materials_data:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown("**Needed:**")
                            needed = [m for m in materials_data if m['Status'] == 'Needed']
                            for mat in needed:
                                st.markdown(f"• {mat['Material']} ({mat['Quantity']})")
                                if mat['Supplier']:
                                    st.markdown(f"  🏪 {mat['Supplier']} - {mat['Delivery']}")
                        
                        with col2:
                            st.markdown("**Ordered:**")
                            ordered = [m for m in materials_data if m['Status'] == 'Ordered']
                            for mat in ordered:
                                st.markdown(f"• {mat['Material']} ({mat['Quantity']})")
                        
                        with col3:
                            st.markdown("**Onsite:**")
                            onsite = [m for m in materials_data if m['Status'] == 'Onsite']
                            for mat in onsite:
                                st.markdown(f"• {mat['Material']} ({mat['Quantity']})")

                        with col4:
                            st.markdown("**On Hand:**")
                            on_hand = [m for m in materials_data if m['Status'] == 'On Hand']
                            for mat in on_hand:
                                st.markdown(f"• {mat['Material']} ({mat['Quantity']})")
                    else:
                        st.markdown("No materials needed today")
            
            st.markdown("---")
            
            # Existing tasks section
            st.header("Existing Tasks")
            
            # Convert tasks to DataFrame for easier grouping
            df = pd.DataFrame(st.session_state.tasks)
            df['Date'] = pd.to_datetime(df['Start']).dt.date
            
            # Get unique dates and sort them
            dates = sorted(df['Date'].unique())
            
            # Create columns for each date
            cols = st.columns(len(dates))
            
            # Group tasks by date in horizontal columns
            for idx, date in enumerate(dates):
                with cols[idx]:
                    # Get tasks for this date
                    day_tasks = df[df['Date'] == date]
                    
                    # Get unique workers for this day
                    workers = sorted(day_tasks['Assigned To'].unique())
                    
                    # Create header with date and workers
                    header = f"### {date.strftime('%A, %d')} \n**Team:** {', '.join(workers)}"
                    st.markdown(header)
                    
                    # Show daily progress if it's today
                    if date == st.session_state.test_date.date():
                        completed = sum(1 for _, task in day_tasks.iterrows() if task.get('Completed', False))
                        total = len(day_tasks)
                        if total > 0:
                            completion_rate = completed / total * 100
                            st.markdown(f"**Today's Progress:** {completion_rate:.1f}%")
                            st.progress(completion_rate / 100)
                    
                    # Display tasks for this day
                    for i, task in day_tasks.iterrows():
                        display_task_with_subtasks(task, i, day_tasks)
            
            # Export tasks
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Export Tasks"):
                    df = pd.DataFrame(st.session_state.tasks)
                    st.download_button(
                        "Download as CSV",
                        df.to_csv(index=False).encode('utf-8'),
                        "project_tasks.csv",
                        "text/csv",
                        key='download-csv'
                    )
    
    with tab2:
        display_materials_dashboard()
    
    # Add new task form at the bottom
    st.markdown("---")
    st.header("Add New Task")
    col1, col2 = st.columns(2)
    
    with col1:
        task_name = st.text_input("Task Name")
        assigned_to = st.selectbox("Assigned To", ["Christian", "Jordan", "Crew"])
        
    with col2:
        start_date = st.date_input("Start Date")
        start_time = st.time_input("Start Time")
        end_date = st.date_input("End Date")
        end_time = st.time_input("End Time")
    
    if st.button("Add Task"):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        
        new_task = {
            "Task": task_name,
            "Assigned To": assigned_to,
            "Start": start_datetime.strftime("%Y-%m-%d %H:%M"),
            "End": end_datetime.strftime("%Y-%m-%d %H:%M")
        }
        new_task['Subtasks'] = []
        st.session_state.tasks.append(new_task)
        st.success("Task added successfully!")

if __name__ == "__main__":
    main() 