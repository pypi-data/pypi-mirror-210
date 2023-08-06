import numpy as np
import trimesh
try:
    import rasterio
except:
    rasterio = None
    
def to_mesh(surface, xs=None, ys=None, xcenter=None, ycenter=None, xscale=None, yscale=None):
    """Turns a surface grid, such as a dtm, into a mesh. Triangles will be
    generated with grid cell centers as vertices.
    
    surface: 2d array of elevation values. NaN values will result in missing triangles.
    
    xs: optional 2d array of x coordinates (same shape as surface)
    ys: optional 2d array of x coordinates (same shape as surface)
    
    Note that while the exact positions of the grid points can be arbitrarily specified using xs and ys,
    their ordering in x/y space must still be respected: If you reorder them triangles will overlap!
    
    Note that without xs, and ys specified, the image will be upside down (mirrored) compared
    to plt.imshow(surface), gltf has y growing upwards, and imshow downwards.
    
    Alternatively, surface can be a path to a geotiff, in which case
    coordinates are those of the geotiff.

    xcenter: subtracted from all x coordinates
    ycenter: subtracted from all y coordinates
    xscale: x coordinates are scaled by this value after subtraction of xcenter (output units per input unit)
    yscale: y coordinates are scaled by this value after subtraction of ycenter (output units per input unit)
    
    """

    if isinstance(surface, str):
        assert rasterio is not None, "Please install rasterio to be able call to_mesh() on geotiffs."
        with rasterio.open(surface) as src:
            surface = src.read(1)

            surface = np.where(surface == src.nodata, np.nan, surface)

            height = surface.shape[0]
            width = surface.shape[1]
            cols, rows = np.meshgrid(np.arange(width), np.arange(height))
            xs, ys = rasterio.transform.xy(src.transform, rows, cols)

            xs = np.array(xs)
            ys = np.array(ys)

    return array_to_mesh(surface, xs, ys)

            
def array_to_mesh(surface, xs=None, ys=None, xcenter=None, ycenter=None, xscale=None, yscale=None):

    if xs is None:
        xs, ys = np.meshgrid(np.arange(surface.shape[1]), np.arange(surface.shape[0]))

    if xcenter is not None: xs = xs - xcenter
    if ycenter is not None: ys = ys - ycenter
    if xscale is not None: xs = xs * xscale
    if yscale is not None: ys = ys * yscale
    
    if ys[0,0] > ys[-1,0]:
        surface = surface[::-1,:]
        xs = xs[::-1,:]
        ys = ys[::-1,:]
    if xs[0,0] > xs[0,-1]:
        surface = surface[:,::-1]
        xs = xs[:,::-1]
        ys = ys[:,::-1]
    
    idxs = np.arange(surface.shape[0] * surface.shape[1]).reshape(surface.shape)

    bottom_left = idxs[:-1,:-1].flatten()
    bottom_right = idxs[:-1,1:].flatten()
    top_left = idxs[1:,:-1].flatten()
    top_right = idxs[1:,1:].flatten()


    faces = np.vstack((
        np.column_stack((bottom_left, bottom_right, top_left)),
        np.column_stack((top_left, bottom_right, top_right))))
        
        
    vertices = np.column_stack((xs.flatten(), ys.flatten(), surface.flatten()))

    nanvertices = np.isnan(vertices).max(axis=1)

    faces = faces[~((nanvertices[faces[:,0]] | nanvertices[faces[:,1]] | nanvertices[faces[:,2]]))]

    return trimesh.Trimesh(vertices=vertices,
                           faces=faces)
