OpenHDRISP: An Open-Source HDR Image Signal Processing Pipeline
Overview
OpenHDRISP is an open-source Image Signal Processing (ISP) pipeline designed for high dynamic range (HDR) imaging. The project is modular, allowing users to customize and extend the pipeline with various processing modules. The pipeline is designed to handle RAW image data and perform a series of transformations, including RAW to RGB conversion, white balance, color space conversion, and more.

This README provides an overview of the project, its planned features, and how to use it.

Features
RAW to RGB Module:

No Demosaic (Default): Directly convert RAW data to RGB without applying any demosaicing.

Basic Demosaic: Apply a simple bilinear demosaicing algorithm to interpolate missing color values.

Camera RGB to XYZ Module:

Direct Conversion: Convert camera RGB to XYZ using the camera's color calibration matrix and exposure parameters.

AWB RGB to XYZ: First apply automatic white balance (AWB) to the camera RGB, then convert the balanced RGB to XYZ.

XYZ to RGB Module:

PQ EOTF (Default): Convert XYZ to RGB using the Perceptual Quantizer (PQ) electro-optical transfer function (EOTF) for HDR imaging.

Project Plan
Phase 1: Core Modules Development
RAW to RGB Module:

Implement the no-demosaic option.

Implement a basic bilinear demosaicing algorithm.

Camera RGB to XYZ Module:

Implement direct conversion using the camera's color calibration matrix and exposure parameters.

Implement AWB RGB to XYZ conversion.

XYZ to RGB Module:

Implement XYZ to RGB conversion using the PQ EOTF.

Phase 2: Pipeline Integration
Integrate all modules into a single ISP pipeline.

Add support for dynamic module loading via a configuration file.

Implement a command-line interface (CLI) for easy usage.

Phase 3: Optimization and Testing
Optimize the pipeline for performance.

Test the pipeline with various RAW images and HDR content.

Add unit tests and continuous integration (CI) for automated testing.

Phase 4: Documentation and Community Support
Write detailed documentation for each module and the pipeline.

Create tutorials and examples for common use cases.

Set up a community forum or issue tracker for user support.