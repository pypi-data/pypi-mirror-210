from scipy import ndimage
from matplotlib.transforms import Affine2D
import numpy as np

def symmetrize_2d(q1, q2, counts, theta_min, theta_max, skew_angle=90, inversion=True):
    # counts=counts.transpose()
    
    # Define Transformation
    skew_angle_adj = 90-skew_angle
    
    t = Affine2D()
    # Scale y-axis to preserve norm while shearing 
    t += Affine2D().scale(1,np.cos(skew_angle_adj*np.pi/180))
    # Shear along x-axis
    t += Affine2D().skew_deg(skew_angle_adj,0)
    # Return to original y-axis scaling
    t += Affine2D().scale(1,np.cos(skew_angle_adj*np.pi/180)).inverted()
    
    # Calculate the angle for each data point
    theta = np.arctan2(q1.reshape((-1, 1)), q2.reshape((1, -1)))

    # Create a boolean array for the range of angles
    symm_region = np.logical_and(theta >= theta_min*np.pi/180, theta <= theta_max*np.pi/180)
    
    # Calculate number of rotations needed to reconstruct the dataset
    if inversion:
        n_rots = abs(int(360/(theta_max-theta_min)/2))
    else:
        n_rots = abs(int(360/(theta_max-theta_min)))
    
    # Scale wedge to preserve norm after skewing
    counts_skew = ndimage.affine_transform(counts,
                                           t.inverted().get_matrix()[:2,:2],
                                           offset=[counts.shape[0]/2*np.sin(skew_angle_adj*np.pi/180), 0],
                                           order=0,
                                          )
    wedge = ndimage.affine_transform(counts_skew,
                                     Affine2D().scale(np.cos(skew_angle_adj*np.pi/180),1).get_matrix()[:2,:2],
                                     offset=[(1-np.cos(skew_angle_adj*np.pi/180))*counts.shape[0]/2, 0],
                                     order=0,
                                    )*symm_region
    
    reconstruct = np.zeros(counts.shape)
    for n in range(0,n_rots):
        reconstruct += wedge
        wedge = ndimage.rotate(wedge, 360/n_rots, reshape=False, order=0)
    
    if inversion:
        reconstruct += np.flip(reconstruct, axis=0)

    reconstruct = ndimage.affine_transform(reconstruct,
                                           Affine2D().scale(np.cos(skew_angle_adj*np.pi/180), 1).inverted().get_matrix()[:2,:2],
                                           offset=[-(1-np.cos(skew_angle_adj*np.pi/180))*counts.shape[0]/2/np.cos(skew_angle_adj*np.pi/180),0],
                                           order=0,
                                          )
    reconstruct = ndimage.affine_transform(reconstruct,
                                           t.get_matrix()[:2,:2],
                                           offset=[(-counts.shape[0]/2*np.sin(skew_angle_adj*np.pi/180)),0],
                                           order=0,
                                          )
    
    return reconstruct
    