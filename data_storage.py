import json
from datetime import datetime
import os

class MaterialEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def save_materials(materials):
    """Save materials to JSON file"""
    materials_data = [
        {
            'name': m.name,
            'task': m.task,
            'needed_by': m.needed_by,
            'status': m.status,
            'quantity': m.quantity,
            'unit': m.unit,
            'delivery_method': m.delivery_method,
            'responsible_person': m.responsible_person,
            'supplier': m.supplier
        }
        for m in materials
    ]
    
    with open('data/materials.json', 'w') as f:
        json.dump(materials_data, f, cls=MaterialEncoder, indent=2)

def load_materials():
    """Load materials from JSON file"""
    from material_management import Material
    
    if not os.path.exists('data/materials.json'):
        return []
        
    with open('data/materials.json', 'r') as f:
        materials_data = json.load(f)
    
    return [
        Material(
            name=m['name'],
            task=m['task'],
            needed_by=datetime.fromisoformat(m['needed_by']),
            status=m['status'],
            quantity=m['quantity'],
            unit=m['unit'],
            delivery_method=m.get('delivery_method', 'Pick-up'),
            responsible_person=m.get('responsible_person', None),
            supplier=m.get('supplier', None)
        )
        for m in materials_data
    ] 