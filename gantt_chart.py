import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit as st

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
        # Add subtasks if they exist
        if 'Subtasks' in task and task['Subtasks']:
            for subtask in task['Subtasks']:
                flat_tasks.append({
                    'Task': f"    └ {subtask['Task']}", # Indent subtasks
                    'Start': subtask['Start'],
                    'End': subtask['End'],
                    'Assigned To': subtask['Assigned To'],
                    'Is Subtask': True
                })
    
    # Convert to DataFrame
    df = pd.DataFrame(flat_tasks)
    
    # Convert string dates to datetime
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End']) + timedelta(hours=1)
    
    # Prepare data for plotly figure factory
    ff_data = []
    for _, task in df.iterrows():
        ff_data.append(dict(
            Task=task['Task'],
            Start=task['Start'],
            Finish=task['End'],
            Resource=task['Assigned To'],
            Description=f"{task['Task']} ({task['Assigned To']})<br>"
                       f"Start: {task['Start'].strftime('%Y-%m-%d %H:%M')}<br>"
                       f"End: {task['End'].strftime('%Y-%m-%d %H:%M')}"
        ))
    
    colors = {
        'Christian': 'rgb(46, 137, 205)',
        'Jordan': 'rgb(114, 44, 121)',
        'Crew': 'rgb(198, 47, 105)'
    }
    
    # Create the chart
    fig = ff.create_gantt(
        ff_data,
        colors=colors,
        index_col='Resource',
        show_colorbar=True,
        showgrid_x=True,
        showgrid_y=True,
        height=600,
        width=None,
        title='Project Timeline',
        bar_width=0.3,
        show_hover_fill=True,
        group_tasks=False
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Project Timeline',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Date/Time',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        margin=dict(l=200, r=50, t=50, b=50),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            tickformat='%Y-%m-%d %H:%M',
            tickangle=45,
            tickmode='linear',
            dtick='H4'
        ),
        yaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,
            gridwidth=2,
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
        st.write(f"**Assigned:** {task['Assigned To']}")
        st.write(f"**Start:** {task['Start'].split(' ')[1]}")
        st.write(f"**End:** {task['End'].split(' ')[1]}")
        
        # Display subtasks if they exist
        if 'Subtasks' in task and task['Subtasks']:
            st.write("**Subtasks:**")
            for j, subtask in enumerate(task['Subtasks']):
                # Create a container for each subtask
                st.markdown("---")
                st.markdown(f"└ **{subtask['Task']}**")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Assigned:** {subtask['Assigned To']}")
                    st.write(f"**Start:** {subtask['Start'].split(' ')[1]}")
                    st.write(f"**End:** {subtask['End'].split(' ')[1]}")
                with col2:
                    if st.button("Delete", key=f"delete_subtask_{i}_{j}"):
                        st.session_state.tasks[i]['Subtasks'].pop(j)
                        st.rerun()
        
        # Task controls
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Add Subtask", key=f"show_subtask_form_{i}"):
                st.session_state[f"show_subtask_form_{i}"] = True
        with col2:
            if st.button("Edit", key=f"edit_{i}"):
                st.session_state.editing = i
        with col3:
            if st.button("Delete", key=f"delete_{i}"):
                st.session_state.tasks.pop(i)
                st.rerun()
        
        # Show subtask form if button was clicked
        if st.session_state.get(f"show_subtask_form_{i}", False):
            add_subtask_form(i)

def main():
    st.set_page_config(layout="wide")
    st.title("Project Timeline Manager")
    
    # Initialize session state for tasks with default data
    if 'tasks' not in st.session_state:
        st.session_state.tasks = [
            {
                "Task": "Mark flagstone pathway locations",
                "Assigned To": "Christian",
                "Start": "2025-01-06 08:00",
                "End": "2025-01-06 10:00",
                "Subtasks": [
                    {
                        "Task": "Measure and mark corners",
                        "Assigned To": "Christian",
                        "Start": "2025-01-06 08:00",
                        "End": "2025-01-06 09:00"
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
    
    if st.session_state.tasks:
        # Create and display Gantt chart at the top
        fig = create_gantt_chart(st.session_state.tasks)
        st.plotly_chart(fig, use_container_width=True, height=600)
        
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