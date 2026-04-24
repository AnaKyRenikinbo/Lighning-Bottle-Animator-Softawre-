#!/usr/bin/env python3
"""
Lightning Bottle Animator - Custom Animation Software for Linux Mint
A retro-styled animation and drawing application inspired by classic tools like Deluxe Paint
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFilter
import json
import os
import math
from collections import OrderedDict
from typing import List, Dict, Tuple, Optional
import threading
import time

# Application metadata
APP_NAME = "Lightning Bottle Animator"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Lightning Bottle Studios"

class RetroStyle:
    """2000s web design aesthetic styling"""
    # Classic 2000s color palette
    COLORS = {
        'bg_dark': '#1a1a2e',
        'bg_medium': '#16213e',
        'bg_light': '#0f3460',
        'accent_primary': '#e94560',
        'accent_secondary': '#ff6b6b',
        'accent_highlight': '#feca57',
        'text_primary': '#ffffff',
        'text_secondary': '#a0a0a0',
        'button_face': '#4a4a6a',
        'button_highlight': '#6a6a8a',
        'button_shadow': '#2a2a4a',
        'toolbar_bg': '#2d2d44',
        'canvas_bg': '#0a0a14',
        'grid_color': '#333355',
        'selection': '#00ff88',
    }
    
    # Gradients for that classic 2000s look
    GRADIENTS = {
        'title_bar': ('#3a3a5a', '#2a2a4a'),
        'button': ('#4a4a6a', '#3a3a5a'),
        'panel': ('#2d2d44', '#1d1d34'),
    }
    
    @staticmethod
    def apply_button_style(button):
        """Apply retro button styling"""
        button.configure(
            relief='raised',
            borderwidth=3,
            bg=RetroStyle.COLORS['button_face'],
            fg=RetroStyle.COLORS['text_primary'],
            activebackground=RetroStyle.COLORS['accent_primary'],
            activeforeground=RetroStyle.COLORS['text_primary'],
            font=('MS Sans Serif', 9, 'bold'),
            cursor='hand2'
        )


class Tool:
    """Base tool class"""
    def __init__(self, name, icon_char, description):
        self.name = name
        self.icon_char = icon_char
        self.description = description
        self.cursor = 'crosshair'
    
    def on_press(self, canvas, x, y, button):
        pass
    
    def on_drag(self, canvas, x, y, button):
        pass
    
    def on_release(self, canvas, x, y, button):
        pass


class BrushTool(Tool):
    """Freehand brush tool"""
    def __init__(self):
        super().__init__("Brush", "🖌", "Freehand brush painting")
        self.last_x = None
        self.last_y = None
    
    def on_press(self, canvas, x, y, button):
        self.last_x = x
        self.last_y = y
        color = canvas.get_current_color(button)
        size = canvas.brush_size
        canvas.draw_ellipse(x-size, y-size, x+size, y+size, color)
    
    def on_drag(self, canvas, x, y, button):
        if self.last_x is not None:
            color = canvas.get_current_color(button)
            canvas.draw_line(self.last_x, self.last_y, x, y, color, canvas.brush_size * 2)
        self.last_x = x
        self.last_y = y
    
    def on_release(self, canvas, x, y, button):
        self.last_x = None
        self.last_y = None


class LineTool(Tool):
    """Straight line tool"""
    def __init__(self):
        super().__init__("Line", "/", "Draw straight lines")
        self.start_x = None
        self.start_y = None
    
    def on_press(self, canvas, x, y, button):
        self.start_x = x
        self.start_y = y
    
    def on_release(self, canvas, x, y, button):
        if self.start_x is not None:
            color = canvas.get_current_color(button)
            canvas.draw_line(self.start_x, self.start_y, x, y, color, canvas.brush_size)
        self.start_x = None
        self.start_y = None


class RectangleTool(Tool):
    """Rectangle tool"""
    def __init__(self, filled=False):
        super().__init__("Rectangle", "▢" if not filled else "▣", 
                        "Filled rectangle" if filled else "Rectangle outline")
        self.filled = filled
        self.start_x = None
        self.start_y = None
    
    def on_press(self, canvas, x, y, button):
        self.start_x = x
        self.start_y = y
    
    def on_release(self, canvas, x, y, button):
        if self.start_x is not None:
            color = canvas.get_current_color(button)
            x1, y1 = min(self.start_x, x), min(self.start_y, y)
            x2, y2 = max(self.start_x, x), max(self.start_y, y)
            if self.filled:
                canvas.draw_rectangle(x1, y1, x2, y2, color, filled=True)
            else:
                canvas.draw_rectangle(x1, y1, x2, y2, color, filled=False, width=canvas.brush_size)
        self.start_x = None
        self.start_y = None


class CircleTool(Tool):
    """Circle tool"""
    def __init__(self, filled=False):
        super().__init__("Circle", "○" if not filled else "●", 
                        "Filled circle" if filled else "Circle outline")
        self.filled = filled
        self.start_x = None
        self.start_y = None
    
    def on_press(self, canvas, x, y, button):
        self.start_x = x
        self.start_y = y
    
    def on_release(self, canvas, x, y, button):
        if self.start_x is not None:
            color = canvas.get_current_color(button)
            radius = int(math.sqrt((x - self.start_x)**2 + (y - self.start_y)**2))
            if self.filled:
                canvas.draw_ellipse(
                    self.start_x - radius, self.start_y - radius,
                    self.start_x + radius, self.start_y + radius,
                    color, filled=True
                )
            else:
                canvas.draw_ellipse(
                    self.start_x - radius, self.start_y - radius,
                    self.start_x + radius, self.start_y + radius,
                    color, filled=False, width=canvas.brush_size
                )
        self.start_x = None
        self.start_y = None


class EllipseTool(Tool):
    """Ellipse tool"""
    def __init__(self, filled=False):
        super().__init__("Ellipse", "⬭" if not filled else "⬬", 
                        "Filled ellipse" if filled else "Ellipse outline")
        self.filled = filled
        self.start_x = None
        self.start_y = None
    
    def on_press(self, canvas, x, y, button):
        self.start_x = x
        self.start_y = y
    
    def on_release(self, canvas, x, y, button):
        if self.start_x is not None:
            color = canvas.get_current_color(button)
            x1, y1 = self.start_x, self.start_y
            x2, y2 = x, y
            if self.filled:
                canvas.draw_ellipse(x1, y1, x2, y2, color, filled=True)
            else:
                canvas.draw_ellipse(x1, y1, x2, y2, color, filled=False, width=canvas.brush_size)
        self.start_x = None
        self.start_y = None


class FillTool(Tool):
    """Flood fill tool"""
    def __init__(self):
        super().__init__("Fill", "🪣", "Flood fill")
    
    def on_press(self, canvas, x, y, button):
        color = canvas.get_current_color(button)
        canvas.flood_fill(x, y, color)


class EraserTool(Tool):
    """Eraser tool"""
    def __init__(self):
        super().__init__("Eraser", "⌫", "Eraser")
        self.last_x = None
        self.last_y = None
    
    def on_press(self, canvas, x, y, button):
        self.last_x = x
        self.last_y = y
        canvas.erase_at(x, y, canvas.brush_size * 2)
    
    def on_drag(self, canvas, x, y, button):
        if self.last_x is not None:
            canvas.erase_line(self.last_x, self.last_y, x, y, canvas.brush_size * 2)
        self.last_x = x
        self.last_y = y
    
    def on_release(self, canvas, x, y, button):
        self.last_x = None
        self.last_y = None


class EyedropperTool(Tool):
    """Color picker tool"""
    def __init__(self):
        super().__init__("Eyedropper", "💧", "Pick color from canvas")
    
    def on_press(self, canvas, x, y, button):
        color = canvas.get_pixel_color(x, y)
        if color:
            if button == 1:
                canvas.set_foreground_color(color)
            else:
                canvas.set_background_color(color)


class SelectionTool(Tool):
    """Selection/brush pickup tool"""
    def __init__(self):
        super().__init__("Select", "⬚", "Select area or pick up brush")
        self.start_x = None
        self.start_y = None
        self.selecting = False
    
    def on_press(self, canvas, x, y, button):
        self.start_x = x
        self.start_y = y
        self.selecting = True
    
    def on_drag(self, canvas, x, y, button):
        if self.selecting:
            canvas.show_selection_rect(self.start_x, self.start_y, x, y)
    
    def on_release(self, canvas, x, y, button):
        if self.selecting and self.start_x is not None:
            # Pick up brush from selection
            x1, y1 = min(self.start_x, x), min(self.start_y, y)
            x2, y2 = max(self.start_x, x), max(self.start_y, y)
            if x2 > x1 and y2 > y1:
                canvas.pick_up_brush(x1, y1, x2, y2, cut=(button == 3))
        self.start_x = None
        self.start_y = None
        self.selecting = False
        canvas.hide_selection_rect()


class TextTool(Tool):
    """Text placement tool"""
    def __init__(self):
        super().__init__("Text", "T", "Place text on canvas")
    
    def on_press(self, canvas, x, y, button):
        canvas.start_text_input(x, y)


class AirbrushTool(Tool):
    """Airbrush spray tool"""
    def __init__(self):
        super().__init__("Airbrush", "🎨", "Airbrush spray effect")
        self.spraying = False
    
    def on_press(self, canvas, x, y, button):
        self.spraying = True
        self._spray(canvas, x, y, button)
    
    def on_drag(self, canvas, x, y, button):
        if self.spraying:
            self._spray(canvas, x, y, button)
    
    def on_release(self, canvas, x, y, button):
        self.spraying = False
    
    def _spray(self, canvas, x, y, button):
        import random
        color = canvas.get_current_color(button)
        for _ in range(canvas.brush_size * 3):
            dx = random.randint(-canvas.brush_size*2, canvas.brush_size*2)
            dy = random.randint(-canvas.brush_size*2, canvas.brush_size*2)
            if dx*dx + dy*dy <= canvas.brush_size*2*canvas.brush_size*2:
                canvas.set_pixel(x + dx, y + dy, color)


class PaintCanvas(tk.Canvas):
    """Main painting canvas with support for layers and animation frames"""
    
    def __init__(self, parent, width=800, height=600, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=RetroStyle.COLORS['canvas_bg'], 
                        highlightthickness=0, **kwargs)
        
        self.canvas_width = width
        self.canvas_height = height
        
        # Drawing state
        self.foreground_color = '#ffffff'
        self.background_color = '#000000'
        self.brush_size = 5
        self.current_tool = None
        self.current_brush = None  # Custom brush image
        
        # Layers
        self.layers = []
        self.current_layer_index = 0
        self._create_layer("Background")
        
        # Animation frames
        self.frames = []
        self.current_frame_index = 0
        self._create_frame()
        
        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 50
        
        # Selection state
        self.selection_rect = None
        self.selection_id = None
        
        # Text input
        self.text_entry = None
        
        # Grid and symmetry
        self.show_grid = False
        self.grid_spacing = 16
        self.symmetry_mode = None  # None, 'horizontal', 'vertical', 'radial'
        
        # Bind events
        self.bind('<Button-1>', lambda e: self._on_mouse_event(e, 'press', 1))
        self.bind('<Button-3>', lambda e: self._on_mouse_event(e, 'press', 3))
        self.bind('<B1-Motion>', lambda e: self._on_mouse_event(e, 'drag', 1))
        self.bind('<B3-Motion>', lambda e: self._on_mouse_event(e, 'drag', 3))
        self.bind('<ButtonRelease-1>', lambda e: self._on_mouse_event(e, 'release', 1))
        self.bind('<ButtonRelease-3>', lambda e: self._on_mouse_event(e, 'release', 3))
        self.bind('<Motion>', self._on_motion)
        
        # Initial render
        self._render()
    
    def _create_layer(self, name="Layer"):
        """Create a new layer"""
        layer_image = Image.new('RGBA', (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self.layers.append({
            'name': name,
            'image': layer_image,
            'visible': True,
            'opacity': 1.0
        })
    
    def _create_frame(self):
        """Create a new animation frame"""
        frame_layers = [layer.copy() for layer in self.layers]
        self.frames.append({
            'layers': frame_layers,
            'duration': 100  # milliseconds
        })
    
    def get_current_layer(self):
        """Get the currently active layer"""
        if 0 <= self.current_layer_index < len(self.layers):
            return self.layers[self.current_layer_index]
        return None
    
    def get_current_draw(self):
        """Get ImageDraw object for current layer"""
        layer = self.get_current_layer()
        if layer:
            return ImageDraw.Draw(layer['image'])
        return None
    
    def _save_undo_state(self):
        """Save current state for undo"""
        state = {
            'layers': [layer.copy() for layer in self.layers],
            'layer_index': self.current_layer_index
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
    
    def undo(self):
        """Undo last action"""
        if self.undo_stack:
            current_state = {
                'layers': [layer.copy() for layer in self.layers],
                'layer_index': self.current_layer_index
            }
            self.redo_stack.append(current_state)
            
            state = self.undo_stack.pop()
            self.layers = state['layers']
            self.current_layer_index = state['layer_index']
            self._render()
    
    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            current_state = {
                'layers': [layer.copy() for layer in self.layers],
                'layer_index': self.current_layer_index
            }
            self.undo_stack.append(current_state)
            
            state = self.redo_stack.pop()
            self.layers = state['layers']
            self.current_layer_index = state['layer_index']
            self._render()
    
    def _on_mouse_event(self, event, event_type, button):
        """Handle mouse events"""
        x, y = event.x, event.y
        
        if self.current_tool:
            if event_type == 'press':
                self._save_undo_state()
                self.current_tool.on_press(self, x, y, button)
            elif event_type == 'drag':
                self.current_tool.on_drag(self, x, y, button)
            elif event_type == 'release':
                self.current_tool.on_release(self, x, y, button)
            
            self._render()
    
    def _on_motion(self, event):
        """Handle mouse motion for cursor updates"""
        pass
    
    def get_current_color(self, button):
        """Get color based on mouse button"""
        if button == 1:
            return self.foreground_color
        return self.background_color
    
    def set_foreground_color(self, color):
        """Set foreground color"""
        self.foreground_color = color
    
    def set_background_color(self, color):
        """Set background color"""
        self.background_color = color
    
    # Drawing primitives
    def draw_line(self, x1, y1, x2, y2, color, width=1):
        """Draw a line on current layer"""
        draw = self.get_current_draw()
        if draw:
            draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
            self._apply_symmetry(lambda d: d.line([(x1, y1), (x2, y2)], fill=color, width=width))
    
    def draw_ellipse(self, x1, y1, x2, y2, color, filled=True, width=1):
        """Draw an ellipse on current layer"""
        draw = self.get_current_draw()
        if draw:
            if filled:
                draw.ellipse([(x1, y1), (x2, y2)], fill=color)
            else:
                draw.ellipse([(x1, y1), (x2, y2)], outline=color, width=width)
    
    def draw_rectangle(self, x1, y1, x2, y2, color, filled=True, width=1):
        """Draw a rectangle on current layer"""
        draw = self.get_current_draw()
        if draw:
            if filled:
                draw.rectangle([(x1, y1), (x2, y2)], fill=color)
            else:
                draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=width)
    
    def set_pixel(self, x, y, color):
        """Set a single pixel"""
        draw = self.get_current_draw()
        if draw:
            draw.point((x, y), fill=color)
    
    def get_pixel_color(self, x, y):
        """Get color at pixel position"""
        layer = self.get_current_layer()
        if layer and 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            pixel = layer['image'].getpixel((x, y))
            return '#{:02x}{:02x}{:02x}'.format(pixel[0], pixel[1], pixel[2])
        return None
    
    def flood_fill(self, x, y, color):
        """Flood fill from point"""
        layer = self.get_current_layer()
        if layer:
            ImageDraw.floodfill(layer['image'], (x, y), color, thresh=40)
    
    def erase_at(self, x, y, size):
        """Erase at position"""
        draw = self.get_current_draw()
        if draw:
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=(0, 0, 0, 0))
    
    def erase_line(self, x1, y1, x2, y2, size):
        """Erase along a line"""
        draw = self.get_current_draw()
        if draw:
            for t in range(100):
                tx = x1 + (x2 - x1) * t / 100
                ty = y1 + (y2 - y1) * t / 100
                draw.ellipse([(tx-size, ty-size), (tx+size, ty+size)], fill=(0, 0, 0, 0))
    
    def clear_layer(self):
        """Clear current layer"""
        self._save_undo_state()
        layer = self.get_current_layer()
        if layer:
            layer['image'] = Image.new('RGBA', (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
            self._render()
    
    def clear_all(self):
        """Clear all layers"""
        self._save_undo_state()
        for layer in self.layers:
            layer['image'] = Image.new('RGBA', (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self._render()
    
    def _apply_symmetry(self, draw_func):
        """Apply symmetry transformation if enabled"""
        # TODO: Implement symmetry drawing
        pass
    
    def show_selection_rect(self, x1, y1, x2, y2):
        """Show selection rectangle"""
        if self.selection_id:
            self.delete(self.selection_id)
        self.selection_id = self.create_rectangle(
            x1, y1, x2, y2,
            outline=RetroStyle.COLORS['selection'],
            dash=(4, 4),
            width=2
        )
    
    def hide_selection_rect(self):
        """Hide selection rectangle"""
        if self.selection_id:
            self.delete(self.selection_id)
            self.selection_id = None
    
    def pick_up_brush(self, x1, y1, x2, y2, cut=False):
        """Pick up area as custom brush"""
        layer = self.get_current_layer()
        if layer:
            self.current_brush = layer['image'].crop((x1, y1, x2, y2)).copy()
            if cut:
                draw = self.get_current_draw()
                draw.rectangle([(x1, y1), (x2, y2)], fill=(0, 0, 0, 0))
    
    def start_text_input(self, x, y):
        """Start text input at position"""
        if self.text_entry:
            self.text_entry.destroy()
        
        self.text_entry = tk.Entry(self, font=('Arial', self.brush_size * 3))
        self.create_window(x, y, window=self.text_entry, anchor='nw')
        self.text_entry.focus_set()
        self.text_entry.bind('<Return>', lambda e: self._place_text(x, y))
        self.text_entry.bind('<Escape>', lambda e: self._cancel_text())
    
    def _place_text(self, x, y):
        """Place typed text on canvas"""
        if self.text_entry:
            text = self.text_entry.get()
            self.text_entry.destroy()
            self.text_entry = None
            
            if text:
                draw = self.get_current_draw()
                if draw:
                    draw.text((x, y), text, fill=self.foreground_color)
                    self._render()
    
    def _cancel_text(self):
        """Cancel text input"""
        if self.text_entry:
            self.text_entry.destroy()
            self.text_entry = None
    
    def _render(self):
        """Render all layers to canvas"""
        # Create composite image
        composite = Image.new('RGBA', (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        
        for layer in self.layers:
            if layer['visible']:
                composite = Image.alpha_composite(composite, layer['image'])
        
        # Convert to PhotoImage and display
        self.photo = ImageTk.PhotoImage(composite)
        self.delete('all')
        self.create_image(0, 0, anchor='nw', image=self.photo)
        
        # Draw grid if enabled
        if self.show_grid:
            for x in range(0, self.canvas_width, self.grid_spacing):
                self.create_line(x, 0, x, self.canvas_height, fill=RetroStyle.COLORS['grid_color'], dash=(2, 4))
            for y in range(0, self.canvas_height, self.grid_spacing):
                self.create_line(0, y, self.canvas_width, y, fill=RetroStyle.COLORS['grid_color'], dash=(2, 4))
    
    def get_composite_image(self):
        """Get the composite image of all layers"""
        composite = Image.new('RGBA', (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        for layer in self.layers:
            if layer['visible']:
                composite = Image.alpha_composite(composite, layer['image'])
        return composite
    
    def save_image(self, filepath, format='PNG'):
        """Save current image"""
        image = self.get_composite_image()
        image.save(filepath, format=format)
    
    def load_image(self, filepath):
        """Load image as new layer"""
        self._save_undo_state()
        image = Image.open(filepath).convert('RGBA')
        image = image.resize((self.canvas_width, self.canvas_height))
        self._create_layer("Imported")
        self.layers[-1]['image'] = image
        self.current_layer_index = len(self.layers) - 1
        self._render()


class AnimationTimeline(tk.Frame):
    """Animation timeline with frame thumbnails"""
    
    def __init__(self, parent, canvas, **kwargs):
        super().__init__(parent, bg=RetroStyle.COLORS['bg_dark'], **kwargs)
        self.canvas = canvas
        self.frames = []
        self.current_frame = 0
        self.on_frame_select = None
        self.playing = False
        self.fps = 12
        
        self._create_ui()
    
    def _create_ui(self):
        """Create timeline UI"""
        # Controls
        controls = tk.Frame(self, bg=RetroStyle.COLORS['bg_medium'])
        controls.pack(fill='x', pady=2)
        
        # Playback buttons
        self.btn_first = tk.Button(controls, text="⏮", width=3, 
                                   command=self._first_frame)
        RetroStyle.apply_button_style(self.btn_first)
        self.btn_first.pack(side='left', padx=2)
        
        self.btn_prev = tk.Button(controls, text="◀", width=3, 
                                  command=self._prev_frame)
        RetroStyle.apply_button_style(self.btn_prev)
        self.btn_prev.pack(side='left', padx=2)
        
        self.btn_play = tk.Button(controls, text="▶", width=3, 
                                  command=self._toggle_play)
        RetroStyle.apply_button_style(self.btn_play)
        self.btn_play.pack(side='left', padx=2)
        
        self.btn_next = tk.Button(controls, text="▶", width=3, 
                                  command=self._next_frame)
        RetroStyle.apply_button_style(self.btn_next)
        self.btn_next.pack(side='left', padx=2)
        
        self.btn_last = tk.Button(controls, text="⏭", width=3, 
                                  command=self._last_frame)
        RetroStyle.apply_button_style(self.btn_last)
        self.btn_last.pack(side='left', padx=2)
        
        # FPS control
        tk.Label(controls, text="FPS:", bg=RetroStyle.COLORS['bg_medium'],
                fg=RetroStyle.COLORS['text_secondary']).pack(side='left', padx=5)
        self.fps_var = tk.StringVar(value="12")
        fps_spin = tk.Spinbox(controls, from_=1, to=60, width=4, 
                             textvariable=self.fps_var, 
                             command=self._update_fps)
        fps_spin.pack(side='left', padx=2)
        
        # Frame management buttons
        self.btn_add = tk.Button(controls, text="+", width=3, 
                                command=self._add_frame)
        RetroStyle.apply_button_style(self.btn_add)
        self.btn_add.pack(side='right', padx=2)
        
        self.btn_del = tk.Button(controls, text="-", width=3, 
                                command=self._del_frame)
        RetroStyle.apply_button_style(self.btn_del)
        self.btn_del.pack(side='right', padx=2)
        
        self.btn_copy = tk.Button(controls, text="📋", width=3, 
                                 command=self._copy_frame)
        RetroStyle.apply_button_style(self.btn_copy)
        self.btn_copy.pack(side='right', padx=2)
        
        # Frame strip with scrollbar
        frame_container = tk.Frame(self, bg=RetroStyle.COLORS['bg_dark'])
        frame_container.pack(fill='both', expand=True)
        
        # Canvas for frames
        self.frame_canvas = tk.Canvas(frame_container, height=80, 
                                      bg=RetroStyle.COLORS['bg_dark'])
        self.frame_canvas.pack(fill='both', expand=True)
        
        self.frame_strip = tk.Frame(self.frame_canvas, bg=RetroStyle.COLORS['bg_dark'])
        self.frame_canvas.create_window((0, 0), window=self.frame_strip, anchor='nw')
        
        # Add initial frame
        self._add_frame()
    
    def _add_frame(self):
        """Add a new frame"""
        frame_thumb = tk.Frame(self.frame_strip, bg=RetroStyle.COLORS['bg_medium'], 
                              relief='raised', borderwidth=2)
        frame_thumb.pack(side='left', padx=2, pady=2)
        
        # Frame number
        frame_num = len(self.frames)
        lbl = tk.Label(frame_thumb, text=str(frame_num + 1), 
                      bg=RetroStyle.COLORS['bg_medium'],
                      fg=RetroStyle.COLORS['text_primary'],
                      font=('Arial', 8))
        lbl.pack()
        
        # Thumbnail placeholder
        thumb = tk.Label(frame_thumb, text="🖼", width=6, height=4,
                        bg=RetroStyle.COLORS['canvas_bg'],
                        fg=RetroStyle.COLORS['text_secondary'])
        thumb.pack()
        
        # Make clickable
        for widget in [frame_thumb, lbl, thumb]:
            widget.bind('<Button-1>', lambda e, i=frame_num: self._select_frame(i))
        
        self.frames.append({
            'container': frame_thumb,
            'thumbnail': thumb,
            'layers': []  # Will store layer data
        })
        
        self._select_frame(frame_num)
    
    def _del_frame(self):
        """Delete current frame"""
        if len(self.frames) > 1 and self.current_frame < len(self.frames):
            self.frames[self.current_frame]['container'].destroy()
            self.frames.pop(self.current_frame)
            self.current_frame = min(self.current_frame, len(self.frames) - 1)
            self._select_frame(self.current_frame)
    
    def _copy_frame(self):
        """Copy current frame"""
        if self.frames:
            self._add_frame()
            # Copy layer data from previous frame
            if self.current_frame > 0:
                self.frames[-1]['layers'] = [
                    layer.copy() for layer in self.frames[self.current_frame - 1]['layers']
                ]
    
    def _select_frame(self, index):
        """Select a frame"""
        if 0 <= index < len(self.frames):
            # Deselect old
            if 0 <= self.current_frame < len(self.frames):
                self.frames[self.current_frame]['container'].configure(
                    bg=RetroStyle.COLORS['bg_medium'])
            
            # Select new
            self.current_frame = index
            self.frames[index]['container'].configure(
                bg=RetroStyle.COLORS['accent_primary'])
            
            if self.on_frame_select:
                self.on_frame_select(index)
    
    def _first_frame(self):
        """Go to first frame"""
        self._select_frame(0)
    
    def _prev_frame(self):
        """Go to previous frame"""
        if self.current_frame > 0:
            self._select_frame(self.current_frame - 1)
    
    def _next_frame(self):
        """Go to next frame"""
        if self.current_frame < len(self.frames) - 1:
            self._select_frame(self.current_frame + 1)
    
    def _last_frame(self):
        """Go to last frame"""
        self._select_frame(len(self.frames) - 1)
    
    def _toggle_play(self):
        """Toggle animation playback"""
        self.playing = not self.playing
        if self.playing:
            self.btn_play.configure(text="⏸")
            self._play_animation()
        else:
            self.btn_play.configure(text="▶")
    
    def _play_animation(self):
        """Play animation loop"""
        if self.playing:
            self._next_frame()
            if self.current_frame >= len(self.frames) - 1:
                self._select_frame(0)
            delay = int(1000 / self.fps)
            self.after(delay, self._play_animation)
    
    def _update_fps(self):
        """Update FPS from spinbox"""
        try:
            self.fps = int(self.fps_var.get())
        except:
            self.fps = 12


class ColorPalette(tk.Frame):
    """Color palette with color picker"""
    
    def __init__(self, parent, canvas, **kwargs):
        super().__init__(parent, bg=RetroStyle.COLORS['bg_dark'], **kwargs)
        self.canvas = canvas
        self.colors = self._get_default_palette()
        self._create_ui()
    
    def _get_default_palette(self):
        """Get default color palette inspired by classic paint programs"""
        return [
            '#000000', '#ffffff', '#808080', '#c0c0c0',
            '#800000', '#ff0000', '#804000', '#ff8000',
            '#808000', '#ffff00', '#008000', '#00ff00',
            '#008080', '#00ffff', '#000080', '#0000ff',
            '#800080', '#ff00ff', '#400000', '#ff4040',
            '#404000', '#ffff40', '#004000', '#40ff40',
            '#004040', '#40ffff', '#000040', '#4040ff',
            '#400040', '#ff40ff', '#200000', '#ff2020',
        ]
    
    def _create_ui(self):
        """Create palette UI"""
        # Current colors display
        color_frame = tk.Frame(self, bg=RetroStyle.COLORS['bg_dark'])
        color_frame.pack(pady=5)
        
        # Foreground color
        self.fg_frame = tk.Frame(color_frame, width=40, height=40, 
                                relief='sunken', borderwidth=2)
        self.fg_frame.pack(side='left', padx=5)
        self.fg_frame.pack_propagate(False)
        self.fg_color = tk.Label(self.fg_frame, bg='#ffffff')
        self.fg_color.pack(fill='both', expand=True)
        self.fg_color.bind('<Button-1>', self._choose_fg_color)
        
        # Background color
        self.bg_frame = tk.Frame(color_frame, width=40, height=40,
                                relief='sunken', borderwidth=2)
        self.bg_frame.pack(side='left', padx=5)
        self.bg_frame.pack_propagate(False)
        self.bg_color = tk.Label(self.bg_frame, bg='#000000')
        self.bg_color.pack(fill='both', expand=True)
        self.bg_color.bind('<Button-1>', self._choose_bg_color)
        
        # Color grid
        grid_frame = tk.Frame(self, bg=RetroStyle.COLORS['bg_dark'])
        grid_frame.pack(pady=5)
        
        for i, color in enumerate(self.colors):
            row = i // 8
            col = i % 8
            btn = tk.Button(grid_frame, bg=color, width=2, height=1,
                           relief='raised', borderwidth=1,
                           command=lambda c=color: self._select_color(c))
            btn.grid(row=row, column=col, padx=1, pady=1)
            btn.bind('<Button-3>', lambda e, c=color: self._select_bg_color(c))
        
        # Add custom color button
        add_btn = tk.Button(self, text="+ Add Color", 
                           command=self._add_custom_color)
        RetroStyle.apply_button_style(add_btn)
        add_btn.pack(pady=5)
    
    def _select_color(self, color):
        """Select foreground color"""
        self.fg_color.configure(bg=color)
        self.canvas.set_foreground_color(color)
    
    def _select_bg_color(self, color):
        """Select background color"""
        self.bg_color.configure(bg=color)
        self.canvas.set_background_color(color)
    
    def _choose_fg_color(self, event=None):
        """Open color chooser for foreground"""
        color = colorchooser.askcolor(title="Choose Foreground Color")[1]
        if color:
            self._select_color(color)
    
    def _choose_bg_color(self, event=None):
        """Open color chooser for background"""
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self._select_bg_color(color)
    
    def _add_custom_color(self):
        """Add a custom color to palette"""
        color = colorchooser.askcolor(title="Add Custom Color")[1]
        if color:
            self.colors.append(color)


class Toolbox(tk.Frame):
    """Tool selection panel"""
    
    def __init__(self, parent, canvas, **kwargs):
        super().__init__(parent, bg=RetroStyle.COLORS['bg_dark'], **kwargs)
        self.canvas = canvas
        self.tools = self._get_tools()
        self.current_tool = None
        self._create_ui()
    
    def _get_tools(self):
        """Get list of available tools"""
        return [
            BrushTool(),
            AirbrushTool(),
            LineTool(),
            RectangleTool(filled=False),
            RectangleTool(filled=True),
            CircleTool(filled=False),
            CircleTool(filled=True),
            EllipseTool(filled=False),
            EllipseTool(filled=True),
            FillTool(),
            EraserTool(),
            EyedropperTool(),
            SelectionTool(),
            TextTool(),
        ]
    
    def _create_ui(self):
        """Create toolbox UI"""
        # Title
        title = tk.Label(self, text="🛠 TOOLS", 
                        bg=RetroStyle.COLORS['bg_medium'],
                        fg=RetroStyle.COLORS['accent_highlight'],
                        font=('Arial', 10, 'bold'))
        title.pack(fill='x', pady=2)
        
        # Tool buttons grid
        tool_frame = tk.Frame(self, bg=RetroStyle.COLORS['bg_dark'])
        tool_frame.pack(pady=5)
        
        for i, tool in enumerate(self.tools):
            row = i // 2
            col = i % 2
            btn = tk.Button(tool_frame, text=tool.icon_char, 
                           width=3, height=1,
                           relief='raised', borderwidth=2,
                           font=('Arial', 12),
                           command=lambda t=tool: self._select_tool(t))
            btn.grid(row=row, column=col, padx=2, pady=2)
            btn.bind('<Enter>', lambda e, b=btn: b.configure(relief='groove'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(relief='raised'))
        
        # Brush size control
        size_frame = tk.Frame(self, bg=RetroStyle.COLORS['bg_dark'])
        size_frame.pack(pady=10)
        
        tk.Label(size_frame, text="Brush Size:", 
                bg=RetroStyle.COLORS['bg_dark'],
                fg=RetroStyle.COLORS['text_primary']).pack()
        
        self.size_var = tk.IntVar(value=5)
        size_scale = tk.Scale(size_frame, from_=1, to=50, 
                             orient='horizontal',
                             variable=self.size_var,
                             bg=RetroStyle.COLORS['bg_dark'],
                             fg=RetroStyle.COLORS['text_primary'],
                             highlightthickness=0,
                             command=self._update_brush_size)
        size_scale.pack()
        
        # Options
        options_frame = tk.Frame(self, bg=RetroStyle.COLORS['bg_dark'])
        options_frame.pack(pady=5)
        
        self.grid_var = tk.BooleanVar(value=False)
        grid_cb = tk.Checkbutton(options_frame, text="Show Grid",
                                variable=self.grid_var,
                                bg=RetroStyle.COLORS['bg_dark'],
                                fg=RetroStyle.COLORS['text_primary'],
                                selectcolor=RetroStyle.COLORS['bg_medium'],
                                command=self._toggle_grid)
        grid_cb.pack(anchor='w')
        
        # Select first tool
        if self.tools:
            self._select_tool(self.tools[0])
    
    def _select_tool(self, tool):
        """Select a tool"""
        self.current_tool = tool
        self.canvas.current_tool = tool
        self.canvas.configure(cursor=tool.cursor)
    
    def _update_brush_size(self, value):
        """Update brush size"""
        self.canvas.brush_size = int(value)
    
    def _toggle_grid(self):
        """Toggle grid visibility"""
        self.canvas.show_grid = self.grid_var.get()
        self.canvas._render()


class LayerPanel(tk.Frame):
    """Layer management panel"""
    
    def __init__(self, parent, canvas, **kwargs):
        super().__init__(parent, bg=RetroStyle.COLORS['bg_dark'], **kwargs)
        self.canvas = canvas
        self._create_ui()
    
    def _create_ui(self):
        """Create layer panel UI"""
        # Title
        title = tk.Label(self, text="📚 LAYERS",
                        bg=RetroStyle.COLORS['bg_medium'],
                        fg=RetroStyle.COLORS['accent_highlight'],
                        font=('Arial', 10, 'bold'))
        title.pack(fill='x', pady=2)
        
        # Layer buttons
        btn_frame = tk.Frame(self, bg=RetroStyle.COLORS['bg_dark'])
        btn_frame.pack(fill='x', pady=5)
        
        add_btn = tk.Button(btn_frame, text="+", width=3,
                           command=self._add_layer)
        RetroStyle.apply_button_style(add_btn)
        add_btn.pack(side='left', padx=2)
        
        del_btn = tk.Button(btn_frame, text="-", width=3,
                           command=self._del_layer)
        RetroStyle.apply_button_style(del_btn)
        del_btn.pack(side='left', padx=2)
        
        up_btn = tk.Button(btn_frame, text="↑", width=3,
                          command=self._move_layer_up)
        RetroStyle.apply_button_style(up_btn)
        up_btn.pack(side='left', padx=2)
        
        down_btn = tk.Button(btn_frame, text="↓", width=3,
                            command=self._move_layer_down)
        RetroStyle.apply_button_style(down_btn)
        down_btn.pack(side='left', padx=2)
        
        # Layer list
        self.layer_list = tk.Listbox(self, height=8,
                                    bg=RetroStyle.COLORS['bg_medium'],
                                    fg=RetroStyle.COLORS['text_primary'],
                                    selectbackground=RetroStyle.COLORS['accent_primary'],
                                    selectforeground=RetroStyle.COLORS['text_primary'])
        self.layer_list.pack(fill='both', expand=True, padx=5, pady=5)
        self.layer_list.bind('<<ListboxSelect>>', self._on_layer_select)
        
        self._refresh_layers()
    
    def _refresh_layers(self):
        """Refresh layer list display"""
        self.layer_list.delete(0, tk.END)
        for i, layer in enumerate(self.canvas.layers):
            name = layer.get('name', f'Layer {i+1}')
            vis = '👁' if layer.get('visible', True) else '◌'
            self.layer_list.insert(tk.END, f"{vis} {name}")
        
        if 0 <= self.canvas.current_layer_index < self.layer_list.size():
            self.layer_list.selection_set(self.canvas.current_layer_index)
    
    def _add_layer(self):
        """Add a new layer"""
        self.canvas._create_layer(f"Layer {len(self.canvas.layers) + 1}")
        self.canvas.current_layer_index = len(self.canvas.layers) - 1
        self._refresh_layers()
    
    def _del_layer(self):
        """Delete current layer"""
        if len(self.canvas.layers) > 1:
            del self.canvas.layers[self.canvas.current_layer_index]
            self.canvas.current_layer_index = min(
                self.canvas.current_layer_index, 
                len(self.canvas.layers) - 1
            )
            self.canvas._render()
            self._refresh_layers()
    
    def _move_layer_up(self):
        """Move current layer up"""
        idx = self.canvas.current_layer_index
        if idx > 0:
            self.canvas.layers[idx], self.canvas.layers[idx-1] = \
                self.canvas.layers[idx-1], self.canvas.layers[idx]
            self.canvas.current_layer_index -= 1
            self.canvas._render()
            self._refresh_layers()
    
    def _move_layer_down(self):
        """Move current layer down"""
        idx = self.canvas.current_layer_index
        if idx < len(self.canvas.layers) - 1:
            self.canvas.layers[idx], self.canvas.layers[idx+1] = \
                self.canvas.layers[idx+1], self.canvas.layers[idx]
            self.canvas.current_layer_index += 1
            self.canvas._render()
            self._refresh_layers()
    
    def _on_layer_select(self, event):
        """Handle layer selection"""
        selection = self.layer_list.curselection()
        if selection:
            self.canvas.current_layer_index = selection[0]
            self.canvas._render()


class CharacterTemplates(tk.Toplevel):
    """Character design templates window"""
    
    def __init__(self, parent, canvas):
        super().__init__(parent)
        self.canvas = canvas
        self.title("Character Templates")
        self.geometry("400x500")
        self.configure(bg=RetroStyle.COLORS['bg_dark'])
        
        self._create_ui()
    
    def _create_ui(self):
        """Create templates UI"""
        # Title
        title = tk.Label(self, text="🎭 Character Templates",
                        bg=RetroStyle.COLORS['bg_medium'],
                        fg=RetroStyle.COLORS['accent_highlight'],
                        font=('Arial', 12, 'bold'))
        title.pack(fill='x', pady=10)
        
        # Template categories
        categories = [
            ("🦸 Comic Book Heroes", self._draw_hero),
            ("😎 Retro Cartoon Characters", self._draw_retro),
            ("🐱 Cute Animals", self._draw_animal),
            ("🤖 Robots & Mechs", self._draw_robot),
            ("🧙 Fantasy Characters", self._draw_fantasy),
            ("👽 Aliens & Creatures", self._draw_alien),
        ]
        
        for name, callback in categories:
            btn = tk.Button(self, text=name, width=25, height=2,
                           command=callback)
            RetroStyle.apply_button_style(btn)
            btn.pack(pady=5)
        
        # Proportions guide
        guide_frame = tk.LabelFrame(self, text="Proportions Guide",
                                   bg=RetroStyle.COLORS['bg_medium'],
                                   fg=RetroStyle.COLORS['text_primary'])
        guide_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        guide_text = """
Standard Character Proportions:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Head: 1 unit
• Torso: 2 units  
• Legs: 3-4 units
• Arms: 3 units (fingertip to shoulder)
• Total height: 6-8 heads

Retro Style Tips:
• Larger heads (2-3 heads tall)
• Exaggerated expressions
• Bold outlines
• Vibrant colors
• Simplified shapes
        """
        tk.Label(guide_frame, text=guide_text, 
                bg=RetroStyle.COLORS['bg_medium'],
                fg=RetroStyle.COLORS['text_secondary'],
                justify='left').pack(padx=10, pady=10)
    
    def _draw_hero(self):
        """Draw comic book hero template"""
        self.canvas._save_undo_state()
        self.canvas.clear_all()
        # Draw basic hero shape
        color = RetroStyle.COLORS['accent_primary']
        # Head
        self.canvas.draw_ellipse(350, 50, 450, 150, color, filled=True)
        # Body
        self.canvas.draw_rectangle(320, 150, 480, 350, color, filled=True)
        # Cape
        self.canvas.draw_rectangle(280, 150, 320, 400, '#ff0000', filled=True)
        self.canvas.draw_rectangle(480, 150, 520, 400, '#ff0000', filled=True)
        # Arms
        self.canvas.draw_rectangle(280, 160, 320, 300, color, filled=True)
        self.canvas.draw_rectangle(480, 160, 520, 300, color, filled=True)
        # Legs
        self.canvas.draw_rectangle(340, 350, 390, 500, color, filled=True)
        self.canvas.draw_rectangle(410, 350, 460, 500, color, filled=True)
        self.canvas._render()
    
    def _draw_retro(self):
        """Draw retro cartoon template"""
        self.canvas._save_undo_state()
        self.canvas.clear_all()
        color = RetroStyle.COLORS['accent_highlight']
        # Large head
        self.canvas.draw_ellipse(300, 50, 500, 250, color, filled=True)
        # Small body
        self.canvas.draw_rectangle(350, 250, 450, 400, color, filled=True)
        # Big eyes
        self.canvas.draw_ellipse(340, 120, 390, 170, '#ffffff', filled=True)
        self.canvas.draw_ellipse(410, 120, 460, 170, '#ffffff', filled=True)
        # Pupils
        self.canvas.draw_ellipse(360, 135, 380, 155, '#000000', filled=True)
        self.canvas.draw_ellipse(430, 135, 450, 155, '#000000', filled=True)
        # Small limbs
        self.canvas.draw_rectangle(320, 260, 350, 350, color, filled=True)
        self.canvas.draw_rectangle(450, 260, 480, 350, color, filled=True)
        self.canvas._render()
    
    def _draw_animal(self):
        """Draw cute animal template"""
        self.canvas._save_undo_state()
        self.canvas.clear_all()
        color = '#ffb347'  # Orange
        # Body
        self.canvas.draw_ellipse(300, 200, 500, 400, color, filled=True)
        # Head
        self.canvas.draw_ellipse(320, 100, 480, 250, color, filled=True)
        # Ears
        self.canvas.draw_ellipse(320, 80, 360, 140, color, filled=True)
        self.canvas.draw_ellipse(440, 80, 480, 140, color, filled=True)
        # Eyes
        self.canvas.draw_ellipse(360, 150, 400, 190, '#ffffff', filled=True)
        self.canvas.draw_ellipse(400, 150, 440, 190, '#ffffff', filled=True)
        # Nose
        self.canvas.draw_ellipse(385, 190, 415, 210, '#ff9999', filled=True)
        # Tail
        self.canvas.draw_rectangle(500, 280, 550, 320, color, filled=True)
        self.canvas._render()
    
    def _draw_robot(self):
        """Draw robot template"""
        self.canvas._save_undo_state()
        self.canvas.clear_all()
        color = '#808080'
        accent = RetroStyle.COLORS['accent_highlight']
        # Head
        self.canvas.draw_rectangle(350, 50, 450, 130, color, filled=True)
        # Eyes (LED style)
        self.canvas.draw_rectangle(370, 70, 400, 100, accent, filled=True)
        self.canvas.draw_rectangle(400, 70, 430, 100, accent, filled=True)
        # Antenna
        self.canvas.draw_rectangle(395, 20, 405, 50, accent, filled=True)
        # Body
        self.canvas.draw_rectangle(330, 130, 470, 300, color, filled=True)
        # Chest light
        self.canvas.draw_ellipse(380, 170, 420, 210, accent, filled=True)
        # Arms
        self.canvas.draw_rectangle(280, 140, 330, 280, color, filled=True)
        self.canvas.draw_rectangle(470, 140, 520, 280, color, filled=True)
        # Legs
        self.canvas.draw_rectangle(350, 300, 390, 450, color, filled=True)
        self.canvas.draw_rectangle(410, 300, 450, 450, color, filled=True)
        self.canvas._render()
    
    def _draw_fantasy(self):
        """Draw fantasy character template"""
        self.canvas._save_undo_state()
        self.canvas.clear_all()
        color = '#9966cc'
        # Wizard hat
        self.canvas.draw_rectangle(360, 20, 440, 80, color, filled=True)
        # Head
        self.canvas.draw_ellipse(350, 80, 450, 180, '#ffcc99', filled=True)
        # Beard
        self.canvas.draw_ellipse(360, 160, 440, 240, '#ffffff', filled=True)
        # Robe
        self.canvas.draw_rectangle(320, 180, 480, 500, color, filled=True)
        # Staff
        self.canvas.draw_rectangle(290, 100, 310, 500, '#8b4513', filled=True)
        # Staff orb
        self.canvas.draw_ellipse(285, 70, 315, 100, '#00ffff', filled=True)
        self.canvas._render()
    
    def _draw_alien(self):
        """Draw alien creature template"""
        self.canvas._save_undo_state()
        self.canvas.clear_all()
        color = '#00ff88'
        # Large head
        self.canvas.draw_ellipse(300, 50, 500, 200, color, filled=True)
        # Big eyes
        self.canvas.draw_ellipse(330, 90, 400, 150, '#000000', filled=True)
        self.canvas.draw_ellipse(400, 90, 470, 150, '#000000', filled=True)
        # Eye shine
        self.canvas.draw_ellipse(350, 100, 370, 120, '#ffffff', filled=True)
        self.canvas.draw_ellipse(420, 100, 440, 120, '#ffffff', filled=True)
        # Small body
        self.canvas.draw_rectangle(360, 200, 440, 350, color, filled=True)
        # Tentacle limbs
        for i in range(3):
            self.canvas.draw_ellipse(340 + i*30, 340, 360 + i*30, 420, color, filled=True)
        # Antennae
        self.canvas.draw_line(350, 50, 320, 20, color, 3)
        self.canvas.draw_line(450, 50, 480, 20, color, 3)
        self.canvas.draw_ellipse(310, 10, 330, 30, '#ffff00', filled=True)
        self.canvas.draw_ellipse(470, 10, 490, 30, '#ffff00', filled=True)
        self.canvas._render()


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1280x800")
        self.root.configure(bg=RetroStyle.COLORS['bg_dark'])
        
        # Set application icon
        try:
            self.root.iconname(APP_NAME)
        except:
            pass
        
        # Create UI components
        self._create_menu()
        self._create_toolbar()
        self._create_main_layout()
        self._create_statusbar()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
        # Track canvas reference
        self.canvas = self.paint_canvas
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg=RetroStyle.COLORS['bg_medium'],
                         fg=RetroStyle.COLORS['text_primary'])
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, 
                           bg=RetroStyle.COLORS['bg_medium'],
                           fg=RetroStyle.COLORS['text_primary'])
        file_menu.add_command(label="New Project", command=self._new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Image...", command=self._open_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save Image...", command=self._save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export Animation...", command=self._export_animation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0,
                           bg=RetroStyle.COLORS['bg_medium'],
                           fg=RetroStyle.COLORS['text_primary'])
        edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Layer", command=self._clear_layer)
        edit_menu.add_command(label="Clear All", command=self._clear_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0,
                           bg=RetroStyle.COLORS['bg_medium'],
                           fg=RetroStyle.COLORS['text_primary'])
        view_menu.add_command(label="Toggle Grid", command=self._toggle_grid)
        view_menu.add_command(label="Character Templates", command=self._show_templates)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Canvas menu
        canvas_menu = tk.Menu(menubar, tearoff=0,
                             bg=RetroStyle.COLORS['bg_medium'],
                             fg=RetroStyle.COLORS['text_primary'])
        canvas_menu.add_command(label="Resize Canvas...", command=self._resize_canvas)
        canvas_menu.add_command(label="Canvas Color...", command=self._canvas_color)
        menubar.add_cascade(label="Canvas", menu=canvas_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0,
                           bg=RetroStyle.COLORS['bg_medium'],
                           fg=RetroStyle.COLORS['text_primary'])
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.configure(menu=menubar)
    
    def _create_toolbar(self):
        """Create main toolbar"""
        toolbar = tk.Frame(self.root, bg=RetroStyle.COLORS['toolbar_bg'])
        toolbar.pack(fill='x')
        
        # File operations
        tk.Button(toolbar, text="📄 New", command=self._new_project).pack(side='left', padx=2, pady=2)
        tk.Button(toolbar, text="📂 Open", command=self._open_image).pack(side='left', padx=2, pady=2)
        tk.Button(toolbar, text="💾 Save", command=self._save_image).pack(side='left', padx=2, pady=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5, pady=2)
        
        # Edit operations
        tk.Button(toolbar, text="↩ Undo", command=self._undo).pack(side='left', padx=2, pady=2)
        tk.Button(toolbar, text="↪ Redo", command=self._redo).pack(side='left', padx=2, pady=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5, pady=2)
        
        # View operations
        tk.Button(toolbar, text="🔢 Grid", command=self._toggle_grid).pack(side='left', padx=2, pady=2)
        tk.Button(toolbar, text="🎭 Templates", command=self._show_templates).pack(side='left', padx=2, pady=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5, pady=2)
        
        # Quick tools
        tk.Label(toolbar, text="Quick Fill:", bg=RetroStyle.COLORS['toolbar_bg'],
                fg=RetroStyle.COLORS['text_secondary']).pack(side='left', padx=5)
        
        for color in ['#ffffff', '#000000', '#ff0000', '#00ff00', '#0000ff', '#ffff00']:
            btn = tk.Button(toolbar, bg=color, width=2, height=1,
                           command=lambda c=color: self._quick_fill(c))
            btn.pack(side='left', padx=1, pady=2)
    
    def _create_main_layout(self):
        """Create main application layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg=RetroStyle.COLORS['bg_dark'])
        main_frame.pack(fill='both', expand=True)
        
        # Left panel (tools and layers)
        left_panel = tk.Frame(main_frame, bg=RetroStyle.COLORS['bg_dark'], width=180)
        left_panel.pack(side='left', fill='y', padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Tools
        self.toolbox = Toolbox(left_panel, None)
        self.toolbox.pack(fill='x', pady=5)
        
        # Layers
        self.layer_panel = LayerPanel(left_panel, None)
        self.layer_panel.pack(fill='both', expand=True, pady=5)
        
        # Center panel (canvas)
        center_panel = tk.Frame(main_frame, bg=RetroStyle.COLORS['bg_dark'])
        center_panel.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Canvas with scrollbars
        canvas_container = tk.Frame(center_panel, bg=RetroStyle.COLORS['bg_dark'])
        canvas_container.pack(fill='both', expand=True)
        
        self.paint_canvas = PaintCanvas(canvas_container, width=800, height=500)
        self.paint_canvas.pack(fill='both', expand=True)
        
        # Update toolbox and layer panel references
        self.toolbox.canvas = self.paint_canvas
        self.layer_panel.canvas = self.paint_canvas
        
        # Timeline
        self.timeline = AnimationTimeline(center_panel, self.paint_canvas)
        self.timeline.pack(fill='x', pady=5)
        self.timeline.on_frame_select = self._on_frame_select
        
        # Right panel (colors)
        right_panel = tk.Frame(main_frame, bg=RetroStyle.COLORS['bg_dark'], width=180)
        right_panel.pack(side='right', fill='y', padx=5, pady=5)
        right_panel.pack_propagate(False)
        
        # Color palette
        self.color_palette = ColorPalette(right_panel, self.paint_canvas)
        self.color_palette.pack(fill='x', pady=5)
    
    def _create_statusbar(self):
        """Create status bar"""
        statusbar = tk.Frame(self.root, bg=RetroStyle.COLORS['bg_medium'])
        statusbar.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(statusbar, text="Ready", 
                                    bg=RetroStyle.COLORS['bg_medium'],
                                    fg=RetroStyle.COLORS['text_secondary'])
        self.status_label.pack(side='left', padx=10)
        
        # Canvas info
        self.canvas_info = tk.Label(statusbar, text="800 x 600",
                                   bg=RetroStyle.COLORS['bg_medium'],
                                   fg=RetroStyle.COLORS['text_secondary'])
        self.canvas_info.pack(side='right', padx=10)
        
        # Tool info
        self.tool_info = tk.Label(statusbar, text="Tool: Brush",
                                 bg=RetroStyle.COLORS['bg_medium'],
                                 fg=RetroStyle.COLORS['text_secondary'])
        self.tool_info.pack(side='right', padx=10)
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self._new_project())
        self.root.bind('<Control-N>', lambda e: self._new_project())
        self.root.bind('<Control-o>', lambda e: self._open_image())
        self.root.bind('<Control-O>', lambda e: self._open_image())
        self.root.bind('<Control-s>', lambda e: self._save_image())
        self.root.bind('<Control-S>', lambda e: self._save_image())
        self.root.bind('<Control-z>', lambda e: self._undo())
        self.root.bind('<Control-Z>', lambda e: self._undo())
        self.root.bind('<Control-y>', lambda e: self._redo())
        self.root.bind('<Control-Y>', lambda e: self._redo())
        self.root.bind('<F5>', lambda e: self.timeline._toggle_play())
    
    # Menu callbacks
    def _new_project(self):
        """Create new project"""
        self.paint_canvas.layers = []
        self.paint_canvas._create_layer("Background")
        self.paint_canvas.current_layer_index = 0
        self.paint_canvas._render()
        self.layer_panel._refresh_layers()
        self.status_label.configure(text="New project created")
    
    def _open_image(self):
        """Open image file"""
        filepath = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.paint_canvas.load_image(filepath)
            self.layer_panel._refresh_layers()
            self.status_label.configure(text=f"Opened: {filepath}")
    
    def _save_image(self):
        """Save image file"""
        filepath = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("GIF", "*.gif"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.paint_canvas.save_image(filepath)
            self.status_label.configure(text=f"Saved: {filepath}")
    
    def _save_as(self):
        """Save image as"""
        self._save_image()
    
    def _export_animation(self):
        """Export animation"""
        filepath = filedialog.asksaveasfilename(
            title="Export Animation",
            defaultextension=".gif",
            filetypes=[
                ("Animated GIF", "*.gif"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            # TODO: Implement animation export
            messagebox.showinfo("Export", "Animation export coming soon!")
    
    def _undo(self):
        """Undo last action"""
        self.paint_canvas.undo()
        self.status_label.configure(text="Undo")
    
    def _redo(self):
        """Redo last action"""
        self.paint_canvas.redo()
        self.status_label.configure(text="Redo")
    
    def _clear_layer(self):
        """Clear current layer"""
        self.paint_canvas.clear_layer()
        self.status_label.configure(text="Layer cleared")
    
    def _clear_all(self):
        """Clear all layers"""
        self.paint_canvas.clear_all()
        self.status_label.configure(text="Canvas cleared")
    
    def _toggle_grid(self):
        """Toggle grid visibility"""
        self.toolbox.grid_var.set(not self.toolbox.grid_var.get())
        self.toolbox._toggle_grid()
    
    def _show_templates(self):
        """Show character templates window"""
        CharacterTemplates(self.root, self.paint_canvas)
    
    def _resize_canvas(self):
        """Resize canvas dialog"""
        # TODO: Implement resize dialog
        messagebox.showinfo("Resize", "Canvas resize coming soon!")
    
    def _canvas_color(self):
        """Change canvas background color"""
        color = colorchooser.askcolor(title="Choose Canvas Color")[1]
        if color:
            self.paint_canvas.configure(bg=color)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = f"""
{APP_NAME} v{APP_VERSION}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

A retro-styled animation and drawing application 
inspired by classic tools like Deluxe Paint.

Features:
• Multi-layer editing
• Animation timeline
• Character templates
• Classic painting tools
• Retro 2000s aesthetic

Created by {APP_AUTHOR}
        """
        messagebox.showinfo("About", about_text)
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = """
Keyboard Shortcuts
━━━━━━━━━━━━━━━━━━━━━━━━━━━

File:
  Ctrl+N     New Project
  Ctrl+O     Open Image
  Ctrl+S     Save Image

Edit:
  Ctrl+Z     Undo
  Ctrl+Y     Redo

Animation:
  F5         Play/Pause

Tools:
  (Click toolbox icons)
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def _quick_fill(self, color):
        """Quick fill canvas with color"""
        self.paint_canvas._save_undo_state()
        self.paint_canvas.foreground_color = color
        self.paint_canvas.draw_rectangle(0, 0, 
                                         self.paint_canvas.canvas_width,
                                         self.paint_canvas.canvas_height,
                                         color, filled=True)
        self.paint_canvas._render()
    
    def _on_frame_select(self, frame_index):
        """Handle frame selection"""
        self.status_label.configure(text=f"Frame {frame_index + 1}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
