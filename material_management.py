from datetime import datetime
import streamlit as st
import pandas as pd
from data_storage import save_materials, load_materials

class Material:
    def __init__(self, name, task, needed_by, status="Needed", quantity=1, unit="unit", 
                 delivery_method="Pick-up", responsible_person=None, supplier=None):
        self.name = name
        self.task = task
        self.needed_by = needed_by
        self.status = status
        self.quantity = quantity
        self.unit = unit
        self.delivery_method = delivery_method
        self.responsible_person = responsible_person
        self.supplier = supplier

def display_material_card(material, index, save_state):
    """Display a single material card with edit functionality"""
    with st.container():
        st.write(f"**{material.name}** ({material.quantity} {material.unit})")
        st.caption(f"For: {material.task}")
        st.caption(f"Need by: {material.needed_by.strftime('%Y-%m-%d %H:%M')}")
        st.caption(f"👤 Responsible: {material.responsible_person or 'Unassigned'}")
        st.caption(f"🚚 Supplier: {material.supplier or 'Not specified'}")
        st.caption(f"🚚 {material.delivery_method}")
        
        # Edit button reveals edit form
        if st.button("✏️", key=f"edit_{index}"):
            st.session_state[f"editing_{index}"] = True
            
        if st.session_state.get(f"editing_{index}", False):
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    new_quantity = st.number_input("Quantity", 
                                                 value=material.quantity,
                                                 min_value=1,
                                                 key=f"edit_quantity_{index}")
                    new_responsible = st.selectbox("Responsible Person",
                                                 ["Christian", "Jordan", "Crew", "Unassigned"],
                                                 index=["Christian", "Jordan", "Crew", "Unassigned"].index(
                                                     material.responsible_person or "Unassigned"),
                                                 key=f"edit_responsible_{index}")
                    new_supplier = st.text_input("Supplier",
                                               value=material.supplier or "",
                                               key=f"edit_supplier_{index}")
                with col2:
                    new_delivery = st.selectbox("Delivery Method",
                                              ["Pick-up", "Get Delivered"],
                                              index=0 if material.delivery_method == "Pick-up" else 1,
                                              key=f"edit_delivery_{index}")
                    
                if st.button("Save Changes", key=f"save_edit_{index}"):
                    st.session_state.materials[index].quantity = new_quantity
                    st.session_state.materials[index].responsible_person = new_responsible
                    st.session_state.materials[index].delivery_method = new_delivery
                    st.session_state.materials[index].supplier = new_supplier or None
                    save_state()
                    st.session_state[f"editing_{index}"] = False
                    st.rerun()

def display_materials_dashboard():
    st.header("Materials Management")
    
    # Initialize materials in session state if not exists
    if 'materials' not in st.session_state:
        st.session_state.materials = load_materials()
    
    # Define save function at the start
    def save_state():
        save_materials(st.session_state.materials)
    
    # Add new material form
    with st.expander("Add New Material"):
        col1, col2 = st.columns(2)
        with col1:
            material_name = st.text_input("Material Name")
            task = st.selectbox("Required For Task", 
                              [task['Task'] for task in st.session_state.tasks])
            quantity = st.number_input("Quantity", min_value=1)
            responsible_person = st.selectbox("Responsible Person", 
                                           ["Christian", "Jordan", "Crew", "Unassigned"])
        with col2:
            unit = st.text_input("Unit (e.g., pieces, yards, etc.)")
            status = st.selectbox("Status", ["Needed", "Ordered", "Onsite", "On Hand"])
            delivery_method = st.selectbox("Delivery Method", ["Pick-up", "Get Delivered"])
            supplier = st.text_input("Supplier")
            
        if st.button("Add Material"):
            # Get the task's start date as needed_by date
            task_data = next(t for t in st.session_state.tasks if t['Task'] == task)
            needed_by = datetime.strptime(task_data['Start'], "%Y-%m-%d %H:%M")
            
            new_material = Material(
                name=material_name,
                task=task,
                needed_by=needed_by,
                status=status,
                quantity=quantity,
                unit=unit,
                delivery_method=delivery_method,
                responsible_person=responsible_person if responsible_person != "Unassigned" else None,
                supplier=supplier if supplier else None
            )
            st.session_state.materials.append(new_material)
            save_state()
            st.success("Material added successfully!")
            st.rerun()

    # Display materials table
    if st.session_state.materials:
        # Convert materials to DataFrame
        materials_data = [{
            'Material': m.name,
            'Quantity': f"{m.quantity} {m.unit}",
            'Task': m.task,
            'Needed By': m.needed_by.strftime("%Y-%m-%d %H:%M"),
            'Status': m.status,
            'Index': i
        } for i, m in enumerate(st.session_state.materials)]
        
        df = pd.DataFrame(materials_data)
        
        # Display materials by status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader("Needed")
            needed_df = df[df['Status'] == 'Needed'].copy()
            if not needed_df.empty:
                for _, row in needed_df.iterrows():
                    display_material_card(st.session_state.materials[row['Index']], 
                                       row['Index'], save_state)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("→ Ordered", key=f"order_{row['Index']}"):
                            st.session_state.materials[row['Index']].status = "Ordered"
                            save_state()
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"del_needed_{row['Index']}"):
                            st.session_state.materials.pop(row['Index'])
                            save_state()
                            st.rerun()
        
        with col2:
            st.subheader("Ordered")
            ordered_df = df[df['Status'] == 'Ordered'].copy()
            if not ordered_df.empty:
                for _, row in ordered_df.iterrows():
                    display_material_card(st.session_state.materials[row['Index']], 
                                       row['Index'], save_state)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("→ Onsite", key=f"received_{row['Index']}"):
                            st.session_state.materials[row['Index']].status = "Onsite"
                            save_state()
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"del_ordered_{row['Index']}"):
                            st.session_state.materials.pop(row['Index'])
                            save_state()
                            st.rerun()
        
        with col3:
            st.subheader("Onsite")
            onsite_df = df[df['Status'] == 'Onsite'].copy()
            if not onsite_df.empty:
                for _, row in onsite_df.iterrows():
                    display_material_card(st.session_state.materials[row['Index']], 
                                       row['Index'], save_state)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("→ On Hand", key=f"on_hand_{row['Index']}"):
                            st.session_state.materials[row['Index']].status = "On Hand"
                            save_state()
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"del_onsite_{row['Index']}"):
                            st.session_state.materials.pop(row['Index'])
                            save_state()
                            st.rerun()
        
        with col4:
            st.subheader("On Hand")
            on_hand_df = df[df['Status'] == 'On Hand'].copy()
            if not on_hand_df.empty:
                for _, row in on_hand_df.iterrows():
                    display_material_card(st.session_state.materials[row['Index']], 
                                       row['Index'], save_state)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Delete", key=f"del_on_hand_{row['Index']}"):
                            st.session_state.materials.pop(row['Index'])
                            save_state()
                            st.rerun()

    # Add save functionality after any changes
    def save_state():
        save_materials(st.session_state.materials) 