## SPAI Project Template

This is a SPAI project template with the following services:

- **Scripts**
    - downloader: Downloads a Sentinel-2 image from Barcelona (runs once every day downloading new images when available).
    - ndvi: Computes and stores the NDVI of Sentinel-2 images (runs once every day computing the NDVI of all the new images).
- **Notebooks**
    - analytics: compute analytics and generate report.
- **APIs**
    - analytics: exposes the analytics as an API endpoint.
    - xyz: exposes the Sentinel-2 images and NDVI layers as an XYZ endpoint.
- **UIs**
    - map: displays the Sentinel-2 images and NDVI layers in a map.