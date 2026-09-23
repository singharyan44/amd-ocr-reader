# Mandated ROCm base — checked by layer identity at grading. DO NOT change,
# DO NOT squash/flatten (destroys the layer identity they verify).
FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0

ENV HF_HOME=/models DEBIAN_FRONTEND=noninteractive
WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app/ /app/
RUN mkdir -p /models /app/input /app/output
EXPOSE 8000
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
