# Dehazer

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)                 
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)   


## Functionality of the Dehazer

- Removes Haze and Fog and enhances quality of Videos/Images.
- Removes Background and enhances quality of Videos/Images.

## Usage

- Make sure you have Python installed in your system.
- Run Following command in the CMD.
 ```
  pip install Dehaze
  ```
## Implementation

 ```
# test.py
# 0 for Dehazing and 1 for Remove Background
import Dehaze
Dehaze.dhazei(img,0)     #Input:image Output:image
Dehaze.dhazei(img,1)

Dehaze.dhaze("gggg.jpg",0)   #Input:path Output:image
Dehaze.dhaze("gggg.jpg",1)

Dehaze.vdhaze("vv.mp4",0)     #Input:path Output:output.mp4 in root directory
Dehaze.vdhaze("vv.mp4",1)

  ```

## Example
 ```
import Dehaze
import cv2

img = cv2.imread("gggg.jpg", cv2.IMREAD_COLOR) 
z=Dehaze.dhazei(img,1)
cv2.imshow('Dehazed_image', z)                     #Input:image Output:image
cv2.waitKey(0)


z=Dehaze.dhaze("gggg.jpg",1)
cv2.imshow('Dehazed_image', z)                    #Input:path Output:image
cv2.waitKey(0)


Dehaze.vdhaze("vv.mp4",1)                         #Input:path Output:output.mp4 in root directory
Dehaze.vdhaze("vv.mp4",0)


 ```

## Screenshots
<table align="center">
<tr>
    <td align="center">&nbsp;<img src="https://private-user-images.githubusercontent.com/91942072/241586034-9213dd87-4639-4621-a81e-ffc626e5f51c.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJrZXkxIiwiZXhwIjoxNjg1MzA2NTQ1LCJuYmYiOjE2ODUzMDYyNDUsInBhdGgiOiIvOTE5NDIwNzIvMjQxNTg2MDM0LTkyMTNkZDg3LTQ2MzktNDYyMS1hODFlLWZmYzYyNmU1ZjUxYy5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBSVdOSllBWDRDU1ZFSDUzQSUyRjIwMjMwNTI4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDIzMDUyOFQyMDM3MjVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05NTc3YmQ0ZmM0MDRhYzAxZTUzMjQxNTZjZjQ4MWEwZGMxN2YxNTZhYTY2OTY5NmE5MzZhYTFhOWNiNGQxODA4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.CKdHpfVvNrKL-IO7v48wFUzRPGVesJFMHxNkxt4r8Tk" alt="parmishh" /></td>
 <td align="center">&nbsp;<img src="https://private-user-images.githubusercontent.com/91942072/241586031-77e13118-a43e-4b3c-a7bf-ca69e21ad59e.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJrZXkxIiwiZXhwIjoxNjg1MzA2NTQ1LCJuYmYiOjE2ODUzMDYyNDUsInBhdGgiOiIvOTE5NDIwNzIvMjQxNTg2MDMxLTc3ZTEzMTE4LWE0M2UtNGIzYy1hN2JmLWNhNjllMjFhZDU5ZS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBSVdOSllBWDRDU1ZFSDUzQSUyRjIwMjMwNTI4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDIzMDUyOFQyMDM3MjVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lYWYwZWYzM2FlMDJlNTU4MjA5OGY0MzBmODk1MTRjNTFmNmUwOThhNzIxYzA2YmU4NzY3YWIzODY3OGE4ODRmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.2lG_CaR8wmXpcqj0hfTw2cnVFAOvzIIlc0Ih6WIr4jk"  alt="parmishh" /></td>
</tr>
</table>
<table align="center">
<tr>
    <td align="center">&nbsp;<img  src="https://private-user-images.githubusercontent.com/91942072/241587779-404a6151-5dbe-4f6f-accf-efc6b34e1584.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJrZXkxIiwiZXhwIjoxNjg1MzA4MTY2LCJuYmYiOjE2ODUzMDc4NjYsInBhdGgiOiIvOTE5NDIwNzIvMjQxNTg3Nzc5LTQwNGE2MTUxLTVkYmUtNGY2Zi1hY2NmLWVmYzZiMzRlMTU4NC5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBSVdOSllBWDRDU1ZFSDUzQSUyRjIwMjMwNTI4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDIzMDUyOFQyMTA0MjZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1kZDNiZmY5ZmE3N2RhMzYwZjViNWU1YTY4MDQ0MTE5OWVhNmQyMzllMWI2ZTMzMmM4MjRjYTg0YzgwNzQ3MmUwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.9eRTYufU__MIE2NKqeAwEgXPPUEdTfWy4EtF7kD3DAM" alt="parmishh" /></td>
 <td align="center">&nbsp;<img  src="https://private-user-images.githubusercontent.com/91942072/241587776-ed760c72-39fd-4417-91d8-8a4f703779d5.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJrZXkxIiwiZXhwIjoxNjg1MzA4MTY2LCJuYmYiOjE2ODUzMDc4NjYsInBhdGgiOiIvOTE5NDIwNzIvMjQxNTg3Nzc2LWVkNzYwYzcyLTM5ZmQtNDQxNy05MWQ4LThhNGY3MDM3NzlkNS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBSVdOSllBWDRDU1ZFSDUzQSUyRjIwMjMwNTI4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDIzMDUyOFQyMTA0MjZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yOGM5MDNiMWRhN2UwYjc0ODMzNDlmMWJjODFlOGY2MTc3ZTY4M2MzYTI1N2FlMDVlNjdmMzlkODc4MGYyMDVkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.2AiNREUNC8o1peToW3VfwilhtfxBT7FGenqNnbUgRoY"  alt="parmishh" /></td>
</tr>
</table>
