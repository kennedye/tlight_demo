FROM arm64v8/python:3
RUN python3 -m pip install --no-cache-dir rpi.gpio
COPY t_light_pod.py ./
CMD [ "python3", "./t_light_pod.py" ]
