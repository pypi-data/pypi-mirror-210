ssh maker@192.168.1.203 "rm -rf /home/maker/.local/lib/python3.9/site-packages/MakerToolbox"
scp -r src/MakerToolbox maker@192.168.1.203:/home/maker/.local/lib/python3.9/site-packages/