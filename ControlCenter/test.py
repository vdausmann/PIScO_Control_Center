import pyqtgraph as pg
import pyqtgraph.flowchart as fc
import numpy as np
from pyqtgraph.flowchart.library.common import CtrlNode
# Use the common PyQt5/PySide2/6 abstraction provided by pyqtgraph.Qt
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

# --- 1. Custom Flowchart Node Definition ---
# This node performs a simple image operation (intensity scaling)
class ImageScaleNode(CtrlNode):
    """
    A custom node that scales the intensity of an input image by a factor.
    This operation simulates a basic image adjustment in the pipeline.
    """
    nodeName = 'ImageScale'

    def __init__(self, name):
        # Define the control widget (a single float spin box for the scale factor)
        self.scale_param = {'Scale Factor': (1.0, 'float', {'min': 0.1, 'max': 5.0, 'step': 0.1, 'decimals': 2})}
        
        # Initialize the base class with input/output terminals and control parameters
        CtrlNode.__init__(self, name, terminals={
            'In': {'io': 'in'},
            'Out': {'io': 'out'}
        })

        # CtrlNode automatically sets up the UI based on self.scale_param
        self.setupUi()

    def process(self, **kargs):
        """Performs the image scaling operation."""
        # Check if the input terminal 'In' is connected and has data
        if 'In' not in kargs or kargs['In'] is None:
            # If input is missing, return None for the output
            return {'Out': None}

        input_data = kargs['In']
        # Retrieve the current scale value from the control widget
        scale_factor = self.ctrls['Scale Factor'].value()

        # Simple pixel-wise multiplication
        output_data = input_data * scale_factor

        # Ensure the output data is a float array for consistency in the pipeline
        return {'Out': output_data.astype(np.float32)}

# --- 2. Main Application Window ---
class ImageFlowchartApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQtGraph Flowchart Image Processor')
        self.setGeometry(100, 100, 1400, 900)

        # Create the initial placeholder image data
        self.input_image_data = self.create_placeholder_image()

        # 1. Setup Central Widget and Layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # Left side: Flowchart Editor and Controls
        left_column = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left_column, 1) # Flowchart column takes 1/3 width

        # Right side: Image Views
        right_column = QtWidgets.QVBoxLayout()
        main_layout.addLayout(right_column, 2) # Image column takes 2/3 width

        # 2. Setup Flowchart
        # Define the main input and output terminals for the entire system
        # FIX: Removed redundant 'name' keys from terminal definitions to resolve TypeError.
        self.flowchart = fc.Flowchart(terminals={
            'In': {'io': 'in', 'multi': False}, # The name is implicitly 'In'
            'Out': {'io': 'out'}               # The name is implicitly 'Out'
        })
        # Add the flowchart widget to the left column
        left_column.addWidget(self.flowchart.widget())

        # Connect the flowchart's main output change signal to our update function
        self.flowchart.sigOutputChanged.connect(self.update_output_image)

        # Add a custom node instance to the flowchart to get started
        self.flowchart.addNode(ImageScaleNode('Scale1'), name='Image Scale')
        
        # 3. Setup Image Views
        # Input View (Original Image)
        self.input_view = pg.ImageView()
        self.input_view.ui.histogram.hide() # Hide unnecessary controls for cleaner view
        right_column.addWidget(QtWidgets.QLabel('<h3>Original Image (Input)</h3>'))
        right_column.addWidget(self.input_view)

        # Output View (Processed Image)
        self.output_view = pg.ImageView()
        self.output_view.ui.histogram.hide() # Hide unnecessary controls for cleaner view
        right_column.addWidget(QtWidgets.QLabel('<h3>Processed Image (Output)</h3>'))
        right_column.addWidget(self.output_view)
        
        # 4. Setup Controls (Load Button)
        load_button = QtWidgets.QPushButton("Load Sample Image / Re-run Flow")
        load_button.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        load_button.clicked.connect(self.load_image_and_run)
        left_column.addWidget(load_button)

        # Initial run
        self.load_image_and_run()
        print("Application initialized. Start connecting nodes in the flowchart!")

    def create_placeholder_image(self):
        """Creates a simple 200x300 8-bit grayscale image with a gradient."""
        # Create an array of 200 rows and 300 columns
        img = np.zeros((200, 300), dtype=np.uint8)
        
        # Create a horizontal gradient from 0 to 255
        for x in range(300):
            # Scale x from 0-299 to 0-255
            img[:, x] = int(x / 300.0 * 255.0)
            
        # Add a simple shape (a circle) in the center for visual feature
        Y, X = np.indices(img.shape)
        center_y, center_x = 100, 150
        radius = 50
        # NOTE: Fixed a small bug in the circle mask where center_x was used for Y twice
        mask = (X - center_x)**2 + (Y - center_y)**2 < radius**2 
        img[mask] = 255 - img[mask] # Invert intensity inside the circle

        return img.astype(np.float32) # Convert to float for processing in the pipeline

    def load_image_and_run(self):
        """Loads the image data into the Input view and triggers the Flowchart."""
        
        # 1. Set the image in the input view
        # We display the initial data as 8-bit, but send float32 to the flow for processing
        self.input_view.setImage(self.input_image_data, autoRange=True, autoLevels=True)

        # 2. Set the data for the flowchart's main 'In' terminal
        # This action automatically triggers the data flow and runs the entire pipeline
        self.flowchart.setInput(In=self.input_image_data.astype(np.float32))
        
        print("\n--- Image loaded and flowchart pipeline initiated. ---")

    @QtCore.Slot(object)
    def update_output_image(self, output_data):
        """
        Slot to receive the processed image data from the Flowchart 'Out' terminal.
        """
        # The output_data is usually a dict of {terminal_name: data}
        if isinstance(output_data, dict) and 'Out' in output_data:
            processed_image = output_data['Out']
        else:
            processed_image = output_data # Fallback if structure is unexpected

        if processed_image is not None and isinstance(processed_image, np.ndarray) and processed_image.size > 0:
            # Set the processed image in the output view
            self.output_view.setImage(processed_image, autoRange=True, autoLevels=True)
            print(f"Output image successfully updated. Shape: {processed_image.shape}, Data Type: {processed_image.dtype}")
        else:
            # Clear output if data is invalid (e.g., node unconnected)
            self.output_view.clear()
            print("Flowchart output is empty or invalid. Output view cleared.")


# --- 3. Run the Application ---
if __name__ == '__main__':
    # Register the custom node so it appears in the right-click menu library
    fc.registerNodeType(ImageScaleNode, [('Image Processing',)])
    
    app = QtWidgets.QApplication([])
    window = ImageFlowchartApp()
    window.show()
    
    # Start the event loop
    app.exec_()

