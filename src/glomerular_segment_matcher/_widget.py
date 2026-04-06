from typing import TYPE_CHECKING

from qtpy.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
import numpy as np
from qtpy.QtCore import QTimer, Qt


if TYPE_CHECKING:
    import napari

class SegmentMatcher(QWidget):
    def __init__(self, viewer: 'napari.viewer.Viewer'):
        super().__init__()
        
        self.viewer = viewer
        self.viewer.grid.enabled = True
        self.viewer.grid.shape = (1, 2)
        self.idx = 0  # initial index

        self.left_img_layer = None
        self.right_img_layer = None
        self.left_mask_layer = None
        self.right_mask_layer = None
        self.left_recon_layer = None
        self.right_recon_layer = None

        # buttons
        self.prev_btn = QPushButton("< Previous")
        self.next_btn = QPushButton("Next >")
        self.save_changes = QPushButton("Save Changes")
        self.prev_btn.clicked.connect(self.on_prev)
        self.next_btn.clicked.connect(self.on_next)
        self.save_changes.clicked.connect(self.on_save)

        self.label = QLabel("Matching: Slices 0 and 1")
        self.label.setAlignment(Qt.AlignCenter)

        # layouts
        mainLayout = QVBoxLayout()
        scrollLayout = QHBoxLayout()

        scrollLayout.addWidget(self.prev_btn)
        scrollLayout.addWidget(self.next_btn)
        mainLayout.addWidget(self.label)
        mainLayout.addLayout(scrollLayout)
        mainLayout.addWidget(self.save_changes)

        self.setLayout(mainLayout)

        self._try_initialize()

        self.viewer.layers.events.inserted.connect(self._maybe_initialize)

    # --------------------- UPDATING VIEWER ---------------------
    def _try_initialize(self):
        if 'images' in self.viewer.layers and 'masks' in self.viewer.layers:
            self._maybe_initialize()

    def _maybe_initialize(self, event=None):
        if 'images' in self.viewer.layers and 'masks' in self.viewer.layers:
            # prevent running multiple times
            self.viewer.layers.events.inserted.disconnect(self._maybe_initialize)
            self.update_view()

    def update_view(self):
        if 'images' not in self.viewer.layers or 'masks' not in self.viewer.layers:
            return
        
        if 'reconstructed' in self.viewer.layers:
            self.viewer.layers['reconstructed'].visible = False
            recon_stack = self.viewer.layers['reconstructed'].data

        img_stack = self.viewer.layers['images'].data
        mask_stack = self.viewer.layers['masks'].data
        self.viewer.layers['images'].visible = False
        self.viewer.layers['masks'].visible = False

        i = self.idx

        left_img = img_stack[i]
        right_img = img_stack[i + 1]

        left_mask = np.asarray(mask_stack[i])
        right_mask = np.asarray(mask_stack[i + 1])

        if 'reconstructed' in self.viewer.layers:
            left_recon = np.asarray(recon_stack[i])
            right_recon = np.asarray(recon_stack[i + 1])

        self.update_labels()

        if self.left_img_layer is None:
            self.right_img_layer = self.viewer.add_image(right_img, name=f"Pos {i + 1} Image") #translate=(0, 1)
            self.left_img_layer = self.viewer.add_image(left_img, name=f"Pos {i} Image")
        else:
            self.right_img_layer.data = right_img
            self.left_img_layer.data = left_img
            self.right_img_layer.name = f"Pos {i + 1} Image"
            self.left_img_layer.name = f"Pos {i} Image"
        
        if 'reconstructed' in self.viewer.layers:
            if self.left_recon_layer is None:
                self.right_recon_layer = self.viewer.add_labels(right_recon, name=f"Pos {i + 1} Reconstructed") # translate=(0, 1
                self.right_recon_layer.visible = False
                self.left_recon_layer = self.viewer.add_labels(left_recon, name=f"Pos {i} Reconstructed")
                self.left_recon_layer.visible = False
            else:
                self.right_recon_layer.data = right_recon
                self.right_recon_layer.visible = False
                self.left_recon_layer.data = left_recon
                self.left_recon_layer.visible = False
                self.right_recon_layer.name = f"Pos {i + 1} Recon"
                self.left_recon_layer.name = f"Pos {i} Recon"

        if self.left_mask_layer is None:
            self.right_mask_layer = self.viewer.add_labels(right_mask, name=f"Pos {i + 1} Mask") #translate=(0, 1)
            self.right_mask_layer.mouse_drag_callbacks.append(self._after_matching)
            self.left_mask_layer = self.viewer.add_labels(left_mask, name=f"Pos {i} Mask")
            self.left_mask_layer.mouse_drag_callbacks.append(self._transfer_label)
        else:
            self.right_mask_layer.data = right_mask
            self.left_mask_layer.data = left_mask
            self.right_mask_layer.name = f"Pos {i + 1} Mask"
            self.left_mask_layer.name = f"Pos {i} Mask"

        QTimer.singleShot(0, self._set_active)

        # update label
        self.label.setText(f"Matching: Slices {self.idx} and {self.idx + 1}")
        
    def _set_active(self):
        self.viewer.layers.selection.clear()
        self.viewer.layers.selection.active = self.left_mask_layer
        self.left_mask_layer.mode = 'pan_zoom'

        # need to rename here as well because of timing issues in updates
        i = self.idx
        self.right_mask_layer.name = f"Pos {i + 1} Mask"
        self.left_mask_layer.name = f"Pos {i} Mask"
        self.right_recon_layer.name = f"Pos {i + 1} Recon"
        self.left_recon_layer.name = f"Pos {i} Recon"
        self.right_img_layer.name = f"Pos {i + 1} Image"
        self.left_img_layer.name = f"Pos {i} Image"

    def update_labels(self):
        label_pos = np.array([[-30, 0]]) 

        # --- RIGHT LABEL ---
        if 'UI_Label_Right' in self.viewer.layers:
            layer_r = self.viewer.layers['UI_Label_Right']
            layer_r.data = label_pos
            layer_r.features = {'txt': [f"Slice {self.idx + 1}"]}
            layer_r.refresh_text()
            #layer_r.grid_index = (0, 1)
        else:
            layer_r = self.viewer.add_points(
                label_pos, name='UI_Label_Right',
                features={'txt': [f"Slice {self.idx + 1}"]},
                text={'string': '{txt}', 'size': 20, 'color': 'white', 'anchor': 'upper_left'},
                size=0, face_color='transparent', border_color='transparent'
            )
            #layer_r.grid_index = (0, 1) # Force Right

        
        # --- LEFT LABEL ---
        if 'UI_Label_Left' in self.viewer.layers:
            layer_l = self.viewer.layers['UI_Label_Left']
            layer_l.data = label_pos
            layer_l.features = {'txt': [f"Slice {self.idx}"]}
            layer_l.refresh_text()
            #layer_l.grid_index = (0, 0)
        else:
            layer_l = self.viewer.add_points(
                label_pos, name='UI_Label_Left',
                features={'txt': [f"Slice {self.idx}"]},
                text={'string': '{txt}', 'size': 20, 'color': 'white', 'anchor': 'upper_left'},
                size=0, face_color='transparent', border_color='transparent'
            )
            #layer_l.grid_index = (0, 0)

    def _transfer_label(self, layer, event):

        # we dont want it to keep moving to the other layer if we didn't pick a label
        if layer.mode != 'pick':
            return
        
        coords = layer.world_to_data(event.position)
        val = layer.get_value(coords)

        if val is not None:
            self.right_mask_layer.selected_label = val
            
            self.viewer.layers.selection.active = self.right_mask_layer
            
            self.right_mask_layer.mode = 'pan_zoom'

    def _after_matching(self, layer, event):

        if layer.mode != 'fill':
            return
        
        yield # wait for fill to be used
        
        self.viewer.layers.selection.active = self.left_mask_layer
        self.left_mask_layer.mode = 'pan_zoom'

    # --------------------- BUTTON HANDLERS ---------------------
    def on_next(self):
        if self.left_mask_layer is not None and self.right_mask_layer is not None:
            self.viewer.layers['masks'].data[self.idx] = self.left_mask_layer.data
            self.viewer.layers['masks'].data[self.idx + 1] = self.right_mask_layer.data

        # beacuse we displaying 2 at a time, we want second to last image be maximum
        max_idx = self.viewer.layers['images'].data.shape[0] - 2
        if self.idx < max_idx:
            self.idx += 1
            self.update_view()

    def on_prev(self):
        if self.left_mask_layer is not None and self.right_mask_layer is not None:
            self.viewer.layers['masks'].data[self.idx] = self.left_mask_layer.data
            self.viewer.layers['masks'].data[self.idx + 1] = self.right_mask_layer.data

        if self.idx > 0:
            self.idx -= 1
            self.update_view()

    def on_save(self):
        if self.left_mask_layer is not None and self.right_mask_layer is not None:
            self.viewer.layers['masks'].data[self.idx] = self.left_mask_layer.data
            self.viewer.layers['masks'].data[self.idx + 1] = self.right_mask_layer.data