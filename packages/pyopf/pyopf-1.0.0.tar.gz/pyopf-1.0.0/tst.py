import numpy as np
from pathlib import Path
from pyopf.pointcloud import GlTFPointCloud

pcl = GlTFPointCloud.open(Path('dense_pcl/dense_pcl.gltf'))

# Generate a new point attribute as a random vector of 0s and 1s
# The attribute must have one scalar per point
new_attribute = np.random.randint(0, 2, size=len(pcl.nodes[0]))

# The attribute must have the shape (number_of_points, 1)
new_attribute = new_attribute.reshape((-1, 1))
# Supported types for custom attributes are np.float32, np.uint32, np.uint16, np.uint8
new_attribute = new_attribute.astype(np.uint32)

# Set the new attribute as a custom attribute for the node
# By default, nodes might be missing custom attributes, so the dictionary might have to be created
if pcl.nodes[0].custom_attributes is not None:
    pcl.nodes[0].custom_attributes['point_class'] = new_attribute
else:
    pcl.nodes[0].custom_attributes = {'point_class': new_attribute}

pcl.write(Path('out/out.gltf'))
