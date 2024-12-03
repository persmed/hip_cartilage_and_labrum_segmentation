import warnings
import numpy as np
import SimpleITK as sitk

def cropRoi(img, destSize = None, phyCenter = None, indexCenter = None, checkLabels = False):
    """
    1.11.2022
    This function crops an image without resampling to avoid loss of information.
    It can also extend an image compared to sitk.RegionOfInterest
    Paramters:
    img: simple itk image
    destSize: size of the new image, same size as input when not defined
    phyCenter: the pysical center for the image. In world coordinates. List/tuple of 3 floats
    indexCenter: the index of the input image, which is the new center of the new image.
    List/tuple of 3 floats. Overwritten by phyCenter when specified.
    checkLabels: Checks if some labels are crpped away or the size has changed.
    return: resampled sitk image
    """
    sourceSize = np.array(img.GetSize())
    
    if destSize is None:
        destSize = np.array(img.GetSize())
    
    if phyCenter is not None:
        centerIndex = np.array(img.TransformPhysicalPointToIndex(phyCenter.tolist()))
    elif indexCenter is not None:
        centerIndex = np.array(indexCenter)
    else:
        centerIndex = sourceSize/2
    
    start = np.ceil(centerIndex - np.array(destSize)/2) 
    end = np.ceil(centerIndex + np.array(destSize) /2)

    destIndexStart = np.zeros(len(centerIndex),dtype =int)
    destIndexEnd = np.zeros(len(centerIndex),dtype =int)   
    sourceIndexStart = np.zeros(len(centerIndex),dtype =int)
    sourceIndexEnd = np.zeros(len(centerIndex),dtype =int)
    
    for i in range(len(destIndexStart)):
        
        if start[i] > 0:
            destIndexStart[i] = 0
        else:
            destIndexStart[i] = -start[i]
            
        if sourceSize[i] -end[i]  >= 0:
            destIndexEnd[i] = 0
        else:
            destIndexEnd[i] = sourceSize[i] -end[i]
            
        if start[i] > 0:
            sourceIndexStart[i] = start[i] 
        else:
            sourceIndexStart[i] = 0
            
        if end[i] - sourceSize[i] < 0:
            sourceIndexEnd[i] = end[i]
        else:
            sourceIndexEnd[i] = 0
    
    sourcenp = sitk.GetArrayFromImage(img)
    destnp = np.zeros(np.flip(destSize), dtype = np.int16)
    
    destIndexStart = np.flip(destIndexStart)
    destIndexEnd = np.flip(destIndexEnd)
    sourceIndexStart = np.flip(sourceIndexStart)
    sourceIndexEnd = np.flip(sourceIndexEnd)
    
    destobj = []
    sourceobj= []
    
    for i in range(len(destIndexStart)):
        destobj.append(slice(destIndexStart[i],destIndexEnd[i] if destIndexEnd[i] != 0 else None))
        sourceobj.append(slice(sourceIndexStart[i],sourceIndexEnd[i] if sourceIndexEnd[i] != 0 else None))

    destnp[tuple(destobj)] = sourcenp[tuple(sourceobj)]
    
    
    dest = sitk.GetImageFromArray(destnp)
    
    #dest.CopyInformation(img)
    dest.SetSpacing(img.GetSpacing())
    dest.SetDirection(img.GetDirection())
    #dest.SetOrigin(img.GetOrigin())
    dest.SetOrigin(img.TransformIndexToPhysicalPoint(start.astype(int).tolist()))
    
    if checkLabels:
        destFilter = sitk.LabelShapeStatisticsImageFilter()
        destFilter.Execute(dest)
        sourceFilter = sitk.LabelShapeStatisticsImageFilter()
        sourceFilter.Execute(img)
        for i in sourceFilter.GetLabels():
            if destFilter.HasLabel(i):
                delta = (destFilter.GetPhysicalSize(i)-sourceFilter.GetPhysicalSize(i))/sourceFilter.GetPhysicalSize(i)*100
                if(abs(delta) > 0.01):
                    warnings.warn("Label{0} has a differnt size of {1:2.2f}%".format(i,delta))
            else:
                warnings.warn("Cropped image has no Label {}".format(i))

    
    return dest


def changeImageOrientationAndSpacing(img, new_spacing = None, new_orientation = None,  interpolator = sitk.sitkLinear):
    """
    1.11.2022
    Changing imgage spacing and/or orientation/direction. Both operation needs resampling and some accuracy can be lost.
    For label images sitk.sitkNearestNeighbor inerpolator should be used.(<1% Volume error)
    Paramters:
    img: simple itk image
    new_spacing: list/tuple of 3 floats
    new_orientation: list/tuple of 9 floats
    interpolator: simple itk interploator
    return: resampled sitk image
    """
    
    if new_spacing is None:
        new_spacing = img.GetSpacing()
        
    if new_orientation is None:
        new_orientation = img.GetDirection()
    
    affine_center = img.TransformContinuousIndexToPhysicalPoint(np.array(img.GetSize())/2.0)
    affine_translation = [0.0, 0.0 ,0]
    affine = sitk.AffineTransform(new_orientation, affine_translation, affine_center)
   
    extreme_points = [img.TransformIndexToPhysicalPoint((0,0,0)), 
                      img.TransformIndexToPhysicalPoint((0,0,img.GetSize()[2])),
                      img.TransformIndexToPhysicalPoint((0,img.GetSize()[1],0)),
                      img.TransformIndexToPhysicalPoint((0,img.GetSize()[1],img.GetSize()[2])),
                      img.TransformIndexToPhysicalPoint((img.GetSize()[0],0,0)), 
                      img.TransformIndexToPhysicalPoint((img.GetSize()[0],0,img.GetSize()[2])),
                      img.TransformIndexToPhysicalPoint((img.GetSize()[0],img.GetSize()[1],0)),
                      img.TransformIndexToPhysicalPoint((img.GetSize()[0],img.GetSize()[1],img.GetSize()[2]))]
    
    inv_affine = affine.GetInverse()
    extreme_points_transformed = [inv_affine.TransformPoint(pnt) for pnt in extreme_points]
    
    min_x = min(extreme_points_transformed)[0]
    min_y = min(extreme_points_transformed, key=lambda p: p[1])[1]
    min_z = min(extreme_points_transformed, key=lambda p: p[2])[2]
    max_x = max(extreme_points_transformed)[0]
    max_y = max(extreme_points_transformed, key=lambda p: p[1])[1]
    max_z = max(extreme_points_transformed, key=lambda p: p[2])[2]

    output_spacing = new_spacing
    output_origin = [min_x, min_y,min_z]
    output_origin = affine.TransformPoint(output_origin)
    output_size = [int((max_x-min_x)/output_spacing[0]), int((max_y-min_y)/output_spacing[1]),int((max_z-min_z)/output_spacing[2])]

    resample = sitk.ResampleImageFilter()
    resample.SetInterpolator(interpolator)
    resample.SetOutputDirection(new_orientation)
    resample.SetOutputOrigin(output_origin)
    resample.SetOutputSpacing(output_spacing)
    resample.SetSize(output_size)
    
    return resample.Execute(img)

    
    """
    #Linear interpolation label per label. Leads to very similar result compared to sitkNearestNeighbor
        if not label:
        return resample.Execute(img)
    
    labelFilter = sitk.LabelShapeStatisticsImageFilter()
    labelFilter.Execute(img)
    labels = labelFilter.GetLabels()
    combined = np.zeros(np.flip(new_size),dtype = np.int16)

    for l in labels:
        labels_np = sitk.GetArrayFromImage(img)
        labels_np[labels_np != l] = 0
        labels_np[labels_np == l] = 1
        
        label_sitk = sitk.GetImageFromArray(labels_np)
        label_sitk.CopyInformation(img)
        label_sitk = sitk.Cast(label_sitk, sitk.sitkFloat32)
        resampled_label_sitk = resample.Execute(label_sitk)
        
        resampled_label_np = sitk.GetArrayFromImage(resampled_label_sitk)
        
        combined[resampled_label_np >= 0.5] = l

    combined_sitk = sitk.GetImageFromArray(combined)
    combined_sitk.CopyInformation(resampled_label_sitk)
    combined_sitk = sitk.Cast(combined_sitk, sitk.sitkUInt16)
        
    
    return combined_sitk
    """
    
def AmiraFlip(img):
    """
    1.11.2022
    When exporting nifi files from Amira the images is rotated 180° around the z axis.
    This function mimics this behavior. Appling on a already flipped image restores the original orientation,
    because it then rotated twice by 180° -> 360°
    To avoid any loss of image information no resampling is used just the metha data is modified. 
    Paramters:
    img: simple itk image
    return: resampled sitk image
    """
    
    #ensure deep copy
    nda = sitk.GetArrayFromImage(img)
    img2 = sitk.GetImageFromArray(nda)
    img2.CopyInformation(img)
    
    affine = sitk.Euler3DTransform((0,0,0), 0, 0, np.pi, (0,0,0))

    output_spacing = img.GetSpacing()
    matrix = np.array(affine.GetMatrix()).reshape((3, 3))
    direction = np.array(img.GetDirection()).reshape((3, 3))
    output_direction = (matrix@direction).reshape(9)
    output_size = img.GetSize()
    output_origin = affine.TransformPoint(img.GetOrigin())
    output_direction = tuple(round(it,15) for it in output_direction)

    #Apply image rotation of 180° arond Z axis
    img2.SetOrigin(output_origin)
    img2.SetDirection(output_direction)
    
    #Permute and rotate axis
    #Note sure if its always fliping and permuting the same or
    #or amira tries to have for example a LAS etc. format
    img2 = sitk.PermuteAxes(img2, [2,0,1])
    img2 = sitk.Flip(img2,[True,False,True])
    
    return img2

def Rotate(img, axes = 0, angle = 0):
    """
    1.11.2022
    This function rotates the images around a given axis by a given angle in radian.
    This is a generalized version of AmiraFlip
    To avoid any loss of image information no resampling is used just the metha data is modified. 
    Paramters:
    img: simple itk image
    return: resampled sitk image
    """
    #ensure deep copy
    nda = sitk.GetArrayFromImage(img)
    img2 = sitk.GetImageFromArray(nda)
    img2.CopyInformation(img)
    
    center = img2.TransformIndexToPhysicalPoint((np.array(img2.GetSize())/2).astype(int).tolist())
    
    if axes == 2:
        affine = sitk.Euler3DTransform(center, 0, 0, angle, (0,0,0))
    elif axes == 1:
        affine = sitk.Euler3DTransform(center, 0, angle, 0, (0,0,0))
    else:
        affine = sitk.Euler3DTransform(center, angle, 0, 0, (0,0,0))

    output_spacing = img.GetSpacing()
    matrix = np.array(affine.GetMatrix()).reshape((3, 3))
    direction = np.array(img.GetDirection()).reshape((3, 3))
    output_direction = (matrix@direction).reshape(9)
    output_size = img.GetSize()
    output_origin = affine.TransformPoint(img.GetOrigin())
    output_direction = tuple(round(it,15) for it in output_direction)

    #Apply image rotation of 180° arond Z axis
    img2.SetOrigin(output_origin)
    img2.SetDirection(output_direction)
    
    return img2