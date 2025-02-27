import bpy
from bpy.types import Panel, Operator
from bpy.props import EnumProperty, BoolProperty, CollectionProperty, StringProperty

# Store the copied modifiers
copied_modifiers = []

# Register the addon in Blender 4.0 and above
bl_info = {
    "name": "Modifier Copy Paste Plus",
    "author": "Your Name",
    "version": (1, 2),
    "blender": (4, 1, 0),
    "location": "3D View > Sidebar > Modifier Copy Paste",
    "description": "Copy and paste specific modifier settings with multi-copy support",
    "category": "Object",
}

# Helper function to handle various property types for copying
def get_property_value(obj, prop_name):
    value = getattr(obj, prop_name)
    
    # Handle different property types
    if hasattr(value, "to_list"):
        return value.to_list()  # For vectors, colors, etc.
    elif hasattr(value, "copy"):
        try:
            return value.copy()  # For collections that can be copied
        except:
            return str(value)  # Fallback to string representation
    
    # Special handling for pointers to other data
    if hasattr(value, "name") and hasattr(value, "id_data"):
        # Store name and data type for later lookup
        data_type = type(value).__name__
        return {"__dataref__": True, "name": value.name, "type": data_type}
    
    return value

# Helper function to set property value with type handling
def set_property_value(obj, prop_name, value):
    # Skip known problematic properties
    if prop_name in {"is_override_data", "rna_type", "active"}:
        return
    
    # Handle data references
    if isinstance(value, dict) and value.get("__dataref__"):
        data_type = value.get("type")
        name = value.get("name")
        
        # Try to find the referenced data
        if data_type == "Object" and name in bpy.data.objects:
            setattr(obj, prop_name, bpy.data.objects[name])
        elif data_type == "VertexGroup" and hasattr(obj.id_data, "vertex_groups") and name in obj.id_data.vertex_groups:
            setattr(obj, prop_name, obj.id_data.vertex_groups[name])
        # Add more types as needed
        
        return
    
    # Handle other types
    try:
        if hasattr(getattr(obj, prop_name), "from_list") and isinstance(value, list):
            getattr(obj, prop_name).from_list(value)
        else:
            setattr(obj, prop_name, value)
    except (AttributeError, TypeError):
        # Silently ignore properties that can't be set
        pass

# Property class for the modifier checkboxes
class ModifierItem(bpy.types.PropertyGroup):
    name: StringProperty()
    enabled: BoolProperty(default=True)

class OBJECT_OT_copy_multiple_modifiers(Operator):
    """Copy multiple modifiers from the selected object"""
    bl_idname = "object.copy_multiple_modifiers"
    bl_label = "Copy Multiple Modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(context.active_object.modifiers) > 0
    
    def invoke(self, context, event):
        # Create the modifiers list
        wm = context.window_manager
        if not hasattr(wm, "modifier_list"):
            bpy.types.WindowManager.modifier_list = CollectionProperty(type=ModifierItem)
        
        # Clear previous entries
        wm.modifier_list.clear()
        
        # Add all modifiers from the active object
        for mod in context.active_object.modifiers:
            item = wm.modifier_list.add()
            item.name = mod.name
            item.enabled = True
        
        # Show dialog to let user select modifiers
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        
        if len(wm.modifier_list) == 0:
            layout.label(text="No modifiers available")
            return
            
        layout.label(text="Select modifiers to copy:")
        
        # Display all modifiers with checkboxes
        for idx, item in enumerate(wm.modifier_list):
            row = layout.row()
            row.prop(item, "enabled", text="")
            mod = context.active_object.modifiers.get(item.name)
            if mod:
                row.label(text=f"{item.name} ({mod.type})")
            else:
                row.label(text=item.name)
    
    def execute(self, context):
        global copied_modifiers
        wm = context.window_manager
        
        # Clear previous copied modifiers
        copied_modifiers = []
        
        # Copy selected modifiers
        for item in wm.modifier_list:
            if item.enabled and item.name in context.active_object.modifiers:
                modifier = context.active_object.modifiers[item.name]
                
                # Store modifier type and properties
                mod_data = {
                    'type': modifier.type,
                    'name': modifier.name,
                    'properties': {},
                    'source_object': context.active_object.name
                }
                
                # Save modifier properties with improved property handling
                for prop in dir(modifier):
                    # Skip built-in attributes and methods
                    if prop.startswith('__') or prop.startswith('bl_') or prop == 'type':
                        continue
                        
                    # Skip known read-only properties
                    if prop in {"is_override_data", "rna_type"}:
                        continue
                        
                    try:
                        # Get property with type handling
                        value = get_property_value(modifier, prop)
                        
                        # Only store non-callable attributes
                        if not callable(value):
                            mod_data['properties'][prop] = value
                    except:
                        pass
                
                copied_modifiers.append(mod_data)
        
        count = len(copied_modifiers)
        if count > 0:
            self.report({'INFO'}, f"Copied {count} modifier{'s' if count > 1 else ''}")
        else:
            self.report({'WARNING'}, "No modifiers were selected for copying")
            
        return {'FINISHED'}

class OBJECT_OT_paste_multiple_modifiers(Operator):
    """Paste all copied modifiers to all selected objects"""
    bl_idname = "object.paste_multiple_modifiers"
    bl_label = "Paste All Modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects and len(copied_modifiers) > 0
    
    def execute(self, context):
        global copied_modifiers
        
        # Check if there are copied modifiers
        if not copied_modifiers:
            self.report({'ERROR'}, "No modifiers have been copied")
            return {'CANCELLED'}
        
        total_count = 0
        affected_objects = 0
        
        # Apply modifiers to all selected objects
        for obj in context.selected_objects:
            # Skip non-mesh objects or other unsupported types if needed
            if obj.type not in {'MESH', 'CURVE', 'LATTICE', 'SURFACE', 'FONT', 'META'}:
                continue
                
            count = 0
            for mod_data in copied_modifiers:
                # Add the same type of modifier
                try:
                    new_modifier = obj.modifiers.new(
                        name=mod_data['name'],
                        type=mod_data['type']
                    )
                    
                    # Set modifier properties with improved handling
                    for prop, value in mod_data['properties'].items():
                        try:
                            set_property_value(new_modifier, prop, value)
                        except:
                            pass
                    
                    count += 1
                except:
                    self.report({'WARNING'}, f"Failed to paste modifier: {mod_data['name']} to {obj.name}")
            
            if count > 0:
                affected_objects += 1
                total_count += count
        
        if affected_objects > 0:
            self.report({'INFO'}, f"Pasted {total_count} modifier{'s' if total_count > 1 else ''} to {affected_objects} object{'s' if affected_objects > 1 else ''}")
        else:
            self.report({'WARNING'}, "No modifiers were pasted to any objects")
            
        return {'FINISHED'}

# Keep the single modifier copy for convenience
class OBJECT_OT_copy_specific_modifier(Operator):
    """Copy a specific modifier from the selected object"""
    bl_idname = "object.copy_specific_modifier"
    bl_label = "Copy Single Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Function for dynamic enum items
    def get_modifier_enum_items(self, context):
        items = []
        if context.active_object:
            for mod in context.active_object.modifiers:
                items.append((mod.name, mod.name, f"Copy modifier {mod.name}"))
        return items if items else [("NONE", "No Modifiers", "This object has no modifiers")]
    
    # Use external function as item source
    modifier_name: EnumProperty(
        name="Select Modifier",
        description="Choose which modifier to copy",
        items=get_modifier_enum_items
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(context.active_object.modifiers) > 0
    
    def invoke(self, context, event):
        # Check if the object has modifiers
        if not context.active_object.modifiers:
            self.report({'ERROR'}, "Selected object has no modifiers")
            return {'CANCELLED'}
        
        # Show dialog to let user select a modifier
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        global copied_modifiers
        
        # Check if a valid modifier is selected
        if self.modifier_name == "NONE":
            self.report({'ERROR'}, "No modifiers available")
            return {'CANCELLED'}
        
        if self.modifier_name not in context.active_object.modifiers:
            self.report({'ERROR'}, "Selected modifier not found")
            return {'CANCELLED'}
        
        modifier = context.active_object.modifiers[self.modifier_name]
        
        # Store modifier type and properties
        mod_data = {
            'type': modifier.type,
            'name': modifier.name,
            'properties': {},
            'source_object': context.active_object.name  # Store source object name
        }
        
        # Save modifier properties with improved property handling
        for prop in dir(modifier):
            # Skip built-in attributes and methods
            if prop.startswith('__') or prop.startswith('bl_') or prop == 'type':
                continue
                
            # Skip known read-only properties
            if prop in {"is_override_data", "rna_type"}:
                continue
                
            try:
                # Get property with type handling
                value = get_property_value(modifier, prop)
                
                # Only store non-callable attributes
                if not callable(value):
                    mod_data['properties'][prop] = value
            except:
                pass
        
        # Store as a single item in the array
        copied_modifiers = [mod_data]
        self.report({'INFO'}, f"Copied modifier: {modifier.name}")
        return {'FINISHED'}

class VIEW3D_PT_modifier_copy_paste(Panel):
    """Modifier Copy Paste Panel"""
    bl_label = "Modifier Copy Paste"
    bl_idname = "VIEW3D_PT_modifier_copy_paste"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Modifier Copy Paste'
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    
    def draw(self, context):
        layout = self.layout
        
        # Copy section
        box = layout.box()
        box.label(text="Copy Modifiers", icon='COPYDOWN')
        col = box.column(align=True)
        col.operator("object.copy_multiple_modifiers", text="Copy Multiple Modifiers", icon='MODIFIER')
        col.operator("object.copy_specific_modifier", text="Copy Single Modifier", icon='MODIFIER')
        
        # Paste section
        box = layout.box()
        box.label(text="Paste Modifiers", icon='PASTEDOWN')
        col = box.column(align=True)
        
        # Show selection count for paste operation
        selected_count = len(context.selected_objects)
        paste_text = f"Paste to {selected_count} Selected Object{'s' if selected_count > 1 else ''}"
        col.operator("object.paste_multiple_modifiers", text=paste_text, icon='MODIFIER')
        
        # Display information about the currently copied modifiers
        if copied_modifiers:
            box = layout.box()
            box.label(text=f"Copied Modifiers: {len(copied_modifiers)}", icon='INFO')
            
            # Show list of copied modifiers
            if len(copied_modifiers) > 0:
                col = box.column(align=True)
                for mod in copied_modifiers:
                    col.label(text=f"• {mod['name']} ({mod['type']})")
                    
            # Warning for specific types
            has_special_types = any(mod['type'] in {'ARMATURE', 'VERTEX_WEIGHT_EDIT', 
                                              'VERTEX_WEIGHT_MIX', 'MIRROR'} 
                               for mod in copied_modifiers)
            if has_special_types:
                box.label(text="Note: Some modifiers may need manual adjustment", icon='ERROR')

def register():
    bpy.utils.register_class(ModifierItem)
    bpy.utils.register_class(OBJECT_OT_copy_multiple_modifiers)
    bpy.utils.register_class(OBJECT_OT_paste_multiple_modifiers)
    bpy.utils.register_class(OBJECT_OT_copy_specific_modifier)
    bpy.utils.register_class(VIEW3D_PT_modifier_copy_paste)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_modifier_copy_paste)
    bpy.utils.unregister_class(OBJECT_OT_copy_specific_modifier)
    bpy.utils.unregister_class(OBJECT_OT_paste_multiple_modifiers)
    bpy.utils.unregister_class(OBJECT_OT_copy_multiple_modifiers)
    bpy.utils.unregister_class(ModifierItem)
    
    # Clean up property
    if hasattr(bpy.types.WindowManager, "modifier_list"):
        del bpy.types.WindowManager.modifier_list

if __name__ == "__main__":
    register()