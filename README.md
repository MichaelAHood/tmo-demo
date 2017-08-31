# FaceNet

This is a working example of facial detection and recognition running on TensorFlow and OpenCV.  Working on OSX and Nvidia Jetson TX2 platforms.

## Installation

- Install Nvidia CUDA and CUDNN packages if using GPU enabled
  TensorFlow on a capable machine.
- Install TensorFlow (tested with version 1.0.0.).  Installed via Python
  requirements.txt file below.
- Install OpenCV (tested with version 3.2.0).  Installed via Homebrew on
  OSX (Apple).
- Clone FaceNet repo and add src PYTHONPATH.

```bash
# Install Python dependencies.
$ pip install -r requirements.txt

# Install OpenCV3 via Homebrew on OSX.
$ brew tap homebrew/science
# Other options like --with-gstreamer can be added if dependencies available.
$ brew install --force opencv3 --with-contrib --with-python --with-vtk
# Add libraries to PYTHONPATH to get picked up in shell profile.
$ vi ~/.bash_profile
export PYTHONPATH=/usr/local/Cellar/opencv3/3.2.0/lib/python2.7/site-packages:$PYTHONPATH
$ source ~/.bash_profile

# Clone Facenet repo and add to PYTHONPATH.
$ git clone https://github.com/davidsandberg/facenet.git
# .bash_profile and/or ~/.bashrc.
$ vi ~/.bash_profile
export PYTHONPATH=<facenet_dir>/src:$PYTHONPATH
$ source ~/.bash_profile
```

Noticed an issue with Nvidia CUDA libraries not getting picked up
appropriately even though in path on OSX El Capitan.  Fix was to disable OSX SIP as follows.

http://stackoverflow.com/questions/33476432/is-there-a-workaround-for-dtrace-cannot-control-executables-signed-with-restri

```
Although not recommended by Apple, you can entirely disable System Integrity Protection on you Mac. Here's how:

Boot your Mac into Recovery Mode: reboot it and hold cmd+R until a progress bar appears.
Go to Utilities menu. Choose Terminal there.
Enter this command to disable System Integrity Protection:
$ csrutil disable

It will ask you to reboot — do so and you're free from SIP!
```


## Usage

Scripts have capability to run the FaceNet model locally or against a Flask web service.  Seems to run a little
faster without the overhead of passing images to backend service.

Standalone Mode

```bash
# Run without Flask web service backend (self-contained standalone).
$ ./test-opencv-facenet.py
```

Web Service Mode

```bash
# Or if running with Flask, start up web service backend for FaceNet services.
$ ./flask-image-detection.py

# Start up client desktop app in separate terminal (set environment variable PK_ENABLE_WS).
$ PK_ENABLE_WS=1 ./test-opencv-facenet.py
```

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History

TODO: Write history

## Credits

TODO: Write credits

## License

TODO: Write license
