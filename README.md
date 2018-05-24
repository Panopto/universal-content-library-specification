# universal-content-library-specification
=======================================

This package contains the UCLS/UCS specifications, associated tools, sample UCLS/UCS, and unit tests to help you get started in generating or consuming UCLS content libraries.

## Installation
To use this package, clone this repository.

#### Prerequisites
The python scripts in this package require the packages enumerated in requirements.txt. To install those packages, run the following:

`$ pip install -r requirements.txt`

## Getting Started
The tools folder contains Python scripts for validating a UCLS library. I.e. given a root folder containing media files and UCLS xml files describing those media files, the validator.py will validate that those xml files are valid UCLS xml files and that the media files they describe exist where they should be. The samples folder contains various examples of such (albeit simple) UCLS libraries. Both can be seen in action by running the following:

```
$ cd <package folder>\tools\validator
$ python validator.py -l "..\..\..\samples\video-only\library.xml" -t unc -o "output.log"
```

You should see the following output:

```
Performing validation...
<Path to package folder>\samples\video_only
Everything looks good!
```

The scrypt also supports validaing a library in AWS S3. The command line for that would look similar to the following:

```$ Python -l <path to library xml file> -b <bucket> -a <your access key> -k <your secret key> -t s3 -o "output.log"```

## Schemas
The schemas folder contain XSD files that constitute the UCLS and UCS specifications. They are described below.

### universal-content-library-1.0.xsd
This XSD defines the schema for a UCLS Library. In addition to defining the schema for a top level xml from which a library definition begins (i.e. where parsing starts), it also defines basic types used in the other XSD files.

### universal-content-directory-1.0.xsd
This XSD defines the schema for a UCLS Directory (session folder). A UCLS Directory can have other UCLS Directories as subdirectories and/or sessions that belong to that folder.

### universal-capture-2.0.xsd
This XSD defines the schema for a session.

### Generating code from XSD
Many languages support automatic code generation from XSDs, and this typically will consitute the easiest way to quickly begin working with UCS and UCLS content.

#### C# 
If you plan on building tooling for UCLS library processing, you could auto-generate .cs files for them with the xsd.exe that comes with a Windows SDK. Below is an example:

```$ "C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.6 Tools\x64\xsd.exe" /classes "universal-capture-2.0.xsd"```

This will output a universal-capture-2.0.cs file you can use to serialize/deserialize a UCS xml file.

#### Python
lxml provides the necessary functionality to do this fairly easily. Please see the validator tool for an example of how to do this.

## UCLS Library Samples
The package comes with sample UCLS libraries to provide examples of what UCLS and UCS xml files look like and how they're structured. Please see the samples folder

All sample media files are derived from https://github.com/mathiasbynens/small

## Running the Unit Tests
This package contains a unit test suite via pytest runner to validate the tooling against provided test content. To run all the tests, do the following:

```
$ cd <package folder>\tools\validator
$ pytest
```

You should see an output like the following:

```
test_validator.py ......                                                 [100%]

========================== 6 passed in 3.47 seconds ===========================
```
