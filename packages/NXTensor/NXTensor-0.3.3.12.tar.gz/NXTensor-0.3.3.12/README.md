# NXTensor

NXTensor is a tensor making framework based on Xarray.
It automates the extraction of multichannel images (tensors) from NetCDF time series of geolocated data.

## License

See LICENSE file.

## Authors

* Sébastien Gardoll

Software Engineer at [IPSL](https://www.ipsl.fr/en/)
contact: sebastien@gardoll.fr

## Requirements

- netcdf data files (all variables):
    - with the same period of time covered
    - with the same metadata names and properties

## Direct dependencies

The tested version in parenthesis.

- Python 3.7 (3.7.7)
- Dask (2.17.2)
- H5py (2.10.0)
- Matplotlib (3.3.2)
- Netcdf4 (1.5.3)
- Numpy (1.18.1)
- Pandas (1.0.3)
- Pyyaml (5.3.1)
- Scikit-learn (0.22.1)
- Scipy (1.4.1)
- Xarray (0.15.1)

## Conda dependencies installation script

```bash
YOUR_ENV_NAME='env_name'
conda create -n ${YOUR_ENV_NAME} python=3.7
conda install -n ${YOUR_ENV_NAME} dask h5py matplotlib netcdf4 numpy pandas pyyaml scikit-learn scipy xarray
conda activate ${YOUR_ENV_NAME}
```
