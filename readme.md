# Hip Cartilage Labrum Segmentation

[![DOI](https://zenodo.org/badge/896065736.svg)](https://doi.org/10.5281/zenodo.14316889)

Welcome to the **Hip Cartilage Labrum Segmentation** repository! This project provides code for preprocessing, training, and evaluation of hip cartilage and labrum segmentation using MP2RAGE and TRUFI MR images. It leverages the powerful [nnU-Net](https://github.com/MIC-DKFZ/nnUNet/tree/v1.7.1) framework.

## Reference Framework

This work is based on nnU-Net, a self-configuring method for deep learning-based biomedical image segmentation:

> Isensee, F., Jaeger, P. F., Kohl, S. A., Petersen, J., & Maier-Hein, K. H. (2020).  
> **nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation.** *Nature Methods, 1-9.*

## Related Publication

For detailed insights into the segmentation process, please refer to our paper:  
[A deep learning approach for automatic 3D segmentation of hip cartilage and labrum from direct hip MR arthrography](https://doi.org/10.1038/s41598-025-86727-z)


---

### Key Features

- **Preprocessing**: Tools for preparing MR images for segmentation.  
- **Training**: Customizable scripts for training nnU-Net on MP2RAGE and TRUFI datasets.  
- **Evaluation**: Robust evaluation tools to validate segmentation performance.  

---

### Citation

If you find this repository useful, kindly cite our paper:  

```plaintext
@article{meier_deep_2025,
	title = {A deep learning approach for automatic {3D} segmentation of hip cartilage and labrum from direct hip {MR} arthrography},
	volume = {15},
	issn = {2045-2322},
	url = {https://www.nature.com/articles/s41598-025-86727-z},
	doi = {10.1038/s41598-025-86727-z},
	language = {en},
	number = {1},
	urldate = {2025-02-10},
	journal = {Sci Rep},
	author = {Meier, Malin Kristin and Helfenstein, Ramon Andreas and Boschung, Adam and Nanavati, Andreas and Ruckli, Adrian and Lerch, Till D. and Gerber, Nicolas and Jung, Bernd and Afacan, Onur and Tannast, Moritz and Siebenrock, Klaus A. and Steppacher, Simon D and Schmaranzer, Florian},
	month = feb,
	year = {2025},
	pages = {4662},
}
```  

Feel free to contribute, report issues, or provide feedback! 🎉
