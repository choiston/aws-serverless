cd /home/ubuntu/aws-serverless
sudo apt update
sudo apt install -y python3.12-venv

python3 -m venv .venv
source .venv/bin/activate
python -m pip install boto3
python -c "import boto3; print(boto3.__version__)"