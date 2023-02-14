# CMRPACK 2.0 Advanced Smart City
Detect and track bikes, vehicles and pedestrians. Object tracking recognizes the same object across successive frames. Detects collisions and near misses. A real-time dashboard visualizes the intelligence extracted from the traffic intersection along with annotated video streams.

### Requirements (You must have)
| Name          | Details                                                     |
|---------------|-------------------------------------------------------------|
| OS:           | Windows 10, 11*, macOS 11, 12 Ubuntu 18.04(LTS), 20.04(LTS) |
| CPU           | 6th to 13th generation Intel Core processor                 |
| PaaS          | Docker, Docker Desktop, DockerHub                           |

Please visit <a href="https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/system-requirements.html">openvino-toolkit system-requirements</a> page for more.


### Additional Software Requirements

A Linux environment needs these components:

```
• GNU Compiler Collection (GCC)* 7.5 for Ubuntu 18, 8.4 for RHEL* 8, 9.3 for Ubuntu 20
• CMake* 3.13 or higher
• Python 3.7-3.10
• OpenCV 4.5
```

A Windows environment needs these components:

```
• Microsoft Visual Studio* 2019
• CMake 3.14 or higher (64 bit)
• Python 3.7-3.10
• OpenCV 4.5
• Intel® HD Graphics Driver (Required only for GPUs.)
```

A macOS environment needs these components:

```
• CMake 3.13 or higher 
• Xcode* 10.3  
• OpenCV 4.5  
• Python 3.7-3.10
```

## Supported AI Models
| Title                                        | Labels                                   |
|----------------------------------------------|------------------------------------------|
| person-vehicle-bike-detection-2000           | 0 - vehicle, 1 - person, 2 - bike        |
| person-vehicle-bike-detection-2001           | 0 - vehicle, 1 - person, 2 - bike        |
| person-vehicle-bike-detection-2002           | 0 - vehicle, 1 - person, 2 - bike        |
| person-vehicle-bike-detection-crossroad-0078 | 1 - person,  2 - vehicle, 3 - bike       |
| person-vehicle-bike-detection-crossroad-1016 | 0 - non-vehicle, 1 - vehicle, 2 - person |

## Setup & run
If you have all the required hardware then open a command prompt and run this command:
```commandline
docker run -p 8000:8000 imammasleap/cmrpack:v3
```
When you will get this message on the command prompt.
```commandline
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

Open a web browser (Recommender Google Chrome or Microsoft Edge) and enter this url. 
```commandline
http://localhost:8000/
```


## References
* <a href="https://docs.docker.com/desktop/install/windows-install/">Docker Install on Window</a>
* <a href="https://visualstudio.microsoft.com/downloads/">Microsoft Visual Studio* with C++ 2019 or 2017 with MSBuild</a>

## Docker
